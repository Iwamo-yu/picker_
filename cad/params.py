"""
Parametric layout parameters for the external XYZ capillary picker around an
Evident/Olympus IX73.  STAGE 1 = spatial validation only (no manufacturing detail).

Every dimension carries a provenance STATUS so unknowns are never hidden:

  STD   official standard (ANSI/SLAS)                          -> authoritative
  MFR   manufacturer data (spec sheet / catalogue / drawing)   -> authoritative
  DER   derived by calculation from STD/MFR values             -> as good as inputs
  APX   approximate envelope (catalogue class, not a frozen part number)
  PH    PLACEHOLDER - not verified, MUST be measured on the real IX73
  DES   design choice made in this layout study (free parameter)

Source IDs (Sxx) refer to docs/source_manifest.md.

Coordinate system (all mm):
  origin  = optical axis  x  plate resting plane (SLAS Datum A = stage insert top)
  +X      = operator's right,  +Y = away from operator (towards illumination pillar)
  +Z      = up.  Optical-table surface is at Z = -STAGE_TOP_ABOVE_TABLE.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class P:
    v: float
    status: str
    src: str = ""
    note: str = ""

    def __float__(self):
        return float(self.v)


# ----------------------------------------------------------------------------
# 96-well plate  (ANSI/SLAS 1-2004, 2-2004, 4-2004; Corning 7007 drawing)
# ----------------------------------------------------------------------------
PLATE_L = P(127.76, "STD", "S10", "footprint length, ANSI/SLAS 1-2004 (+-0.25)")
PLATE_W = P(85.48, "STD", "S10", "footprint width, ANSI/SLAS 1-2004 (+-0.25)")
PLATE_H = P(14.35, "STD", "S11", "overall height, ANSI/SLAS 2-2004 (+-0.76)")
A1_X_FROM_LEFT = P(14.38, "STD", "S12", "ANSI/SLAS 4-2004")
A1_Y_FROM_TOP = P(11.24, "STD", "S12", "ANSI/SLAS 4-2004")
WELL_PITCH = P(9.0, "STD", "S12", "ANSI/SLAS 4-2004")
N_COLS, N_ROWS = 12, 8
WELL_D_TOP = P(6.86, "MFR", "S13", "Corning 7007 U-bottom ULA: 0.270 in")
WELL_D_BOT = P(6.35, "MFR", "S13", "Corning 7007: 0.250 in")
WELL_DEPTH = P(11.30, "MFR", "S13", "Corning 7007: 0.445 in")
WELL_BOTTOM_Z = P(PLATE_H.v - WELL_DEPTH.v, "DER", "S11,S13",
                  "assumes well rim = max plate height; real value plate-specific")
PLATE_CENTER_XY = (P(0.0, "DES", "", "plate centred on optical axis = 'stage reference position'"),
                   P(0.0, "DES", "", ""))

# Other plate formats (SBS footprint).  Flat-bottom Corning Costar TC plates.
# d_top/d_bot/depth/pitch from Corning dimension-sheet excerpts (S16); 6-well diameter is a single value.
PLATE_FORMATS = {
    "96 U-bottom (Corning 7007)": dict(rows=8, cols=12, d_top=6.86, d_bot=6.35, depth=11.30, pitch=9.00,
                                       status="MFR", src="S13"),
    "48-well (Corning 3548)": dict(rows=6, cols=8, d_top=11.56, d_bot=11.05, depth=17.4, pitch=13.08,
                                   status="MFR", src="S16"),
    "24-well (Corning 3524)": dict(rows=4, cols=6, d_top=16.26, d_bot=15.62, depth=17.4, pitch=19.3,
                                   status="MFR", src="S16"),
    "12-well (Corning 3513)": dict(rows=3, cols=4, d_top=22.73, d_bot=22.11, depth=17.5, pitch=26.01,
                                   status="MFR", src="S16"),
    "6-well (Corning 3516)": dict(rows=2, cols=3, d_top=34.8, d_bot=34.8, depth=17.4, pitch=39.12,
                                  status="MFR", src="S16"),
}
# Exchangeable angle blocks on the kinematic mount (design choice; 0-12 deg fine tilt is replaced by blocks)
ANGLE_BLOCKS = [8.0, 20.0, 30.0]          # 45 deg evaluated but not needed (see docs/10)
ANGLES_EVALUATED = [0.0, 8.0, 20.0, 30.0, 45.0]
MIN_MARGIN = P(2.0, "DES", "", "minimum clearance accepted for rim / holder-over-rim / condenser at safe-Z (placeholder condenser -> keep >= 2 mm)")
RIM_MARGIN = P(0.5, "DES", "", "minimum shaft-to-rim clearance (well geometry is MFR data, +-0.25 mm)")
EXPOSED_OPTIONS = [30.0, 27.0, 24.0]  # capillary length below the collet nose; set by the depth stop

# ----------------------------------------------------------------------------
# IX73  (Evident).  Only a few numbers are manufacturer-verified.
# ----------------------------------------------------------------------------
IX73_W = P(323.0, "MFR", "S01", "IX73 1-deck standard configuration W")
IX73_D = P(475.0, "MFR", "S01", "IX73 1-deck standard configuration D")
IX73_H = P(656.0, "MFR", "S01", "IX73 1-deck standard configuration H (incl. illumination pillar)")
STAGE_TOP_ABOVE_TABLE = P(200.0, "PH", "", "NOT FOUND in any reachable source -> measure M1")
STAGE_X = P(232.0, "MFR", "S01", "plain stage 232 (X) x 240 (Y)")
STAGE_Y = P(240.0, "MFR", "S01", "")
STAGE_T = P(20.0, "PH", "", "stage plate thickness (M3)")
STAGE_TRAVEL_X = P(114.0, "MFR", "S02", "IX3-SVR mechanical stage stroke X")
STAGE_TRAVEL_Y = P(75.0, "MFR", "S02", "IX3-SVR mechanical stage stroke Y")
# location of the body/stage relative to the optical axis
BODY_Y_FRONT = P(-235.0, "PH", "", "front face of body rel. optical axis (M5)")
STAGE_CENTER_Y = P(0.0, "PH", "", "stage assumed centred on optical axis (M4)")
# illumination pillar + condenser carrier
PILLAR_W = P(90.0, "PH", "", "IX3-ILL pillar width (M9)")
PILLAR_Y0 = P(150.0, "PH", "", "front face of pillar rel. optical axis (M9)")
PILLAR_Y1 = P(240.0, "PH", "", "rear face of pillar")
PILLAR_TOP_Z = P(IX73_H.v - STAGE_TOP_ABOVE_TABLE.v, "DER", "S01+PH", "")
COND_ARM_W = P(90.0, "PH", "", "condenser holder / arm width (M7)")
COND_D = P(80.0, "PH", "", "condenser outer diameter (M6)")
COND_BODY_H = P(70.0, "PH", "", "condenser body height (M6)")
# condenser working distances (manufacturer)
CONDENSERS = {
    "IX2-LWUCD": dict(NA=0.55, WD=P(27.0, "MFR", "S03", "long-WD universal condenser")),
    "IX2-MLWCD": dict(NA=0.50, WD=P(45.0, "MFR", "S03", "")),
    "IX-ULWCD":  dict(NA=0.30, WD=P(73.0, "MFR", "S04", "ultra-long WD condenser")),
}
# front observation tube / eyepieces - completely unknown position
OBS_TUBE_BOX = dict(x=(-70, 70), y=(-380, -215), z=(-150, 180),
                    status="PH", note="observation tube + eyepieces envelope (M12)")
STAGE_HANDLE = dict(x=(105, 135), y=(-110, -80), z=(-140, -20),
                    status="PH", note="IX3-SVR right-hand coaxial handle (M13)")
OBJECTIVE_ZONE = dict(r=45.0, z=(-110, -2), status="PH", note="nosepiece/objectives under stage (M14)")

# ----------------------------------------------------------------------------
# Capillary + holder
# ----------------------------------------------------------------------------
CAP_OD = P(1.0, "DES", "S20", "SpheroidPicker-class reference, user spec")
CAP_ID = P(0.6, "DES", "S20", "")
CAP_L = P(40.0, "DES", "S20", "")
CAP_GRIP = P(10.0, "DES", "", "length held in collet (adjustable insertion depth)")
CAP_EXPOSED = P(CAP_L.v - CAP_GRIP.v, "DER", "", "")
# Capillary set by object size (target objects 100 um - 1 mm, user requirement 2026-09-26).
# OD/ID from WPI catalogue excerpts (S14), incl. thin-wall 2.00/1.56.
CAPILLARY_SET = [
    dict(name="S  (100-300 um)", od=1.0, id=0.58, status="MFR", src="S14", part="WPI 1B100-4 (or tip cut/pulled to ID 0.2-0.35)"),
    dict(name="M  (300-600 um)", od=1.5, id=0.84, status="MFR", src="S14", part="WPI 1B150-4 / Sutter B150-86 (ID 0.86)"),
    dict(name="L  (600-800 um)", od=2.0, id=1.12, status="MFR", src="S14", part="WPI 1B200-4 - only 1.12x a 1 mm object"),
    dict(name="L' (800-1000 um)", od=2.0, id=1.56, status="MFR", src="S14", part="WPI thin-wall 2.00/1.56 (no filament)"),
]
HOLDER_D = P(10.0, "APX", "", "collet body diameter envelope")
HOLDER_L = P(14.0, "APX", "", "collet body length envelope")
TIP_CLEAR_BOTTOM = P(0.3, "DES", "", "pick height of tip above well bottom")

# ----------------------------------------------------------------------------
# Motion (target travels; user spec, confirmed by coverage analysis)
# ----------------------------------------------------------------------------
TRAVEL_Z = P(50.0, "DES", "", "user spec 30-50")
SAFE_Z_TIP = P(PLATE_H.v + 5.0, "DER", "", "tip safe plane = plate top + 5 mm (no lid)")

# actuator envelopes (catalogue class: THK KR20/KR26, MISUMI LX20/LX26 size)
ACT_W = P(26.0, "APX", "S30,S31", "rail/body width class")
ACT_H = P(30.0, "APX", "S30,S31", "body+table height class")
ACT_END = P(35.0, "APX", "", "end blocks + table length beyond stroke (each side)")
ACT_TABLE_L = P(50.0, "APX", "", "carriage length")
NEMA17 = P(42.3, "APX", "S34", "NEMA17 flange")
NEMA17_L = P(48.0, "APX", "S34", "")

# ----------------------------------------------------------------------------
# Workflows (decision D1) and the frame layout derived from them.
# SINGLE SOURCE OF TRUTH: model.py, analysis.py, views.py and the rendered docs
# (docs/src -> docs, README) read every layout number from here.
# ----------------------------------------------------------------------------
ARM_T = P(12.0, "DES", "", "arm section under the condenser (y and z)")
ARM_DEEP_EXTRA = P(55.0, "DES", "", "deep arm section + kinematic mount beyond the thin section")
COND_MARGIN = P(5.0, "DES", "", "margin beyond condenser radius for the thin-arm end")
BODY_CLEAR = P(10.0, "DES", "", "X actuator inner end: condenser radius + this")
FOV_4X = P(5.5, "APX", "", "field of view at 4x: field number 22 / 4 (eyepiece); camera FOV is smaller")

WORKFLOWS = {
    "WA": dict(
        label="W-A stage fixed: picker covers the plate",
        tip_x=(-75.0, 75.0), tip_y=(-50.0, 50.0), travel_z=50.0,
        stage_moves=False,
        note="picker reaches all 96 wells; only the well on the optical axis is observed"),
    "WB": dict(
        label="W-B stage moves wells to the optical axis: picker works locally",
        tip_x=(-15.0, 85.0), tip_y=(-15.0, 15.0), travel_z=50.0,
        stage_moves=True,
        note="source and destination wells are brought to the axis by the IX73 stage; "
             "+X travel is the park / capillary-change retreat outside the condenser keep-out"),
}
DEFAULT_WORKFLOW = "WB"   # baseline after D1

# Stages that could move the plate (for W-B).  Required: >= 99 x 63 mm (well span).
STAGES = {
    "IX3-SVR (manual)": dict(travel=(114.0, 75.0), status="MFR", src="S02", motorised=False),
    "IX3-SSU (ultrasonic, motorised)": dict(travel=(76.0, 52.0), status="MFR", src="S01", motorised=True),
    "Maerzhaeuser SCAN IM for IX73": dict(travel=(120.0, 80.0), status="MFR", src="S15", motorised=True),
}


def layout(wf=DEFAULT_WORKFLOW):
    """Derived frame layout for a workflow.  All positions relative to the optical axis (mm)."""
    w = WORKFLOWS[wf]
    rc = COND_D.v / 2
    x_min, x_max = w["tip_x"]
    y_min, y_max = w["tip_y"]
    thin_l = abs(x_min) + rc + COND_MARGIN.v                 # thin section must cover the keep-out
    arm_l = thin_l + ARM_DEEP_EXTRA.v                         # tip axis -> Z carriage face
    zb_d = 30.0                                               # Z actuator depth (APX)
    xcc = arm_l + zb_d / 2                                    # X carriage centre rel. tip
    travel_x, travel_y = x_max - x_min, y_max - y_min
    x_lo = xcc + x_min - ACT_TABLE_L.v / 2 - ACT_END.v        # X body inner end (Y-group, fixed x)
    x_body = travel_x + ACT_TABLE_L.v + 2 * ACT_END.v
    x_hi = x_lo + x_body
    tower_x = round(x_hi + NEMA17_L.v + 30.0)
    x_band = (24.0, 50.0)
    yc0 = sum(x_band) / 2                                     # Y carriage centre rel. tip y
    y_body = travel_y + ACT_TABLE_L.v + 2 * ACT_END.v
    y_lo = yc0 + y_min - ACT_TABLE_L.v / 2 - ACT_END.v
    post_y = (round(y_lo - 77.0), round(y_lo + y_body + 83.0))
    return dict(wf=wf, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, travel_x=travel_x,
                travel_y=travel_y, travel_z=w["travel_z"], thin_l=thin_l, arm_l=arm_l, zb_d=zb_d,
                xcc=xcc, x_lo=x_lo, x_hi=x_hi, x_body=x_body, tower_x=tower_x, x_band=x_band, yc0=yc0,
                y_lo=y_lo, y_body=y_body, post_y=post_y, x_inner_clear=x_lo - rc)
