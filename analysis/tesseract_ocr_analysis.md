# Tesseract 5 — analysis

**Category:** Classic open-source OCR (Apache-2.0) — the baseline
**Output file:** `output/tesseract_ocr.md`
**Overall rank in this test:** #9

## Scorecard

| Factor | Result |
|---|---|
| Version | `tesseract 5.5.3` (Homebrew), LSTM models `eng` + `fra` (tessdata_fast) |
| How it was called | CLI per page image, default page segmentation, `-l eng+fra`, plain-text output |
| Key fields correct | 33 / 55 (60%) |
| Word F1 / recall / precision | 62.3% / 57.4% / 70.0% |
| F1 on invoices (p1–3) | **86.2%** (Free invoice 94.8%) |
| F1 on noisy scanned forms (p4–10) | 52.0% (worst) |
| Latency | **0.72 s per page** on CPU (7.2 s for 10 pages) |
| Cost | $0. Throughput ≈ 5,000 pages/hour on one CPU |
| Tables | None — plain text; columns are merged into lines |
| Checkboxes | Not represented (`[ )`, `CS`, `ik.`) |
| Handwriting | Not read |
| Grounding | Available via hOCR/TSV output (not used here) |

## Errors that matter

| Page | Ground truth | Tesseract wrote |
|---|---|---|
| 1 | `OD304175096047380001` | `0D304175096047380001` (zero instead of letter O) |
| 1 | `VAT/TIN: 29670869006` | `VATITIN: 29671 Ka ads` |
| 10 | `LRB 1946`, `$4.50`, `$8,000`, `262-6423` | all missed (noisy fiscal-estimate form, F1 30%) |
| 7 | `Peter J. Marzullo`, `Lorillard Tobacco Company` | missed |

## What it did well

- Very fast and free; zero setup beyond `brew install tesseract`.
- Good on clean, single-column printed text (Free invoice 94.8% F1, better than Docling and PaddleOCR-VL there).

## Weak points

- No structure: no tables, no reading-order model, no Markdown.
- Breaks down on faxes, low resolution (~90 dpi), and form layouts.

## Best for / avoid for

- **Best for:** clean printed text at huge volume, offline, on any hardware; a cheap first pass.
- **Avoid for:** invoices with tables, forms, scans, anything you need to extract fields from.

## Reproduce

```bash
python code/tesseract_ocr.py
```
