# Docling (default pipeline, RapidOCR) — analysis

**Category:** Open-source document pipeline (MIT, IBM / LF AI & Data)
**Output file:** `output/docling_ocr.md`
**Overall rank in this test:** #8

## Scorecard

| Factor | Result |
|---|---|
| Version | `docling 2.140.0`, standard PDF pipeline, default options (layout Heron, TableFormer, RapidOCR) |
| Where it ran | CPU only |
| Key fields correct | 46 / 55 (84%) |
| Word F1 / recall / precision | 69.5% / 71.7% / 75.5% |
| F1 on invoices (p1–3) | 74.0% |
| F1 on noisy scanned forms (p4–10) | 67.5% |
| Latency | Cold 107 s, warm 66 s for 10 pages → **~6.6 s per page** (CPU) |
| Cost | $0. Throughput ≈ 545 pages/hour on one CPU (depends on hardware) |
| Tables | 8 tables detected; merged cells are **repeated** in every column |
| Checkboxes (p6) | Correct (`- [x] ALUMINUM`) |
| Handwriting | Not read |
| Grounding / images | Full JSON with boxes for every element; **18 pictures** with crops |

## Errors that matter

| Page | What happened |
|---|---|
| 4 (fax) | The layout model classified **the whole form as one picture**. The Markdown has only `<!-- image -->` — all 239 words of the form are lost (F1 7.7%) |
| 5 | Table cells repeated across merged columns: 510 output words for a 198-word page (precision 28%) |
| 1 | Same repetition on the Flipkart table (precision 53%) |
| 2 | Page footer (AWS footnotes, service provider) removed — Docling puts headers/footers in the "furniture" layer and the default Markdown export skips them |

## What it did well

- Good on typed scanned forms (pages 6–10: 80–89% F1) and checkboxes.
- Richest local data model (`DoclingDocument`): layout, tables, pictures, reading order, provenance boxes, many export formats.
- Free, private, CPU-only; easy `pip install`.

## Weak points

- Default settings are fragile on dark/heavy faxes (page-as-picture) and on spanned table cells.
- Slower than Tesseract and the APIs on CPU.

## How to improve (not used in the scored run)

- Use a VLM pipeline (`--pipeline vlm`, e.g. GraniteDocling) or a stronger OCR engine via `ocr_options`.
- Set `force_full_page_ocr=True` and enable OCR inside picture regions, so text in "picture" areas is not lost.
- Export with furniture included if headers/footers matter.

## Best for / avoid for

- **Best for:** digital-born PDFs and Office files, RAG ingestion, when you need a rich structured document and local execution.
- **Avoid for:** low-quality faxes/scans with default settings.

## Reproduce

```bash
python code/docling_ocr.py
```
