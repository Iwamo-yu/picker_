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

# ----------------------------------------------------------------------------
# IX73  (Evident).  Only a few numbers are manufacturer-verified.
# ----------------------------------------------------------------------------
IX73_W = P(323.0, "MFR", "S01", "IX73 1-deck standard configuration W")
IX73_D = P(475.0, "MFR", "S01", "IX73 1-deck standard configuration D")
IX73_H = P(656.0, "MFR", "S01", "IX73 1-deck standard configuration H (incl. illumination pillar)")
STAGE_TOP_ABOVE_TABLE = P(200.0, "PH", "", "NOT FOUND in any reachable source -> measure M1")
STAGE_X = P(232.0, "MFR", "S01", "plain stage 232 (X) x 240 (Y)")
STAGE_Y = P(240.0, "MFR", "S01", "")
STAGE_T = P(20.0, "PH", "", "stage plate thickness")
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
COND_BODY_H = P(70.0, "PH", "", "condenser body height")
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
OBJECTIVE_ZONE = dict(r=45.0, z=(-110, -2), status="PH", note="nosepiece/objectives under stage")

# ----------------------------------------------------------------------------
# Capillary + holder
# ----------------------------------------------------------------------------
CAP_OD = P(1.0, "DES", "S20", "SpheroidPicker-class reference, user spec")
CAP_ID = P(0.6, "DES", "S20", "")
CAP_L = P(40.0, "DES", "S20", "")
CAP_GRIP = P(10.0, "DES", "", "length held in collet (adjustable insertion depth)")
CAP_EXPOSED = P(CAP_L.v - CAP_GRIP.v, "DER", "", "")
# Capillary set by object size (target objects 100 um - 1 mm, user requirement 2026-09-26).
# OD/ID verified for WPI 1B100-4 / 1B150-4 / 1B200-4 (S14); thin-wall 2.0 mm ID is NOT verified.
CAPILLARY_SET = [
    dict(name="S  (100-300 um)", od=1.0, id=0.58, status="MFR", src="S14", part="WPI 1B100-4 (or tip cut/pulled to ID 0.2-0.35)"),
    dict(name="M  (300-600 um)", od=1.5, id=0.84, status="MFR", src="S14", part="WPI 1B150-4 / Sutter B150-86 (ID 0.86)"),
    dict(name="L  (600-1000 um)", od=2.0, id=1.12, status="MFR", src="S14", part="WPI 1B200-4 - only 1.12x a 1 mm object"),
    dict(name="L' (800-1000 um)", od=2.0, id=1.5, status="PH", src="", part="thin-wall 2.0 mm OD, ID ~1.5 - verify catalogue"),
]
HOLDER_D = P(10.0, "APX", "", "collet body diameter envelope")
HOLDER_L = P(14.0, "APX", "", "collet body length envelope")
TIP_CLEAR_BOTTOM = P(0.3, "DES", "", "pick height of tip above well bottom")

# ----------------------------------------------------------------------------
# Motion (target travels; user spec, confirmed by coverage analysis)
# ----------------------------------------------------------------------------
TRAVEL_X = P(150.0, "DES", "", "user spec 120-150; 99 mm span + 25.5 margin each side")
TRAVEL_Y = P(100.0, "DES", "", "user spec 80-100; 63 mm span + 18.5 margin each side")
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
# Recommended frame (side tower, right-hand side) - design choices
# ----------------------------------------------------------------------------
ARM_L = P(130.0, "DES", "", "dog-leg arm length, tip axis -> Z carriage face")
ARM_T = P(12.0, "DES", "", "arm section (y and z)")
POST_X = P(350.0, "DES", "", "post centre-line X")
POST_Y = (P(-230.0, "DES"), P(230.0, "DES"))
POST_SEC = P(80.0, "APX", "", "80x80 aluminium extrusion / machined column")
BEAM_SEC = P(80.0, "APX", "", "80x80 beam")
