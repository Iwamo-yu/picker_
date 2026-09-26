"""Render the Japanese assembly guide: numbers from cad/keynums.py, images embedded as data URIs.
    python docs/assembly_ja/build_guide.py  -> docs/assembly_ja/assembly_guide_ja.html"""
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "cad"))
from keynums import keynums  # noqa: E402
from render_docs import render  # noqa: E402


def img(name):
    for d in (os.path.join(HERE, "img"), os.path.join(ROOT, "docs", "img")):
        fn = os.path.join(d, name)
        if os.path.exists(fn):
            return "data:image/png;base64," + base64.b64encode(open(fn, "rb").read()).decode()
    raise FileNotFoundError(name)


import html
import subprocess
from keynums import placeholders  # noqa: E402


def git(*a):
    try:
        return subprocess.check_output(["git", "-C", ROOT, *a], text=True).strip()
    except Exception:
        return ""


src = open(os.path.join(HERE, "guide.src.html"), encoding="utf-8").read()
info = git("log", "-1", "--format=%cd · %h", "--date=format:%Y-%m-%d") or "unknown"
ph_rows = "".join(f"<tr><td><code>{html.escape(n)}</code></td><td>{html.escape(str(v))}</td><td>{html.escape(note)}</td></tr>"
                  for n, v, note in placeholders())
log = git("log", "-8", "--format=%cd|%s", "--date=format:%Y-%m-%d")
changelog = "".join(f"<li>{html.escape(l.split('|', 1)[0])}: {html.escape(l.split('|', 1)[1])}</li>" for l in log.splitlines() if "|" in l)
parts = open(os.path.join(ROOT, "docs", "parts", "parts_table_ja.html"), encoding="utf-8").read()
src = src.replace("{{PARTS_TABLE}}", parts).replace("{{BUILD_INFO}}", html.escape(info)).replace("{{PH_TABLE}}", ph_rows).replace("{{CHANGELOG}}", changelog)
src = re.sub(r"\{\{IMG:([^}]+)\}\}", lambda m: img(m.group(1)), src)
out = render(src, keynums())
fn = os.path.join(HERE, "assembly_guide_ja.html")
open(fn, "w", encoding="utf-8").write(out)
print(fn, round(len(out) / 1e6, 2), "MB")
