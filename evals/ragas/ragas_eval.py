"""
Ragas RAG metrics for the Maple Leaf Bank sample app.

Scores every in-scope golden question on four classic RAG metrics:
  - faithfulness       : is the answer supported by the retrieved context?
  - answer_relevancy   : does the answer address the question?
  - context_precision  : is the retrieved context relevant (ranked well)?
  - context_recall     : did retrieval find everything the reference needs?

Then compares the mean of each metric with a threshold and exits non-zero
on failure, so you can use it as a CI gate.

Uses the Ragas 0.4 "collections" metrics API (checked with ragas 0.4.3,
October 2026). Docs: https://docs.ragas.io

Run (sample app on localhost:8000):
    make eval-ragas          # local judge on Ollama (make up-llm first)

Judge (JUDGE environment variable):
    ollama  (default) local, free. Uses Ollama's OpenAI-compatible API at
            OLLAMA_BASE_URL/v1. Pull an embedding model too:
            docker compose exec ollama ollama pull nomic-embed-text
    openai  uses OPENAI_API_KEY (and OPENAI_BASE_URL for Azure OpenAI / Foundry:
            https://<resource>.openai.azure.com/openai/v1/)

Small local judges can return invalid JSON. If a metric errors, lower
concurrency, raise the timeout, or try a bigger judge model (week 4).
"""

from __future__ import annotations

import asyncio
import json
import os
import statistics
import sys
from pathlib import Path

import httpx
import yaml
from openai import AsyncOpenAI
from ragas.embeddings import OpenAIEmbeddings
from ragas.llms import llm_factory
from ragas.metrics.collections import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness

APP_URL = os.getenv("APP_URL", "http://localhost:8000")
JUDGE = os.getenv("JUDGE", "ollama")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "qwen2.5:7b" if JUDGE == "ollama" else "gpt-4.1-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text" if JUDGE == "ollama" else "text-embedding-3-small")
GOLDEN = Path(__file__).parents[2] / "datasets" / "golden_v1.jsonl"
REPORT = Path(__file__).parents[2] / "reports" / "ragas.json"

GATES = Path(__file__).parents[1] / "quality_gates.yaml"
THRESHOLDS = yaml.safe_load(GATES.read_text(encoding="utf-8"))["ragas"]


async def main() -> int:
    if JUDGE == "ollama":
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        client = AsyncOpenAI(api_key="ollama", base_url=f"{base}/v1", timeout=120)
    else:
        client = AsyncOpenAI()  # reads OPENAI_API_KEY / OPENAI_BASE_URL
    llm = llm_factory(JUDGE_MODEL, client=client)
    embeddings = OpenAIEmbeddings(client=client, model=EMBED_MODEL)

    faithfulness = Faithfulness(llm=llm)
    relevancy = AnswerRelevancy(llm=llm, embeddings=embeddings)
    precision = ContextPrecision(llm=llm)
    recall = ContextRecall(llm=llm)

    rows = [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [r for r in rows if r["category"] == "in_scope"]

    results = []
    async with httpx.AsyncClient(timeout=60) as http:
        for r in rows:
            app = (await http.post(f"{APP_URL}/ask", json={"question": r["question"]})).json()
            q, a, ctx, ref = r["question"], app["answer"], app["contexts"], r["reference"]
            scores = {
                "faithfulness": (await faithfulness.ascore(user_input=q, response=a, retrieved_contexts=ctx)).value,
                "answer_relevancy": (await relevancy.ascore(user_input=q, response=a)).value,
                "context_precision": (await precision.ascore(user_input=q, reference=ref, retrieved_contexts=ctx)).value,
                "context_recall": (await recall.ascore(user_input=q, retrieved_contexts=ctx, reference=ref)).value,
            }
            results.append({"id": r["id"], "risk": r["risk"], **scores})
            print(f"{r['id']}: " + "  ".join(f"{k}={v:.2f}" for k, v in scores.items()))

    means = {m: statistics.mean(x[m] for x in results) for m in THRESHOLDS}
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps({"means": means, "rows": results}, indent=2), encoding="utf-8")

    print("\nMetric             mean   threshold  result")
    failed = False
    for m, t in THRESHOLDS.items():
        ok = means[m] >= t
        failed |= not ok
        print(f"{m:<18} {means[m]:.2f}   {t:.2f}       {'PASS' if ok else 'FAIL'}")
    print(f"\nReport written to {REPORT}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
