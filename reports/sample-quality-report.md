> **Sample output.** Made by running `make eval`, `python evals/judges/calibrate.py --baseline`, `make gate` and `make report` in offline mode. It says NO-GO on purpose: the keyword judge (kappa 0.50) is below the 0.60 gate, which is exactly what week 4 teaches. Your own report will differ.

# Release quality report: Maple Leaf Bank assistant

**Date:** 2026-10-29  
**System under test:** Maple Leaf Bank assistant (`/ask` RAG endpoint, `/agent` tool endpoint)  
**Golden dataset:** golden_v1 (adversarial: 1, in_scope: 16, out_of_scope: 2, safety: 1 (total 20))

## Recommendation

**NO-GO: one or more quality gates failed. See the table below.**

## Quality gates

| Check | Value | Gate | Result |
| --- | --- | --- | --- |
| promptfoo_offline | 100% | >= 100% | PASS |
| promptfoo_judge | not run | >= 90% | SKIPPED |
| ragas | not run | see quality_gates.yaml | SKIPPED |
| judge cohen_kappa | 0.50 | >= 0.60 | FAIL |

## Judge reliability

Judge `keyword-baseline` agreed with human labels on 75% of 16 answers (Cohen's kappa 0.50). It passed 1 answer(s) humans failed. Scores from a judge below the kappa gate are advisory only.

## Security testing

Red team results are reviewed separately (`npx promptfoo@0.125.1 redteam report`). Record each finding with its OWASP ID and severity from `redteam/owasp-mapping.md`.

| Finding | OWASP ID | Severity | Status |
| --- | --- | --- | --- |
| _add findings here_ | | | |

## Not tested (scope)

- Long-term memory and multi-agent flows (not present in this system)
- Load and soak testing
- Accessibility of the chat UI beyond Playwright smoke checks

## Model inventory entry (for model risk management)

| Field | Value |
| --- | --- |
| Model ID | maple-bank-assistant-v1 |
| Owner | _business owner_ |
| Underlying model | _set from MODEL in .env_ |
| Approved uses | Answer customer questions from bank policy; lock cards; transfers with confirmation under $1,000 |
| Limitations | Policy questions only; no advice; no other customers' data |
| Last validation | 2026-10-29 |
| Next review | _date_ |
