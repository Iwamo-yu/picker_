"""
Stage-1 feasibility analysis.

  1. well-wall access vs capillary angle (analytic, Corning 7007 U-bottom geometry)
  2. transmitted-light obstruction by the holder vs angle and condenser NA (analytic)
  3. clearance sweep (OpenCascade min-distance) for every head variant x condenser:
     all 96 wells at pick height and at safe-Z, plus a travel grid at safe-Z and top-Z.

    python cad/analysis.py   -> cad/out/analysis.json, docs/generated_analysis_tables.md
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import params as p  # noqa: E402
from model import (CONDENSER_CHOICES, VARIANTS, Z_PICK, build, head_geometry,  # noqa: E402
                   posed, well_name, well_xy)
from build123d import Compound  # noqa: E402

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "out")
DOCS = os.path.join(HERE, "..", "docs")

R_TOP = p.WELL_D_TOP.v / 2
DEPTH = p.WELL_DEPTH.v
R_CAP = p.CAP_OD.v / 2


# ----------------------------------------------------------------------------- 1
def well_access(theta_deg):
    """Capillary tip at well-bottom centre; shaft must pass inside the rim.
    Returns rim clearance (mm, >0 ok), max centred reach depth below rim, and the
    largest off-centre tip shift towards the far wall that still allows bottom access."""
    t = math.radians(theta_deg)
    shaft_off = (DEPTH - p.TIP_CLEAR_BOTTOM.v) * math.tan(t) + R_CAP / math.cos(t)
    rim_clear = R_TOP - shaft_off
    reach = (R_TOP - R_CAP / math.cos(t)) / math.tan(t) if t > 0 else float("inf")
    # tip may move to the far wall (bottom radius) -> extra allowance
    r_bot = p.WELL_D_BOT.v / 2
    best_shift_clear = (R_TOP + (r_bot - R_CAP)) - shaft_off  # tip at far wall, shaft at near rim
    return dict(theta=theta_deg, rim_clearance_centre=rim_clear,
                max_centred_depth=min(reach, DEPTH), bottom_reachable_centre=rim_clear > 0,
                bottom_reachable_any=best_shift_clear > 0)


def max_angle_centre(r_cap=None):
    global R_CAP
    old = R_CAP
    if r_cap is not None:
        R_CAP = r_cap
    lo, hi = 0.0, 45.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if well_access(mid)["rim_clearance_centre"] > 0:
            lo = mid
        else:
            hi = mid
    R_CAP = old
    return lo


def capillary_set_table():
    rows = []
    global R_CAP
    old = R_CAP
    for c in p.CAPILLARY_SET:
        R_CAP = c["od"] / 2
        rim8 = well_access(8.0)["rim_clearance_centre"]
        R_CAP = old
        rows.append(dict(c, max_angle=max_angle_centre(c["od"] / 2), rim_clear_8deg=rim8,
                         id_over_100um=c["id"] / 0.1, id_over_1mm=c["id"] / 1.0))
    return rows


# ----------------------------------------------------------------------------- 2
def circle_overlap(r1, r2, d):
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2
    a = r1 * r1 * math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1))
    b = r2 * r2 * math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2))
    c = 0.5 * math.sqrt((-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2))
    return a + b - c


def illumination_block(theta_deg, na_c):
    """Fraction of the illumination cone blocked by the holder nose (disc of holder
    diameter, at the nose height, offset by the capillary lean).  Arm is ignored
    because it sits directly above the holder and is narrower (12 mm)."""
    hg = head_geometry(theta_deg)
    nx, _, nz = hg["nose"]
    h = nz - p.WELL_BOTTOM_Z.v
    rc = h * math.tan(math.asin(na_c))
    # holder projected footprint ~ disc of radius HOLDER_D/2 centred at nose x (conservative)
    rh = p.HOLDER_D.v / 2
    return circle_overlap(rc, rh, abs(nx)) / (math.pi * rc * rc), rc, nx


# ----------------------------------------------------------------------------- 3
OBST_CATS = {"ix73", "condenser", "plate", "pump", "electronics"}


def sweep(variant, condenser, workflow="WA"):
    """Clearance sweep.  Pose = (kind, name, tip dx, tip dy, tip dz, stage sx, stage sy)."""
    from build123d import Pos
    m = build(variant, condenser, workflow)
    L = p.layout(workflow)
    obst = [q for q in m.parts if q.group in ("fixed", "S") and q.category in OBST_CATS]
    mv = [q for q in m.parts if q.group in ("Y", "X", "Z")]

    poses = []
    dz_safe = p.SAFE_Z_TIP.v - Z_PICK
    dz_top = L["travel_z"] - 3.0
    for r in range(p.N_ROWS):
        for c in range(p.N_COLS):
            x, y = well_xy(r, c)
            if p.WORKFLOWS[workflow]["stage_moves"]:
                # stage brings the well to the optical axis; picker works at the axis
                poses.append(("pick", well_name(r, c), 0.0, 0.0, 0.0, -x, -y))
                poses.append(("safe", well_name(r, c), 0.0, 0.0, dz_safe, -x, -y))
            else:
                poses.append(("pick", well_name(r, c), x, y, 0.0, 0.0, 0.0))
                poses.append(("safe", well_name(r, c), x, y, dz_safe, 0.0, 0.0))
    for i in range(7):
        for j in range(5):
            x = L["x_min"] + i * (L["travel_x"] / 6)
            y = L["y_min"] + j * (L["travel_y"] / 4)
            poses.append(("grid_safe", f"g{i}{j}", x, y, dz_safe, 0.0, 0.0))
            poses.append(("grid_top", f"g{i}{j}", x, y, dz_top, 0.0, 0.0))
    if p.WORKFLOWS[workflow]["stage_moves"]:
        hx, hy = p.STAGE_TRAVEL_X.v / 2, p.STAGE_TRAVEL_Y.v / 2
        for sx in (-hx, 0, hx):
            for sy in (-hy, 0, hy):
                poses.append(("stage_corner", f"s{sx:+.0f}{sy:+.0f}", 0.0, 0.0, dz_safe, sx, sy))  # stage moves only at safe-Z

    def bb(s):
        b = s.bounding_box()
        return (b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z)

    def shift(b, o):
        return (b[0] + o[0], b[1] + o[1], b[2] + o[2], b[3] + o[0], b[4] + o[1], b[5] + o[2])

    def gap(a, b):
        g = 0.0
        for i in range(3):
            g = max(g, a[i] - b[i + 3], b[i] - a[i + 3], 0.0)
        return g

    ob_bb = {q.name: bb(q.solid) for q in obst}
    mv_bb = {q.name: bb(q.solid) for q in mv}
    NEAR = 25.0
    res = []
    for kind, name, x, y, dz, sx, sy in poses:
        worst = (NEAR, None, None)
        hits = []
        ob_cache = {}
        for q in mv:
            o = {"Y": (0, y, 0), "X": (x, y, 0), "Z": (x, y, dz)}[q.group]
            b = shift(mv_bb[q.name], o)
            s = None
            for ob in obst:
                oo = (sx, sy, 0) if ob.group == "S" else (0, 0, 0)
                g = gap(b, shift(ob_bb[ob.name], oo))
                if g > 0 and g >= worst[0]:
                    continue
                if s is None:
                    s = Pos(*o) * q.solid
                if ob.name not in ob_cache:
                    ob_cache[ob.name] = Pos(*oo) * ob.solid if ob.group == "S" else ob.solid
                d = s.distance_to(ob_cache[ob.name])
                is_cap_in_well = (q.category == "capillary" and ob.category == "plate" and kind == "pick")
                if d <= 1e-6:
                    hits.append((q.name, ob.name))
                if not is_cap_in_well and d < worst[0]:
                    worst = (d, q.name, ob.name)
        res.append(dict(kind=kind, name=name, x=round(x, 2), y=round(y, 2), dz=round(dz, 2), sx=round(sx, 2),
                        sy=round(sy, 2), min_clear=round(worst[0], 2), pair=[worst[1], worst[2]],
                        hits=sorted(set(tuple(h) for h in hits))))
    return res


def d1_metrics():
    """Workflow comparison against the criterion 'each well observed through the IX73 while picking'."""
    wells = [well_xy(r, c) for r in range(p.N_ROWS) for c in range(p.N_COLS)]
    fov_r = p.FOV_4X.v / 2
    out = {}
    for wf, w in p.WORKFLOWS.items():
        L = p.layout(wf)
        if w["stage_moves"]:
            stages = {}
            for sname, st in p.STAGES.items():
                hx, hy = st["travel"][0] / 2, st["travel"][1] / 2
                n = sum(1 for x, y in wells if abs(x) <= hx + 1e-9 and abs(y) <= hy + 1e-9)
                stages[sname] = dict(wells_to_axis=n, motorised=st["motorised"], travel=st["travel"])
            observed = max(v["wells_to_axis"] for v in stages.values())
        else:
            stages = {}
            observed_ref = sum(1 for x, y in wells if math.hypot(x, y) <= fov_r)
            observed = max(observed_ref, 1)  # one well if the stage is set once so a well sits on the axis
            out_ref = observed_ref
        out[wf] = dict(label=w["label"], observed_pick=observed,
                       observed_pick_at_centred_plate=(out_ref if not w["stage_moves"] else None),
                       reach_by_picker_only=sum(1 for x, y in wells if L["x_min"] <= x <= L["x_max"]
                                                and L["y_min"] <= y <= L["y_max"]),
                       layout=L, stages=stages)
    return out


def summarize(res):
    s = {}
    for kind in ("pick", "safe", "grid_safe", "grid_top", "stage_corner"):
        rr = [r for r in res if r["kind"] == kind]
        if not rr:
            continue
        ok = [r for r in rr if not r["hits"]]
        hit_obs = {}
        for r in rr:
            for a, b in r["hits"]:
                hit_obs[b] = hit_obs.get(b, 0) + 1
        mc = min(rr, key=lambda r: r["min_clear"])
        s[kind] = dict(n=len(rr), ok=len(ok), min_clear=mc["min_clear"], worst_pose=mc["name"],
                       worst_pair=mc["pair"], collisions_by_obstacle=hit_obs)
    return s


if __name__ == "__main__":
    t0 = time.time()
    out = {"well_access": [well_access(t) for t in (0, 5, 8, 10, 12, 14, 15, 20, 30, 45)],
           "max_angle_centre_deg": max_angle_centre(), "illumination": [], "sweeps": {}}
    for th in (0, 8, 30, 45):
        for na in (0.1, 0.3):
            f, rc, nx = illumination_block(th, na)
            out["illumination"].append(dict(theta=th, NA_c=na, cone_r_at_nose=round(rc, 2),
                                            holder_offset=round(nx, 2), blocked_fraction=round(f, 3)))
    out["capillary_set"] = capillary_set_table()
    out["d1"] = d1_metrics()
    from model import EXPORT_SET
    for wf, variants in EXPORT_SET.items():
      for var in variants:
        for cond in CONDENSER_CHOICES:
            res = sweep(var, cond, wf)
            out["sweeps"][f"{wf}|{var}|{cond}"] = dict(summary=summarize(res), poses=res)
            s = out["sweeps"][f"{wf}|{var}|{cond}"]["summary"]
            print(f"{wf} {var:4s} {cond:28s} pick ok {s['pick']['ok']:3d}/96  safe ok {s['safe']['ok']:3d}/96 "
                  f" grid_safe {s['grid_safe']['ok']}/35 grid_top {s['grid_top']['ok']}/35  "
                  f"minclear(pick)={s['pick']['min_clear']} {s['pick']['worst_pair']}  [{time.time()-t0:.0f}s]")
    with open(os.path.join(OUT, "analysis.json"), "w") as f:
        json.dump(out, f, indent=1)

    # markdown tables
    L = ["<!-- generated by cad/analysis.py - do not edit by hand -->",
         "# Generated analysis tables", "",
         "## 1. Well-wall access (Corning 7007 U-bottom: top Ø6.86, depth 11.30; capillary OD 1.0)", "",
         "| angle from vertical | rim clearance, tip at bottom centre (mm) | max centred reach below rim (mm) | bottom centre reachable | bottom reachable anywhere |",
         "|---|---|---|---|---|"]
    for w in out["well_access"]:
        L.append(f"| {w['theta']}° | {w['rim_clearance_centre']:.2f} | {w['max_centred_depth']:.1f} | "
                 f"{'yes' if w['bottom_reachable_centre'] else 'NO'} | {'yes' if w['bottom_reachable_any'] else 'NO'} |")
    L += ["", f"Maximum angle for reaching the bottom centre: **{out['max_angle_centre_deg']:.1f}°** "
          "(tip 0.3 mm above bottom, no margin).", "",
          "### 1b. Capillary set vs well access (object size 100 um - 1 mm)", "",
          "| class | OD | ID | max angle for bottom centre | rim clearance at 8° (mm) | catalogue part | data |",
          "|---|---|---|---|---|---|---|"]
    for c in out["capillary_set"]:
        L.append(f"| {c['name']} | {c['od']} | {c['id']} | {c['max_angle']:.1f}° | {c['rim_clear_8deg']:.2f} | {c['part']} | {c['status']} |")
    L += ["", "## 2. Holder obstruction of transmitted light (holder Ø10 at the collet nose)", "",
          "| angle | condenser NA used | cone radius at holder nose (mm) | holder offset (mm) | blocked fraction |",
          "|---|---|---|---|---|"]
    for r in out["illumination"]:
        L.append(f"| {r['theta']}° | {r['NA_c']} | {r['cone_r_at_nose']} | {r['holder_offset']} | {r['blocked_fraction']:.0%} |")
    L += ["", "## 3. Clearance sweep (OCC min distance; moving parts vs IX73/condenser/plate/pump envelopes)", "",
          "W-A poses: 96 wells at pick height and at safe-Z (plate top + 5 mm), with the picker moving to each well.",
          "W-B poses: the IX73 stage brings each well to the optical axis (plate and stage translate), picker at the axis;",
          "plus the IX3-SVR stage-travel corners. Both: 35-point grid over the picker's own travel at safe-Z and at top-Z.",
          "PH = placeholder geometry is involved in every condenser/IX73 result; treat as provisional.", "",
          "| workflow | head | condenser | pick OK /96 | safe-Z OK /96 | grid safe-Z OK /35 | grid top-Z OK /35 | stage corners OK | colliding obstacles (pose count) | min clearance, safe-Z (mm) |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in out["sweeps"].items():
        wf, var, cond = k.split("|")
        s = v["summary"]
        obs = {}
        for kind in s:
            for o, n in s[kind]["collisions_by_obstacle"].items():
                obs[o] = obs.get(o, 0) + n
        obs_s = ", ".join(f"{o} ({n})" for o, n in sorted(obs.items(), key=lambda x: -x[1])) or "none"
        sc = f"{s['stage_corner']['ok']}/{s['stage_corner']['n']}" if "stage_corner" in s else "–"
        L.append(f"| {wf} | {var} | {cond} | {s['pick']['ok']} | {s['safe']['ok']} | {s['grid_safe']['ok']} | "
                 f"{s['grid_top']['ok']} | {sc} | {obs_s} | {s['safe']['min_clear']} |")
    L += ["", "## 4. Workflow comparison (D1): wells that can be picked while observed through the IX73", "",
          f"Field of view assumed {p.FOV_4X.v} mm at 4x (APX). W-A: plate centred on the axis.", "",
          "| workflow | wells observed while picking | wells reachable by picker XY alone | picker travel X x Y x Z (mm) | arm length / thin section (mm) | tower axis x (mm) |",
          "|---|---|---|---|---|---|"]
    for wf, d in out["d1"].items():
        Ly = d["layout"]
        obs_txt = (f"{d['observed_pick']} (at a centred plate: {d['observed_pick_at_centred_plate']})"
                   if d["observed_pick_at_centred_plate"] is not None else f"{d['observed_pick']} (best stage)")
        L.append(f"| {d['label']} | {obs_txt} | {d['reach_by_picker_only']} | {Ly['travel_x']:.0f} x {Ly['travel_y']:.0f} x "
                 f"{Ly['travel_z']:.0f} | {Ly['arm_l']:.0f} / {Ly['thin_l']:.0f} | {Ly['tower_x']} |")
    L += ["", "W-B: wells the stage can bring to the optical axis, per stage (needs >= 99 x 63 mm travel):", "",
          "| stage | travel X x Y (mm) | motorised | wells reachable on the axis |", "|---|---|---|---|"]
    for sname, st in out["d1"]["WB"]["stages"].items():
        L.append(f"| {sname} | {st['travel'][0]:.0f} x {st['travel'][1]:.0f} | {'yes' if st['motorised'] else 'no'} | {st['wells_to_axis']}/96 |")
    with open(os.path.join(DOCS, "generated_analysis_tables.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("total", time.time() - t0)
