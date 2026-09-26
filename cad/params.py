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
  MEAS  measured on the real IX73 / real part (replaces PH after the freeze-gate measurements)

STATUS says where a value comes from (its ORIGIN).  How well it was checked is a separate axis,
VERIFICATION (see verification() below):
  DIRECT_OFFICIAL   official document/drawing inspected directly
  FILE_RETRIEVED    file downloaded and inspected (e.g. a git repository)
  MEASURED          measured on the real hardware
  SECONDARY_SOURCE  reseller / distributor page
  SEARCH_EXCERPT    read from a search-engine excerpt only (page itself not opened)
  NOT_VERIFIED      approximate / catalogue class, not checked
  PLACEHOLDER       guess, must be measured
  DESIGN            our own design choice or derived value

Note: most MFR values were read from search-engine excerpts of manufacturer pages, not from the
documents themselves (see the "Retrieval" column of docs/source_manifest.md).

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
# Plates.  SLAS footprint / well positions are standard; well geometry is PLATE-SPECIFIC.
# V1_PLATE is the single plate the first prototype is designed and accepted for (issue #10).
# ----------------------------------------------------------------------------
PLATE_L = P(127.76, "STD", "S10", "footprint length, ANSI/SLAS 1-2004 (+-0.25)")
PLATE_W = P(85.48, "STD", "S10", "footprint width, ANSI/SLAS 1-2004 (+-0.25)")
A1_X_FROM_LEFT = P(14.38, "STD", "S12", "ANSI/SLAS 4-2004 (96-well)")
A1_Y_FROM_TOP = P(11.24, "STD", "S12", "ANSI/SLAS 4-2004 (96-well)")
WELL_PITCH = P(9.0, "STD", "S12", "ANSI/SLAS 4-2004 (96-well)")
N_COLS, N_ROWS = 12, 8

# Plate profiles.  height = plate top above the stage datum; bottom = "U" | "flat".
# scope: "V1" = frozen for the first prototype; "experimental" = kept for later, not a V1 requirement.
# target: where in the well the object must be pickable (acceptance test).
PLATE_PROFILES = {
    "96 U-bottom (Corning 7007)": dict(
        manufacturer="Corning", sku="7007", bottom="U", rows=8, cols=12,
        d_top=6.86, d_bot=6.35, depth=11.30, pitch=9.00, height=14.35,
        status="MFR", src="S13",
        drawing="Corning 7007 product description PDF (rev. 2026-02-09) + SLAS 2-2004 height; search excerpts",
        lid="removed during picking", scope="V1",
        target=dict(kind="bottom centre", radius=1.0,
                    note="one spheroid settled at the U-bottom centre, within 1.0 mm of the well axis")),
    "48-well (Corning 3548)": dict(manufacturer="Corning", sku="3548", bottom="flat", rows=6, cols=8,
        d_top=11.56, d_bot=11.05, depth=17.4, pitch=13.08, height=None, status="MFR", src="S16",
        drawing="Corning dimension sheet (search excerpt)", lid="removed", scope="experimental",
        target=dict(kind="area", fraction=0.5)),
    "24-well (Corning 3524)": dict(manufacturer="Corning", sku="3524", bottom="flat", rows=4, cols=6,
        d_top=16.26, d_bot=15.62, depth=17.4, pitch=19.3, height=None, status="MFR", src="S16",
        drawing="Corning dimension sheet (search excerpt; pitch weakly confirmed)", lid="removed",
        scope="experimental", target=dict(kind="area", fraction=0.5)),
    "12-well (Corning 3513)": dict(manufacturer="Corning", sku="3513", bottom="flat", rows=3, cols=4,
        d_top=22.73, d_bot=22.11, depth=17.5, pitch=26.01, height=None, status="MFR", src="S16",
        drawing="Corning dimension sheet (search excerpt)", lid="removed", scope="experimental",
        target=dict(kind="area", fraction=0.5)),
    "6-well (Corning 3516)": dict(manufacturer="Corning", sku="3516", bottom="flat", rows=2, cols=3,
        d_top=34.8, d_bot=34.8, depth=17.4, pitch=39.12, height=None, status="MFR", src="S16",
        drawing="Corning dimension sheet (search excerpt; single diameter)", lid="removed",
        scope="experimental", target=dict(kind="area", fraction=0.5)),
}
MULTIWELL_HEIGHT_EXTRA = P(3.0, "PH", "", "multiwell plate top above the well rim/bottom-depth (plate height unknown, M19)")
PLATE_FORMATS = PLATE_PROFILES          # historical name used by analysis code
V1_PLATE = "96 U-bottom (Corning 7007)"


def plate_height(name):
    pr = PLATE_PROFILES[name]
    return pr["height"] if pr["height"] is not None else pr["depth"] + MULTIWELL_HEIGHT_EXTRA.v


def well_bottom_z(name):
    """Well-bottom (focal plane) height above the stage datum for a plate profile."""
    return plate_height(name) - PLATE_PROFILES[name]["depth"]


_V1 = PLATE_PROFILES[V1_PLATE]
PLATE_H = P(_V1["height"], "STD", "S11", f"V1 plate ({V1_PLATE}) overall height, ANSI/SLAS 2-2004")
WELL_D_TOP = P(_V1["d_top"], _V1["status"], _V1["src"], f"V1 plate {V1_PLATE}")
WELL_D_BOT = P(_V1["d_bot"], _V1["status"], _V1["src"], f"V1 plate {V1_PLATE}")
WELL_DEPTH = P(_V1["depth"], _V1["status"], _V1["src"], f"V1 plate {V1_PLATE}")
WELL_BOTTOM_Z = P(well_bottom_z(V1_PLATE), "DER", "S11,S13",
                  "V1 plate: assumes well rim = max plate height; plate-specific")
PLATE_CENTER_XY = (P(0.0, "DES", "", "plate centred on optical axis = 'stage reference position'"),
                   P(0.0, "DES", "", ""))

# Exchangeable angle blocks at the holder seat (design choice; replaces a continuous tilt)
ANGLE_BLOCKS = [8.0, 20.0, 30.0]          # 45 deg evaluated but not needed (see docs/10)
ANGLES_EVALUATED = [0.0, 8.0, 20.0, 30.0, 45.0]
MIN_MARGIN = P(2.0, "DES", "", "minimum clearance accepted for holder-over-rim / condenser at safe-Z (placeholder condenser -> keep >= 2 mm)")
RIM_MARGIN = P(0.5, "DES", "", "minimum shaft-to-rim clearance (well geometry is MFR data, +-0.25 mm)")
MIN_REACH = P(0.5, "DES", "", "flat wells: minimum reachable fraction of the bottom area")
EXPOSED_OPTIONS = [30.0, 27.0, 24.0]  # capillary length below the collet nose; set by the depth stop

# ----------------------------------------------------------------------------
# IX73  (Evident).  Only a few numbers are manufacturer-verified.
# ----------------------------------------------------------------------------
IX73_W = P(323.0, "MFR", "S01", "IX73 1-deck standard configuration W")
IX73_D = P(475.0, "MFR", "S01", "IX73 1-deck standard configuration D")
# Height depends on the deck configuration (issue #4).  656 mm is the 1-deck standard configuration
# (S01); the 2-deck IX73P2F was listed at 721 mm high in one search excerpt (S36, unconfirmed).  M5/M9
# record which one is on the bench.
IX73_H_BY_DECKS = {1: P(656.0, "MFR", "S01", "IX73 1-deck standard configuration H (incl. pillar)"),
                   2: P(721.0, "APX", "S36", "IX73P2F 2-deck H, search excerpt only, unverified")}
IX73_DECKS = P(1, "PH", "", "number of decks on the lab's IX73 (M5)")
IX73_H = IX73_H_BY_DECKS[int(IX73_DECKS.v)]
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
# Stepped condenser envelope (issue #4), from the front lens upwards: (outer diameter, step height).
# No official drawing was reachable.  Until M6/M8 are measured, the profile is ONE conservative
# cylinder of COND_D; a measured profile (e.g. a narrower front nose) replaces this list, and every
# clearance below the condenser is recomputed from it.  The IX-ULWCD mount is the IX bayonet
# (outer 47.0 mm, forum measurement, S38 - excerpt only), so the front nose is probably narrower
# than 80 mm: the placeholder errs on the side of collision.
COND_PROFILE = P([(COND_D.v, COND_BODY_H.v)], "PH", "", "condenser (diameter, height) steps from the front (M6, M8)")
# Motorised stage envelope for W-B (issue #4).  Datasheet (S37, Maerzhaeuser SCANplus IM 120x80) was
# NOT retrieved; these are placeholders.  The plate-holder frame top above the plate resting plane is
# what the arm sees; its value enters safe_z_lower() through STAGE_CLIP_TOP.
MOTOR_STAGE_ENVELOPE = dict(name="SCANplus IM 120x80 (candidate)", plan=(None, None), frame_top=None,
                            status="PH", src="S37", note="record plan size, frame height above insert, "
                                                        "cable exit and controller (M3, O-2)")
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
HOLDER_AXIAL_LEN = P(14.0, "APX", "", "holder length along the capillary axis, collet nose -> holder top (M23)")
TIP_CLEAR_BOTTOM = P(0.3, "DES", "", "pick height of tip above well bottom")

# ----------------------------------------------------------------------------
# Motion (target travels; user spec, confirmed by coverage analysis)
# ----------------------------------------------------------------------------
TRAVEL_Z = P(50.0, "DES", "", "user spec 30-50")
# SAFE_Z_TIP (V1 corridor lower bound) is defined at the end of this file from safe_z_lower().

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
BODY_CLEAR = P(10.0, "DES", "", "X support beam inner end: condenser carrier arm half-width + this")
TUBING_ABOVE_ARM = P(2.3, "DES", "", "tubing (1/16 in) + clip above the arm top")
ARM_HALF_HEIGHT = P(ARM_T.v / 2, "DER", "", "holder top sits at arm mid-height")
# M23 (freeze gate): measured vertical distance from the collet nose to the highest point of the
# complete head (holder, arm, tubing, clip) with the V1 head configuration mounted.  None -> model.
HEAD_TOP_FROM_NOSE_MEAS = None


def head_top_from_nose(theta_deg):
    """Vertical distance collet nose -> highest point of the head (holder top at arm mid-height)."""
    import math
    if HEAD_TOP_FROM_NOSE_MEAS is not None and abs(theta_deg - HEAD_CONFIGS["R08"]["theta"]) < 1e-9:
        return HEAD_TOP_FROM_NOSE_MEAS
    return HOLDER_AXIAL_LEN.v * math.cos(math.radians(theta_deg)) + ARM_HALF_HEIGHT.v + TUBING_ABOVE_ARM.v


def head_top_from_tip(theta_deg, exposed):
    """Vertical distance capillary tip -> highest point of the head."""
    import math
    return exposed * math.cos(math.radians(theta_deg)) + head_top_from_nose(theta_deg)


# Head configurations: ONE record per exported head, used by analysis, CAD/STEP, viewer and docs.
HEAD_CONFIGS = {
    "R08": dict(theta=8.0, exposed=30.0, od=1.0, plate="96 U-bottom (Corning 7007)", scope="V1",
                label="8° block, 30 mm exposed (V1)"),
    "V20": dict(theta=20.0, exposed=27.0, od=1.0, plate="12-well (Corning 3513)", scope="experimental",
                label="20° block, 27 mm exposed (12-well)"),
    "V30": dict(theta=30.0, exposed=30.0, od=1.0, plate="6-well (Corning 3516)", scope="experimental",
                label="30° block, 30 mm exposed (6-well)"),
    "V00": dict(theta=0.0, exposed=30.0, od=1.0, plate="96 U-bottom (Corning 7007)", scope="comparison",
                label="0° (vertical), comparison only"),
    "V45": dict(theta=45.0, exposed=30.0, od=1.0, plate="96 U-bottom (Corning 7007)", scope="comparison",
                label="45°, comparison only"),
}
V1_HEAD = "R08"
Z_REF_MARGIN = P(2.0, "DES", "", "head top below the condenser front when Z is at the reference switch = corridor upper margin")
STAGE_CLIP_TOP = P(14.35, "PH", "", "highest moving stage/insert/clip feature above the datum, other than the plate (M3)")
CORRIDOR_LOWER_MARGIN = P(5.0, "DES", "", "tip above the highest moving plate/stage feature during stage moves")
MIN_CORRIDOR = P(2.0, "DES", "", "preferred minimum safe-Z corridor width (tip), below which the configuration is flagged")
# Measured condenser-front height above the plate datum (stage top); None -> derive from WD (M8)
COND_FRONT_Z_MEAS = None
FOV_4X = P(5.5, "APX", "", "field of view at 4x: field number 22 / 4 (eyepiece); camera FOV is smaller")

WORKFLOWS = {
    "WA": dict(
        label="W-A stage fixed: picker covers the plate",
        tip_x=(-75.0, 75.0), tip_y=(-50.0, 50.0), travel_z=50.0,
        stroke=(150.0, 100.0, 80.0),   # catalogue strokes X/Y/Z (APX, P01-P03 class)
        stage_moves=False,
        note="picker reaches all 96 wells; only the well on the optical axis is observed"),
    "WB": dict(
        label="W-B stage moves wells to the optical axis: picker works locally",
        tip_x=(-15.0, 85.0), tip_y=(-15.0, 15.0), travel_z=50.0,
        stroke=(110.0, 50.0, 80.0),    # catalogue strokes X/Y/Z: KR26-0110 / LX26 >=50 / KR2001A-0080 (APX, P01-P03)
        stage_moves=True,
        note="source and destination wells are brought to the axis by the IX73 stage; "
             "+X travel is the park / capillary-change retreat outside the condenser keep-out"),
}
# Frame z-levels (above stage top) and y-bands relative to the tip (APX envelopes)
BEAM_Z = (70.0, 150.0)        # Y beam 80 x 80
Y_ACT_Z = (150.0, 168.0)      # Y actuator on the beam
X_Z = (150.0, 180.0)          # X actuator (hangs under the X support beam)
XSB_Z = (180.0, 260.0)        # X support beam, 40 wide x 80 tall
X_BAND = (24.0, 50.0)         # X actuator y-band
XSB_BAND = (24.0, 64.0)       # X support beam y-band (40 mm)
# ---------------------------------------------------------------- V1 acceptance, stage centring, loads, safety
V1_TARGET_RADIUS = P(0.5, "DES", "", "V1 acceptance: spheroid pickable when within this radius of the U-bottom centre (confirm from real samples)")
STAGE_SELECTED = "Maerzhaeuser SCAN IM for IX73"
STAGE_AXIS_OFFSET = (P(0.0, "PH", "", "stage travel centre vs optical axis, X (M4)"), P(0.0, "PH", "", "Y (M4)"))
PLATE_HOLDER_OFFSET = (P(0.0, "PH", "", "plate centre vs stage insert centre, X (M3)"), P(0.0, "PH", "", "Y (M3)"))
ACCEL = P(0.5, "DES", "", "planned axis acceleration for the moment check [m/s^2]")
# moving masses per model part [kg] (APX catalogue-class estimates; replace with datasheet masses)
MASS_APX = {
    "Z_carriage": 0.10, "breakaway_kinematic_mount": 0.05, "arm_thin": 0.05, "arm_deep": 0.06,
    "capillary_holder_collet": 0.04, "glass_capillary_OD1.0": 0.001, "tubing_head": 0.01,
    "X_carriage_bracket": 0.10, "Z_actuator_body": 0.55, "Z_motor": 0.35, "Z_home_switch_top": 0.01,
    "Z_reference_switch": 0.01, "tubing_clamp_Zbody": 0.01,
    "Y_carriage": 0.15, "X_support_beam": 0.80, "X_actuator_body": 1.10, "X_motor": 0.35,
    "X_home_switch": 0.01, "X_cable_chain": 0.20,
}
# allowable static moments of the chosen actuators [N m]: fill from the catalogue (MA pitch, MB yaw, MC roll)
ALLOWABLE_MOMENTS = {"Y": None, "X": None, "Z": None}
BREAKAWAY_HOLD_N = P(16.0, "MFR", "P12", "Thorlabs KB25/M magnetic holding force (search excerpt)")
BREAKAWAY_LEVER = P(12.5, "APX", "", "effective pivot lever of a 25 mm kinematic mount")
GLASS_STRENGTH = P(50.0, "APX", "", "practical bending strength of borosilicate capillary [MPa] (conservative)")
PLATE_FORCE_LIMIT = P(5.0, "PH", "", "acceptable force on the plate bottom before damage [N] (to be defined)")

# Freeze gate: nothing is frozen before these are measured / confirmed (see docs/05, docs/09)
FREEZE_GATE = ["M1", "M3", "M4", "M6", "M7", "M8", "M10", "M15", "M19", "M23"]
DEFAULT_WORKFLOW = "WB"   # baseline after D1

# Stages that could move the plate (for W-B).  Required: >= 99 x 63 mm (well span).
STAGES = {
    "IX3-SVR (manual)": dict(travel=(114.0, 75.0), status="MFR", src="S02", motorised=False),
    "IX3-SSU (ultrasonic, motorised)": dict(travel=(76.0, 52.0), status="MFR", src="S01", motorised=True),
    "Maerzhaeuser SCAN IM for IX73": dict(travel=(120.0, 80.0), status="MFR", src="S15", motorised=True),
}


def cond_front_z(cond="IX-ULWCD", plate=None):
    """Condenser front height above the stage datum.  The condenser is focused on the well bottom of
    the plate in use, so it follows that plate's well-bottom height.  A measured V1 value (M8)
    replaces the WD-derived one."""
    plate = plate or V1_PLATE
    if COND_FRONT_Z_MEAS is not None:
        return COND_FRONT_Z_MEAS + (well_bottom_z(plate) - well_bottom_z(V1_PLATE))
    return well_bottom_z(plate) + CONDENSERS[cond]["WD"].v


# ---------------------------------------------------------------- safe-Z corridor (issue #5)
def safe_z_lower(plate=None):
    """Lowest tip height allowed while the stage moves: above every moving plate/stage feature."""
    plate = plate or V1_PLATE
    return max(plate_height(plate), STAGE_CLIP_TOP.v) + CORRIDOR_LOWER_MARGIN.v


def safe_z_upper(cfg=None, cond="IX-ULWCD"):
    """Highest tip height allowed near the optical axis: head top stays Z_REF_MARGIN under the condenser."""
    c = HEAD_CONFIGS[cfg or V1_HEAD]
    return cond_front_z(cond, c["plate"]) - Z_REF_MARGIN.v - head_top_from_tip(c["theta"], c["exposed"])


def corridor(cfg=None, cond="IX-ULWCD"):
    c = HEAD_CONFIGS[cfg or V1_HEAD]
    lo, hi = safe_z_lower(c["plate"]), safe_z_upper(cfg, cond)
    return dict(cfg=cfg or V1_HEAD, plate=c["plate"], lower=lo, upper=hi, width=hi - lo,
                feasible=hi > lo, preferred=hi - lo >= MIN_CORRIDOR.v)


# ---------------------------------------------------------------- one physical Z reference switch
def z_ref_head_top(cond="IX-ULWCD"):
    """Absolute height of the head top when the Z carriage sits on the reference switch.  The arm is
    fixed to the carriage and the holder top sits at arm mid-height for every head configuration, so
    this height is the same for all configurations: ONE physical switch, set from the worst case
    (lowest condenser front) over the supported (V1 + experimental) configurations."""
    supported = {c["plate"] for c in HEAD_CONFIGS.values() if c["scope"] in ("V1", "experimental")}
    return min(cond_front_z(cond, pl) for pl in supported) - Z_REF_MARGIN.v


def tip_at_ref(cfg, cond="IX-ULWCD"):
    c = HEAD_CONFIGS[cfg]
    return z_ref_head_top(cond) - head_top_from_tip(c["theta"], c["exposed"])


def layout(wf=DEFAULT_WORKFLOW):
    """Derived frame layout for a workflow.  All positions relative to the optical axis (mm).
    Actuator bodies are sized from the CATALOGUE stroke and anchored at the inner (X), front (Y) and
    lower (Z) ends, so extra stroke grows outboard / rearward / upward."""
    w = WORKFLOWS[wf]
    rc = COND_D.v / 2
    x_min, x_max = w["tip_x"]
    y_min, y_max = w["tip_y"]
    stroke_x, stroke_y, stroke_z = w["stroke"]
    travel_x, travel_y = x_max - x_min, y_max - y_min
    assert stroke_x >= travel_x and stroke_y >= travel_y and stroke_z >= w["travel_z"], "stroke < travel"
    thin_l = abs(x_min) + rc + COND_MARGIN.v                 # thin section must cover the keep-out
    zb_d = 30.0                                               # Z actuator depth (APX)
    end = ACT_TABLE_L.v / 2 + ACT_END.v                       # carriage centre -> body end at end of stroke
    # X body inner end must clear the condenser carrier arm (+ support-beam overhang 5 mm)
    x_lo_min = COND_ARM_W.v / 2 + BODY_CLEAR.v + 5.0
    arm_l = thin_l + ARM_DEEP_EXTRA.v                         # tip axis -> Z carriage face
    xcc = arm_l + zb_d / 2
    if xcc + x_min - end < x_lo_min:                          # lengthen the arm if needed
        arm_l += x_lo_min - (xcc + x_min - end)
        xcc = arm_l + zb_d / 2
    x_lo = xcc + x_min - end
    x_body = stroke_x + ACT_TABLE_L.v + 2 * ACT_END.v
    x_hi = x_lo + x_body
    tower_x = round(x_hi + NEMA17_L.v + 30.0)
    x_band = X_BAND
    yc0 = sum(x_band) / 2                                     # Y carriage centre rel. tip y
    y_body = stroke_y + ACT_TABLE_L.v + 2 * ACT_END.v
    y_lo = yc0 + y_min - end
    post_y = (round(y_lo - 77.0), round(y_lo + y_body + 83.0))
    z_body = stroke_z + ACT_TABLE_L.v + 2 * ACT_END.v
    return dict(wf=wf, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, travel_x=travel_x,
                travel_y=travel_y, travel_z=w["travel_z"], stroke_x=stroke_x, stroke_y=stroke_y,
                stroke_z=stroke_z, z_body=z_body, thin_l=thin_l, arm_l=arm_l, zb_d=zb_d,
                xcc=xcc, x_lo=x_lo, x_hi=x_hi, x_body=x_body, tower_x=tower_x, x_band=x_band, yc0=yc0,
                y_lo=y_lo, y_body=y_body, post_y=post_y, x_inner_clear=x_lo - rc)


# derived V1 constants (kept for plots and older code)
SAFE_Z_TIP = P(safe_z_lower(V1_PLATE), "DER", "", "V1 safe-Z corridor lower bound (tip) for stage moves")


# ---------------------------------------------------------------- provenance: origin vs verification (issue #9)
# Retrieval state per source ID (docs/source_manifest.md).  Nothing was inspected as an official file in
# the authoring session; only the SpheroidPicker git repositories were downloaded.
SOURCE_RETRIEVAL = {sid: "SEARCH_EXCERPT" for sid in
                    ["S01", "S02", "S03", "S10", "S11", "S12", "S13", "S14", "S15", "S16", "S20", "S21", "S22",
                     "S23", "S24", "S30", "S31", "S32", "S33", "S34", "S35", "S36", "S38"]}
SOURCE_RETRIEVAL.update({"S04": "SECONDARY_SOURCE", "S27": "FILE_RETRIEVED", "S28": "FILE_RETRIEVED",
                         "S05": "NOT_RETRIEVED", "S06": "NOT_RETRIEVED", "S25": "NOT_RETRIEVED",
                         "S26": "NOT_RETRIEVED", "S37": "NOT_RETRIEVED"})
VERIFICATION_RANK = ["MEASURED", "DIRECT_OFFICIAL", "FILE_RETRIEVED", "SECONDARY_SOURCE", "SEARCH_EXCERPT",
                     "NOT_VERIFIED", "PLACEHOLDER"]


def verification(status, src=""):
    """Verification level of a value, separate from its origin STATUS."""
    if status == "MEAS":
        return "MEASURED"
    if status == "PH":
        return "PLACEHOLDER"
    if status == "APX":
        return "NOT_VERIFIED"
    if status in ("DES", "DER"):
        return "DESIGN"
    ids = [x.strip() for x in str(src).replace("+", ",").split(",") if x.strip()]
    states = [SOURCE_RETRIEVAL.get(i, "NOT_VERIFIED") for i in ids] or ["NOT_VERIFIED"]
    states = [("NOT_VERIFIED" if st == "NOT_RETRIEVED" else st) for st in states]
    return max(states, key=VERIFICATION_RANK.index)          # the weakest source decides
