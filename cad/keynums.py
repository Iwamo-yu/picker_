"""Key numbers for the documents, computed from params.py (single source of truth) and
cad/out/analysis.json.  docs/src/*.md and README.src.md use {{KEY}} or {{KEY:fmt}}."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import params as p  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "out")


def keynums():
    k = {}
    for wf in p.WORKFLOWS:
        L = p.layout(wf)
        for name in ("travel_x", "travel_y", "travel_z", "arm_l", "thin_l", "tower_x", "x_min", "x_max",
                     "y_min", "y_max", "x_lo", "x_inner_clear"):
            k[f"{wf}_{name.upper()}"] = L[name]
        k[f"{wf}_POST_Y0"], k[f"{wf}_POST_Y1"] = L["post_y"]
        k[f"{wf}_GAP"] = L["tower_x"] - p.IX73_W.v / 2
        k[f"{wf}_FOOT_X"] = L["tower_x"] + 90
    k["ARM_T_TXT"] = f"{p.ARM_T.v:.0f} × {p.ARM_T.v:.0f} mm"
    k.update(PLATE_H=p.PLATE_H.v, SAFE_Z=p.SAFE_Z_TIP.v, COND_D=p.COND_D.v, COND_R=p.COND_D.v / 2,
             STAGE_TOP=p.STAGE_TOP_ABOVE_TABLE.v, FOV=p.FOV_4X.v, IX73_HALF_W=p.IX73_W.v / 2)
    import model as mdl
    k["BEAM_Z0"], k["BEAM_Z1"] = mdl.BEAM_Z
    k["XSB_Z0"], k["XSB_Z1"] = mdl.XSB_Z
    k["Z_PICK"] = mdl.Z_PICK
    k["BEAM_ABOVE_TABLE"] = mdl.BEAM_Z[0] + p.STAGE_TOP_ABOVE_TABLE.v
    k["WB_Y_BEAM_LEN"] = p.layout("WB")["post_y"][1] - p.layout("WB")["post_y"][0] + 80
    an = json.load(open(os.path.join(OUT, "analysis.json")))
    k["MAX_ANGLE"] = an["max_angle_centre_deg"]
    for w in an["well_access"]:
        t = int(w["theta"])
        k[f"RIM_{t}"] = w["rim_clearance_centre"]
        k[f"REACH_{t}"] = w["max_centred_depth"]
    for c in an["capillary_set"]:
        tag = c["name"].split()[0].replace("'", "p")
        k[f"CAP_{tag}_MAXANG"] = c["max_angle"]
        k[f"CAP_{tag}_RIM8"] = c["rim_clear_8deg"]
    for key, v in an["sweeps"].items():
        wf, var, cond = key.split("|")
        c = {"IX2-LWUCD": "LWUCD", "IX2-MLWCD": "MLWCD", "IX-ULWCD": "ULWCD"}.get(cond, "NONE")
        s = v["summary"]
        base = f"SW_{wf}_{var}_{c}"
        for kind in s:
            k[f"{base}_{kind.upper()}"] = s[kind]["ok"]
            k[f"{base}_{kind.upper()}_N"] = s[kind]["n"]
        k[f"{base}_SAFE_CLEAR"] = s["safe"]["min_clear"]
    for wf, d in an["d1"].items():
        k[f"D1_{wf}_OBSERVED"] = d["observed_pick"]
        k[f"D1_{wf}_PICKER_REACH"] = d["reach_by_picker_only"]
        for sname, st in d["stages"].items():
            tag = {"IX3-SVR (manual)": "SVR", "IX3-SSU (ultrasonic, motorised)": "SSU"}.get(sname, "SCANIM")
            k[f"D1_{wf}_{tag}_WELLS"] = st["wells_to_axis"]
    return k
