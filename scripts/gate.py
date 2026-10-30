"""
Week 8: the quality gate.

Reads every results file that exists in reports/ and compares it with
evals/quality_gates.yaml. Exits 1 if any gate fails, so CI blocks the merge.
Missing result files are skipped (so the PR job can run only offline checks)
but listed, so nobody thinks a skipped check passed.

Also writes a Markdown summary to $GITHUB_STEP_SUMMARY when running in
GitHub Actions.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
REPORTS = ROOT / "reports"
GATES = yaml.safe_load((ROOT / "evals" / "quality_gates.yaml").read_text(encoding="utf-8"))


def promptfoo_pass_rate(path: Path) -> float:
    stats = json.loads(path.read_text(encoding="utf-8"))["results"]["stats"]
    total = stats["successes"] + stats["failures"] + stats["errors"]
    return stats["successes"] / total if total else 0.0


def main() -> int:
    rows: list[tuple[str, str, str, str]] = []  # check, value, gate, result
    failed = False

    for key, file in (("promptfoo_offline", "promptfoo-offline.json"), ("promptfoo_judge", "promptfoo-judge.json")):
        path = REPORTS / file
        gate = GATES[key]["min_pass_rate"]
        if not path.exists():
            rows.append((key, "not run", f">= {gate:.0%}", "SKIPPED"))
            continue
        rate = promptfoo_pass_rate(path)
        ok = rate >= gate
        failed |= not ok
        rows.append((key, f"{rate:.0%}", f">= {gate:.0%}", "PASS" if ok else "FAIL"))

    ragas_path = REPORTS / "ragas.json"
    if ragas_path.exists():
        means = json.loads(ragas_path.read_text(encoding="utf-8"))["means"]
        for metric, gate in GATES["ragas"].items():
            ok = means.get(metric, 0) >= gate
            failed |= not ok
            rows.append((f"ragas.{metric}", f"{means.get(metric, 0):.2f}", f">= {gate:.2f}", "PASS" if ok else "FAIL"))
    else:
        rows.append(("ragas", "not run", "see quality_gates.yaml", "SKIPPED"))

    cal_path = REPORTS / "judge-calibration.json"
    if cal_path.exists():
        kappa = json.loads(cal_path.read_text(encoding="utf-8"))["cohen_kappa"]
        gate = GATES["judge_calibration"]["min_cohen_kappa"]
        ok = kappa >= gate
        failed |= not ok
        rows.append(("judge cohen_kappa", f"{kappa:.2f}", f">= {gate:.2f}", "PASS" if ok else "FAIL"))
    else:
        rows.append(("judge calibration", "not run", "see quality_gates.yaml", "SKIPPED"))

    table = ["| Check | Value | Gate | Result |", "| --- | --- | --- | --- |"]
    table += [f"| {c} | {v} | {g} | {r} |" for c, v, g, r in rows]
    verdict = "❌ Quality gate FAILED" if failed else "✅ Quality gate passed"
    text = f"## {verdict}\n\n" + "\n".join(table) + "\n"
    print(text)

    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(text)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
