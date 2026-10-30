"""
UI smoke test for the Maple Leaf Bank sample app with Playwright (Python).

Uses accessible locators (role, label, test id) instead of CSS selectors,
so tests survive small UI changes.

Run (sample app on localhost:8000):
    pytest automation/playwright-python -q --browser chromium
"""

from __future__ import annotations

import os
import re

from playwright.sync_api import Page, expect

BASE_URL = os.getenv("APP_URL", "http://localhost:8000")


def test_user_can_ask_a_question(page: Page) -> None:
    page.goto(BASE_URL)
    expect(page).to_have_title("Maple Leaf Bank Assistant")

    page.get_by_placeholder("Ask about fees, cards, transfers...").fill("How much does an international wire transfer cost?")
    page.get_by_role("button", name="Ask").click()

    answer = page.get_by_test_id("answer")
    expect(answer).not_to_have_text("Thinking...", timeout=15_000)
    expect(answer).to_contain_text(re.compile(r"\$30"))
