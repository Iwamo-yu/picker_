"""Embed STL meshes + analysis results into viewer/template.html -> viewer/ix73_picker_viewer.html"""
import base64, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "cad", "out")
sys.path.insert(0, os.path.join(HERE, "..", "cad"))
from model import CONDENSER_CHOICES, well_xy, well_name  # noqa
meta = json.load(open(os.path.join(OUT, "parts.json")))
an = json.load(open(os.path.join(OUT, "analysis.json")))
stl = {k: base64.b64encode(open(os.path.join(OUT, v["file"]), "rb").read()).decode() for k, v in meta["parts"].items()}
wells = [dict(name=well_name(r, c), x=round(well_xy(r, c)[0], 2), y=round(well_xy(r, c)[1], 2)) for r in range(8) for c in range(12)]
sweep = {}
for k, v in an["sweeps"].items():
    w = {}
    for ps in v["poses"]:
        if ps["kind"] not in ("pick", "safe"):
            continue
        e = w.setdefault(ps["name"], {})
        e[ps["kind"] + "_hits"] = sorted({b for a, b in ps["hits"]})
        e[ps["kind"] + "_clear"] = ps["min_clear"]
    s = v["summary"]
    obs = {}
    for kind in s:
        for o, n in s[kind]["collisions_by_obstacle"].items():
            obs[o] = obs.get(o, 0) + n
    sweep[k] = dict(wells=w, summary=dict(pick=s["pick"]["ok"], safe=s["safe"]["ok"], gsafe=s["grid_safe"]["ok"],
                    gtop=s["grid_top"]["ok"], corner=(f"{s['stage_corner']['ok']}/{s['stage_corner']['n']}" if "stage_corner" in s else "–"), obst=", ".join(sorted(obs, key=lambda o: -obs[o]))))
theta = {k: v["theta"] for k, v in meta["variants"].items()}
# assembly steps (W-B baseline): cumulative; regexes over part keys (without the 'WB__' prefix)
STEPS = [
    dict(n=1, parts=[r"^base_plate$"]),
    dict(n=2, parts=[r"^post_\d$", r"^post_brace_\d$"]),
    dict(n=3, parts=[r"^y_beam$"]),
    dict(n=4, parts=[r"^Y_actuator_body$", r"^Y_motor$", r"^Y_home_switch$"]),
    dict(n=5, parts=[r"^Y_carriage$", r"^X_support_beam$", r"^X_actuator_body$", r"^X_motor$", r"^X_home_switch$"]),
    dict(n=6, parts=[r"^X_carriage_bracket$", r"^Z_actuator_body$", r"^Z_motor$", r"^Z_home_switch_top$", r"^R08__Z_carriage$"]),
    dict(n=7, parts=[r"^R08__breakaway_kinematic_mount$", r"^R08__arm_thin$", r"^R08__arm_deep$", r"^R08__capillary_holder_collet$"]),
    dict(n=8, parts=[r"^Y_cable_chain$", r"^X_cable_chain$", r"^motion_controller_24V$"]),
    dict(n=9, parts=[r"tubing", r"^syringe_pump_existing$"]),
    dict(n=10, parts=[r"^R08__glass_capillary"]),
]
d1 = {k: dict(label=v["label"], observed=v["observed_pick"]) for k, v in an["d1"].items()}
import analysis  # noqa
access = {}
for k, t in theta.items():
    a = analysis.well_access(t)
    access[k] = dict(ok=a["bottom_reachable_centre"], rim=a["rim_clearance_centre"], depth=a["max_centred_depth"])
data = dict(parts=meta["parts"], variants=meta["variants"], condensers=meta["condensers"], condenser_choices=CONDENSER_CHOICES,
            Z_PICK=meta["Z_PICK"], safe_z=meta["safe_z"], corridor=meta.get("corridor", {}), wells=wells, sweep=sweep, access=access,
            workflows={k: dict(label=v["label"], layout=v["layout"]) for k, v in meta["workflows"].items()},
            export_set=meta["export_set"], d1=d1, steps=STEPS)
html = open(os.path.join(HERE, "template.html")).read()
from keynums import keynums  # noqa: E402
from render_docs import render  # noqa: E402
html = render(html, keynums())
html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))).replace("/*__STL__*/null", json.dumps(stl, separators=(",", ":")))
fn = os.path.join(HERE, "ix73_picker_viewer.html")
open(fn, "w").write(html)
print(fn, len(html) / 1e6, "MB")
