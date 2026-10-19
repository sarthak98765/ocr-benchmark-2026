"""Score every output/*.md against data/ground_truth and data/key_fields.json.

Run: python code/score.py
Writes analysis/results.csv (one row per engine) and analysis/per_page.csv.

- Word F1: bag-of-words match per page (order ignored, because FUNSD ground truth is not in
  reading order), averaged over the 10 pages.
- Key fields: a field counts when it appears in the page output after lowercasing and
  removing all whitespace and markup.
"""

import csv
import html
import json
import re
import unicodedata
from collections import Counter

from common import N_PAGES, OUTPUT, ROOT, split_pages

DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
RUN_INFO = re.compile(r"<!-- run: (\{.*?\}) -->")


def to_plain(md: str) -> str:
    """Remove Markdown/HTML markup so only the visible text is left."""
    text = html.unescape(md)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)  # image links
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # keep link text
    text = re.sub(r"<[^>]+>", " ", text)  # HTML tags, page markers
    text = re.sub(r"\\([_*#|\[\]()$-])", r"\1", text)  # Markdown escapes
    text = re.sub(r"^\s*[-:| ]{3,}\s*$", " ", text, flags=re.M)  # table rules
    text = re.sub(r"[|#*`>]", " ", text)
    return unicodedata.normalize("NFKC", text)


def words(text: str) -> list[str]:
    out = []
    for tok in to_plain(text).lower().split():
        tok = tok.strip(".,:;()[]{}\"'“”‘’!?")
        if any(ch.isalnum() for ch in tok):
            out.append(tok)
    return out


def squash(text: str) -> str:
    return re.sub(r"\s+", "", to_plain(text).lower())


def score_page(output: str, truth: str, fields: list[str]) -> dict:
    o, g = Counter(words(output)), Counter(words(truth))
    hit = sum((o & g).values())
    recall, precision = hit / max(sum(g.values()), 1), hit / max(sum(o.values()), 1)
    f1 = 2 * recall * precision / (recall + precision) if recall + precision else 0.0
    return {"f1": f1, "recall": recall, "precision": precision,
            "fields_found": sum(squash(f) in squash(output) for f in fields), "fields_total": len(fields)}


def main() -> None:
    truths = [(DATA / "ground_truth" / f"page_{i:02d}.txt").read_text() for i in range(1, N_PAGES + 1)]
    fields = json.loads((DATA / "key_fields.json").read_text())
    rows, page_rows = [], []
    for path in sorted(OUTPUT.glob("*.md")):
        text = path.read_text()
        run = json.loads(RUN_INFO.search(text).group(1))
        pages = [score_page(md, truths[i], fields.get(str(i + 1), [])) for i, md in enumerate(split_pages(text))]
        times = run["runs_total_seconds"]
        warm = times[1:] or times
        cost = run.get("cost_usd")
        rows.append({
            "engine": path.stem,
            "key_fields": f"{sum(p['fields_found'] for p in pages)}/{sum(p['fields_total'] for p in pages)}",
            "word_f1": round(sum(p["f1"] for p in pages) / N_PAGES, 4),
            "recall": round(sum(p["recall"] for p in pages) / N_PAGES, 4),
            "precision": round(sum(p["precision"] for p in pages) / N_PAGES, 4),
            "f1_invoices_p1_3": round(sum(p["f1"] for p in pages[:3]) / 3, 4),
            "f1_forms_p4_10": round(sum(p["f1"] for p in pages[3:]) / 7, 4),
            "seconds_per_page": round(sum(warm) / len(warm) / N_PAGES, 2),
            "usd_per_1000_pages": None if cost is None else round(cost * 1000 / N_PAGES, 2),
            "version": run.get("version"),
        })
        page_rows += [{"engine": path.stem, "page": i, **{k: round(v, 4) for k, v in p.items()}} for i, p in enumerate(pages, 1)]
    rows.sort(key=lambda r: -r["word_f1"])
    for name, data in (("results.csv", rows), ("per_page.csv", page_rows)):
        with (ANALYSIS / name).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    print(f"{'engine':24} {'fields':>7} {'F1':>6} {'s/page':>7} {'$/1k':>7}")
    for r in rows:
        cost = "-" if r["usd_per_1000_pages"] is None else f"{r['usd_per_1000_pages']:.2f}"
        print(f"{r['engine']:24} {r['key_fields']:>7} {r['word_f1']:>6.3f} {r['seconds_per_page']:>7} {cost:>7}")
    print("wrote analysis/results.csv and analysis/per_page.csv")


if __name__ == "__main__":
    main()
