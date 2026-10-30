# Troubleshooting

Still stuck after this page? Open an issue with the **I'm stuck** template. Include the week, the command and the full error.

## Setup

| Problem | Fix |
| --- | --- |
| `make: command not found` (Windows) | Use WSL2, or Git Bash with make installed. Or run the commands inside each Makefile target by hand |
| `python3: command not found` | Install Python 3.11+ and reopen the terminal. On Windows it may be `python` or `py` |
| `npx: command not found` | Install Node.js 20+ |
| Playwright says the browser is missing | `.venv/bin/python -m playwright install chromium` |
| Port 8000 already in use | `make down`, or stop whatever else uses it. On Mac/Linux: `lsof -i :8000` |

## The app

| Problem | Fix |
| --- | --- |
| `make health` fails right after `make up` | Wait 10 seconds. The container has a health check; `docker compose ps` shows when it's healthy |
| `"mode": "offline"` but you wanted llm | Use `make up-llm`, not `make up` |
| Answers are slow in llm mode | Normal on a CPU: 5 to 30 seconds per answer for a 7B model. Try `JUDGE_MODEL=qwen2.5:3b` |
| `model "qwen2.5:7b" not found` | `docker compose exec ollama ollama pull qwen2.5:7b` |

## Evals

| Problem | Fix |
| --- | --- |
| promptfoo hangs with no output | A test with `llm-rubric` is waiting for Ollama. Start it with `make up-llm`, or use `make eval` (offline config) |
| promptfoo shows old results | It caches. The Makefile passes `--no-cache`; add it if you run promptfoo by hand |
| Ragas: `ModuleNotFoundError: langchain_community...` | `pip install "langchain-community<0.4"` (already pinned in requirements.txt) |
| Ragas or DeepEval: JSON parse or "invalid output" errors | Small local judges sometimes return bad JSON. Re-run, or use a bigger judge model. Week 3 explains why |
| DeepEval asks for an OpenAI key | Make sure `JUDGE=ollama` is set (the Makefile does this) |
| `make gate` says SKIPPED | That report hasn't been generated yet. It's not a failure |

## Red team

| Problem | Fix |
| --- | --- |
| PyRIT or garak install breaks other packages | Use `make setup-redteam`. It makes a separate `.venv-redteam` |
| garak runs for hours | Use fewer probes and `--generations 1` |
| `make redteam` is very slow | Lower `numTests` in `redteam/promptfoo/redteamconfig.yaml` to 2 |

## Docker

| Problem | Fix |
| --- | --- |
| `Cannot connect to the Docker daemon` | Start Docker Desktop |
| Build fails with SSL certificate errors (corporate laptop) | Your company proxy inspects traffic. Ask IT for the proxy CA certificate, or run without Docker: `make run` |
| Not enough disk | `docker system prune` removes unused images. The Ollama model alone is about 5 GB |
