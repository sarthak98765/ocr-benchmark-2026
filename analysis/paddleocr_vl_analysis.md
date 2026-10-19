# Baidu PaddleOCR-VL 1.6 — analysis

**Category:** Open-source VLM pipeline (Apache-2.0), 0.9B VL model + PP-DocLayoutV3 layout model; top open model on OmniDocBench v1.6 in public leaderboards
**Output file:** `output/paddleocr_vl.md`
**Overall rank in this test:** #7

## Scorecard

| Factor | Result |
|---|---|
| Model / version | `PaddlePaddle/PaddleOCR-VL-1.6`, pipeline `v1.6`, paddleocr 3.7.0 / paddlex 3.7.2 |
| Where it ran | Official pipeline; the VLM served by a separate local server (`vl_rec_backend`) on a GPU |
| Key fields correct | 42 / 55 (76%) — several misses are only a dropped `$` sign |
| Word F1 / recall / precision | 81.0% / **74.6%** / 90.4% |
| F1 on invoices (p1–3) | 76.2% (Flipkart scan 91.2%, AWS 59.1%, Free 78.4%) |
| F1 on noisy scanned forms (p4–10) | 83.1% |
| Latency | **~12.5 s per page** warm (9–20 s); pipeline init 43 s |
| Cost | $0 API. Throughput ≈ 290 pages/hour on the test GPU (depends on hardware) |
| Tables | 21 HTML tables — strong table detection |
| Checkboxes (p6) | Correct (ALUMINUM ☒) |
| Handwriting | Not read; "Charges to cancel" became "Charges to **Curbs**" |
| Grounding / images | Block boxes from the layout model; **9 image crops** saved with positions |

## Errors that matter

| Page | What happened |
|---|---|
| 2 (AWS) | Footnotes and the service-provider footer **not exported** (pipeline treats them as page furniture); `$` signs dropped from the detail table (`1.87` instead of `$1.87`); LaTeX artifacts such as `$4.11$`, `VAT $ ^{{**}} $`, `<nl>` |
| 3 (Free) | Sender block and part of the customer-service footer missing |
| 4 | Missed the distributor name and number and two amounts |

## What it did well

- High precision (90.4%): it rarely adds text that is not on the page.
- Best open-source result on the Flipkart scan (91.2% F1), where Unlimited-OCR failed.
- Proper document pipeline: layout, reading order, tables, image crops.

## Weak points

- Low recall because headers/footers/footnotes are dropped by default — important on invoices (legal entity, address, tax notes live there).
- Formula-style artifacts (`$…$`) leak into normal text and numbers.
- A separate environment and a VLM server for good speed; more moving parts than an API.

## Best for / avoid for

- **Best for:** free, private OCR with good tables and image crops, when you can tune or post-process (keep headers/footers, strip LaTeX).
- **Avoid for:** "out-of-the-box complete text" needs, such as compliance archiving of every line on an invoice.

## Reproduce

```bash
python code/paddleocr_vl.py
```
