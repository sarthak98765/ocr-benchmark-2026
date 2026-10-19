"""PaddleOCR-VL 1.6 official pipeline: layout detection + reading order + VLM recognition.

Run in its own environment (see requirements.txt):  python code/paddleocr_vl.py
Optional, faster: serve the VLM separately and set PADDLE_VL_BACKEND (vllm-server or
mlx-vlm-server) and PADDLE_VL_SERVER_URL in .env.
"""

import os

from paddleocr import PaddleOCRVL

from common import Timer, page_images, save

MODEL = "PaddlePaddle/PaddleOCR-VL-1.6"

options = {"pipeline_version": "v1.6"}
if backend := os.environ.get("PADDLE_VL_BACKEND", "").strip():
    options |= {"vl_rec_backend": backend, "vl_rec_server_url": os.environ["PADDLE_VL_SERVER_URL"],
                "vl_rec_api_model_name": MODEL}
with Timer() as init:
    pipeline = PaddleOCRVL(**options)

pages, per_page = [], []
for png in page_images():
    with Timer() as t:
        results = list(pipeline.predict(str(png)))
    pages.append("\n\n".join(r.markdown["markdown_texts"] for r in results))
    per_page.append(round(t.seconds, 2))
    print(f"{png.name}: {t.seconds:.1f}s", flush=True)

# Page 1 also warms up the models, so the warm run is the mean of pages 2-10, scaled to 10 pages.
warm = round(sum(per_page[1:]) / (len(per_page) - 1) * len(per_page), 2)
save("paddleocr_vl", pages,
     {"engine": "PaddleOCR-VL 1.6 official pipeline (pipeline_version=v1.6)", "version": MODEL,
      "runs_total_seconds": [round(sum(per_page) + init.seconds, 2), warm], "cost_usd": 0.0})
