"""Baidu Unlimited-OCR (open weights, MIT), one page image at a time, through mlx-vlm.

Run: python code/unlimited_ocr.py
mlx-vlm needs Apple Silicon. On an NVIDIA GPU, use the runtime in the model card
with the same prompt and repetition settings.
"""

import re

import mlx.core as mx
from mlx_vlm import generate, load
from mlx_vlm.models.base import install_auto_processor_patch
from mlx_vlm.models.unlimited_ocr import UnlimitedOCRProcessor

from common import Timer, page_images, save

REPO = "baidu/Unlimited-OCR"
PROMPT = "<image>document parsing."  # raw model-card prompt, no chat template
NGRAM_SIZE, NGRAM_WINDOW = 35, 128  # model-card repetition settings
DET = re.compile(r"<\|det\|>(\w+) \[[\d, ]+\]<\|/det\|>")

# mlx-vlm 0.7.8 registers the processor as "unlimited-ocr", but the model config says
# "unlimited_ocr"; without this line the wrong processor loads and generation fails.
install_auto_processor_patch("unlimited_ocr", UnlimitedOCRProcessor)


def no_repeat_ngram(tokens, logits):
    """Ban any token that would repeat a 35-gram seen in the last 128 tokens.
    Without it, the model repeated one line on a form page until max_tokens."""
    recent = tokens.tolist()[-NGRAM_WINDOW:]
    if len(recent) < NGRAM_SIZE:
        return logits
    prefix = recent[-(NGRAM_SIZE - 1):]
    banned = {recent[i + NGRAM_SIZE - 1] for i in range(len(recent) - NGRAM_SIZE + 1)
              if recent[i:i + NGRAM_SIZE - 1] == prefix}
    if not banned:
        return logits
    mask = mx.zeros(logits.shape[-1], dtype=mx.bool_)
    mask[mx.array(sorted(banned))] = True
    return mx.where(mask, mx.array(-mx.inf, dtype=logits.dtype), logits)


def to_markdown(raw: str) -> str:
    """'<|det|>label [box]<|/det|>content' blocks -> Markdown (title -> ##, image -> placeholder)."""
    blocks = DET.split(raw)
    out = [blocks[0].strip()] if blocks[0].strip() else []
    for label, content in zip(blocks[1::2], blocks[2::2]):
        content = content.strip()
        if label == "image":
            out.append("<!-- image -->")
        elif label == "title":
            out.append(f"## {content}")
        elif content:
            out.append(content)
    return "\n\n".join(out)


with Timer() as load_t:
    model, processor = load(REPO)
pages, per_page = [], []
for png in page_images():
    with Timer() as t:
        r = generate(model, processor, PROMPT, image=[str(png)], max_tokens=8192, temperature=0.0,
                     logits_processors=[no_repeat_ngram], verbose=False)
    pages.append(to_markdown(r.text))
    per_page.append(round(t.seconds, 2))
    print(f"{png.name}: {t.seconds:.1f}s", flush=True)

total = round(sum(per_page), 2)
save("unlimited_ocr", pages,
     {"engine": f"Unlimited-OCR ({REPO}), prompt '{PROMPT}', no_repeat_ngram {NGRAM_SIZE}/{NGRAM_WINDOW}",
      "version": REPO, "runs_total_seconds": [round(total + load_t.seconds, 2), total], "cost_usd": 0.0})
