# AI Quality Engineer course: every command you need.
# Run `make help` to see them all.

SHELL := /bin/bash
PY ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
APP_URL ?= http://localhost:8000
JUDGE_MODEL ?= qwen2.5:7b
PROMPTFOO := npx -y promptfoo@0.125.1

.DEFAULT_GOAL := help

help: ## Show all commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- setup ----
setup: ## Create .venv and install everything (Python 3.11+)
	$(PY) -m venv $(VENV)
	$(BIN)/pip install -U pip
	$(BIN)/pip install -r requirements.txt
	$(BIN)/playwright install chromium
	@test -f .env || cp .env.example .env
	@echo "Setup done. Next: make up && make health"

# ------------------------------------------------------------- run app ----
up: ## Start the bank app in offline mode (Docker)
	docker compose up -d --build app

up-llm: ## Start the app + Ollama with a local model (Docker)
	LLM_MODE=llm docker compose --profile llm up -d --build
	docker compose exec ollama ollama pull $(JUDGE_MODEL)

up-tracing: ## Start the app + Ollama + Phoenix tracing (week 7)
	WITH_TRACING=1 LLM_MODE=llm PHOENIX_COLLECTOR_ENDPOINT=http://phoenix:6006 docker compose --profile llm --profile tracing up -d --build
	docker compose exec ollama ollama pull $(JUDGE_MODEL)

run: ## Run the app without Docker (offline mode)
	$(BIN)/uvicorn app.app:app --port 8000 --reload

down: ## Stop everything
	docker compose --profile llm --profile tracing down

health: ## Check the app is up
	@curl -fsS $(APP_URL)/health && echo

# ---------------------------------------------------------------- tests ----
test: ## Week 6-7: API and agent tests (offline, no model needed)
	$(BIN)/pytest tests/api tests/agent -q

test-ui: ## Week 7: Playwright UI test
	$(BIN)/pytest tests/ui -q --browser chromium

dataset-check: ## Week 2: validate the golden dataset
	$(BIN)/python scripts/validate_dataset.py datasets/golden_v1.jsonl

# ---------------------------------------------------------------- evals ----
eval: ## Week 1: promptfoo deterministic checks (no model needed)
	$(PROMPTFOO) eval -c evals/promptfoo/promptfooconfig.offline.yaml -o reports/promptfoo-offline.json --no-cache

eval-judge: ## Week 1+: promptfoo with an LLM grader (needs make up-llm)
	$(PROMPTFOO) eval -c evals/promptfoo/promptfooconfig.yaml -o reports/promptfoo-judge.json --no-cache

eval-deepeval: ## Week 3: DeepEval RAG metrics with a local judge
	JUDGE=ollama $(BIN)/pytest evals/deepeval -q

eval-ragas: ## Week 3: Ragas RAG metrics with a local judge
	JUDGE=ollama $(BIN)/python evals/ragas/ragas_eval.py

calibrate: ## Week 4: measure how well the judge agrees with humans
	$(BIN)/python evals/judges/calibrate.py

redteam: ## Week 5: promptfoo red team mapped to OWASP (needs make up-llm)
	$(PROMPTFOO) redteam run -c redteam/promptfoo/redteamconfig.yaml

redteam-manual: ## Week 5: hand-written OWASP attacks (rubric checks need make up-llm)
	$(PROMPTFOO) eval -c redteam/attacks_owasp_2026.yaml -o reports/redteam-manual.json --no-cache

setup-redteam: ## Week 5: separate venv for PyRIT and garak (they pin many packages)
	python3 -m venv .venv-redteam && .venv-redteam/bin/pip install -q -r requirements-redteam.txt

redteam-pyrit: ## Week 5: PyRIT attack script (run make setup-redteam first)
	.venv-redteam/bin/python redteam/pyrit/attack.py

redteam-garak: ## Week 5: garak scan of the /ask endpoint (slow, run make setup-redteam first)
	.venv-redteam/bin/python -m garak --target_type rest.RestGenerator -G redteam/garak/garak_rest.json --spec probes.promptinject.HijackHateHumans,probes.dan.DanInTheWild --generations 1

# --------------------------------------------------------- gates/report ----
gate: ## Week 8: fail if any score is below quality_gates.yaml
	$(BIN)/python scripts/gate.py

report: ## Week 8: build the quality report (reports/quality-report.md)
	$(BIN)/python scripts/quality_report.py

clean: ## Remove caches and generated reports
	rm -rf .pytest_cache reports/*.json reports/quality-report.md
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

.PHONY: help setup up up-llm up-tracing run down health test test-ui dataset-check eval eval-judge eval-deepeval eval-ragas calibrate redteam redteam-manual setup-redteam redteam-pyrit redteam-garak gate report clean
