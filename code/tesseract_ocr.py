"""Tesseract 5 CLI on each page image, default page segmentation, English + French.

Run: python code/tesseract_ocr.py
Install first: brew install tesseract tesseract-lang  /  apt install tesseract-ocr tesseract-ocr-fra
"""

import os
import shutil
import subprocess

from common import Timer, page_images, save

binary = shutil.which("tesseract")
if not binary:
    raise SystemExit("tesseract not found on PATH")
# The published run used tessdata_fast; set TESSDATA_DIR in .env to use a specific folder.
extra = ["--tessdata-dir", os.environ["TESSDATA_DIR"]] if os.environ.get("TESSDATA_DIR") else []
version = subprocess.run([binary, "--version"], capture_output=True, text=True).stdout.split("\n")[0]

pages, per_page = [], []
for png in page_images():
    with Timer() as t:
        out = subprocess.run([binary, str(png), "stdout", "-l", "eng+fra", *extra],
                             capture_output=True, text=True, check=True).stdout
    pages.append(out)
    per_page.append(round(t.seconds, 2))

save("tesseract_ocr", pages,
     {"engine": "Tesseract CLI, default page segmentation, eng+fra", "version": version,
      "runs_total_seconds": [round(sum(per_page), 2)], "cost_usd": 0.0})
