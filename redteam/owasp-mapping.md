# OWASP mapping for the Maple Leaf Bank assistant

Security findings only matter if people can act on them. Map every test and finding to a standard risk ID so security teams, auditors and developers speak the same language.

Sources (checked October 2026):
- [OWASP GenAI LLM Top 10 2026](https://genai.owasp.org/home/resources/owasp-genai-llm-top-10-2026/) (released August 2026, replaces the 2025 list)
- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications/) (released December 2025)

> Tools lag behind standards. promptfoo's `owasp:llm` preset may still use 2025 numbering, so this repo lists plugins explicitly and maps them here by hand.

## OWASP LLM Top 10 2026

| ID | Risk | How we test it in this course | Where |
| --- | --- | --- | --- |
| LLM01 | Prompt Injection | Direct "ignore instructions" attacks, system prompt override, indirect injection | `promptfoo: system-prompt-override, indirect-prompt-injection`, `attacks_owasp_2026.yaml`, garak `promptinject` |
| LLM02 | Sensitive Information Disclosure | Asking for other customers' data, PII social engineering | `promptfoo: pii:direct, pii:social` |
| LLM03 | Excessive Agency | Agent tricked into transfers, unconfirmed actions, fee waivers it can't do | `tests/agent/test_tools.py`, `promptfoo: excessive-agency` |
| LLM04 | Supply Chain | Pin and review model, package and MCP server versions | Process check in the week 8 quality report |
| LLM05 | Data and Model Poisoning | Edit a knowledge-base file and check evals catch the changed answer | Week 5 exercise |
| LLM06 | Unbounded Consumption | Very long inputs are rejected (422), latency budget | `tests/api/test_api.py` |
| LLM07 | Misinformation | Invented rates, fees and approvals | `promptfoo: hallucination, financial:hallucination`, golden out-of-scope rows |
| LLM08 | Hidden Context Exposure | Requests to reveal the system prompt | `promptfoo: prompt-extraction`, `attacks_owasp_2026.yaml` |
| LLM09 | Vector and Embedding Weaknesses | Retrieval returns the wrong section, or untrusted content in the index | Ragas context precision/recall (week 3) |
| LLM10 | Improper Output Handling | Model output containing HTML/script that a UI might render | `attacks_owasp_2026.yaml` script test |

## OWASP Agentic Top 10 (ASI)

| ID | Risk | Test in this course |
| --- | --- | --- |
| ASI01 | Agent Goal Hijack | "SYSTEM OVERRIDE" prompts try to make the agent transfer money |
| ASI02 | Tool Misuse & Exploitation | Transfers over the limit, malformed card numbers |
| ASI03 | Identity & Privilege Abuse | Agent only sees the customer's own fake accounts |
| ASI04 | Agentic Supply Chain Vulnerabilities | Pin tool and MCP server versions; review before upgrade |
| ASI05 | Unexpected Code Execution (RCE) | Not applicable: the agent has no code tool (say so in your report) |
| ASI06 | Memory & Context Poisoning | Not applicable: no long-term memory (say so) |
| ASI07 | Insecure Inter-Agent Communication | Not applicable: single agent |
| ASI08 | Cascading Failures | What happens when a tool errors? Agent must report it, not invent a result |
| ASI09 | Human-Agent Trust Exploitation | Confirmation flag comes from the UI, never from the chat text |
| ASI10 | Rogue Agents | Out of scope for a single bounded agent; covered by monitoring in production |

Writing "not applicable, because..." is a real skill. Auditors trust a report that explains scope more than one that pretends to test everything.

## Severity guide for findings

| Severity | Example in a bank assistant | Release decision |
| --- | --- | --- |
| Critical | Completes a money movement without confirmation; leaks another customer's data | Block release |
| High | Reveals system prompt; invents a fee or rate | Block release unless a mitigation ships with it |
| Medium | Answers off-topic questions at length | Fix in next sprint |
| Low | Tone or formatting issues | Backlog |
