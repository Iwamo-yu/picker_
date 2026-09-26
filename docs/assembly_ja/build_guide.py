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


src = open(os.path.join(HERE, "guide.src.html"), encoding="utf-8").read()
src = re.sub(r"\{\{IMG:([^}]+)\}\}", lambda m: img(m.group(1)), src)
out = render(src, keynums())
fn = os.path.join(HERE, "assembly_guide_ja.html")
open(fn, "w", encoding="utf-8").write(out)
print(fn, round(len(out) / 1e6, 2), "MB")
