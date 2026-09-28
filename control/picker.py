"""Python control layer for the picker (issue #12): PC -> USB -> TMCM-3110 -> X/Y (LXR26), Z (LX20).

    from control.picker import Picker, SimBackend          # dry run, no hardware
    from control.picker import TrinamicBackend              # real TMCM-3110 via pytrinamic (usb_tmcl)

    pk = Picker(TrinamicBackend())
    pk.home()                    # Z to its reference switch, then X to park, then Y
    pk.move_abs("X", 12.5)       # tip coordinates in mm (design frame: tip x/y relative to the optical axis,
    pk.move_rel("Z", -3.0)       # z = tip height above the stage datum)
    pk.park()
    pk.stop()

Safety rules (docs/03 section 5, docs/06) are enforced here, not left to the caller:
  * nothing moves before home(); home() always runs Z -> X -> Y;
  * X/Y move only while the tip is at or above the safe-Z corridor lower bound;
  * Z goes above the reference height only at the X park position;
  * soft limits = the design tip travel (params.layout) and the Z floor.
All numbers come from cad/params.py (single source of truth).
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cad"))
import params as p  # noqa: E402

AXES = ("X", "Y", "Z")
AXIS_INDEX = {"X": 0, "Y": 1, "Z": 2}          # TMCM-3110 motor connectors 0/1/2
TOL = 1e-6


class SafetyError(RuntimeError):
    """A requested move would break one of the picker's safety rules; nothing was moved."""


def default_config(workflow="WB", head=None):
    """Axis limits and reference positions from params.py."""
    head = head or p.V1_HEAD
    L = p.layout(workflow)
    cr = p.corridor(head)
    z_ref = p.tip_at_ref(head)
    z_pick = p.well_bottom_z(p.HEAD_CONFIGS[head]["plate"]) + p.TIP_CLEAR_BOTTOM.v
    steps = {a: p.FULL_STEPS * p.MICROSTEPS / p.DRIVE[a]["lead"] for a in AXES}   # microsteps per mm
    return dict(
        steps_per_mm=steps,
        limits={"X": (L["x_min"], L["x_max"]), "Y": (L["y_min"], L["y_max"]),
                "Z": (z_pick, z_pick + L["stroke_z"])},
        # coordinate of each axis when its reference switch trips
        home={"X": L["x_max"], "Y": L["y_min"], "Z": z_ref},
        park_x=L["x_max"], z_ref=z_ref, z_safe=cr["lower"], z_floor=z_pick,
    )


class SimBackend:
    """Stands in for the controller: positions in microsteps, a log of commands."""

    def __init__(self):
        self.pos = {a: 0 for a in AXES}
        self.log = []

    def reference_search(self, axis):
        self.log.append(("ref", axis))
        self.pos[axis] = 0

    def move_to(self, axis, microsteps):
        self.log.append(("move", axis, microsteps))
        self.pos[axis] = microsteps

    def wait(self, axis):
        pass

    def stop(self, axis):
        self.log.append(("stop", axis))

    def position(self, axis):
        return self.pos[axis]


class TrinamicBackend:
    """ADI/Trinamic TMCM-3110 over USB via pytrinamic (pip install pytrinamic).  Reference-search mode,
    speeds and motor current must be set for the installed switches and motors before first use."""

    def __init__(self, interface="usb_tmcl", port="any", poll_s=0.02):
        from pytrinamic.connections import ConnectionManager
        from pytrinamic.modules import TMCM3110
        self._cm = ConnectionManager(f"--interface {interface} --port {port}")
        self._iface = self._cm.connect()
        self.mod = TMCM3110(self._iface)
        self.poll_s = poll_s

    def reference_search(self, axis):
        i = AXIS_INDEX[axis]
        self.mod.start_reference_search(i)
        while self.mod.get_reference_search_status(i):
            time.sleep(self.poll_s)

    def move_to(self, axis, microsteps):
        self.mod.move_to(AXIS_INDEX[axis], int(round(microsteps)))

    def wait(self, axis):
        m = self.mod.motors[AXIS_INDEX[axis]]
        while not m.get_position_reached():
            time.sleep(self.poll_s)

    def stop(self, axis):
        self.mod.stop(AXIS_INDEX[axis])

    def position(self, axis):
        return self.mod.motors[AXIS_INDEX[axis]].get_actual_position()

    def close(self):
        self._cm.disconnect()


class Picker:
    def __init__(self, backend, config=None):
        self.b = backend
        self.c = config or default_config()
        self.homed = False
        self.pos = dict(self.c["home"])        # tip coordinates [mm] (valid after home())

    # ---------------------------------------------------------------- queries
    def position(self, axis=None):
        return dict(self.pos) if axis is None else self.pos[axis]

    # ---------------------------------------------------------------- motion
    def home(self, axis=None):
        """Home all axes in the safe order Z -> X -> Y.  Single-axis homing is allowed only for Z, or for
        X/Y once Z has been referenced (the tip is then above every plate at any XY)."""
        order = ("Z", "X", "Y") if axis is None else (axis,)
        if axis in ("X", "Y") and not self.homed:
            raise SafetyError("home Z (or all axes) first: X/Y must not move with the tip possibly in a well")
        for a in order:
            self.b.reference_search(a)
            self.pos[a] = self.c["home"][a]
        if axis is None:
            self.homed = True

    def move_abs(self, axis, value, wait=True):
        self._check(axis, value)
        self._go(axis, value, wait)

    def move_rel(self, axis, delta, wait=True):
        self.move_abs(axis, self.pos[axis] + delta, wait)

    def park(self):
        """Tip up to the reference height, then X to the park (capillary change) position."""
        self._require_homed()
        if self.pos["Z"] < self.c["z_ref"] - TOL:
            self._go("Z", self.c["z_ref"], True)
        self._go("X", self.c["park_x"], True)

    def stop(self):
        for a in AXES:
            self.b.stop(a)

    # ---------------------------------------------------------------- internals
    def _require_homed(self):
        if not self.homed:
            raise SafetyError("not homed: call home() first")

    def _check(self, axis, value):
        self._require_homed()
        if axis not in AXES:
            raise ValueError(f"unknown axis {axis!r}")
        lo, hi = self.c["limits"][axis]
        if not lo - TOL <= value <= hi + TOL:
            raise SafetyError(f"{axis}={value:.3f} mm is outside the soft limits {lo:.3f}..{hi:.3f} mm")
        if axis in ("X", "Y") and self.pos["Z"] < self.c["z_safe"] - TOL:
            raise SafetyError(f"raise Z to the safe height ({self.c['z_safe']:.2f} mm) before moving {axis}")
        if axis == "Z" and value > self.c["z_ref"] + TOL and self.pos["X"] < self.c["park_x"] - TOL:
            raise SafetyError("Z above the reference height is allowed only at the X park position "
                              "(near the optical axis the arm would hit the condenser)")
        if axis == "Z" and value < self.c["z_floor"] - TOL:
            raise SafetyError(f"Z below the floor ({self.c['z_floor']:.2f} mm)")

    def _go(self, axis, value, wait):
        steps = (value - self.c["home"][axis]) * self.c["steps_per_mm"][axis]
        self.b.move_to(axis, steps)
        if wait:
            self.b.wait(axis)
        self.pos[axis] = value
