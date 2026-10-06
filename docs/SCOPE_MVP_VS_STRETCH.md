# THREATWEAVE — MVP / Stretch Control Sheet

## MVP — DO NOT COMPROMISE

| Feature | Status gate |
|---|---|
| Canonical event schema | Must |
| JSONL/CSV ingestion | Must |
| Normalization | Must |
| Attack signal rules | Must |
| Entity novelty | Must |
| Sequence correlation | Must |
| Entity graph | Must |
| Attack timeline | Must |
| Stage evidence | Must |
| Risk Index | Must |
| False-positive suppression | Must |
| Benign scenario | Must |
| Evidence-bounded Copilot | Must |
| AI response verifier | Must |
| Playwright smoke test | Must |
| README | Must |

## Stretch — ONLY AFTER MVP WORKS

| Feature | Add only after MVP |
|---|---|
| multiple attack families | Yes |
| natural-language investigation search | Yes |
| live log streaming | Yes |
| advanced anomaly model | Yes |
| cross-session identity stitching | Yes |
| external threat-intel feeds | Yes |
| persistent analyst feedback | Yes |
| ATT&CK-style mapping | Yes |
| hosted database | Yes |
| autonomous remediation | No for qualifier MVP |

## Kill List

Immediately remove or defer any feature that:
- makes the demo less stable;
- introduces unsupported claims;
- creates dependency on an unreliable external service;
- adds UI clutter;
- cannot be explained by the team;
- consumes time needed for evidence, false-positive control or testing.

