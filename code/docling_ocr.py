"""Docling standard PDF pipeline with default settings (layout model, TableFormer, RapidOCR).

Run: python code/docling_ocr.py
(Not named docling.py, because that would hide the docling package.)
"""

from importlib.metadata import version

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from common import N_PAGES, PDF, Timer, save

# generate_picture_images keeps figure crops; it does not change the text output.
options = PdfPipelineOptions(generate_picture_images=True)
converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})

times = []
for _ in range(2):  # run 1 = cold (loads models), run 2 = warm
    with Timer() as t:
        result = converter.convert(PDF)
    times.append(round(t.seconds, 2))

doc = result.document
save("docling_ocr", [doc.export_to_markdown(page_no=i) for i in range(1, N_PAGES + 1)],
     {"engine": "Docling standard PDF pipeline, RapidOCR (default)", "version": f"docling {version('docling')}",
      "runs_total_seconds": times, "cost_usd": 0.0})
