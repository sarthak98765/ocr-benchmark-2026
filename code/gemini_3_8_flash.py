"""Gemini 3.8 Flash as OCR: the whole PDF sent to the model through OpenRouter (native PDF input).

Run: python code/gemini_3_8_flash.py   (needs OPENROUTER_API_KEY)
The prompt and the request are in common.py (run_gemini).
"""

from common import run_gemini

run_gemini("google/gemini-3.8-flash", "gemini_3_8_flash")
