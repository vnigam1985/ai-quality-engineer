"""
Week 2: validate a golden dataset before anyone trusts it.

Checks every row for required fields, allowed values and duplicates, then
prints a coverage table (category x risk) so you can spot gaps.

Usage: python scripts/validate_dataset.py datasets/golden_v1.jsonl
Exit code 1 if anything is wrong, so it can run in CI.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REQUIRED = {"id", "question", "reference", "source_section", "category", "risk"}
CATEGORIES = {"in_scope", "out_of_scope", "safety", "adversarial"}
RISKS = {"low", "medium", "high"}

# Minimum share of each category. Real apps need plenty of "should refuse" cases.
MIN_SHARE = {"out_of_scope": 0.10, "safety": 0.05, "adversarial": 0.05}


def main(path: str) -> int:
    rows, errors = [], []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {n}: not valid JSON ({exc})")
            continue
        missing = REQUIRED - row.keys()
        if missing:
            errors.append(f"line {n}: missing fields {sorted(missing)}")
        if row.get("category") not in CATEGORIES:
            errors.append(f"line {n}: category must be one of {sorted(CATEGORIES)}")
        if row.get("risk") not in RISKS:
            errors.append(f"line {n}: risk must be one of {sorted(RISKS)}")
        if not str(row.get("reference", "")).strip():
            errors.append(f"line {n}: empty reference (every row needs a human-written expected answer)")
        if row.get("category") == "in_scope" and not row.get("source_section"):
            errors.append(f"line {n}: in_scope rows need a source_section")
        rows.append(row)

    ids = Counter(r.get("id") for r in rows)
    errors += [f"duplicate id: {i}" for i, c in ids.items() if c > 1]
    questions = Counter(r.get("question", "").strip().lower() for r in rows)
    errors += [f"duplicate question: {q!r}" for q, c in questions.items() if c > 1]

    total = len(rows) or 1
    by_cat = Counter(r.get("category") for r in rows)
    for cat, share in MIN_SHARE.items():
        if by_cat[cat] / total < share:
            errors.append(f"coverage: only {by_cat[cat]} '{cat}' rows ({by_cat[cat] / total:.0%}), want at least {share:.0%}")

    print(f"{len(rows)} rows in {path}\n")
    print(f"{'category':<14}{'low':>6}{'medium':>8}{'high':>6}{'total':>7}")
    for cat in sorted(CATEGORIES):
        counts = Counter(r["risk"] for r in rows if r.get("category") == cat)
        print(f"{cat:<14}{counts['low']:>6}{counts['medium']:>8}{counts['high']:>6}{by_cat[cat]:>7}")

    if errors:
        print("\nPROBLEMS:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nDataset OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "datasets/golden_v1.jsonl"))
