"""Regenerate everything from cad/params.py (single source of truth).

    python tools/build_all.py          # model, clearance sweep (~8 min), views, docs, viewer, guide
    python tools/build_all.py --fast   # skip the clearance sweep (keeps the last analysis.json)
    python tools/build_all.py --check  # only verify that rendered docs are up to date

The 3D step renders for the Japanese guide need Chromium (Playwright); set RENDER_JS to a
script that screenshots viewer steps (see docs/assembly_ja/README.md) or leave the committed PNGs.
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def run(*cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run([sys.executable, *cmd], cwd=ROOT, check=True)


def analysis_stale():
    sys.path.insert(0, os.path.join(ROOT, "cad"))
    import json
    import analysis
    fn = os.path.join(ROOT, "cad", "out", "analysis.json")
    if not os.path.exists(fn):
        return "cad/out/analysis.json missing"
    an = json.load(open(fn))
    if an.get("params_hash") != analysis.params_hash():
        return "analysis.json was made with different params/model/analysis code"
    bad = [r["cfg"] for r in an.get("head_consistency", []) if not r["ok"]]
    if bad:
        return f"exported CAD head differs from the analytic head record: {bad}"
    bad = [r["cfg"] for r in an.get("corridors", []) if r["scope"] in ("V1", "experimental")
           and not (r["feasible"] and r["ref_ok"])]
    if bad:
        return f"no positive safe-Z corridor / reference outside corridor for: {bad}"
    return None


if "--check" in sys.argv:
    why = analysis_stale()
    if why:
        sys.exit(f"stale or inconsistent analysis: {why}")
    sys.path.insert(0, os.path.join(ROOT, "docs", "parts"))
    import build_parts
    if open(os.path.join(ROOT, "docs", "12_parts_candidates.md"), encoding="utf-8").read() != build_parts.markdown():
        sys.exit("docs/12_parts_candidates.md is stale: run tools/build_all.py")
    run("cad/render_docs.py", "--check")
    run("docs/parts/build_partmap.py", "--check")
    print("analysis, parts list and rendered docs are up to date (guide/viewer: rebuild with build_all)")
    sys.exit(0)
run("cad/model.py")
if "--fast" in sys.argv:
    why = analysis_stale()
    if why:
        sys.exit(f"--fast refused: {why}.  Run the full `python tools/build_all.py` (clearance sweep ~10 min).")
else:
    run("cad/analysis.py")
run("cad/views.py")
run("docs/assembly_ja/figures.py")
run("docs/parts/build_parts.py")
run("cad/render_docs.py")
run("viewer/build_viewer.py")
if os.environ.get("RENDER_JS"):
    subprocess.run(["node", os.environ["RENDER_JS"]], check=True)
run("docs/assembly_ja/build_guide.py")
run("docs/assembly_ja/build_actions.py")
run("docs/parts/build_partmap.py")
print("done. Re-publish viewer/ix73_picker_viewer.html, docs/assembly_ja/assembly_guide_ja.html and part_map_ja.html if they are shared as pages.")
