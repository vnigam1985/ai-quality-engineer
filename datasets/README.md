# Golden datasets

A golden dataset is your test suite for an AI system: questions with the answer a human expert would accept, plus metadata so you can slice results.

## golden_v1.jsonl

20 items for the [bank assistant](../app/kb/maple-bank-policies.md). One JSON object per line:

| Field | Meaning |
| --- | --- |
| `id` | Stable ID. Never reuse an ID for a different question |
| `question` | What the user asks |
| `reference` | The expected answer (ground truth), written by a human |
| `source_section` | Which knowledge-base section should be retrieved. `null` = nothing should be found |
| `category` | `in_scope`, `out_of_scope`, `safety`, `adversarial` |
| `risk` | `low`, `medium`, `high`. High-risk items (money, fees, fraud) get stricter thresholds |

## Rules for good golden data

1. **Write references by hand**, or have an expert review every generated one. A wrong reference silently breaks every metric.
2. **Cover the risk, not just the happy path.** This set is about 75% in-scope, 10% out-of-scope, 15% safety/adversarial. Real apps need more negatives.
3. **Version it.** Never edit `golden_v1` in place after it's been used for a baseline. Copy to `golden_v2` and record what changed.
4. **Size:** start with 20 to 50 to learn, grow to 100 to 300 for a production gate, stratified by risk.
5. **Use real questions** from logs or support tickets when you can (with personal data removed).
6. **Don't let it leak** into prompts or fine-tuning data, or your scores will look better than reality.
