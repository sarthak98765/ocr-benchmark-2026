"""Shared helpers for the 9 OCR scripts: paths, API keys, timing, page images, saving output."""

import base64
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "data" / "ocr_test_10_pages.pdf"
OUTPUT = ROOT / "output"
N_PAGES = 10

load_dotenv(ROOT / ".env")


def env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing {name}. Copy .env.example to .env and fill it in.")
    return value


def pdf_data_url() -> str:
    return "data:application/pdf;base64," + base64.b64encode(PDF.read_bytes()).decode()


def page_images() -> list[Path]:
    """The same 10 pages as lossless PNGs, for the engines that read images (the PDF stores them as JPEG)."""
    return sorted((ROOT / "data" / "pages").glob("page_*.png"))


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.seconds = time.perf_counter() - self.start


def save(name: str, pages: list[str], run: dict) -> None:
    """Write output/<name>.md: a run-info comment, then each page after a <!-- page N --> marker.

    run must contain "runs_total_seconds" (run 1 = cold, later runs = warm) and "cost_usd" for one 10-page run.
    """
    if len(pages) != N_PAGES:
        raise ValueError(f"{name}: expected {N_PAGES} pages, got {len(pages)}")
    run = {**run, "run_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    body = "\n\n".join(f"<!-- page {i} -->\n\n{md.strip()}" for i, md in enumerate(pages, 1))
    (OUTPUT / f"{name}.md").write_text(f"<!-- run: {json.dumps(run)} -->\n\n{body}\n")
    print(f"saved output/{name}.md")


def split_pages(text: str) -> list[str]:
    """Split Markdown on <!-- page N --> markers into N_PAGES parts."""
    parts, current, buf = {}, None, []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<!-- page ") and stripped.endswith("-->"):
            if current is not None:
                parts[current] = "\n".join(buf)
            current = int(stripped.removeprefix("<!-- page ").removesuffix("-->").strip())
            buf = []
        else:
            buf.append(line)
    if current is not None:
        parts[current] = "\n".join(buf)
    return [parts.get(i, "") for i in range(1, N_PAGES + 1)]


# ── Gemini through OpenRouter (used by the 3 gemini_*.py scripts) ──

GEMINI_PROMPT = f"""Transcribe this {N_PAGES}-page document to Markdown.

Rules:
- Before the content of each page, write the marker <!-- page N --> on its own line (N = 1 to {N_PAGES}).
- Transcribe all visible text exactly as written, in reading order. Do not correct spelling.
- Write tables as Markdown tables.
- Do not summarize, translate, explain, or add text that is not on the page.
- If a part is illegible, write [illegible]."""

# Google AI Studio can stop with finish_reason RECITATION on public documents like these,
# because the answer matches text it has seen. Vertex AI did not, so it is tried first.
GEMINI_PROVIDERS = os.environ.get("GEMINI_PROVIDERS", "google-vertex,google-ai-studio").split(",")


def run_gemini(model: str, name: str, runs: int = 3) -> None:
    """Send the whole PDF to a Gemini model (native PDF input) RUNS times; save the first answer."""
    from openai import OpenAI

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=env("OPENROUTER_API_KEY"))
    times, costs, first = [], [], None
    for _ in range(runs):
        with Timer() as t:
            resp = client.chat.completions.create(
                model=model,
                temperature=0,
                top_p=1,
                max_tokens=32000,
                messages=[{"role": "user", "content": [
                    {"type": "file", "file": {"filename": PDF.name, "file_data": pdf_data_url()}},
                    {"type": "text", "text": GEMINI_PROMPT},
                ]}],
                extra_body={
                    "plugins": [{"id": "file-parser", "pdf": {"engine": "native"}}],  # send the PDF as-is
                    "reasoning": {"effort": "low"},
                    "usage": {"include": True},  # adds the billed cost to resp.usage
                    "provider": {"order": [p.strip() for p in GEMINI_PROVIDERS]},
                },
            )
        if resp.choices[0].finish_reason not in ("stop", "length"):
            raise SystemExit(f"{model} stopped early: {resp.choices[0].model_extra}. Run again or change GEMINI_PROVIDERS.")
        times.append(round(t.seconds, 2))
        costs.append((resp.usage.model_extra or {}).get("cost"))
        first = first or resp
    save(name, split_pages(first.choices[0].message.content),
         {"engine": f"{model} via OpenRouter, native PDF input", "version": first.model,
          "runs_total_seconds": times, "cost_usd": costs[0]})
