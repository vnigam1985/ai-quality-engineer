# Observability notes

The hands-on lab is [weeks/07-observability](../weeks/07-observability/README.md). This page is the cheat sheet.

## Turn tracing on

| Where | How |
| --- | --- |
| Docker | `make up-tracing` (builds the app with `WITH_TRACING=1`, starts Ollama and Phoenix) |
| Without Docker | `pip install -r requirements-tracing.txt`, run Phoenix (`docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix`), then `LLM_MODE=llm PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006 uvicorn app.app:app --port 8000` |

Phoenix UI: http://localhost:6006. Project name: `maple-bank-assistant`.

With `PHOENIX_COLLECTOR_ENDPOINT=http://<host>:6006`, `phoenix.otel.register()` sends spans over gRPC to port 4317 on the same host (checked with arize-phoenix-otel in October 2026). Offline mode makes no model calls, so there's nothing to trace.

## What each span tells you

| Field | Use it to |
| --- | --- |
| Input messages | See the exact prompt, including retrieved context |
| Output | See the raw model answer before any post-processing |
| Token counts | Estimate cost and spot rambling |
| Latency | Find slow calls |
| Tool calls | See which tool the agent picked and with what arguments |

## From trace to test

1. Filter for answers users disliked, or that contain the refusal text when they shouldn't
2. Copy the question into a new golden dataset version with the correct reference
3. Re-run weeks 1 to 4 evals. If the new row fails, you've got a regression test
