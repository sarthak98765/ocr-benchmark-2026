# Gemini 3 Flash Preview (via OpenRouter) — analysis

**Category:** General LLM used as OCR (closed, API)
**Output file:** `output/gemini_3_flash_preview.md`
**Overall rank in this test:** #3

## Scorecard

| Factor | Result |
|---|---|
| Model / version | `google/gemini-3-flash-preview` (OpenRouter, run 2026-10-17) |
| How it was called | Same as Gemini 3.8 Flash: whole PDF, native PDF input, `temperature=0`, reasoning `low`, same prompt |
| Key fields correct | **54 / 55 (98%)** |
| Word F1 / recall / precision | 91.7% / **91.6%** (highest recall) / 91.8% |
| F1 on invoices (p1–3) | 98.5% |
| F1 on noisy scanned forms (p4–10) | 88.8% |
| Latency (10 pages, 3 runs) | 30.8 s / 38.3 s / 35.7 s → **~3.7 s per page** |
| Cost (billed by OpenRouter) | $0.026 per 10 pages → **≈ $2.59 per 1,000 pages** |
| Tables | Markdown tables, correct |
| Checkboxes (p6) | All correct (`[X]` / `[ ]`) |
| Handwriting | Read `4060` and `8650`, and labeled them: `[handwritten: 4060 - TOTAL - 8650]` |
| Signatures | Marked as `[signature]` |
| Images / figures | None; no bounding boxes |

## Errors that matter

| Page | Ground truth | Wrote |
|---|---|---|
| 4 | Distributor No. `20182` | not found |

## What it did well

- Almost as accurate as 3.8 Flash, **18% cheaper and ~20% faster**.
- The only engine that **labeled** handwriting as handwriting — useful when a reviewer must know which values a human wrote.
- Good choice if you already use it: the upgrade to 3.8 Flash gained only +1 key field and +0.3 F1 points on this set.

## Weak points

- "Preview" model: Google can change or retire it; pin and monitor.
- Same LLM limits as 3.8 Flash: no coordinates, prompt-dependent format.

## Best for / avoid for

- **Best for:** PDF → LLM → JSON pipelines where cost matters.
- **Avoid for:** long-term contracts on a preview model; audit trails that need boxes.

## Reproduce

```bash
python code/gemini_3_flash_preview.py
```
