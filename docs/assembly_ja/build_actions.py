"""docs/11_pre_assembly_actions_ja.md (rendered) -> docs/assembly_ja/pre_assembly_actions_ja.html
with the guide's styling.  python docs/assembly_ja/build_actions.py"""
import os
import re

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
md = open(os.path.join(ROOT, "docs", "11_pre_assembly_actions_ja.md"), encoding="utf-8").read()
md = re.sub(r"^<!--.*?-->\n", "", md)
# mermaid fences -> <pre class="mermaid"> (rendered natively by the artifact viewer)
md = re.sub(r"```mermaid\n(.*?)```", lambda m: '<pre class="mermaid">\n' + m.group(1) + "</pre>", md, flags=re.S)
body = markdown.markdown(md, extensions=["tables", "sane_lists"])
body = body.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
guide = open(os.path.join(HERE, "guide.src.html"), encoding="utf-8").read()
style = guide[guide.index("<style>"):guide.index("</style>") + len("</style>")]
fonts = guide[guide.index("<link rel=\"preconnect\""):guide.index("<style>")]
extra = """<style>
main h1{margin-bottom:8px} main h2{margin-top:18px} blockquote{margin:0;border-left:4px solid var(--meas);
background:var(--measbg);padding:8px 14px;border-radius:0 6px 6px 0} pre.mermaid{background:var(--paper);
border:1px solid var(--line);border-radius:6px;padding:10px;overflow-x:auto} td,th{font-size:13px}
</style>"""
html = f"<title>IX73 ピッカー 組立前の作業</title>\n{fonts}{style}\n{extra}\n<main>\n{body}\n</main>\n"
open(os.path.join(HERE, "pre_assembly_actions_ja.html"), "w", encoding="utf-8").write(html)
print("ok", round(len(html) / 1e3), "kB")
