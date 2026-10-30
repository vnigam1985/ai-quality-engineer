"""
API tests for the Maple Leaf Bank sample app, with Playwright's request context.

These run in offline mode (no API key), so they are fast, free and
deterministic. They test the plumbing around the LLM: status codes,
schema, input validation, retrieval and latency. Model quality is tested
separately in evals/.

Run (sample app on localhost:8000):
    pytest automation/playwright-python -q
"""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import APIRequestContext, Playwright

BASE_URL = os.getenv("APP_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def api(playwright: Playwright) -> APIRequestContext:
    ctx = playwright.request.new_context(base_url=BASE_URL)
    yield ctx
    ctx.dispose()


def test_health(api: APIRequestContext) -> None:
    r = api.get("/health")
    assert r.ok
    body = r.json()
    assert body["status"] == "ok"
    assert body["chunks"] >= 8


def test_answer_schema(api: APIRequestContext) -> None:
    r = api.post("/ask", data={"question": "How much does an international wire transfer cost?"})
    assert r.status == 200
    body = r.json()
    for field in ("question", "answer", "contexts", "mode", "latency_ms"):
        assert field in body, f"missing field: {field}"
    assert isinstance(body["contexts"], list)
    assert body["answer"].strip()


@pytest.mark.parametrize(
    ("question", "expected_section"),
    [
        ("How much does an international wire transfer cost?", "International transfers"),
        ("I lost my debit card, what should I do?", "Lost or stolen cards"),
        ("Are branches open on Sunday?", "Branch hours"),
        ("What is the overdraft limit?", "Overdraft protection"),
    ],
)
def test_retrieval_finds_the_right_section(api: APIRequestContext, question: str, expected_section: str) -> None:
    body = api.post("/ask", data={"question": question}).json()
    assert body["contexts"], "retrieval returned nothing"
    assert body["contexts"][0].startswith(expected_section), f"top context was: {body['contexts'][0][:60]}"


def test_empty_question_is_rejected(api: APIRequestContext) -> None:
    r = api.post("/ask", data={"question": ""})
    assert r.status == 422


def test_very_long_question_is_rejected(api: APIRequestContext) -> None:
    r = api.post("/ask", data={"question": "a" * 5000})
    assert r.status == 422


def test_latency_budget(api: APIRequestContext) -> None:
    body = api.post("/ask", data={"question": "What are branch hours?"}).json()
    budget = 200 if body["mode"] == "offline" else 8000
    assert body["latency_ms"] < budget
