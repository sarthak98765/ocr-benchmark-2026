"""Mistral OCR 4.1: the whole PDF in one request, default options.

Run: python code/mistral.py   (needs MISTRAL_API_KEY)
"""

from mistralai.client import Mistral  # mistralai v3: import from .client

from common import Timer, env, pdf_data_url, save

MODEL = "mistral-ocr-latest"  # = mistral-ocr-4-1 on 2026-10-17
PRICE_PER_PAGE_USD = 4.0 / 1000  # list price
RUNS = 3

client = Mistral(api_key=env("MISTRAL_API_KEY"))
times, first = [], None
for _ in range(RUNS):
    with Timer() as t:
        resp = client.ocr.process(
            model=MODEL,
            document={"type": "document_url", "document_url": pdf_data_url()},
            include_image_base64=True,  # also returns cropped figures with coordinates
        )
    times.append(round(t.seconds, 2))
    first = first or resp

save("mistral", [p.markdown for p in sorted(first.pages, key=lambda p: p.index)],
     {"engine": "Mistral OCR API, default options", "version": first.model, "runs_total_seconds": times,
      "cost_usd": round(first.usage_info.pages_processed * PRICE_PER_PAGE_USD, 4)})
