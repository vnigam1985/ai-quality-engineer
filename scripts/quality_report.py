"""
Week 8: build the release quality report (reports/quality-report.md).

This is the document a QA lead hands to a release manager or a model risk
reviewer: what was tested, how it scored against the gates, what's still
risky, and a go / no-go recommendation. It pulls numbers from whatever result
files exist in reports/ and says clearly what was NOT run.

Usage: python scripts/quality_report.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).parents[1]
REPORTS = ROOT / "reports"
GATES = yaml.safe_load((ROOT / "evals" / "quality_gates.yaml").read_text(encoding="utf-8"))
OUT = REPORTS / "quality-report.md"


def load(name: str) -> dict | None:
    p = REPORTS / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def golden_coverage() -> str:
    rows = [json.loads(x) for x in (ROOT / "datasets" / "golden_v1.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    c = Counter(r["category"] for r in rows)
    return ", ".join(f"{k}: {v}" for k, v in sorted(c.items())) + f" (total {len(rows)})"


def main() -> int:
    gate = subprocess.run([sys.executable, str(ROOT / "scripts" / "gate.py")], capture_output=True, text=True)
    gate_table = gate.stdout.split("\n", 2)[2].strip() if gate.stdout.count("\n") >= 2 else gate.stdout
    passed = gate.returncode == 0
    skipped = gate.stdout.count("SKIPPED")

    pf_off, pf_judge, ragas, cal = (load(n) for n in ("promptfoo-offline.json", "promptfoo-judge.json", "ragas.json", "judge-calibration.json"))
    not_run = [n for n, v in (("LLM-graded promptfoo", pf_judge), ("Ragas RAG metrics", ragas), ("Judge calibration", cal)) if v is None]

    if passed and not not_run:
        decision = "GO: all gates passed and every planned check ran."
    elif passed:
        decision = f"CONDITIONAL GO: gates that ran passed, but {len(not_run)} check(s) did not run: {', '.join(not_run)}."
    else:
        decision = "NO-GO: one or more quality gates failed. See the table below."

    lines = [
        "# Release quality report: Maple Leaf Bank assistant",
        "",
        f"**Date:** {date.today().isoformat()}  ",
        "**System under test:** Maple Leaf Bank assistant (`/ask` RAG endpoint, `/agent` tool endpoint)  ",
        f"**Golden dataset:** golden_v1 ({golden_coverage()})",
        "",
        "## Recommendation",
        "",
        f"**{decision}**",
        "",
        "## Quality gates",
        "",
        gate_table,
        "",
        "## Judge reliability",
        "",
    ]
    if cal:
        lines.append(
            f"Judge `{cal['judge']}` agreed with human labels on {cal['agreement']:.0%} of {cal['rows']} answers "
            f"(Cohen's kappa {cal['cohen_kappa']:.2f}). It passed {cal['false_pass']} answer(s) humans failed. "
            "Scores from a judge below the kappa gate are advisory only."
        )
    else:
        lines.append("Judge calibration was not run. Treat all LLM-graded scores as advisory.")
    lines += [
        "",
        "## Security testing",
        "",
        "Red team results are reviewed separately (`npx promptfoo@0.125.1 redteam report`). "
        "Record each finding with its OWASP ID and severity from `redteam/owasp-mapping.md`.",
        "",
        "| Finding | OWASP ID | Severity | Status |",
        "| --- | --- | --- | --- |",
        "| _add findings here_ | | | |",
        "",
        "## Not tested (scope)",
        "",
        "- Long-term memory and multi-agent flows (not present in this system)",
        "- Load and soak testing",
        "- Accessibility of the chat UI beyond Playwright smoke checks",
        "",
        "## Model inventory entry (for model risk management)",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| Model ID | maple-bank-assistant-v1 |",
        "| Owner | _business owner_ |",
        "| Underlying model | _set from MODEL in .env_ |",
        "| Approved uses | Answer customer questions from bank policy; lock cards; transfers with confirmation under $1,000 |",
        "| Limitations | Policy questions only; no advice; no other customers' data |",
        f"| Last validation | {date.today().isoformat()} |",
        "| Next review | _date_ |",
        "",
    ]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}  ({'gates passed' if passed else 'gates FAILED'}, {skipped} skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
