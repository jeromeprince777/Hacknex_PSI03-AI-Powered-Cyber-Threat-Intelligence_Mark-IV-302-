# THREATWEAVE — External Resources & Dependencies Declaration

This document declares all external open-source libraries, packages, fonts, schemas, and assets utilized in the ThreatWeave platform for HackNex 2026 Qualifier Problem Statement **HNX26PSI03: AI-Powered Cyber Threat Intelligence**.

---

## 1. Backend Core & Analysis Engine (Python 3.11+)

| Package / Resource | Version | Category | Where Used | License | Upstream Source |
|---|---|---|---|---|---|
| `fastapi` | 0.115.6 | Framework | REST API routers, routing endpoints | MIT | https://github.com/fastapi/fastapi |
| `uvicorn` | 0.34.0 | Server | ASGI asynchronous web server | BSD-3 | https://github.com/encode/uvicorn |
| `pydantic` | 2.10.4 | Data Validation | Canonical schema enforcement & types | MIT | https://github.com/pydantic/pydantic |
| `networkx` | 3.4.2 | Graph Theory | Entity-event bipartite graph & incident 1-hop subgraph | BSD-3 | https://github.com/networkx/networkx |
| `numpy` | 2.2.1 | Numerical Analysis | Robust multivariate anomaly scoring ($\mu, \sigma$ z-excess) | BSD-3 | https://github.com/numpy/numpy |
| `pandas` | 2.2.3 | Data Processing | Tabular log normalization & filtering | BSD-3 | https://github.com/pandas-dev/pandas |
| `scipy` | 1.14.1 | Scientific | Scientific statistical algorithms | BSD-3 | https://github.com/scipy/scipy |
| `pyyaml` | 6.0.2 | Configuration | Parsing `configs/detection_rules.yaml` | MIT | https://github.com/yaml/pyyaml |
| `pytest` | 9.1.1 | Testing | Automated test suite (32 tests) | MIT | https://github.com/pytest-dev/pytest |
| `httpx` | 0.28.1 | HTTP Client | Integration test runner client | BSD-3 | https://github.com/encode/httpx |

---

## 2. Frontend Analyst Console (Next.js 16 / React 19)

| Package / Resource | Version | Category | Where Used | License | Upstream Source |
|---|---|---|---|---|---|
| `next` | 16.1.6 | Framework | App router, SSR, proxy rewrites | MIT | https://github.com/vercel/next.js |
| `react` | 19.2.4 | UI Runtime | Component rendering & state | MIT | https://github.com/facebook/react |
| `react-dom` | 19.2.4 | UI Runtime | DOM mounting | MIT | https://github.com/facebook/react |
| `tailwindcss` | 4.0.0 | Styling | SOC dark-mode aesthetic styling | MIT | https://github.com/tailwindlabs/tailwindcss |
| `lucide-react` | 0.475.0 | Icons | SOC interface iconography (terminal, shield, graph) | ISC | https://github.com/lucide-icons/lucide |
| `clsx` | 2.1.1 | Utility | Conditional class merging | MIT | https://github.com/lukeed/clsx |
| `tailwind-merge` | 3.0.1 | Utility | Tailwind class resolution | MIT | https://github.com/dcastil/tailwind-merge |

---

## 3. Fonts & Typography

| Font Family | Provider | Usage | License | Source |
|---|---|---|---|---|
| JetBrains Mono | Google Fonts / CDN | Hex IDs, Event telemetry, JSON payloads | SIL Open Font License 1.1 | https://fonts.google.com/specimen/JetBrains+Mono |
| Inter / Geon | Vercel System Font Stack | High-density analyst data tables & copy | SIL Open Font License 1.1 | https://fonts.google.com/specimen/Inter |

---

## 4. Seed Datasets & Attack Scenarios

| Dataset Name | Records | Type | Purpose | Location |
|---|---|---|---|---|
| `attack_insider_usb.jsonl` | 15 events | Curated Telemetry | Multi-stage insider data exfiltration across 4 stages (`evt-001` to `evt-015`) | `data/scenarios/` |
| `benign_admin.jsonl` | 10 events | Curated Telemetry | Routine sysadmin maintenance, backup, & authorized USB | `data/scenarios/` |
| `attack_partial.jsonl` | 7 events | Curated Telemetry | Incomplete chain missing USB write (demonstrates score degradation) | `data/scenarios/` |
| `malformed_logs.jsonl` | 8 records | Negative Telemetry | Corrupted logs testing quarantine pipeline (invalid JSON, missing ID) | `data/scenarios/` |

---

## 5. Security Principles & Non-Negotiable Rules Compliance

1. **Zero Hallucination / Zero Synthetic Detection:** No LLM is used as a detector of truth. All signals are generated deterministically by declarative rule engines and statistical baseline algorithms.
2. **Deterministic Evidence Attribution:** Every reconstructed attack stage is backed 100% by concrete `event_id` references from stored telemetry.
3. **Verified Copilot Guard:** The AI Copilot operates strictly on bounded evidence packs. Output containing ungrounded event IDs, unknown attack stages, or unauthorized playbook actions is rejected deterministically before display.
