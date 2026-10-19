# Gemini 3.8 Flash (via OpenRouter) — analysis

**Category:** General LLM used as OCR (closed, API)
**Output file:** `output/gemini_3_8_flash.md`
**Overall rank in this test:** #1 (tied on word F1 with Mistral OCR 4.1, best on key fields)

## Scorecard

| Factor | Result |
|---|---|
| Model / version | `google/gemini-3.8-flash` (OpenRouter, run 2026-10-17) |
| How it was called | Whole 10-page PDF in one request, native PDF input, `temperature=0`, reasoning effort `low`, one fixed transcription prompt |
| Key fields correct | **55 / 55 (100%)** |
| Word F1 / recall / precision | **92.0%** / 91.5% / 92.5% |
| F1 on invoices (p1–3) | 98.1% |
| F1 on noisy scanned forms (p4–10) | 89.4% (best of all engines) |
| Latency (10 pages, 3 runs) | 46.6 s / 44.8 s / 45.5 s → **~4.5 s per page** (slowest API) |
| Cost (billed by OpenRouter) | $0.0317 per 10 pages → **≈ $3.17 per 1,000 pages** (a `:batch` variant is listed at half the token price) |
| Tables | Markdown tables, structure correct on all invoice tables |
| Checkboxes (p6, 8 checked) | All 8 correct, written as ☑ / ☐ |
| Handwriting | Read `4060` and `TOTAL 8650` correctly (p6) |
| Signatures | Marked as `[signature]` — never invented a name |
| Strike-through | Not marked (no engine marked it) |
| Images / figures | None extracted; no bounding boxes |
| Self-host / data privacy | No self-hosting. Data goes to OpenRouter and Google |

## What it did well

- The only engine that found **every** business-critical value, including the faxed amounts on page 4 (`$143,922.60`, `$12,764.00`, `$156,686.60`) that Mistral and LandingAI misread.
- Read the handwritten `4060` on page 6, which matches the printed arithmetic (3,015 + 1,045).
- Kept checkbox state and table structure on old, low-resolution (≈90 dpi) faxes.
- Did not hallucinate text into empty table cells or invent signer names.

## Weak points

- Slowest of the API engines (~45 s for 10 pages in one request). Split the PDF and send pages in parallel to cut wall-clock time.
- Output depends on a prompt. A different prompt can change format and behavior. The page markers worked on all 10 pages here, but a production system must validate them.
- No coordinates: you cannot draw a box around a value or prove where it came from.
- Non-deterministic in principle, even at `temperature=0` (cost varied slightly across the 3 runs: $0.0317 / $0.0313 / $0.0324).

## Best for / avoid for

- **Best for:** highest accuracy on messy scans at low cost; teams already on Google / OpenRouter; extraction where you post-process with the same LLM.
- **Avoid for:** audit trails that need bounding boxes; strict data-residency rules; very low-latency per-page needs.

## Reproduce

```bash
python code/gemini_3_8_flash.py
```
