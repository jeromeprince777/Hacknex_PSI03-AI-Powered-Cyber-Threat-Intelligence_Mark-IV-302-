# ThreatWeave

> **HNX26PSI03: AI-Powered Cyber Threat Intelligence**  
> Evidence-first cyber threat intelligence platform for reconstructing coordinated attack chains from multi-source security logs with deterministic scoring and anti-hallucination verification.

---

## 1. Problem Statement

Security telemetry from enterprise environments presents a core challenge: **individual events appear benign in isolation, but reveal coordinated malicious campaigns when correlated across users, devices, source IPs, and sensitive resources.**

Traditional security operations face two failure modes:
1. **Alert Fatigue & Disconnection:** Point detectors produce dozens of fragmented alerts without correlating temporal sequence or entity links.
2. **AI Hallucination in Generic SOC Tools:** Naive LLM integrations invent fake timestamps, fabricate indicators of compromise, or summarize data that was never present in raw logs.

**ThreatWeave** solves this by enforcing an uncompromising **evidence-first architecture**:
- **Normalized Ingestion:** Ingests Windows EventLogs, VPN authentication, and EDR telemetry into a strict Canonical Schema with automated quarantining of malformed records.
- **Deterministic Multi-Stage Attack Reconstruction:** Correlates authentication novelty, sensitive resource discovery, and removable-media exfiltration into chronological attack stages.
- **Anti-Hallucination AI Copilot:** The LLM operates strictly on a **bounded evidence pack**. Every statement, stage, and action recommendation is cryptographically and logically verified against stored telemetry before being presented to the analyst.
- **Explainable Risk Index:** Clamps a transparent multi-factor formula $(0\text{--}100)$ combining Signal Severity, Sequence Consistency, Entity Novelty, and Statistical Anomaly.
- **First-Class False-Positive Suppression:** Routine administrator tasks and isolated events are audited and suppressed without raising high-confidence incidents.

---

## 2. System Architecture

```text
       Raw Multi-Source Logs (Windows EventLog, VPN, EDR, Syslog)
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │  Ingestion & Schema Check   │──► Quarantined Records
                   │    (Canonical Event-v1)     │    (Invalid JSON, Bad IDs)
                   └──────────────┬──────────────┘
                                  │ Valid Events
                                  ▼
                   ┌─────────────────────────────┐
                   │    Atomic Signal Detectors  │◄── configs/detection_rules.yaml
                   │   + Entity Novelty Baseline │
                   └──────────────┬──────────────┘
                                  │ Security Signals
                                  ▼
                   ┌─────────────────────────────┐
                   │ Entity Graph & Correlator   │
                   │ (Actor Clustering & Windows)│
                   └──────────────┬──────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
      [Pass Promotion Gate]             [Fail Promotion Gate]
       (≥3 events, ≥2 stages)            (<3 events or 1 stage)
                  │                               │
                  ▼                               ▼
      ┌───────────────────────┐       ┌───────────────────────┐
      │  Incident Promotion   │       │ False-Positive Audit  │
      │  & Multi-Factor Risk  │       │   Suppression Log     │
      └───────────┬───────────┘       └───────────────────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │ Bounded Evidence Pack │
      └───────────┬───────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │  AI Copilot Engine    │
      └───────────┬───────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │ Anti-Hallucination    │──► Rejected (Fake event or action)
      │  Verification Guard   │
      └───────────┬───────────┘
                  │ Verified Output
                  ▼
      ┌───────────────────────┐
      │ High-Density SOC UI   │
      │ (Timeline, Graph,     │
      │  Drawer, Risk Meter)  │
      └───────────────────────┘
```

---

## 3. Tech Stack

### Backend Core
- **Python 3.11+ / FastAPI:** High-performance async REST API with Pydantic v2 data contracts.
- **NetworkX:** Entity-event graph topology and 1-hop neighborhood subgraph extraction.
- **NumPy & Pandas:** Statistical baseline modeling and standardized multivariate anomaly detection.
- **SQLite & Pure-Python Storage:** Local persistence layer for incidents, stages, evidence links, and suppression audits.
- **Pytest:** 32 comprehensive unit and integration tests covering positive, negative, and edge-case scenarios.

### Frontend Analyst Console
- **Next.js 16 (React 19, TypeScript):** High-density SOC interface optimized for rapid triage.
- **Tailwind CSS v4:** Bespoke dark-theme telemetry color palette (`#080a11` midnight background, cyan timeline telemetry, emerald verified badges, rose critical flags).
- **Lucide Icons:** Specialized security operations iconography.
- **Interactive SVG Entity Graph:** Direct visualization of correlated actors, devices, IP addresses, files, and USB storage volumes.

---

## 4. Getting Started Locally

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
# From repository root
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server on port 8000
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be live at `http://127.0.0.1:8000`. API documentation available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

```bash
# In a new terminal from repository root
cd frontend

# Install dependencies
npm install

# Start Next.js development server on port 3000
npm run dev -- -p 3000
```

Analyst Console will be live at `http://localhost:3000`.

---

## 5. Automated Evaluation & Demo Scripts

ThreatWeave includes complete headless verification scripts designed for instant evaluator testing:

### Pre-Flight Schema Verification
```bash
python scripts/seed_demo.py
```
Validates all 4 seed datasets against the Canonical Event Schema and tests quarantine isolation of malformed logs.

### Full End-to-End Headless Demo & Benchmark
```bash
python scripts/run_demo.py
```
Executes the complete pipeline from CLI:
1. Reconstructs the canonical 4-stage insider USB attack with Risk Index 89/100.
2. Generates an evidence-bounded AI Copilot explanation verified by the anti-hallucination guard.
3. Injects a simulated hallucination (`evt-HALLUCINATED-FAKEEVENT-999`) and proves the verifier rejects it with zero UI leakage.
4. Replays the benign administrator dataset and verifies 100% false-positive suppression (0 incidents promoted).
5. Prints an automated benchmark summary table.

---

## 6. Seed Scenarios & Benchmark Matrix

| Scenario File | Records | Expected Incidents | Risk Index | Reconstructed Stages | False Positives |
|---|---|---|---|---|---|
| `attack_insider_usb.jsonl` | 15 events | **1 (inc-001)** | **89 / 100** | Initial Access $\rightarrow$ Discovery $\rightarrow$ USB Exfiltration | 0 |
| `benign_admin.jsonl` | 10 events | **0** | **N/A** | Suppressed by Promotion Gate (Audit Logged) | 0 |
| `attack_partial.jsonl` | 7 events | **1 (inc-001)** | **76 / 100** | Initial Access $\rightarrow$ Resource Access (No Exfil) | 0 |
| `malformed_logs.jsonl` | 8 records | **0** | **N/A** | 6 Quarantined (`INVALID_JSON`, `MISSING_ID`), 2 Valid | 0 |

### Scenario Profiles

1. **`attack_insider_usb.jsonl` (Canonical Attack):**
   - Telemetry from actor `user-42` on `device-17`.
   - Stage 1 (`evt-003`): Unusual VPN logon from novel external IP `203.0.113.10`.
   - Stage 2 (`evt-008`, `evt-009`): Unauthorized access and bulk reading of `Finance/Q4/payroll.xlsx` and `Legal/M&A/Project_Titan.pdf`.
   - Stage 3 (`evt-011`, `evt-012`, `evt-013`): Mount of removable media `usb-kingston-992` and direct exfiltration copy.
2. **`benign_admin.jsonl` (Benign IT Operations):**
   - Routine administrator logon `admin-01` from workstation `it-workstation-01` on subnet `10.10.1.100`.
   - Routine backup script execution and authorized USB drive mounting for driver updates.
   - Suppressed by the correlation gate because activity does not cross multiple stages or demonstrate anomalous access sequences.
3. **`attack_partial.jsonl` (Graceful Degradation):**
   - Attack terminates after sensitive file discovery; attacker disconnects without copying to USB.
   - Correctly produces lower sequence score and lowers overall Risk Index from 89 to 76.

---

## 7. Deterministic Risk Index Formulation

ThreatWeave does **not** generate arbitrary or opaque risk scores. Every score exposes its underlying factors:

$$\text{Risk Index} = \text{clamp}\Big(100 \times \big[0.35 \cdot S_{\text{signal}} + 0.30 \cdot S_{\text{sequence}} + 0.20 \cdot S_{\text{novelty}} + 0.15 \cdot S_{\text{anomaly}}\big]\Big)$$

Where:
- **$S_{\text{signal}}$ (Signal Severity, 35%):** Normalized average weight of triggered atomic detection rules.
- **$S_{\text{sequence}}$ (Sequence Consistency, 30%):** Completeness of observed stages against chronological attack lifecycle:
  $$S_{\text{sequence}} = \min\left(1.0, \frac{|\text{stages}|}{3}\right) \times \text{order\_penalty}$$
- **$S_{\text{novelty}}$ (Entity Novelty, 20%):** Standardized distance from baseline history ($1.0$ for novel IP/device/resource, $0.0$ for known benign).
- **$S_{\text{anomaly}}$ (Statistical Anomaly, 15%):** Standardized multivariate z-excess ($\mu, \sigma$) across 6 behavioral dimensions (event velocity, transfer size, unique resources, after-hours ratio).

---

## 8. Anti-Hallucination AI Copilot Verification Guard

The Copilot is engineered strictly as an **advisory summarizer**, not an autonomous detector of truth:
1. **Bounded Evidence Pack:** The LLM prompt receives strictly:
   - Incident ID and severity.
   - Exact list of verified `evidence_event_ids`.
   - Chronological stages with their reason codes.
   - List of pre-approved response actions (`isolate-device`, `disable-session`, `review-resource-access`, `preserve-evidence`).
2. **Deterministic Pre-Display Verifier (`verify_copilot`):**
   - Rejects the output if any cited `event_id` is missing from the evidence pack.
   - Rejects the output if any cited attack stage does not exist in the incident.
   - Rejects the output if any suggested action is not in the approved playbook library.
3. **Evaluator Negative Test Controls:** The UI includes built-in toggles allowing evaluators to inject synthetic event IDs (`evt-fake-9999`) or unauthorized actions (`nuke-all-firewalls`) to witness real-time verifier interception and rejection.

---

## 9. Reproducibility & Semantic Versioning

For a fixed dataset and configuration, ThreatWeave yields 100% byte-for-byte identical detection:
- `analysis_version`: `0.1.0`
- `rule_version`: `demo-2026-01`
- `schema_version`: `event-v1`
- `prompt_version`: `copilot-v1`

---

## 10. External Resources Declaration

Declared in compliance with HackNex Agent Engineering Rule I and Qualifier Transparency Guidelines:

| Resource | Category | Where Used | Source / License |
|---|---|---|---|
| `fastapi` | Web Framework | REST API endpoints | MIT (https://github.com/fastapi/fastapi) |
| `uvicorn` | ASGI Server | Backend web server | BSD-3 (https://github.com/encode/uvicorn) |
| `pydantic` | Data Validation | Canonical event schema & contracts | MIT (https://github.com/pydantic/pydantic) |
| `networkx` | Graph Library | Entity graph & 1-hop subgraph extraction | BSD-3 (https://github.com/networkx/networkx) |
| `numpy` | Numerical Computing | Multivariate anomaly z-excess scorer | BSD-3 (https://github.com/numpy/numpy) |
| `next.js` | Web Framework | Analyst Console App Router & SSR | MIT (https://github.com/vercel/next.js) |
| `react` | UI Runtime | Dashboard component hierarchy | MIT (https://github.com/facebook/react) |
| `tailwindcss` | Styling | High-density SOC dark theme | MIT (https://github.com/tailwindlabs/tailwindcss) |
| `lucide-react` | Icons | Terminal, Shield, and Graph iconography | ISC (https://github.com/lucide-icons/lucide) |
| JetBrains Mono | Typography | Event IDs, JSON payloads, and timestamps | SIL OFL 1.1 (Google Fonts) |
| Synthetic Datasets | Data | 4 benchmark scenarios (`data/scenarios/`) | Proprietary / Authored by Team |

---

## 11. MVP vs. Stretch Scope

| Feature / Capability | HackNex MVP Status | Stretch Scope |
|---|---|---|
| Multi-Source Log Ingestion & Normalizer | **Complete** (Windows, VPN, EDR) | Cloudtrail & Zeek parsers |
| Atomic Detection Engine | **Complete** (YAML-driven rules) | Sigma rule transpiler |
| Entity Graph Reconstruction | **Complete** (NetworkX 1-hop export) | WebGL 10,000+ node visualizer |
| Chronological Stage Reconstruction | **Complete** (Ordered evidence chains) | Automated killchain tree branching |
| Explainable Risk Index Formula | **Complete** (4 transparent factors) | Bayesian dynamic belief network |
| Anti-Hallucination Copilot Verifier | **Complete** (Bounded pack & rejection) | Live external LLM streaming endpoint |
| False-Positive Suppression Log | **Complete** (Suppression audit records) | Active learning analyst feedback loop |
| High-Density SOC Console | **Complete** (Next.js 16 + SVG graph) | Multi-tenant SOC role-based access |

---

## 12. Verification & Test Suite

Run the full automated test suite:
```bash
# From repository root
.\backend\.venv\Scripts\pytest backend/tests/ -v
```
**Result:** 32 passed unit & integration tests covering canonical schema validation, negative controls, attack promotion, suppression gates, IsolationForest/z-excess scoring, and Copilot hallucination rejection.
