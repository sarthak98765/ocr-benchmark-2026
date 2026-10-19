# Baidu Unlimited-OCR — analysis

**Category:** Open-source VLM (MIT license), released June 2026, claims SOTA on OmniDocBench v1.5/v1.6
**Output file:** `output/unlimited_ocr.md`
**Overall rank in this test:** #6 (best open-source engine)

## Scorecard

| Factor | Result |
|---|---|
| Model / version | `baidu/Unlimited-OCR` official weights (bf16, 3B MoE / ~0.5B active) via `mlx-vlm` 0.7.8 |
| Where it ran | Local GPU through `mlx-vlm`. Peak memory **9.3 GB** |
| How it was called | One page image per call, model-card prompt `<image>document parsing.`, `no_repeat_ngram_size=35`, window 128 (as in the model card) |
| Key fields correct | 45 / 55 (82%) |
| Word F1 / recall / precision | 84.5% / 84.1% / 85.6% |
| F1 on invoices (p1–3) | 84.0% (pulled down by the Flipkart scan: 57.1%) |
| F1 on noisy scanned forms (p4–10) | 84.7% |
| Latency | **~27 s per page** warm (18–30 s; 63 s on the failed page 1); model load 4 s |
| Cost | $0 API. Throughput ≈ 130 pages/hour on the test GPU (depends on hardware) |
| Tables | HTML tables; correct on the AWS and Free invoices |
| Checkboxes (p6) | Lost the checked state (`STEEL □ ALUMINUM`, no mark) |
| Handwriting | Not read (`4060`, `8650`, "Charges to cancel" missing) |
| Grounding | Label + bounding box for every block (`header`, `title`, `table`, `image`…) |
| Images | 3 image regions with boxes (no crops) |

## Errors that matter

| Page | What happened |
|---|---|
| 1 (Flipkart scan) | **Hallucination**: 14 lines of `1. 2017年1月1日` (a Chinese date), broken fragments ("Order ID: 0" ×3) and an invented formula `\( \therefore m = \frac{3}{11} \)`. Order ID, service tax no., FSN all lost |
| 5 (first run, without n-gram blocking) | Repeated a table until the 8,192-token limit and lost the rest of the page. Fixed by the model-card setting `no_repeat_ngram_size=35` |
| 4 | Missed `$12,764.00` and `$156,686.60` |

The first run (without the setting) is not included in this repo; `code/unlimited_ocr.py` uses the setting.

## What it did well

- On clean or moderately noisy pages it matches the paid APIs: AWS invoice 99.5% F1, Free invoice 95.3%, research form (p8) 93.4%.
- Fully local and free; good structure (labeled blocks with coordinates).

## Weak points

- **Unstable on a low-quality phone/scan image**: it degenerated into repeated and invented text.
- Slow on the test GPU (~27 s/page). A data-center GPU with vLLM is expected to be much faster.
- Needs the repetition guard; without it, pages can loop until the token limit.

## Caveat

This test used the community-maintained `mlx-vlm` port, not Baidu's official CUDA code. I also had to work around an `mlx-vlm` 0.7.8 bug (processor registered for `unlimited-ocr` instead of `unlimited_ocr`). Results on the official CUDA/vLLM path may differ.

## Best for / avoid for

- **Best for:** private, on-prem parsing of clean digital-born or decent scans; teams with a GPU.
- **Avoid for:** low-quality mobile photos/scans without a fallback; latency-sensitive work without a strong GPU.

## Reproduce

```bash
python code/unlimited_ocr.py
```
