# AGENTS.md

Instructions for AI coding assistants (Claude Code, Copilot, Cursor and others) helping a learner with this repo.

## What this repo is

An 8-week build-along course. Learners test one system, the Maple Leaf Bank assistant in `app/`, with evals, red teaming, Playwright tests, tracing and CI gates. Most learners are QA engineers who are new to Python.

## How to help

- **Explain before you change.** The learner is here to learn. When they ask for a fix, explain the cause in plain words, then make the smallest change
- **Don't solve the week's exercise for them** unless they ask directly. Offer a hint first
- **Keep offline mode working.** `LLM_MODE=offline` must never need a model, network or API key. `make test` and `make eval` must pass offline
- **Never add paid APIs as defaults.** Local Ollama is the default judge and model
- **Don't loosen gates to make CI green.** Changing `evals/quality_gates.yaml` needs a reason written in the commit message

## Commands

```bash
make setup        # venv, packages, Playwright browser
make run          # app without Docker, offline
make test         # API + agent tests
make eval         # promptfoo offline checks
make gate report  # gates and the release report
make help         # everything else
```

## Layout

| Path | What |
| --- | --- |
| `app/` | System under test (FastAPI). Policy docs in `app/kb/` |
| `datasets/` | Golden dataset and human labels |
| `evals/` | promptfoo, DeepEval, Ragas, judge calibration, gate thresholds |
| `redteam/` | Attack configs and scripts, OWASP mapping |
| `tests/` | Playwright API, agent and UI tests |
| `scripts/` | Dataset validator, gate, report |
| `weeks/` | The lessons |

## Style for any text you write

Simple words, short sentences, no em-dashes.
