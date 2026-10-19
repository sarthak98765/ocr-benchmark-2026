# Gemini 3.5 Flash Lite (via OpenRouter) — analysis

**Category:** Small general LLM used as OCR (closed, API) — the budget option
**Output file:** `output/gemini_3_5_flash_lite.md`
**Overall rank in this test:** #4

## Scorecard

| Factor | Result |
|---|---|
| Model / version | `google/gemini-3.5-flash-lite` (OpenRouter, run 2026-10-17) |
| How it was called | Same as the other Gemini runs |
| Key fields correct | 51 / 55 (93%) |
| Word F1 / recall / precision | 91.5% / 90.7% / 92.4% |
| F1 on invoices (p1–3) | 97.9% |
| F1 on noisy scanned forms (p4–10) | 88.8% |
| Latency (10 pages, 3 runs) | 18.8 s / 18.2 s / 20.7 s → **~1.9 s per page** (fastest Gemini) |
| Cost (billed by OpenRouter) | $0.0188 per 10 pages → **≈ $1.88 per 1,000 pages** (cheapest paid engine) |
| Tables | Markdown tables, correct on invoices |
| Checkboxes (p6) | **Wrong — inverted.** Wrote `STEEL X  ALUMINUM ☐`; the page has ALUMINUM checked |
| Handwriting | Read `8650`, missed `4060` |
| Images / figures | None; no bounding boxes |

## Errors that matter

| Page | Ground truth | Wrote | Impact |
|---|---|---|---|
| 6 | ALUMINUM ☑, STEEL ☐ | `STEEL X ALUMINUM ☐` | **Inverted checkbox** — a form field silently gets the wrong value |
| 4 | `39A00A`, `$12,764.00` | `$12.784.00`; `39A00A` missing | Wrong digit and wrong separator in an amount on the fax |
| 5 | `WEBCRAFT TECHNOLOGIES` | not found | Supplier name lost |

## What it did well

- Word-level accuracy almost equal to the bigger models (F1 91.5% vs 92.0%).
- Half the price and 2.4× faster than Gemini 3.8 Flash.

## Weak points

- The word score hides **semantic** errors: the checkbox inversion and wrong amounts barely change F1 but would break a form-processing system.

## Best for / avoid for

- **Best for:** cheap bulk text extraction for search/RAG, where a few wrong values are acceptable.
- **Avoid for:** forms, checkboxes, and money fields without a validation step.

## Reproduce

```bash
python code/gemini_3_5_flash_lite.py
```
