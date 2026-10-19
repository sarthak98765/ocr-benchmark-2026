# OCR comparison: 9 engines on 10 hard pages

Run date: 2026-10-17.
Per-engine details: `analysis/<engine>_analysis.md`. Raw outputs: `output/<engine>.md`. Numbers: `analysis/results.csv` and `analysis/per_page.csv`.

## TL;DR

1. **Gemini 3.8 Flash** was the most accurate engine: 55/55 key fields correct, best on old faxes. Cost ≈ $3.17 per 1,000 pages. Speed ≈ 4.5 s/page.
2. **Mistral OCR 4.1** tied on word accuracy and was **10× faster** than everything else with similar quality (0.4 s/page, $4 per 1,000 pages). It made one wrong-digit error on a faxed amount.
3. The **premium API (LandingAI ADE)** cost 7–16× more and was **less** accurate. In 4 of 4 runs it invented a name for an illegible signature, and in 1 of 4 runs it wrote paragraphs about NMR spectroscopy into empty table rows.
4. The best **free/local** engine was **Unlimited-OCR** (84.5% F1). It matched the paid APIs on clean pages, but it hallucinated Chinese dates and a math formula on the noisy Flipkart scan.
5. **Word accuracy hides the dangerous errors.** Gemini 3.5 Flash Lite scored 91.5% F1, yet it **inverted a checkbox** (STEEL ☑ instead of ALUMINUM ☑). Always validate fields, totals, and checkboxes.

## The big table

| # | Engine | Category | Key fields (55) | Word F1 | Recall | Precision | F1 invoices p1–3 | F1 faxed forms p4–10 | Speed (warm, s/page) | Cost / 1,000 pages | Tables | Checkboxes (p6) | Handwriting (2 values) | Boxes / grounding | Images | Runs where |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gemini 3.8 Flash | General LLM (API) | **55** | **92.0** | 91.5 | 92.5 | 98.1 | **89.4** | 4.5 | $3.17 | Markdown | ✅ | **2/2** | ❌ | ❌ | OpenRouter / Google |
| 2 | Mistral OCR 4.1 | OCR API | 53 | **92.0** | 91.2 | **92.8** | **98.6** | 89.1 | **0.4** | $4.00 | Markdown | ✅ | 1/2 | Images only | ✅ 2 crops | Mistral API |
| 3 | Gemini 3 Flash Preview | General LLM (API) | 54 | 91.7 | **91.6** | 91.8 | 98.5 | 88.8 | 3.7 | $2.59 | Markdown | ✅ | **2/2** (labeled) | ❌ | ❌ | OpenRouter / Google |
| 4 | Gemini 3.5 Flash Lite | Small LLM (API) | 51 | 91.5 | 90.7 | 92.4 | 97.9 | 88.8 | 1.9 | **$1.88** | Markdown | ❌ inverted | 1/2 | ❌ | ❌ | OpenRouter / Google |
| 5 | LandingAI ADE (dpt-2) | Premium doc-AI API | 53 | 87.6 | 88.8 | 86.9 | 97.4 | 83.4 | 2.1 | **$30.00** | HTML + cell boxes | ✅ | 1/2 | ✅✅ every chunk + cell | Logos described | LandingAI API |
| 6 | Unlimited-OCR (Baidu) | Open-source VLM (MIT) | 45 | 84.5 | 84.1 | 85.6 | 84.0 | 84.7 | 27.2 (GPU) | $0 | HTML | ❌ state lost | 0/2 | ✅ every block | Boxes | Local (9.3 GB RAM) |
| 7 | PaddleOCR-VL 1.6 (Baidu) | Open-source VLM pipeline (Apache-2.0) | 42 | 81.0 | 74.6 | 90.4 | 76.2 | 83.1 | 12.5 (GPU) | $0 | HTML | ✅ | 0/2 | ✅ blocks | ✅ 9 crops | Local |
| 8 | Docling 2.140 (RapidOCR) | Open-source pipeline (MIT) | 46 | 69.5 | 71.7 | 75.5 | 74.0 | 67.5 | 6.6 (CPU) | $0 | Markdown (repeats merged cells) | ✅ | 0/2 | ✅ full JSON | ✅ 18 crops | Local CPU |
| 9 | Tesseract 5.5 | Classic open-source OCR | 33 | 62.3 | 57.4 | 70.0 | 86.2 | 52.0 | 0.7 (CPU) | $0 | ❌ plain text | ❌ | 0/2 | hOCR (not used) | ❌ | Local CPU |

Notes:
- Word F1 / recall / precision are order-independent word matches against ground truth, averaged over pages (%).
- The ground truth for pages 4–10 is the FUNSD annotation, which has its own errors (we found 3 wrong values). So ~90% is close to the ceiling on those pages.
- API speed is the wall-clock time of one 10-page request ÷ 10 (avg of runs 2–3). Local speed is warm per-page time on the test machine; it depends on hardware.
- API costs are the billed amounts (Gemini via OpenRouter `usage.cost`, LandingAI credits) or the official list price (Mistral). Local engines cost $0 in API fees; you pay for hardware and power.

Per-page F1 (%) — where each engine breaks:

| Engine | p1 Flipkart scan | p2 AWS | p3 Free (FR) | p4 fax check req. | p5 purchase req. | p6 proposal | p7 finance report | p8 application | p9 insertion order | p10 fiscal est. |
|---|---|---|---|---|---|---|---|---|---|---|
| Gemini 3.8 Flash | 98.8 | 99.7 | 95.8 | 81.1 | 83.4 | 93.8 | 89.7 | 94.8 | 93.8 | 89.0 |
| Mistral OCR 4.1 | 100.0 | 99.5 | 96.3 | 81.4 | 82.5 | 93.3 | 89.6 | 94.9 | 94.1 | 88.2 |
| Gemini 3 Flash Preview | 99.8 | 99.5 | 96.3 | 80.9 | 81.2 | 92.7 | 90.2 | 94.8 | 93.8 | 87.9 |
| Gemini 3.5 Flash Lite | 98.9 | 98.7 | 95.9 | 80.9 | 80.4 | 93.2 | 90.3 | 94.8 | 93.8 | 88.0 |
| LandingAI ADE | 97.0 | 100.0 | 95.2 | 81.2 | 79.6 | 90.6 | **57.0** | 94.4 | 93.0 | 87.9 |
| Unlimited-OCR | **57.1** | 99.5 | 95.3 | 70.2 | 75.6 | 92.2 | 88.1 | 93.4 | 93.8 | 79.4 |
| PaddleOCR-VL 1.6 | 91.2 | **59.1** | 78.4 | 76.4 | 70.7 | 90.8 | 84.6 | 87.1 | 91.3 | 80.7 |
| Docling (RapidOCR) | 67.7 | 72.8 | 81.5 | **7.7** | 40.4 | 83.8 | 87.2 | 84.2 | 88.6 | 80.6 |
| Tesseract 5 | 90.1 | 73.8 | 94.8 | 25.6 | 47.2 | 52.5 | 75.4 | 67.6 | 65.4 | **30.3** |

## Hall of shame: errors a word score does not show

| Engine | Page | What the page says | What the engine wrote | Repeatable? |
|---|---|---|---|---|
| LandingAI ADE | 7 | (empty table rows) | "The ¹H NMR spectrum of 2 in CDCl₃ … IR … UV-Vis … mass spectrum …" | 1 of 4 runs |
| LandingAI ADE | 7 | illegible signature (typed name: Peter J. Marzullo) | "Signature: Legible (Peter J. **Mayhew**)" / "Peter J. **Mayell**" | **4 of 4 runs** |
| LandingAI ADE | 4 | Check Total `$156,686.60` | `$155,686.60` (−$1,000) | scored run |
| Mistral OCR 4.1 | 4 | `$12,764.00` | `$12,784.00` (+$20) | scored run |
| Gemini 3.5 Flash Lite | 6 | ALUMINUM ☑, STEEL ☐ | `STEEL X  ALUMINUM ☐` | scored run |
| Unlimited-OCR | 1 | Flipkart invoice | 14× `1. 2017年1月1日` and `\( \therefore m = \frac{3}{11} \)` | 2 of 2 runs |
| Docling | 4 | a full check-request form | `<!-- image -->` (whole form treated as a picture) | scored run |
| PaddleOCR-VL | 2 | `$1.87` | `1.87`, `$4.11$`, `VAT $ ^{{**}} $` | scored run |
| All 9 engines | 5 | crossed-out lines | written as normal text, no strike-through mark | — |

## Quick take on each engine

- **Gemini 3.8 Flash** — Most accurate. Reads handwriting and checkboxes; marks signatures as `[signature]` instead of guessing. No coordinates; prompt-dependent; slowest API.
- **Mistral OCR 4.1** — Best speed/accuracy balance. Perfect on the scanned invoice. One wrong digit on a fax. Cheap, simple, image crops included.
- **Gemini 3 Flash Preview** — 99% of 3.8's quality, 18% cheaper. Labels handwriting. Preview model: can change.
- **Gemini 3.5 Flash Lite** — Cheapest paid option, fine for search/RAG text; inverted a checkbox, so not for forms without checks.
- **LandingAI ADE** — Best structure and grounding (boxes for every chunk and table cell), but most expensive and showed generation-style hallucinations.
- **Unlimited-OCR** — Best free engine on clean/typical pages; unstable on low-quality scans; needs a GPU to be fast.
- **PaddleOCR-VL 1.6** — Precise, good tables and image crops, free; drops headers/footers/footnotes and `$` signs by default.
- **Docling** — Richest open data model and pipeline; default settings failed on a dark fax and repeat merged table cells.
- **Tesseract** — Fast, free baseline; fine for clean printed text, poor for forms and scans.

## Which one in which situation

| Situation | Pick | Why | Runner-up |
|---|---|---|---|
| Highest accuracy on messy scans, cost matters | **Gemini 3.8 Flash** | 55/55 fields, best on faxes, ≈ $3/1k pages | Gemini 3 Flash Preview |
| High-volume production, low latency | **Mistral OCR 4.1** | 0.4 s/page, 92% F1, $4/1k | Gemini 3.5 Flash Lite |
| Lowest cost per page (API) | **Gemini 3.5 Flash Lite** | $1.88/1k, ~92% F1 — add field validation | Gemini 3 Flash Preview |
| Need coordinates / citations / "click to source" UI | **LandingAI ADE** | Boxes for every chunk and table cell | Unlimited-OCR / PaddleOCR-VL (local, boxes per block) |
| Data must not leave your machine (privacy, air-gapped) | **Unlimited-OCR** on a GPU | Best local accuracy; MIT | PaddleOCR-VL 1.6 (more stable on bad scans) |
| Low-quality phone photos or scans, local only | **PaddleOCR-VL 1.6** | 91% F1 on the Flipkart scan where Unlimited-OCR failed | Docling with a VLM pipeline |
| Forms with checkboxes | **Gemini 3.8 Flash** or **Mistral OCR 4.1** | Both kept every checkbox state | PaddleOCR-VL, Docling |
| Handwritten values matter | **Gemini 3.8 Flash / 3 Flash Preview** | Only engines that read both handwritten numbers | — |
| Rich structured document for RAG (digital PDFs, Office files) | **Docling** | One `DoclingDocument` for PDF/DOCX/PPTX/HTML…, local, MIT | PaddleOCR-VL |
| Clean printed text at huge volume on CPU | **Tesseract** | ~5,000 pages/hour on one CPU, $0 | Docling |
| Regulated workflows (signatures, identity, money) | **Mistral OCR 4.1 or Gemini + validation rules** | Avoid engines that generate descriptions or names | — |

## Cost at scale (1 million pages)

| Engine | API cost | Notes |
|---|---|---|
| Gemini 3.5 Flash Lite | ≈ $1,880 | billed price via OpenRouter; the `:batch` variant is listed at about half the token price |
| Gemini 3 Flash Preview | ≈ $2,590 | |
| Gemini 3.8 Flash | ≈ $3,170 | |
| Mistral OCR 4.1 | $4,000 | list price |
| LandingAI ADE | ≈ $30,000 | 3 credits/page in this test |
| Unlimited-OCR / PaddleOCR-VL / Docling / Tesseract | $0 | hardware time: on the test machine, 1M pages ≈ 7,550 h (Unlimited), 3,500 h (PaddleOCR-VL), 1,800 h (Docling CPU), 200 h (Tesseract); a datacenter GPU is much faster |

LLM costs depend on output length. These pages averaged ~690–770 output tokens per page (by model); dense pages cost more.

## Method

- **Test file:** `data/ocr_test_10_pages.pdf`, image-only (0 characters of embedded text), so every engine had to do OCR.
  - p1: real scanned Flipkart retail invoice (low quality). The customer's name, address and phone are blacked out in this repo.
  - p2–3: public invoices from `invoice2data` (MIT): AWS (English) and Free (French), rasterized to 200 dpi grayscale.
  - p4–10: real 1980s–90s faxed business forms from the FUNSD dataset (~90 dpi): check request, purchase requisition, proposal, finance report, research application, insertion order, fiscal estimate.
- **Ground truth:** p1 transcribed by hand from the image; p2–3 from the original PDFs' text layer; p4–10 from FUNSD annotations.
- **Key fields:** 55 business-critical values (IDs, dates, amounts, names, 2 handwritten numbers), read from the images. Page 4 amounts were verified by arithmetic; FUNSD had them wrong.
- **Settings:** defaults for every engine, no tuning. Gemini used one fixed transcription prompt, `temperature=0`. Unlimited-OCR used the model card's prompt and repetition settings. APIs ran 3 times for latency.
- **Scripts:** one per engine in `code/`, scoring in `code/score.py`.

## Limits — read before you quote these numbers

- 10 pages is a stress test, not a statistically strong benchmark. Treat differences under ~1 F1 point as a tie.
- FUNSD ground truth has annotation errors; all engines are scored against the same noise.
- The two Baidu models ran through `mlx-vlm`, not on the official CUDA/vLLM path. Their speed (and possibly their accuracy) will differ on a server GPU.
- Docling and PaddleOCR-VL ran with default settings; both have options (VLM pipeline, keep headers/footers) that could raise their scores.
- LLM outputs vary between runs. We saved only the first run for scoring and repeated the LandingAI page-7 test to confirm.
- Prices are from 2026-10-17 and change often.
- FUNSD is licensed for non-commercial research and education; cite it if you show those pages.
