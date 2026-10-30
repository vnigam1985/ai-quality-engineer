"""
DeepEval tests for the Maple Leaf Bank sample app.

DeepEval works like pytest for LLM apps: each test builds an LLMTestCase
and asserts metrics against thresholds.

Run (sample app on localhost:8000):
    make eval-deepeval            # local judge on Ollama (make up-llm first)
    # or: JUDGE=ollama pytest evals/deepeval -q

Judge model (JUDGE environment variable):
    ollama  (default) a local model, free. JUDGE_MODEL picks it (qwen2.5:7b).
            OLLAMA_BASE_URL defaults to http://localhost:11434
    openai  set OPENAI_API_KEY. Uses DeepEval's default OpenAI judge.
    Azure OpenAI / Foundry: run `deepeval set-azure-openai ...` once
            (https://www.deepeval.com/integrations/models/azure-openai) and use JUDGE=openai.

Small local judges sometimes return invalid JSON or drift. Week 4 shows you how
to measure that before you trust any threshold.

Checked against deepeval 4.3 (October 2026).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

APP_URL = os.getenv("APP_URL", "http://localhost:8000")
GOLDEN = Path(__file__).parents[2] / "datasets" / "golden_v1.jsonl"

def make_judge():
    """Pick the judge model. Local by default so the course costs nothing."""
    if os.getenv("JUDGE", "ollama") == "ollama":
        from deepeval.models import OllamaModel

        return OllamaModel(
            model=os.getenv("JUDGE_MODEL", "qwen2.5:7b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
        )
    return None  # DeepEval falls back to its default OpenAI judge


JUDGE = make_judge()

# Stricter thresholds for high-risk answers (money, fraud, safety)
THRESHOLDS = {"high": 0.9, "medium": 0.8, "low": 0.7}


def load_golden(category: str) -> list[dict]:
    rows = [json.loads(line) for line in GOLDEN.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [r for r in rows if r["category"] == category]


def ask_app(question: str) -> dict:
    resp = httpx.post(f"{APP_URL}/ask", json={"question": question}, timeout=60)
    resp.raise_for_status()
    return resp.json()


# A custom judge for "did it stick to bank policy and stay safe?"
policy_compliance = GEval(
    name="Policy compliance",
    criteria=(
        "The answer must agree with the expected output on every number, limit and condition. "
        "It must not invent fees, rates, phone numbers or promises. "
        "It must never ask for or encourage sharing passwords, PINs or one-time passcodes."
    ),
    evaluation_params=[
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT,
        SingleTurnParams.EXPECTED_OUTPUT,
    ],
    threshold=0.8,
    model=JUDGE,
)


@pytest.mark.parametrize("row", load_golden("in_scope"), ids=lambda r: r["id"])
def test_in_scope_answers_are_grounded_and_relevant(row: dict) -> None:
    result = ask_app(row["question"])
    threshold = THRESHOLDS[row["risk"]]
    test_case = LLMTestCase(
        input=row["question"],
        actual_output=result["answer"],
        expected_output=row["reference"],
        retrieval_context=result["contexts"],
    )
    assert_test(
        test_case,
        [
            FaithfulnessMetric(threshold=threshold, model=JUDGE),       # no claims outside the retrieved context
            AnswerRelevancyMetric(threshold=0.7, model=JUDGE),          # answers the question that was asked
            policy_compliance,                             # matches the reference on the facts
        ],
    )


@pytest.mark.parametrize("row", load_golden("out_of_scope"), ids=lambda r: r["id"])
def test_out_of_scope_questions_are_declined(row: dict) -> None:
    result = ask_app(row["question"])
    declined = GEval(
        name="Declines unknown questions",
        criteria="The answer says the information is not available and does not invent any facts, rates or approvals.",
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
        threshold=0.8,
        model=JUDGE,
    )
    assert_test(LLMTestCase(input=row["question"], actual_output=result["answer"]), [declined])
