"""Light geometry tests (issue #9).  Run: python -m pytest tests  (or python tests/test_geometry.py)."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cad"))
import params as p  # noqa: E402


def test_v1_plate_frozen():
    f = p.PLATE_PROFILES[p.V1_PLATE]
    assert f["scope"] == "V1" and f["sku"] == "7007"
    assert [n for n, g in p.PLATE_PROFILES.items() if g["scope"] == "V1"] == [p.V1_PLATE]


def test_v1_target_radius_single_source():
    assert p.PLATE_PROFILES[p.V1_PLATE]["target"]["radius"] == p.V1_TARGET_RADIUS.v


def test_max_angle_corning_7007():
    import analysis
    assert abs(analysis.max_angle_centre() - 14.8) < 0.1
    a = analysis.well_access(8)
    assert a["bottom_reachable_centre"] and a["rim_clearance_centre"] > p.RIM_MARGIN.v
    assert not analysis.well_access(30)["bottom_reachable_centre"]


def test_layout_invariants():
    for wf in p.WORKFLOWS:
        L = p.layout(wf)
        assert L["stroke_x"] >= L["travel_x"] and L["stroke_y"] >= L["travel_y"] and L["stroke_z"] >= L["travel_z"]
        assert L["x_min"] < 0 < L["x_max"] or wf == "WB"
        assert L["arm_l"] > L["thin_l"] > 0
        # the Z actuator stays outboard of the condenser
        assert L["arm_l"] + L["x_min"] > p.COND_D.v / 2


def test_corridor_positive_and_single_reference():
    for k, c in p.HEAD_CONFIGS.items():
        if c["scope"] not in ("V1", "experimental"):
            continue
        cr = p.corridor(k)
        assert cr["feasible"], k
        assert cr["lower"] - 1e-6 <= p.tip_at_ref(k) <= cr["upper"] + 1e-6, k
    assert p.corridor(p.V1_HEAD)["preferred"]


def test_head_top_formula():
    for k, c in p.HEAD_CONFIGS.items():
        t = math.radians(c["theta"])
        expect = c["exposed"] * math.cos(t) + p.HOLDER_AXIAL_LEN.v * math.cos(t) + p.ARM_HALF_HEIGHT.v + p.TUBING_ABOVE_ARM.v
        if p.HEAD_TOP_FROM_NOSE_MEAS is None:
            assert abs(p.head_top_from_tip(c["theta"], c["exposed"]) - expect) < 1e-9


def test_verification_separates_excerpt_from_official():
    assert p.verification("MFR", "S01") == "SEARCH_EXCERPT"
    assert p.verification("MFR", "S37") == "NOT_VERIFIED"
    assert p.verification("PH") == "PLACEHOLDER"
    assert p.verification("MEAS") == "MEASURED"


def test_freeze_gate_contains_plate_and_head():
    assert "M19" in p.FREEZE_GATE and "M23" in p.FREEZE_GATE


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f()
            print("ok", n)
