"""Render docs/src/*.md and README.src.md with key numbers.  `--check` exits 1 if a rendered
file is out of date (use before committing / in CI)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from keynums import keynums  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAIRS = [(os.path.join(ROOT, "README.src.md"), os.path.join(ROOT, "README.md"))]
SRC = os.path.join(ROOT, "docs", "src")
PAIRS += [(os.path.join(SRC, f), os.path.join(ROOT, "docs", f)) for f in sorted(os.listdir(SRC)) if f.endswith(".md")]
HDR = "<!-- GENERATED from {src} by cad/render_docs.py - edit the source, not this file -->\n"


def render(text, k):
    def sub(m):
        key, fmt = m.group(1), m.group(2)
        if key not in k:
            raise KeyError(f"unknown key {{{{{key}}}}}")
        v = k[key]
        if fmt:
            return format(v, fmt)
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    return re.sub(r"\{\{([A-Za-z0-9_]+)(?::([^}]+))?\}\}", sub, text)


def main(check=False):
    k = keynums()
    stale = []
    for src, dst in PAIRS:
        out = HDR.format(src=os.path.relpath(src, ROOT)) + render(open(src).read(), k)
        cur = open(dst).read() if os.path.exists(dst) else ""
        if cur != out:
            stale.append(os.path.relpath(dst, ROOT))
            if not check:
                open(dst, "w").write(out)
    if check and stale:
        print("out of date:", ", ".join(stale)); sys.exit(1)
    print(("checked" if check else "rendered"), len(PAIRS), "files;", "stale:" if check else "updated:", stale)


if __name__ == "__main__":
    main("--check" in sys.argv)
