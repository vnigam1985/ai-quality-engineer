# Contributing

Thanks for helping make this course better. Good contributions:

- **Fixes:** a broken link, a command that no longer works, a tool version that changed
- **New test cases:** golden dataset rows, attacks, agent tests. Tag each with a category and, for attacks, an OWASP ID
- **Your story:** finished the course and got an interview or a role? Open an issue and share what helped

## Rules

1. `make test` and `make eval` must pass in offline mode. No API keys in any default path
2. Every link you add must point to an official source or a well-reviewed course. Say when you checked it
3. Keep the writing simple: short sentences, plain words, no em-dashes
4. One change per pull request

## How

```bash
git checkout -b fix/short-description
# make your change
make test && make eval && python scripts/validate_dataset.py datasets/golden_v1.jsonl
git commit -m "Fix: short description"
```

Open a pull request. The PR check runs the same commands.
