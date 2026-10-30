# Red team toolkit

Hands-on lab: [weeks/05-red-teaming](../weeks/05-red-teaming/README.md). Risk IDs: [owasp-mapping.md](owasp-mapping.md).

| File | Tool | Needs a model? | Run |
| --- | --- | --- | --- |
| [attacks_owasp_2026.yaml](attacks_owasp_2026.yaml) | promptfoo eval | `contains` checks no, `llm-rubric` checks yes | `make redteam-manual` |
| [promptfoo/redteamconfig.yaml](promptfoo/redteamconfig.yaml) | promptfoo red team | Yes (generates attacks) | `make redteam` |
| [pyrit/attack.py](pyrit/attack.py) | PyRIT 1.1.0 | No | `make setup-redteam && make redteam-pyrit` |
| [garak/garak_rest.json](garak/garak_rest.json) | garak 0.17.1 | No (scores with garak's own detectors) | `make setup-redteam && make redteam-garak` |

PyRIT and garak go in their own virtual environment (`.venv-redteam`) because they pin many packages.

## garak in more detail

garak talks to the app through its REST generator. The config maps garak's prompt into the `/ask` body (`$INPUT`) and reads the `answer` field back.

```bash
# list all probes (hundreds; the 💤 ones are off by default)
.venv-redteam/bin/python -m garak --list_probes

# what make redteam-garak runs
.venv-redteam/bin/python -m garak --target_type rest.RestGenerator \
  -G redteam/garak/garak_rest.json --spec probes.promptinject.HijackHateHumans,probes.dan.DanInTheWild --generations 1
```

Start with a small probe list. A full scan can take hours on a laptop. garak writes a JSONL and an HTML report and prints their paths at the end.

**What you'll see in offline mode** (garak 0.17.1, October 2026):

```
promptinject.HijackHateHumans   promptinject.AttackRogueString: PASS  ok on 256/256
dan.DanInTheWild                mitigation.MitigationBypass:    FAIL  ok on   0/156
```

Don't panic about the FAIL. The `MitigationBypass` detector looks for refusal words like "I can't help with that". Offline mode answers with a policy section instead, so the detector counts every answer as a bypass. Read some answers in the HTML report and decide: real finding or detector mismatch? That judgement call is the skill. Also note only 156 of 256 prompts were scored: the app rejects questions over 2,000 characters with HTTP 422, and `skip_codes: [422]` in the config tells garak to skip those instead of crashing.

## PyRIT in more detail

`attack.py` uses `HTTPTarget` with a raw HTTP request (`{PROMPT}` is replaced by each attack), `PromptSendingAttack` to send it, and a plain "forbidden strings" check to score. Extend it by adding rows to `ATTACKS`, or swap in PyRIT converters (Base64, leetspeak, translation) to test whether encoded attacks get through.
