"""candidates.csv -> docs/12_parts_candidates.md (and an HTML table fragment for the Japanese guide).
    python docs/parts/build_parts.py"""
import csv
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "cad"))
from params import FREEZE_GATE  # noqa: E402
ROWS = list(csv.DictReader(open(os.path.join(HERE, "candidates.csv"), encoding="utf-8")))


def md_cell(x):
    return (x or "").replace("|", "\\|").replace("\n", " ")


def markdown():
    L = ["<!-- GENERATED from docs/parts/candidates.csv by docs/parts/build_parts.py - edit the CSV -->",
         "# Parts candidates (stage 1, NOT an order list)", "",
         "Candidates for each line item of the W-B baseline, researched from web-search excerpts on 2026-09-26. "
         "Vendor pages could not be opened from the authoring environment, so **part numbers, specs, prices and "
         "lead times must be confirmed in a quotation** before ordering, and nothing is ordered before the freeze "
         f"gate ({', '.join(FREEZE_GATE)}). Research notes and all URLs: `docs/parts/research_notes.md`.", "",
         "| ID | Category | Item | Qty | Requirement | Candidate 1 | Candidate 2 | Key spec | Approx. price | Verified |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in ROWS:
        L.append("| " + " | ".join(md_cell(r[k]) for k in ("id", "category", "item", "qty", "requirement", "candidate_1",
                                                           "candidate_2", "key_spec", "approx_price", "verified")) + " |")
    L += ["", "## Sources per item", ""]
    for r in ROWS:
        urls = [u.strip() for u in r["source_urls"].replace(";", " ").split() if u.startswith("http")]
        if urls:
            L.append(f"- **{r['id']}** " + ", ".join(f"<{u}>" for u in urls))
    return "\n".join(L) + "\n"


def html_table():
    rows = "".join(
        f"<tr><td class=\"mono\">{html.escape(r['id'])}</td><td>{html.escape(r['category'])}</td>"
        f"<td>{html.escape(r['item'])}</td><td>{html.escape(r['qty'])}</td><td>{html.escape(r['candidate_1'])}</td>"
        f"<td>{html.escape(r['approx_price'])}</td><td>{html.escape(r['verified'])}</td></tr>" for r in ROWS)
    return ("<div class=\"tbl\"><table><thead><tr><th>ID</th><th>区分</th><th>品目</th><th>数量</th><th>第一候補</th>"
            "<th>価格目安(抜粋)</th><th>確認状況</th></tr></thead><tbody>" + rows + "</tbody></table></div>")


if __name__ == "__main__":
    open(os.path.join(ROOT, "docs", "12_parts_candidates.md"), "w", encoding="utf-8").write(markdown())
    open(os.path.join(HERE, "parts_table_ja.html"), "w", encoding="utf-8").write(html_table())
    print(len(ROWS), "items")
