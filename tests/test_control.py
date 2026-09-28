"""Control-layer safety rules, checked against the simulator backend (no hardware)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from control.picker import Picker, SafetyError, SimBackend, default_config  # noqa: E402


def homed():
    pk = Picker(SimBackend())
    pk.home()
    return pk


def test_nothing_moves_before_home():
    pk = Picker(SimBackend())
    with pytest.raises(SafetyError):
        pk.move_abs("X", 0.0)
    with pytest.raises(SafetyError):
        pk.home("X")


def test_home_order_is_z_x_y():
    pk = homed()
    assert [c[1] for c in pk.b.log if c[0] == "ref"] == ["Z", "X", "Y"]


def test_xy_needs_safe_z():
    pk = homed()
    c = pk.c
    pk.move_abs("X", 0.0)                     # at the reference height: allowed
    pk.move_abs("Z", c["z_floor"])            # down to pick height
    with pytest.raises(SafetyError):
        pk.move_abs("Y", 5.0)
    pk.move_abs("Z", c["z_safe"])
    pk.move_abs("Y", 5.0)


def test_z_above_reference_only_at_park():
    pk = homed()
    pk.move_abs("X", 0.0)
    with pytest.raises(SafetyError):
        pk.move_abs("Z", pk.c["z_ref"] + 5)
    pk.park()
    pk.move_abs("Z", pk.c["z_ref"] + 5)


def test_soft_limits_and_units():
    pk = homed()
    lo, hi = pk.c["limits"]["X"]
    with pytest.raises(SafetyError):
        pk.move_abs("X", hi + 1)
    pk.move_abs("X", hi - 10)
    # 10 mm on a 2 mm lead, 200 full steps x 16 microsteps -> -16000 microsteps from the X home (park)
    assert pk.b.pos["X"] == pytest.approx(-10 * default_config()["steps_per_mm"]["X"])
    assert default_config()["steps_per_mm"]["Z"] == pytest.approx(3200.0)
