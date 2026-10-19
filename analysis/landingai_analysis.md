# LandingAI ADE (Agentic Document Extraction) — analysis

**Category:** Premium document-AI API (closed) — positioned as "best quality"
**Output file:** `output/landingai.md`
**Overall rank in this test:** #5

## Scorecard

| Factor | Result |
|---|---|
| Model / version | `dpt-2-20260903` (default parse model, run 2026-10-17) |
| How it was called | `client.parse(document=PDF, split="page")`, defaults |
| Key fields correct | 53 / 55 (96%) |
| Word F1 / recall / precision | 87.6% / 88.8% / 86.9% |
| F1 on invoices (p1–3) | 97.4% |
| F1 on noisy scanned forms (p4–10) | 83.4% |
| Latency (10 pages, 3 runs) | 26.5 s / 19.6 s / 22.9 s → **~2.1 s per page** |
| Cost (billed credits) | 30 credits per 10 pages = **$0.30 → $30 per 1,000 pages** (1 credit = $0.01) — 7–16× the other APIs |
| Tables | HTML tables with cell IDs and per-cell grounding — the richest table output |
| Checkboxes (p6, p7) | Correct (`[x]` / `[ ]`) |
| Handwriting | Read `8650` and "Charges to cancel"; missed `4060` |
| Grounding | **Bounding box for every chunk and table cell** (best of all engines) |
| Images / figures | No `figure` chunks; 5 `logo` and 6 `attestation` chunks with text descriptions |

## Errors that matter

| Page | Ground truth | Wrote | Seen in |
|---|---|---|---|
| 7 | Empty table rows | Paragraphs about **NMR, IR, UV-Vis and mass spectra** ("The ¹H NMR spectrum of 2 in CDCl₃…") inside empty cells | 1 of 4 runs |
| 7 | Illegible signature | `Signature: Legible (Peter J. Mayhew)` / `Peter J. Mayell` — **an invented name**; the typed name on the page is Peter J. Marzullo | **4 of 4 runs** |
| 4 | Check Total `$156,686.60` | `$155,686.60` — wrong by $1,000, while both line amounts were read correctly | 1 of 1 scored run |

Evidence: `output/landingai.md` (run 1). The page-7 checks (2 more runs of page 7 alone, 1 more run of the full PDF) are not included in this repo.

## What it did well

- Best structure: typed chunks (text, table, logo, attestation, marginalia), table cells with row/column positions, and coordinates for everything — ideal for "click a value, see where it came from" UIs.
- Clean invoice output (100% F1 on the AWS invoice).

## Weak points

- **Hallucination risk**: the model writes descriptions (logos, attestations), and once invented unrelated chemistry text. It also names illegible signatures. In regulated workflows, an invented signer name is a serious defect.
- Most expensive engine in the test by a wide margin.
- The descriptive text lowers precision (86.9%), so downstream search/RAG gets extra words that are not on the page.

## Best for / avoid for

- **Best for:** UIs and agents that need grounding (citations to page regions); complex tables where cell positions matter.
- **Avoid for:** high-volume, cost-sensitive OCR; signature/identity fields; any workflow without a human or rule-based check on generated text.

## Reproduce

```bash
python code/landingai.py
```
