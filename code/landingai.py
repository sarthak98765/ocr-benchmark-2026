"""LandingAI ADE (Agentic Document Extraction): parse with the default model, one split per page.

Run: python code/landingai.py   (needs VISION_AGENT_API_KEY)
"""

from landingai_ade import LandingAIADE

from common import N_PAGES, PDF, Timer, env, save

USD_PER_CREDIT = 0.01
RUNS = 3

client = LandingAIADE(apikey=env("VISION_AGENT_API_KEY"))
times, first = [], None
for _ in range(RUNS):
    with Timer() as t:
        resp = client.parse(document=PDF, split="page")
    times.append(round(t.seconds, 2))
    first = first or resp

base = min(s.pages[0] for s in first.splits)  # page numbers can be 0- or 1-based
by_page = {s.pages[0] - base + 1: s.markdown for s in first.splits}
save("landingai", [by_page.get(i, "") for i in range(1, N_PAGES + 1)],
     {"engine": "LandingAI ADE parse, default model, split=page", "version": first.metadata.version,
      "runs_total_seconds": times, "cost_usd": round(first.metadata.credit_usage * USD_PER_CREDIT, 4)})
