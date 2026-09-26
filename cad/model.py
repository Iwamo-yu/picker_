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
VARIANTS = {
    "V00": dict(theta=0.0, label="0 deg (vertical)"),
    "R08": dict(theta=8.0, label="8 deg near-vertical dog-leg (RECOMMENDED)"),
    "V30": dict(theta=30.0, label="30 deg inclined"),
    "V45": dict(theta=45.0, label="45 deg inclined"),
}
CONDENSER_CHOICES = ["IX2-LWUCD", "IX2-MLWCD", "IX-ULWCD", "NONE (pillar tilted back)"]

Z_PICK = p.WELL_BOTTOM_Z.v + p.TIP_CLEAR_BOTTOM.v  # tip z at reference pose

# frame / stacking layout (design parameters; see docs/architecture.md)
ARM_L = 175.0            # tip axis -> Z-carriage face (x)   [DES]
ARM_T = 12.0             # arm section under the condenser  [DES]
ZB_W = 26.0              # Z actuator width (y)              [APX]
ZB_D = 30.0              # Z actuator depth (x)              [APX]
Z_BODY_L = p.TRAVEL_Z.v + p.ACT_TABLE_L.v + 2 * p.ACT_END.v   # 170
X_BODY_L = p.TRAVEL_X.v + p.ACT_TABLE_L.v + 2 * p.ACT_END.v   # 270
Y_BODY_L = p.TRAVEL_Y.v + p.ACT_TABLE_L.v + 2 * p.ACT_END.v   # 220
X_BAND = (24.0, 50.0)    # X actuator y-band relative to tip y
X_Z = (150.0, 180.0)     # X actuator z (hangs under X support beam)
XSB_Z = (180.0, 220.0)   # X support beam z
TOWER_X = 400.0          # Y beam centre-line x
Y_ACT_Z = (150.0, 168.0)
BEAM_Z = (70.0, 150.0)
POST_Y = (-150.0, 230.0)
TABLE_Z = -p.STAGE_TOP_ABOVE_TABLE.v


def head_geometry(theta_deg):
    """Return key points of capillary/holder for a given angle (tip at origin xy, z=Z_PICK)."""
    t = math.radians(theta_deg)
    ux, uz = math.sin(t), math.cos(t)
    tip = (0.0, 0.0, Z_PICK)
    cap_top = (p.CAP_L.v * ux, 0.0, Z_PICK + p.CAP_L.v * uz)
    nose = (p.CAP_EXPOSED.v * ux, 0.0, Z_PICK + p.CAP_EXPOSED.v * uz)  # holder nose
    hold_top = ((p.CAP_EXPOSED.v + p.HOLDER_L.v) * ux, 0.0,
                Z_PICK + (p.CAP_EXPOSED.v + p.HOLDER_L.v) * uz)
    return dict(tip=tip, cap_top=cap_top, nose=nose, hold_top=hold_top, u=(ux, 0, uz))


def build(variant="R08", condenser="IX-ULWCD") -> Model:
    m = Model(variant, condenser)
    th = VARIANTS[variant]["theta"]
    hg = head_geometry(th)

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
          "ix73", "MFR", note="232 x 240 plain stage MFR; thickness & position PH")
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
        zc = p.WELL_BOTTOM_Z.v + wd
        rc = p.COND_D.v / 2
        m.add("condenser_" + condenser, zcyl(0, 0, rc, zc, zc + p.COND_BODY_H.v), "condenser", "PH",
              note=f"WD {wd} mm MFR ({condenser}); diameter/height PH")
        zc_top = zc + p.COND_BODY_H.v
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
    m.add("plate_96_SLAS", plate, "plate", "STD", note="SLAS 1/2/4 + Corning 7007 wells")

    # ------------------------------------------------------------------ frame (fixed)
    bx0, bx1 = TOWER_X - 70, TOWER_X + 90
    m.add("base_plate", box(bx0, bx1, POST_Y[0] - 70, POST_Y[1] + 70, T, T + 15), "frame", "DES",
          note="15 mm Al plate bolted to table (M25 hole grid)")
    for i, py in enumerate(POST_Y):
        m.add(f"post_{i}", box(TOWER_X - 40, TOWER_X + 40, py - 40, py + 40, T + 15, BEAM_Z[1]),
              "frame", "APX", note="80x80 extrusion/column")
        m.add(f"post_brace_{i}", rod((TOWER_X + 40, py, T + 20), (TOWER_X + 88, py, T + 170), 8),
              "frame", "APX")
    m.add("y_beam", box(TOWER_X - 40, TOWER_X + 40, POST_Y[0] - 40, POST_Y[1] + 40, *BEAM_Z),
          "frame", "APX")
    # Y actuator body on the beam (carriage centre y = tip_y + 37)
    yc0 = sum(X_BAND) / 2
    y_lo = yc0 - p.TRAVEL_Y.v / 2 - p.ACT_TABLE_L.v / 2 - p.ACT_END.v
    m.add("Y_actuator_body", box(TOWER_X - 13, TOWER_X + 13, y_lo, y_lo + Y_BODY_L, *Y_ACT_Z),
          "actuator", "APX", note="100 mm stroke, ball-screw, width-26 class")
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
    x_lo = xcc - p.TRAVEL_X.v / 2 - p.ACT_TABLE_L.v / 2 - p.ACT_END.v
    x_hi = x_lo + X_BODY_L
    m.add("Y_carriage", box(TOWER_X - 25, TOWER_X + 25, yc0 - 25, yc0 + 25, Y_ACT_Z[1], XSB_Z[0]),
          "actuator", "APX", group="Y")
    m.add("X_support_beam", box(x_lo - 5, TOWER_X + 25, X_BAND[0], X_BAND[1], *XSB_Z),
          "frame", "APX", group="Y", note="stiff box section carrying the X actuator")
    m.add("X_actuator_body", box(x_lo, x_hi, X_BAND[0], X_BAND[1], *X_Z), "actuator", "APX", group="Y",
          note="150 mm stroke, ball-screw, width-26 class, table facing -Y")
    m.add("X_motor", box(x_hi, x_hi + p.NEMA17_L.v, X_BAND[0] - 8, X_BAND[1] + 8,
                         X_Z[0] - 6, X_Z[0] + 36), "motor", "APX", group="Y")
    m.add("X_home_switch", box(x_hi - 12, x_hi, X_BAND[1], X_BAND[1] + 8, X_Z[0], X_Z[0] + 10),
          "switch", "DES", group="Y")
    m.add("X_cable_chain", box(x_lo + 60, x_hi, X_BAND[1] + 10, X_BAND[1] + 30, XSB_Z[0], XSB_Z[0] + 25),
          "cable", "DES", group="Y")

    # ------------------------------------------------------------------ X group
    zx0 = ARM_L                     # Z actuator face towards the tip
    z_lo = Z_PICK + 30.0            # Z body bottom at reference pose
    z_hi = z_lo + Z_BODY_L
    m.add("X_carriage_bracket", box(xcc - 25, xcc + 25, ZB_W / 2, X_BAND[0], X_Z[0], X_Z[1]),
          "actuator", "APX", group="X")
    m.add("Z_actuator_body", box(zx0, zx0 + ZB_D, -ZB_W / 2, ZB_W / 2, z_lo, z_hi),
          "actuator", "APX", group="X", note="50 mm stroke, lead 1 mm ball screw or TR8x2")
    m.add("Z_motor", box(zx0 - 6, zx0 + 36, -21, 21, z_hi, z_hi + p.NEMA17_L.v), "motor", "APX", group="X")
    m.add("Z_home_switch_top", box(zx0 + ZB_D, zx0 + ZB_D + 8, -5, 5, z_hi - 14, z_hi - 2),
          "switch", "DES", group="X")
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
          "moving", "DES", group="Z", note="3-ball kinematic + magnet preload: collision fuse")
    # dog-leg arm: thin section under condenser (first 120 mm), deep section outboard
    thin_end = ht[0] + 120.0  # must cover |tip_x|max + condenser radius + margin
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
    pts = [(ht[0], 0, tz), (ht[0] + 8, -ARM_T / 2 - 1.5, arm_z0 + ARM_T + 1.5),
           (zx0 - 30, -ARM_T / 2 - 1.5, arm_z0 + ARM_T + 1.5),
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


def posed(m: Model, dx=0.0, dy=0.0, dz=0.0):
    """Return list of (Part, solid-at-pose)."""
    out = []
    for q in m.parts:
        if q.group == "Y":
            s = Pos(0, dy, 0) * q.solid
        elif q.group == "X":
            s = Pos(dx, dy, 0) * q.solid
        elif q.group == "Z":
            s = Pos(dx, dy, dz) * q.solid
        else:
            s = q.solid
        out.append((q, s))
    return out


def zones(condenser="IX-ULWCD"):
    """Visual-only zones: tip travel envelope, safe-Z slab, condenser keep-out, illumination cone."""
    z = {}
    hx, hy = p.TRAVEL_X.v / 2, p.TRAVEL_Y.v / 2
    z["tip_travel_envelope"] = box(-hx, hx, -hy, hy, Z_PICK - 3, Z_PICK - 3 + p.TRAVEL_Z.v)
    z["safe_z_plane"] = box(-hx, hx, -hy, hy, p.SAFE_Z_TIP.v, p.SAFE_Z_TIP.v + 0.5)
    if condenser in p.CONDENSERS:
        zc = p.WELL_BOTTOM_Z.v + p.CONDENSERS[condenser]["WD"].v
        z["condenser_keepout"] = zcyl(0, 0, p.COND_D.v / 2 + 10, zc - 5, zc + 400)
        # illumination cone (NA_c = 0.3) from focal point to condenser front
        na = min(0.3, p.CONDENSERS[condenser]["NA"])
        from build123d import Cone
        h = zc - p.WELL_BOTTOM_Z.v
        rt = h * math.tan(math.asin(na))
        z["illumination_cone_NA0.3"] = Pos(0, 0, p.WELL_BOTTOM_Z.v + h / 2) * Cone(0.01, rt, h)
    return z


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    stl_dir = os.path.join(OUT, "stl")
    os.makedirs(stl_dir, exist_ok=True)
    meta = {"variants": {}, "parts": {}, "Z_PICK": Z_PICK, "ARM_L": ARM_L,
            "travel": [p.TRAVEL_X.v, p.TRAVEL_Y.v, p.TRAVEL_Z.v],
            "safe_z": p.SAFE_Z_TIP.v, "condensers": {}}
    for k, v in p.CONDENSERS.items():
        meta["condensers"][k] = {"WD": v["WD"].v, "NA": v["NA"],
                                 "z_bottom": p.WELL_BOTTOM_Z.v + v["WD"].v}
    for var in VARIANTS:
        m = build(var, "IX-ULWCD")
        children = []
        for q, s in posed(m):
            s.label = q.name
            children.append(s)
        asm = Compound(children=children, label=f"IX73_picker_{var}_ULWCD")
        export_step(asm, os.path.join(OUT, f"assembly_{var}_IX-ULWCD.step"))
        meta["variants"][var] = VARIANTS[var]
        # STL export of variant-specific (head) parts + all fixed parts once
        for q in m.parts:
            key = q.name if q.group != "Z" else f"{var}__{q.name}"
            if var != "R08" and q.group != "Z":
                continue
            fn = os.path.join(stl_dir, key + ".stl")
            export_stl(q.solid, fn, tolerance=0.05 if q.category in ("capillary", "tubing") else 0.2,
                       angular_tolerance=0.3)
            meta["parts"][key] = dict(file=f"stl/{key}.stl", category=q.category, status=q.status,
                                      group=q.group, variant=(var if q.group == "Z" else "all"),
                                      note=q.note)
        print("built", var)
    # condenser alternatives (fixed parts that differ)
    for cond in CONDENSER_CHOICES:
        m = build("R08", cond)
        for q in m.parts:
            if q.category == "condenser" or q.name.startswith("illum_arm"):
                key = f"COND[{cond}]__{q.name}"
                safe = key.replace(" ", "_").replace("(", "").replace(")", "")
                export_stl(q.solid, os.path.join(stl_dir, safe + ".stl"), tolerance=0.2)
                meta["parts"][safe] = dict(file=f"stl/{safe}.stl", category=q.category, status=q.status,
                                           group="fixed", variant="all", condenser=cond, note=q.note)
    # drop generic condenser parts from the 'all' set (they are condenser-specific)
    for k in list(meta["parts"]):
        if not k.startswith("COND[") and (meta["parts"][k]["category"] == "condenser"
                                          or k.startswith("illum_arm")):
            del meta["parts"][k]
    for cond in ["IX-ULWCD", "IX2-LWUCD"]:
        for name, s in zones(cond).items():
            key = f"ZONE[{cond}]__{name}"
            export_stl(s, os.path.join(stl_dir, key + ".stl"), tolerance=0.3)
            meta["parts"][key] = dict(file=f"stl/{key}.stl", category="zone", status="DER",
                                      group="fixed", variant="all", condenser=cond, note=name)
    zs = zones("IX-ULWCD")
    zc = Compound(children=[s for s in zs.values()], label="zones")
    export_step(zc, os.path.join(OUT, "zones_IX-ULWCD.step"))
    with open(os.path.join(OUT, "parts.json"), "w") as f:
        json.dump(meta, f, indent=1)
    print("done")
