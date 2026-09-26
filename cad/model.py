"""
Parametric stage-1 layout model: IX73 envelope + 96-well plate + external XYZ picker.

    python cad/model.py            -> STEP assemblies + per-part STL + parts.json in cad/out/

Parts are simple envelopes (boxes/cylinders).  Each part is tagged with
  category : for colouring / collision grouping
  status   : STD / MFR / DER / APX / PH / DES  (see params.py)
  group    : fixed | Y | X | Z   (which axis carries it)
The moving groups are built at the REFERENCE POSE (tip on the optical axis, at
pick height) and are moved by pure translation:
  Y group  += (0,  dy, 0)
  X group  += (dx, dy, 0)
  Z group  += (dx, dy, dz)
"""
from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import dataclass, field

from build123d import (Box, Compound, Cylinder, Location, Pos, Rot, Solid, Sphere,
                       export_step, export_stl)

sys.path.insert(0, os.path.dirname(__file__))
import params as p  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "out")

# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------

def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def zcyl(cx, cy, r, z0, z1):
    return Pos(cx, cy, (z0 + z1) / 2) * Cylinder(r, z1 - z0)


def rod(a, b, r):
    """Cylinder from point a to point b."""
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx - ax, by - ay, bz - az
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    c = Cylinder(r, L)  # along Z, centred
    # rotation taking +Z to direction d
    ux, uy, uz = dx / L, dy / L, dz / L
    tilt = math.degrees(math.acos(max(-1, min(1, uz))))
    yaw = math.degrees(math.atan2(uy, ux))
    return Pos((ax + bx) / 2, (ay + by) / 2, (az + bz) / 2) * Rot(0, 0, yaw) * Rot(0, tilt, 0) * c


def polyline_tube(pts, r):
    parts = [rod(pts[i], pts[i + 1], r) for i in range(len(pts) - 1)]
    parts += [Pos(*q) * Sphere(r) for q in pts[1:-1]]
    return parts


@dataclass
class Part:
    name: str
    solid: object
    category: str
    status: str
    group: str = "fixed"
    note: str = ""
    src: str = ""


@dataclass
class Model:
    variant: str
    condenser: str
    parts: list = field(default_factory=list)

    def add(self, *a, **k):
        self.parts.append(Part(*a, **k))

    def by_group(self, g):
        return [q for q in self.parts if q.group == g]


# ----------------------------------------------------------------------------
# head variants (capillary angle from vertical, measured in the XZ plane; holder
# leans outboard towards +X = towards the picker tower)
# ----------------------------------------------------------------------------
VARIANTS = {k: dict(theta=c["theta"], exposed=c["exposed"], od=c["od"], plate=c["plate"], scope=c["scope"],
                   label=c["label"]) for k, c in p.HEAD_CONFIGS.items()}   # single source: params.HEAD_CONFIGS
CONDENSER_CHOICES = ["IX2-LWUCD", "IX2-MLWCD", "IX-ULWCD", "NONE (pillar tilted back)"]

Z_PICK = p.WELL_BOTTOM_Z.v + p.TIP_CLEAR_BOTTOM.v  # tip z at reference pose

# frame / stacking layout: derived in params.layout(workflow) (single source of truth).
# Module-level names below are the DEFAULT workflow's values, kept for importers.
_L0 = p.layout(p.DEFAULT_WORKFLOW)
ARM_L = _L0["arm_l"]
ARM_T = p.ARM_T.v
ZB_W = 26.0              # Z actuator width (y)              [APX]
ZB_D = _L0["zb_d"]       # Z actuator depth (x)              [APX]
X_BAND = p.X_BAND        # X actuator y-band relative to tip y
XSB_BAND = p.XSB_BAND
X_Z = p.X_Z              # X actuator z (hangs under X support beam)
XSB_Z = p.XSB_Z          # X support beam z
TOWER_X = _L0["tower_x"]
Y_ACT_Z = p.Y_ACT_Z
BEAM_Z = p.BEAM_Z
POST_Y = _L0["post_y"]
TABLE_Z = -p.STAGE_TOP_ABOVE_TABLE.v


def head_geometry(theta_deg, exposed=None):
    """Key points of capillary / holder (tip at origin xy, z = Z_PICK).  exposed defaults to CAP_EXPOSED;
    pass the head configuration's exposed length (head_geometry_cfg) for exported heads."""
    L = p.CAP_EXPOSED.v if exposed is None else exposed
    t = math.radians(theta_deg)
    ux, uz = math.sin(t), math.cos(t)
    tip = (0.0, 0.0, Z_PICK)
    grip = p.CAP_L.v - L
    cap_top = ((L + grip) * ux, 0.0, Z_PICK + (L + grip) * uz)
    nose = (L * ux, 0.0, Z_PICK + L * uz)                                   # collet nose
    hold_top = ((L + p.HOLDER_AXIAL_LEN.v) * ux, 0.0, Z_PICK + (L + p.HOLDER_AXIAL_LEN.v) * uz)
    return dict(tip=tip, cap_top=cap_top, nose=nose, hold_top=hold_top, u=(ux, 0, uz), exposed=L)


def head_geometry_cfg(variant):
    c = p.HEAD_CONFIGS[variant]
    return head_geometry(c["theta"], c["exposed"])


def z_ref_dz(variant="R08", cond="IX-ULWCD"):
    """Tip lift from pick height (V1 plate) to the ONE physical reference switch."""
    return p.tip_at_ref(variant, cond) - Z_PICK


def arm_bottom_at_pick(variant):
    return head_geometry_cfg(variant)["hold_top"][2] - p.ARM_HALF_HEIGHT.v


# Z body is fixed on the X carriage at ONE height for every head configuration: its bottom sits below
# the lowest carriage position needed by the supported (V1 + experimental) configurations.
Z_BODY_BOTTOM = min(arm_bottom_at_pick(k) for k, c in p.HEAD_CONFIGS.items()
                    if c["scope"] in ("V1", "experimental")) - 10.0
# arm bottom when the carriage is on the reference switch (absolute, same for all configurations)
Z_REF_ARM_BOTTOM = p.z_ref_head_top() - p.TUBING_ABOVE_ARM.v - p.ARM_T.v


def build(variant="R08", condenser="IX-ULWCD", workflow=p.DEFAULT_WORKFLOW) -> Model:
    m = Model(variant, condenser)
    m.workflow = workflow
    LY = p.layout(workflow)
    ARM_L, TOWER_X, POST_Y = LY["arm_l"], LY["tower_x"], LY["post_y"]
    X_BODY_L, Y_BODY_L, Z_BODY_L = LY["x_body"], LY["y_body"], LY["z_body"]
    th = VARIANTS[variant]["theta"]
    hg = head_geometry_cfg(variant)

    # ------------------------------------------------------------------ IX73
    T = TABLE_Z
    m.add("optical_table_patch", box(-420, 820, -420, 420, T - 20, T), "table", "PH",
          note="optical table / breadboard surface, level = M1")
    m.add("ix73_body_lower", box(-p.IX73_W.v / 2, p.IX73_W.v / 2, p.BODY_Y_FRONT.v,
                                 p.BODY_Y_FRONT.v + p.IX73_D.v, T, -p.STAGE_T.v - 25),
          "ix73", "PH", note="W x D = 323 x 475 MFR; placement & height PH")
    m.add("ix73_stage", box(-p.STAGE_X.v / 2, p.STAGE_X.v / 2,
                            p.STAGE_CENTER_Y.v - p.STAGE_Y.v / 2, p.STAGE_CENTER_Y.v + p.STAGE_Y.v / 2,
                            -p.STAGE_T.v, 0.0),
          "ix73", "MFR", group="S", note="232 x 240 plain stage MFR; thickness & position PH; moves with stage", src="S01")
    m.add("ix73_stage_support", box(-p.IX73_W.v / 2 + 20, p.IX73_W.v / 2 - 20, -120, 120,
                                    -p.STAGE_T.v - 25, -p.STAGE_T.v), "ix73", "PH")
    oz = p.OBJECTIVE_ZONE
    m.add("ix73_objective_zone", zcyl(0, 0, oz["r"], *oz["z"]), "ix73", "PH", note=oz["note"])
    ob = p.OBS_TUBE_BOX
    m.add("ix73_obs_tube_eyepieces", box(*ob["x"], *ob["y"], *ob["z"]), "ix73", "PH", note=ob["note"])
    sh = p.STAGE_HANDLE
    m.add("ix73_stage_handle", box(*sh["x"], *sh["y"], *sh["z"]), "ix73", "PH", note=sh["note"])
    top = p.PILLAR_TOP_Z.v
    m.add("ix73_illum_pillar", box(-p.PILLAR_W.v / 2, p.PILLAR_W.v / 2, p.PILLAR_Y0.v, p.PILLAR_Y1.v,
                                   -p.STAGE_T.v, top), "ix73", "PH",
          note="pillar height from MFR total H 656; x/y/section PH")
    m.add("ix73_lamp_house", box(-60, 60, p.PILLAR_Y1.v, p.PILLAR_Y1.v + 140, top - 150, top - 20),
          "ix73", "PH")

    # condenser + carrier arm
    if condenser in p.CONDENSERS:
        wd = p.CONDENSERS[condenser]["WD"].v
        zc = p.cond_front_z(condenser)
        rc = p.COND_D.v / 2
        zs = zc
        for i, (dstep, hstep) in enumerate(p.COND_PROFILE.v):
            m.add(f"condenser_{condenser}" + (f"_step{i}" if i else ""), zcyl(0, 0, dstep / 2, zs, zs + hstep),
                  "condenser", "PH", note=f"WD {wd} mm MFR ({condenser}); stepped envelope PH (M6, M8)")
            zs += hstep
        zc_top = zs
        m.add("condenser_carrier_arm", box(-p.COND_ARM_W.v / 2, p.COND_ARM_W.v / 2, -rc,
                                           p.PILLAR_Y0.v, zc_top, zc_top + 60), "condenser", "PH")
        m.add("illum_arm_to_pillar", box(-p.COND_ARM_W.v / 2, p.COND_ARM_W.v / 2, -rc, p.PILLAR_Y0.v,
                                         max(zc_top + 60, top - 120), top), "ix73", "PH")
    else:
        # pillar tilted back ~30 deg: model only the upper arm, swung rearwards (PH)
        m.add("illum_arm_tilted_back", box(-p.COND_ARM_W.v / 2, p.COND_ARM_W.v / 2, p.PILLAR_Y1.v,
                                           p.PILLAR_Y1.v + 200, top - 180, top - 40), "ix73", "PH",
              note="tilted-back illumination column; geometry PH (M10)")

    # ------------------------------------------------------------------ plate
    L, W, H = p.PLATE_L.v, p.PLATE_W.v, p.PLATE_H.v
    plate = box(-L / 2, L / 2, -W / 2, W / 2, 0.0, H)
    wells = []
    for r in range(p.N_ROWS):
        for c in range(p.N_COLS):
            x, y = well_xy(r, c)
            wells.append(zcyl(x, y, p.WELL_D_TOP.v / 2, p.WELL_BOTTOM_Z.v, H + 1))
    plate = plate - Compound(wells)
    m.add("plate_96_SLAS", plate, "plate", "STD", group="S", note=f"V1 plate {p.V1_PLATE}: SLAS 1/2/4 + well profile",
          src="S10,S11,S12,S13")

    # ------------------------------------------------------------------ frame (fixed)
    bx0, bx1 = TOWER_X - 70, TOWER_X + 90
    m.add("base_plate", box(bx0, bx1, POST_Y[0] - 70, POST_Y[1] + 70, T, T + 15), "frame", "DES",
          note="15 mm Al plate bolted to table (M25 hole grid)")
    for i, py in enumerate(POST_Y):
        m.add(f"post_{i}", box(TOWER_X - 40, TOWER_X + 40, py - 40, py + 40, T + 15, BEAM_Z[0]),
              "frame", "APX", note="80x80 extrusion/column")
        m.add(f"post_brace_{i}", rod((TOWER_X + 40, py, T + 20), (TOWER_X + 88, py, T + 170), 8),
              "frame", "APX")
    m.add("y_beam", box(TOWER_X - 40, TOWER_X + 40, POST_Y[0] - 40, POST_Y[1] + 40, *BEAM_Z),
          "frame", "APX")
    # Y actuator body on the beam (carriage centre y = tip_y + 37)
    yc0 = sum(X_BAND) / 2
    y_lo = LY["y_lo"]
    m.add("Y_actuator_body", box(TOWER_X - 13, TOWER_X + 13, y_lo, y_lo + Y_BODY_L, *Y_ACT_Z),
          "actuator", "APX", note=f"{LY['stroke_y']:.0f} mm catalogue stroke (tip travel {LY['travel_y']:.0f} mm), ball-screw, width-26 class")
    m.add("Y_motor", box(TOWER_X - 21, TOWER_X + 21, y_lo + Y_BODY_L, y_lo + Y_BODY_L + p.NEMA17_L.v,
                         Y_ACT_Z[0] - 6, Y_ACT_Z[0] + 36), "motor", "APX")
    m.add("Y_home_switch", box(TOWER_X + 14, TOWER_X + 24, y_lo + 2, y_lo + 14, Y_ACT_Z[0], Y_ACT_Z[0] + 10),
          "switch", "DES")
    m.add("Y_cable_chain", box(TOWER_X + 45, TOWER_X + 70, y_lo, y_lo + Y_BODY_L, BEAM_Z[1] - 30, BEAM_Z[1]),
          "cable", "DES", note="motor/switch cables only; tubing is routed separately")
    m.add("tubing_fixed_clamp", box(TOWER_X - 60, TOWER_X - 40, POST_Y[0] + 45, POST_Y[0] + 65,
                                    BEAM_Z[0], BEAM_Z[0] + 20), "tubing", "DES",
          note="fixed strain relief on frame")

    # external pump + controller (fixed, NOT on moving assembly)
    m.add("syringe_pump_existing", box(520, 760, -120, 40, T, T + 140), "pump", "PH",
          note="existing Harvard/Tecan pump - footprint PH (M17)")
    m.add("motion_controller_24V", box(520, 700, 120, 260, T, T + 70), "electronics", "DES")

    # ------------------------------------------------------------------ Y group
    xcc = ARM_L + ZB_D / 2  # X-carriage centre x (tip-relative)
    x_lo = LY["x_lo"]
    x_hi = x_lo + X_BODY_L
    m.add("Y_carriage", box(TOWER_X - 25, TOWER_X + 25, yc0 - 25, yc0 + 25, Y_ACT_Z[1], XSB_Z[0]),
          "actuator", "APX", group="Y")
    m.add("X_support_beam", box(x_lo - 5, TOWER_X + 25, XSB_BAND[0], XSB_BAND[1], *XSB_Z),
          "frame", "APX", group="Y", note="stiff box section carrying the X actuator")
    m.add("X_actuator_body", box(x_lo, x_hi, X_BAND[0], X_BAND[1], *X_Z), "actuator", "APX", group="Y",
          note=f"{LY['stroke_x']:.0f} mm catalogue stroke (tip travel {LY['travel_x']:.0f} mm), ball-screw, width-26 class, table facing -Y")
    m.add("X_motor", box(x_hi, x_hi + p.NEMA17_L.v, X_BAND[0] - 8, X_BAND[1] + 8,
                         X_Z[0] - 6, X_Z[0] + 36), "motor", "APX", group="Y")
    m.add("X_home_switch", box(x_hi - 12, x_hi, X_BAND[1], X_BAND[1] + 8, X_Z[0], X_Z[0] + 10),
          "switch", "DES", group="Y")
    m.add("X_cable_chain", box(x_lo + 60, x_hi, X_BAND[1] + 10, X_BAND[1] + 30, XSB_Z[0], XSB_Z[0] + 25),
          "cable", "DES", group="Y")

    # ------------------------------------------------------------------ X group
    zx0 = ARM_L                     # Z actuator face towards the tip
    z_lo = Z_BODY_BOTTOM            # fixed for all head configurations
    z_hi = z_lo + Z_BODY_L
    m.add("X_carriage_bracket", box(xcc - 25, xcc + 25, ZB_W / 2, X_BAND[0], X_Z[0], X_Z[1]),
          "actuator", "APX", group="X")
    m.add("Z_actuator_body", box(zx0, zx0 + ZB_D, -ZB_W / 2, ZB_W / 2, z_lo, z_hi),
          "actuator", "APX", group="X", note=f"{LY['stroke_z']:.0f} mm catalogue stroke (tip travel {LY['travel_z']:.0f} mm), lead 1 mm ball screw or TR8x2")
    m.add("Z_motor", box(zx0 - 6, zx0 + 36, -21, 21, z_hi, z_hi + p.NEMA17_L.v), "motor", "APX", group="X")
    m.add("Z_home_switch_top", box(zx0 + ZB_D, zx0 + ZB_D + 8, -5, 5, z_hi - 14, z_hi - 2),
          "switch", "DES", group="X", note="top limit (not the homing reference)")
    # Z reference switch: carriage level where the head top is Z_REF_MARGIN below the condenser front
    zref = Z_REF_ARM_BOTTOM          # ONE physical switch: carriage (arm bottom) level at reference
    m.add("Z_reference_switch", box(zx0 + ZB_D, zx0 + ZB_D + 8, 6, 16, zref - 6, zref + 6),
          "switch", "DES", group="X", note="homing reference: head clears the condenser at any XY")
    m.add("tubing_clamp_Zbody", box(zx0 + ZB_D, zx0 + ZB_D + 12, -ZB_W / 2 - 14, -ZB_W / 2,
                                    z_hi - 30, z_hi - 10), "tubing", "DES", group="X")

    # ------------------------------------------------------------------ Z group (head)
    ht = hg["hold_top"]
    arm_z0 = ht[2] - ARM_T / 2
    # Z carriage
    m.add("Z_carriage", box(zx0 - 10, zx0, -ZB_W / 2, ZB_W / 2, arm_z0 - 5, arm_z0 + 45),
          "moving", "APX", group="Z")
    # kinematic magnetic break-away interface (concept)
    m.add("breakaway_kinematic_mount", box(zx0 - 22, zx0 - 10, -15, 15, arm_z0 - 5, arm_z0 + 30),
          "moving", "DES", group="Z", note="3-ball kinematic + magnet preload: kinematic repositioner after a crash; NOT a capillary force limiter (docs/06)")
    # dog-leg arm: thin section under condenser (first 120 mm), deep section outboard
    thin_end = ht[0] + LY["thin_l"]  # covers |tip_x min| + condenser radius + margin
    m.add("arm_thin", box(ht[0] - 6, thin_end, -ARM_T / 2, ARM_T / 2, arm_z0, arm_z0 + ARM_T),
          "moving", "DES", group="Z")
    m.add("arm_deep", box(thin_end, zx0 - 22, -ARM_T / 2, ARM_T / 2, arm_z0, arm_z0 + 30),
          "moving", "DES", group="Z")
    # holder (collet) along capillary axis
    m.add("capillary_holder_collet", rod(hg["nose"], hg["hold_top"], p.HOLDER_D.v / 2), "holder", "APX",
          group="Z", note="collet/split holder with depth stop, OD<=10")
    m.add("glass_capillary_OD1.0", rod(hg["tip"], hg["cap_top"], p.CAP_OD.v / 2), "capillary", "DES",
          group="Z", note="OD 1.0 / ID 0.6 / L 40")
    # tubing: leaves holder top, runs along arm (front face), up to Z-body clamp
    tz = ht[2] + 2
    tub_z = arm_z0 + ARM_T + p.TUBING_ABOVE_ARM.v - 0.8   # tube top = arm top + TUBING_ABOVE_ARM
    pts = [(ht[0], 0, tz), (ht[0] + 8, -ARM_T / 2 - 1.5, tub_z),
           (zx0 - 30, -ARM_T / 2 - 1.5, tub_z),
           (zx0 - 26, -ZB_W / 2 - 6, arm_z0 + 40)]
    for i, s in enumerate(polyline_tube(pts, 0.8)):
        m.add(f"tubing_head_{i}", s, "tubing", "DES", group="Z", note="PTFE/FEP 1/16in OD, liquid-filled")
    # service loops (drawn at reference pose)
    loop_z = [(zx0 - 26, -ZB_W / 2 - 6, arm_z0 + 40), (zx0 - 40, -30, arm_z0 + 90),
              (zx0 - 10, -32, z_hi - 20), (zx0 + ZB_D + 6, -ZB_W / 2 - 7, z_hi - 20)]
    for i, s in enumerate(polyline_tube(loop_z, 0.8)):
        m.add(f"tubing_loopZ_{i}", s, "tubing", "DES", group="X")
    loop_xy = [(zx0 + ZB_D + 6, -ZB_W / 2 - 7, z_hi - 20), (zx0 + 80, -40, z_hi + 30),
               (TOWER_X - 80, -45, z_hi + 30), (TOWER_X - 50, POST_Y[0] + 55, BEAM_Z[0] + 10)]
    for i, s in enumerate(polyline_tube(loop_xy, 0.8)):
        m.add(f"tubing_loopXY_{i}", s, "tubing", "DES", group="Y")
    to_pump = [(TOWER_X - 50, POST_Y[0] + 55, BEAM_Z[0] + 10), (TOWER_X - 50, POST_Y[0] + 55, T + 40),
               (560, -60, T + 40), (560, -60, T + 100)]
    for i, s in enumerate(polyline_tube(to_pump, 0.8)):
        m.add(f"tubing_to_pump_{i}", s, "tubing", "DES")
    return m


def well_xy(r, c):
    """row r (0=A) col c (0=1) -> stage xy.  Row A at +Y (rear), column 1 at -X (left)."""
    x0 = -p.PLATE_L.v / 2 + p.A1_X_FROM_LEFT.v
    y0 = p.PLATE_W.v / 2 - p.A1_Y_FROM_TOP.v
    return x0 + c * p.WELL_PITCH.v, y0 - r * p.WELL_PITCH.v


def well_name(r, c):
    return "ABCDEFGH"[r] + str(c + 1)


def posed(m: Model, dx=0.0, dy=0.0, dz=0.0, sx=0.0, sy=0.0):
    """Return list of (Part, solid-at-pose).  (sx, sy) = IX73 stage offset (plate + stage move)."""
    out = []
    for q in m.parts:
        if q.group == "S":
            s = Pos(sx, sy, 0) * q.solid if (sx or sy) else q.solid
        elif q.group == "Y":
            s = Pos(0, dy, 0) * q.solid
        elif q.group == "X":
            s = Pos(dx, dy, 0) * q.solid
        elif q.group == "Z":
            s = Pos(dx, dy, dz) * q.solid
        else:
            s = q.solid
        out.append((q, s))
    return out


def zones(condenser="IX-ULWCD", workflow=p.DEFAULT_WORKFLOW):
    """Visual-only zones: tip travel envelope, safe-Z slab, condenser keep-out, illumination cone."""
    z = {}
    L = p.layout(workflow)
    x0, x1, y0, y1 = L["x_min"], L["x_max"], L["y_min"], L["y_max"]
    z["tip_travel_envelope"] = box(x0, x1, y0, y1, Z_PICK - 3, Z_PICK - 3 + L["travel_z"])
    # safe-Z corridor of the V1 head (issue #5): the stage moves only while the tip is inside it
    cr = p.corridor(p.V1_HEAD)
    z["safe_z_corridor"] = box(x0, x1, y0, y1, cr["lower"], max(cr["upper"], cr["lower"] + 0.5))
    if condenser in p.CONDENSERS:
        zc = p.cond_front_z(condenser)
        z["condenser_keepout"] = zcyl(0, 0, p.COND_D.v / 2 + 10, zc - 5, zc + 400)
        na = min(0.3, p.CONDENSERS[condenser]["NA"])
        from build123d import Cone
        h = zc - p.WELL_BOTTOM_Z.v
        rt = h * math.tan(math.asin(na))
        z["illumination_cone_NA0.3"] = Pos(0, 0, p.WELL_BOTTOM_Z.v + h / 2) * Cone(0.01, rt, h)
    return z


SHARED_CATS = {"ix73", "plate", "table", "condenser"}
EXPORT_SET = {"WA": ["R08", "V00", "V20", "V30", "V45"], "WB": ["R08", "V20", "V30"]}


def safe_key(k):
    return k.replace(" ", "_").replace("(", "").replace(")", "")


if __name__ == "__main__":
    import glob
    os.makedirs(OUT, exist_ok=True)
    stl_dir = os.path.join(OUT, "stl")
    os.makedirs(stl_dir, exist_ok=True)
    for old in glob.glob(os.path.join(OUT, "*.step")) + glob.glob(os.path.join(stl_dir, "*.stl")):
        os.remove(old)
    meta = {"variants": VARIANTS, "parts": {}, "Z_PICK": Z_PICK, "safe_z": p.SAFE_Z_TIP.v,
            "corridor": {k: p.corridor(k) for k in p.HEAD_CONFIGS}, "head_configs": p.HEAD_CONFIGS,
            "condensers": {}, "workflows": {}, "export_set": EXPORT_SET}
    for k, v in p.CONDENSERS.items():
        meta["condensers"][k] = {"WD": v["WD"].v, "NA": v["NA"], "z_bottom": p.WELL_BOTTOM_Z.v + v["WD"].v}

    def put(key, q_solid, **kw):
        key = safe_key(key)
        tol = 0.05 if kw.get("category") in ("capillary", "tubing") else 0.2
        export_stl(q_solid, os.path.join(stl_dir, key + ".stl"), tolerance=tol, angular_tolerance=0.3)
        kw.setdefault("ver", p.verification(kw.get("status", ""), kw.pop("src", "")))
        meta["parts"][key] = dict(file=f"stl/{key}.stl", **kw)

    for wf, variants in EXPORT_SET.items():
        L = p.layout(wf)
        meta["workflows"][wf] = dict(p.WORKFLOWS[wf], layout={k: v for k, v in L.items()})
        for var in variants:
            m = build(var, "IX-ULWCD", wf)
            children = []
            for q, s in posed(m):
                s.label = q.name
                children.append(s)
            export_step(Compound(children=children, label=f"IX73_picker_{wf}_{var}_ULWCD"),
                        os.path.join(OUT, f"assembly_{wf}_{var}_IX-ULWCD.step"))
            for q in m.parts:
                shared = q.category in SHARED_CATS or q.name.startswith("illum_arm")
                if shared:
                    continue  # exported once below
                if q.group == "Z":
                    put(f"{wf}__{var}__{q.name}", q.solid, category=q.category, status=q.status, src=q.src, group="Z",
                        workflow=wf, variant=var, note=q.note)
                elif var == variants[0]:
                    put(f"{wf}__{q.name}", q.solid, category=q.category, status=q.status, src=q.src, group=q.group,
                        workflow=wf, variant="all", note=q.note)
            print("built", wf, var)
    # shared microscope / plate parts, condenser alternatives
    for cond in CONDENSER_CHOICES:
        m = build("R08", cond)
        for q in m.parts:
            if q.category == "condenser" or q.name.startswith("illum_arm"):
                put(f"COND[{cond}]__{q.name}", q.solid, category=q.category, status=q.status, group="fixed",
                    workflow="all", variant="all", condenser=cond, note=q.note)
            elif cond == CONDENSER_CHOICES[0] and q.category in SHARED_CATS:
                put(q.name, q.solid, category=q.category, status=q.status, src=q.src, group=q.group, workflow="all",
                    variant="all", note=q.note)
    for wf in EXPORT_SET:
        for cond in ["IX-ULWCD", "IX2-LWUCD"]:
            for name, s in zones(cond, wf).items():
                put(f"ZONE[{wf}][{cond}]__{name}", s, category="zone", status="DER", group="fixed",
                    workflow=wf, variant="all", condenser=cond, note=name)
        zs = zones("IX-ULWCD", wf)
        export_step(Compound(children=list(zs.values()), label=f"zones_{wf}"),
                    os.path.join(OUT, f"zones_{wf}_IX-ULWCD.step"))
    with open(os.path.join(OUT, "parts.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("done", len(meta["parts"]), "parts")
