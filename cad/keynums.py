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
    fa = an.get("format_angle", {}).get("recommended", {})
    ang = set()
    md = ["| Plate | Capillary class | Angle block | Exposed length | Rim clearance | Head under condenser at safe-Z | Reachable bottom | Light blocked (NA 0.3) | Note |",
          "|---|---|---|---|---|---|---|---|---|"]
    ja = []
    for key, r in fa.items():
        fmt, cls = key.split("|")
        tag = fmt.split("-")[0].split(" ")[0] + "_" + cls[0]     # e.g. 96_S, 48_M
        name = fmt.split(" (")[0]
        if not r:
            md.append(f"| {name} | {cls} | none | – | – | – | – | – | no block meets the margins |")
            ja.append(f"<tr><td>{name}</td><td>{cls}</td><td colspan=6>条件を満たすブロックなし</td></tr>")
            continue
        ang.add(r["theta"])
        reach = "centre (U-bottom)" if r["reach"] is None else f"{r['reach']:.0%}"
        note = r.get("note") or ""
        k[f"FMT{tag}_ANGLE"], k[f"FMT{tag}_EXP"] = r["theta"], r["exposed"]
        md.append(f"| {name} | {cls} | {r['theta']:.0f}° | {r['exposed']:.0f} mm | {r['rim']:.2f} mm | {r['cond']:.1f} mm | "
                  f"{reach} | {r['block']:.0%} | {note} |")
        reach_ja = "中央(U 底)" if r["reach"] is None else f"{r['reach']:.0%}"
        note_ja = ("底面の到達範囲が基準未満。0° ブロックなら広がるが透過光を大きく遮る(D8)" if note else "")
        ja.append(f"<tr><td>{name}</td><td>{cls}</td><td>{r['theta']:.0f}°</td><td>{r['exposed']:.0f} mm</td>"
                  f"<td>{r['rim']:.2f} mm</td><td>{r['cond']:.1f} mm</td><td>{reach_ja}</td><td>{r['block']:.0%}</td><td>{note_ja}</td></tr>")
    k["FMT_TABLE_MD"] = "\n".join(md)
    k["FMT_TABLE_JA"] = "".join(ja)
    k["ANGLE_BLOCKS_TXT"] = " / ".join(f"{a:.0f}°" for a in sorted(ang))
    hl = [r["holder_l_max"] for r in fa.values() if r]
    k["HOLDER_L"] = p.HOLDER_L.v
    k["HOLDER_L_MAX_MIN"] = min(hl) if hl else float("nan")
    # condenser WD needed for MIN_MARGIN with the current head (from the W-B baseline sweep)
    sw = an["sweeps"].get("WB|R08|IX-ULWCD")
    if sw:
        k["WD_REQ"] = p.CONDENSERS["IX-ULWCD"]["WD"].v - (sw["summary"]["safe"]["min_clear"] - p.MIN_MARGIN.v)
    import model as mdl
    for v in ("R08", "V20", "V30"):
        k[f"ZREF_TIP_{v}"] = mdl.Z_PICK + mdl.z_ref_dz(v)
    k["COND_ARM_W"] = p.COND_ARM_W.v
    k["HEAD_TOP_ALLOW"] = p.HEAD_TOP_ALLOW.v
    k["Z_REF_MARGIN"] = p.Z_REF_MARGIN.v
    Lb = p.layout("WB")
    k["WB_Z_MIN_DIST"] = Lb["arm_l"] + Lb["x_min"]
    k["FREEZE_GATE"] = ", ".join(p.FREEZE_GATE)
    k["FREEZE_GATE_N"] = len(p.FREEZE_GATE)
    k["PARAMS_HASH_OK"] = an.get("params_hash") == __import__("analysis").params_hash()
    k["PH_COUNT"] = len(placeholders())
    k["MIN_MARGIN"] = p.MIN_MARGIN.v
    k["RIM_MARGIN"] = p.RIM_MARGIN.v
    return k


def placeholders():
    """All parameters still marked PH (placeholder, to be measured)."""
    out = []
    for name, v in vars(p).items():
        if isinstance(v, p.P) and v.status == "PH":
            out.append((name, v.v, v.note))
        elif isinstance(v, dict) and v.get("status") == "PH":
            out.append((name, "", v.get("note", "")))
    return out
