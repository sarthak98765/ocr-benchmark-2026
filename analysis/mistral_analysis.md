# Mistral OCR 4.1 — analysis

**Category:** Dedicated OCR API (closed, most used "LLM-era" OCR API)
**Output file:** `output/mistral.md`
**Overall rank in this test:** #2 (tied #1 on word F1, by far the fastest)

## Scorecard

| Factor | Result |
|---|---|
| Model / version | `mistral-ocr-latest` = `mistral-ocr-4-1` (OCR 4.1), resolved from `/v1/models` aliases, run 2026-10-17 |
| How it was called | `client.ocr.process` with the whole PDF, default options, `include_image_base64=True` |
| Key fields correct | **53 / 55 (96%)** |
| Word F1 / recall / precision | **92.0%** / 91.2% / **92.8%** (highest precision) |
| F1 on invoices (p1–3) | **98.6%** (best) — 100% on the Flipkart scan |
| F1 on noisy scanned forms (p4–10) | 89.1% |
| Latency (10 pages, 3 runs) | 4.7 s / 4.1 s / 3.9 s → **~0.4 s per page** (fastest of all 9) |
| Cost | Official list price **$4 per 1,000 pages** (docs.mistral.ai pricing, OCR 4.1) |
| Tables | Markdown tables; very clean on invoices |
| Checkboxes (p6) | Correct, written as ☒ / ☐ |
| Handwriting | Read `8650` but missed `4060` (p6); read "Charges to cancel" (p5) |
| Images / figures | **2 images extracted** with coordinates and base64 crops |
| Self-host / data privacy | API only in this test (Mistral also sells self-hosted / VPC deployments) |

## Errors that matter

| Page | Ground truth | Mistral wrote | Impact |
|---|---|---|---|
| 4 | `$12,764.00` | `$12,784.00` | Wrong amount by $20 on a check request — silent error |
| 6 | handwritten `4060` | not transcribed | Handwritten subtotal lost (`8650` was read) |

The page-4 error is a good example of why you should validate totals: `143,922.60 + 12,784.00 ≠ 156,686.60`.

## What it did well

- Perfect transcription of the scanned Flipkart invoice (100% F1, all 8 key fields).
- 10 pages in ~4 seconds — 10× faster than any other engine with similar accuracy.
- Returns image crops with positions, so you can store figures/logos separately.
- Predictable, schema-stable output (no prompt to tune).

## Weak points

- Misread one digit in a faxed amount (see above).
- Skipped one of the two handwritten numbers.
- No word- or block-level coordinates in the default Markdown (only image boxes).

## Best for / avoid for

- **Best for:** high-volume production pipelines, invoices and typed documents, low latency, simple integration.
- **Avoid for:** forms where handwritten values matter, unless you add a second check.

## Reproduce

```bash
python code/mistral.py
```
