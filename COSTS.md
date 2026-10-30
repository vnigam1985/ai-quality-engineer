# What this course costs

**$0.** Every week runs on your laptop with free, open-source tools. No API keys, no cloud account, no credit card.

| Week | What runs | Cost |
| --- | --- | --- |
| 0 to 2 | Bank app in offline mode, promptfoo, pytest | $0 |
| 3 to 5 | Local model (qwen2.5:7b) and embeddings through Ollama | $0, needs about 6 GB disk and 16 GB RAM |
| 6 | Playwright tests | $0 |
| 7 | Arize Phoenix (self-hosted container) | $0 |
| 8 | GitHub Actions on a public repo or fork | $0 on public repos (GitHub's standard runners are free for public repositories) |

## Optional costs

| Item | Approximate cost | Do you need it? |
| --- | --- | --- |
| A hosted model instead of Ollama (set `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `MODEL`) | A few dollars for the whole course with a small model. Check your provider's current prices | No. Use it only if your laptop is too slow |
| Udemy courses in [resources.md](resources.md) | Usually CA$15 to CA$30 on sale (approximate) | No. Free docs cover everything |
| ISTQB exam | Roughly CA$350 to CA$450 (approximate, verify) | Optional, see [certifications.md](certifications.md) |

If you use a hosted model, set a spending limit in the provider's console before you start.

## Laptop too slow for a 7B model?

Use a smaller model: `make up-llm JUDGE_MODEL=qwen2.5:3b`. Scores will be noisier. That's a good thing to write about in your week 4 calibration notes.
