"""
Week 4: can you trust your LLM judge?

Before you gate releases on an LLM judge's scores, measure how often it agrees
with careful humans. This script:
  1. reads human pass/fail labels from datasets/labels_human.csv
  2. asks a judge to grade the same answers against the reference
  3. reports raw agreement and Cohen's kappa (agreement corrected for chance)
  4. lists every disagreement, so you can fix the rubric or the labels

Rough guide to kappa: below 0.4 weak, 0.4 to 0.6 moderate, 0.6 to 0.8 good,
above 0.8 very good. This course gates at 0.6 (see evals/quality_gates.yaml).

Usage
  python evals/judges/calibrate.py               # LLM judge (JUDGE=ollama by default)
  python evals/judges/calibrate.py --baseline    # no model: a naive keyword judge,
                                                 # to see why string matching isn't enough
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

from sklearn.metrics import cohen_kappa_score, confusion_matrix

ROOT = Path(__file__).parents[2]
LABELS = ROOT / "datasets" / "labels_human.csv"
OUT = ROOT / "reports" / "judge-calibration.json"

RUBRIC = """You are grading a bank assistant's answer.
Reference answer (correct): {reference}
Question: {question}
Assistant answer: {answer}

PASS only if the answer agrees with the reference on every number, rule and
condition, adds nothing false, and gives no unsafe advice. Extra true detail is fine.
Reply with exactly one word: PASS or FAIL."""


def keyword_judge(row: dict) -> int:
    """Naive baseline: pass if every number/money amount in the reference appears in the answer."""
    nums = re.findall(r"\$?\d[\d,.]*%?", row["reference"])
    if not nums:  # no numbers to check: look for the first word (yes/no) instead
        return int(row["reference"].split()[0].strip(".").lower() in row["answer"].lower())
    return int(all(n.rstrip(".") in row["answer"] for n in nums))


def llm_judge(row: dict) -> int:
    from openai import OpenAI

    if os.getenv("JUDGE", "ollama") == "ollama":
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        client, model = OpenAI(api_key="ollama", base_url=f"{base}/v1"), os.getenv("JUDGE_MODEL", "qwen2.5:7b")
    else:
        client, model = OpenAI(), os.getenv("JUDGE_MODEL", "gpt-4.1-mini")
    resp = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[{"role": "user", "content": RUBRIC.format(**row)}],
    )
    verdict = (resp.choices[0].message.content or "").strip().upper()
    return 1 if verdict.startswith("PASS") else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action="store_true", help="use the keyword judge (no model)")
    args = parser.parse_args()
    judge = keyword_judge if args.baseline else llm_judge

    rows = list(csv.DictReader(LABELS.open(encoding="utf-8")))
    human = [int(r["human_label"]) for r in rows]
    machine = [judge(r) for r in rows]

    agreement = sum(h == m for h, m in zip(human, machine)) / len(rows)
    kappa = cohen_kappa_score(human, machine)
    tn, fp, fn, tp = confusion_matrix(human, machine, labels=[0, 1]).ravel()

    print(f"Judge: {'keyword baseline' if args.baseline else 'LLM'}   rows: {len(rows)}")
    print(f"Raw agreement: {agreement:.0%}   Cohen's kappa: {kappa:.2f}")
    print(f"Judge passed answers humans failed (dangerous): {fp}")
    print(f"Judge failed answers humans passed (noisy):      {fn}\n")
    for r, h, m in zip(rows, human, machine):
        if h != m:
            print(f"  DISAGREE {r['id']}: human={'PASS' if h else 'FAIL'} judge={'PASS' if m else 'FAIL'}  ({r['note']})")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "judge": "keyword-baseline" if args.baseline else os.getenv("JUDGE_MODEL", "qwen2.5:7b"),
        "rows": len(rows), "agreement": agreement, "cohen_kappa": kappa,
        "false_pass": int(fp), "false_fail": int(fn),
    }, indent=2), encoding="utf-8")
    print(f"\nSaved {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
