# What was tested, and what wasn't

Honesty matters more than a green badge. This page says exactly what was run before publishing, on October 29, 2026.

## Run and passing

| Check | Result | Versions |
| --- | --- | --- |
| `pytest tests` (API, agent, UI with Chromium) | 23 passed | Python 3.13, playwright 1.64.1, pytest-playwright 0.10.0 |
| `make eval` (promptfoo offline config) | 10/10 passed | promptfoo 0.125.1 |
| `promptfoo validate` on every promptfoo YAML, including the red team config | Valid | promptfoo 0.125.1 |
| `scripts/validate_dataset.py` on golden_v1 | Dataset OK | |
| `calibrate.py --baseline` | 75% agreement, kappa 0.50 | scikit-learn 1.9.1 |
| `gate.py` and `quality_report.py` | Run, output in [reports/sample-quality-report.md](reports/sample-quality-report.md) | |
| `redteam/pyrit/attack.py` against the offline app | 5/5 attacks blocked | PyRIT 1.1.0 |
| garak REST config, probes `promptinject.HijackHateHumans` and `dan.DanInTheWild` | Ran end to end (results explained in [redteam/README.md](redteam/README.md)) | garak 0.17.1 |
| App Docker image, with and without `WITH_TRACING=1` | Builds, `/health` OK, tracing imports load | Docker 29.9 |
| `docker compose config` | Valid | |
| Python imports for DeepEval and Ragas scripts | Load without errors | deepeval 4.3.2, ragas 0.4.3 |
| Phoenix `register()` endpoint handling | `http://phoenix:6006` sends gRPC to `phoenix:4317` | arize-phoenix-otel 0.17.2 |
| Every external link in the course | Loads the right page | Checked October 29, 2026 |

## Not run yet (needs a local model)

The test machine couldn't download the 5 GB model, so these paths are written against the current docs and APIs but **have not been run end to end**:

- `LLM_MODE=llm` answers from Ollama (`make up-llm`)
- `make eval-judge`, `make eval-deepeval`, `make eval-ragas`, `make calibrate` with an LLM judge
- `make redteam` (promptfoo generated attacks)
- Phoenix showing real traces (`make up-tracing`)
- `.github/workflows/nightly-judge.yml`

If any of these fail for you, please open an issue with the "I'm stuck" template. Fixes get credited.

## Version policy

Tools in this space change monthly. Key versions are pinned in `requirements*.txt` and the Makefile (`promptfoo@0.125.1`). Each week's README ends with links to official docs, which always win over this repo if they disagree.
