# ThreatWeave

<p align="center">
  <img src="assets/diagrams/architecture_overview.svg" alt="ThreatWeave Architecture" width="100%" />
</p>

<p align="center">
  <strong>HNX26PSI03: AI-Powered Cyber Threat Intelligence</strong><br />
  <em>Evidence-First Attack Chain Reconstruction &bull; Explainable 4-Factor Risk Index &bull; Zero-Hallucination AI Copilot &bull; 100% Deterministic & Offline</em>
</p>

<p align="center">
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Status-Working%20System-06b6d4?style=for-the-badge&logo=shield" alt="Status" /></a>
  <a href="#-test-suite--evaluator-verification"><img src="https://img.shields.io/badge/Pytest-42%2F42%20Passing-10b981?style=for-the-badge&logo=pytest" alt="Pytest" /></a>
  <a href="#-the-2-golden-rules-compliance"><img src="https://img.shields.io/badge/False%20Positive%20Limit-0%20FP%20on%20Benign-10b981?style=for-the-badge" alt="Rule 1" /></a>
  <a href="#-the-2-golden-rules-compliance"><img src="https://img.shields.io/badge/Proof%20per%20Stage-100%25%20Telemetry%20Backed-06b6d4?style=for-the-badge" alt="Rule 2" /></a>
  <a href="#-declared-resources--provenance"><img src="https://img.shields.io/badge/Environment-100%25%20Offline%20%2F%20Air--Gapped-a855f7?style=for-the-badge" alt="Offline" /></a>
</p>

---

## 📑 Table of Contents
1. [Problem Statement & HackNex Mandate](#-problem-statement--hacknex-mandate)
2. [The 2 Golden Rules Compliance](#-the-2-golden-rules-compliance)
3. [End-to-End System Architecture](#-end-to-end-system-architecture)
4. [Core Model & Reasoning Mechanism](#-core-model--reasoning-mechanism)
5. [Data Pipeline Demonstration](#-data-pipeline-demonstration)
6. [Interactive UI & Forensic Elements Walkthrough](#-interactive-ui--forensic-elements-walkthrough)
7. [Sample Input & Output Trace](#-sample-input--output-trace)
8. [Scope Note: MVP vs. Stretch Goals](#-scope-note-mvp-vs-stretch-goals)
9. [Tech Stack & Declared Resources](#-tech-stack--declared-resources)
10. [Quick Start & Setup Instructions](#-quick-start--setup-instructions)
11. [How to Reproduce Demonstrated Results](#-how-to-reproduce-demonstrated-results)
12. [Presentation Deck & Submission Links](#-presentation-deck--submission-links)

---

## 🎯 Problem Statement & HackNex Mandate

Enterprise security operations collect millions of raw logs daily from user logins, workstations, applications, file shares, and network firewalls. In isolation, nearly every single log entry appears benign:
- A user authenticates from a VPN.
- An employee opens an internal spreadsheet.
- A USB peripheral is mounted.
- Data is transmitted to an external IP.

Traditional Security Operations Centers (SOCs) face two failure modes:
1. **Alert Fatigue & Disconnection:** Point-detection SIEMs flood analysts with fragmented alerts without linking temporal sequence or entity graphs across users, devices, IPs, and applications.
2. **AI Hallucination in Generic SOC Tools:** Naive LLM integrations invent fake timestamps, fabricate indicators of compromise (IOCs), or summarize data that was never present in raw logs.

**ThreatWeave** solves this by implementing an uncompromising **evidence-first architecture**:
- **Normalized Ingestion:** Ingests Windows EventLogs, VPN authentication, and EDR telemetry into a strict canonical schema ([`CanonicalEvent-v1`](backend/app/schemas/events.py)) with quarantine isolation for malformed data.
- **Deterministic Multi-Stage Attack Reconstruction:** Correlates authentication novelty, sensitive resource discovery, and removable-media exfiltration into chronological attack stages.
- **Bounded Anti-Hallucination Copilot:** The AI operates exclusively on a **bounded evidence pack**. Every statement, stage, and action recommendation is verified against stored telemetry before being presented to the analyst.
- **Explainable 4-Factor Risk Index:** Clamps a transparent multi-factor formula $(0\text{--}100)$ combining Signal Severity, Sequence Consistency, Entity Novelty, and Statistical Anomaly.
- **First-Class False-Positive Suppression:** Routine administrator tasks and isolated events are audited and suppressed without raising high-confidence incidents.

---

## ⚖️ The 2 Golden Rules Compliance

The authoritative **HackNex 2026 Problem Statement Booklet (Page 7)** establishes two strict evaluation rules:

### 🛡️ Rule 1: False Positive Limit
> *"If your system raises too many false alarms on clean logs, your score gets capped. More alerts ≠ better score."*

ThreatWeave implements an **Incident Promotion Gate** in [`TemporalSequenceCorrelator`](backend/app/detectors/sequence.py). A cluster of events is promoted to an Incident **only if** it satisfies all three conditions:
1. **Event Count:** Contains $\ge 3$ concrete telemetry events.
2. **Stage Progression:** Spans $\ge 2$ distinct attack stages (e.g., initial access + resource collection).
3. **Temporal Ordering:** Preserves strict chronological monotonicity.

Clusters failing this gate (e.g. routine sysadmin maintenance in [`data/scenarios/benign_admin.jsonl`](data/scenarios/benign_admin.jsonl)) are **quietly routed to an immutable Suppression Audit Ledger** with reason `INSUFFICIENT_CHAIN_EVIDENCE`.
- **Result on Benign Baseline:** **0 false-positive incidents created**; SOC queue remains clean.

<p align="center">
  <img src="assets/diagrams/promotion_gate.svg" alt="Promotion Gate Logic" width="80%" />
</p>

### 🔍 Rule 2: Proof for Every Stage
> *"Every stage of the attack must have proof. An unsupported claim = doesn't count."*

Every promoted attack stage in ThreatWeave enforces that `stage.evidence_event_ids` contains at least one verified event ID from raw telemetry. Evaluators can click any stage to open the Forensic Evidence Drawer and inspect the raw event payload, timestamps, and detection rules.
- **Result on Canonical Attack:** All 4 stages reference concrete event IDs (`evt-003`, `evt-008`, `evt-009`, `evt-011`, `evt-012`, `evt-013`, `evt-015`). Zero synthetic or inferred stages exist.

<p align="center">
  <img src="assets/diagrams/copilot_verification.svg" alt="Anti-Hallucination Verification Guard" width="85%" />
</p>

---

## 🏗️ End-to-End System Architecture

```text
       Raw Multi-Source Telemetry (Windows EventLog, VPN, EDR, Firewall)
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

## 🧠 Core Model & Reasoning Mechanism

### 1. Explainable 4-Factor Risk Engine
Rather than relying on ungrounded AI predictions, ThreatWeave calculates a deterministic **Risk Index (0–100)**:

$$\text{Risk Index} = 100 \times \left(0.35 \times S_{\text{signal}} + 0.30 \times S_{\text{sequence}} + 0.20 \times S_{\text{novelty}} + 0.15 \times S_{\text{anomaly}}\right)$$

| Component | Weight | Canonical Attack Score | What It Represents |
| :--- | :---: | :---: | :--- |
| **Signal Severity ($S_{\text{signal}}$)** | **35%** | **0.7143** | Average base severity across all triggering atomic detectors. |
| **Sequence Consistency ($S_{\text{sequence}}$)** | **30%** | **1.0000** | Monotonic alignment across attack stages (Initial Access $\to$ Collection $\to$ USB $\to$ Exfil). Penalized to $0.0$ if reversed. |
| **Entity Novelty ($S_{\text{novelty}}$)** | **20%** | **1.0000** | Frequency deviation of actor accessing novel external IP locations or confidential shares. |
| **Statistical Anomaly ($S_{\text{anomaly}}$)** | **15%** | **0.9412** | Standardized multivariate $z$-score deviation across hourly volume, sensitive access ratio, USB events, and egress bytes. |
| **Composite Result** | **100%** | **89 / 100 (HIGH)** | **94% Statistical Confidence** |

### 2. NetworkX Multi-Relational Entity Graph
Correlates entities across a bipartite graph topology implemented in [`backend/app/graph/builder.py`](backend/app/graph/builder.py):
- **Nodes:** Users (`user-42`), Workstations (`device-17`), Ingress IPs (`203.0.113.10`), Sensitive Files (`payroll.xlsx`, `Project_Titan.pdf`), Peripherals (`Volume:E:\`), Egress IPs (`198.51.100.88`).
- **Edges:** `FROM_IP`, `OCCURRED_ON`, `ACCESSED_RESOURCE`, `MOUNTED_USB`, `CONNECTED_TO_IP`.

<p align="center">
  <img src="assets/diagrams/entity_graph_topology.svg" alt="Entity Graph Topology" width="80%" />
</p>

### 3. Anti-Hallucination Output Verifier
Implemented in [`backend/app/copilot/verifier.py`](backend/app/copilot/verifier.py):
- Evaluates synthesized output before it reaches the UI.
- Validates that every referenced `event_id` belongs to the incident's bounded evidence pack.
- Validates that every proposed action belongs to the approved response catalog (`APPROVED_ACTION_CATALOG`).
- Ungrounded tokens or unauthorized actions are immediately rejected.

---

## 🔄 Data Pipeline Demonstration

### 1. Ingestion & Normalization
Incoming raw logs from heterogeneous formats (Windows EventLogs, VPN authentication records, Syslog) are parsed into standardized Pydantic models:
```json
{
  "event_id": "evt-003",
  "timestamp": "2026-10-06T09:41:12Z",
  "source": "vpn",
  "event_type": "login_success",
  "action": "authenticate",
  "user_id": "user-42",
  "device_id": "device-17",
  "src_ip": "203.0.113.10",
  "dst_ip": "10.10.1.5",
  "attributes": {
    "login_location": "Bucharest, Romania",
    "vpn_profile": "Corp-Global-Access"
  }
}
```

### 2. Atomic Rule Matching & Novelty
The event triggers detector `AUTH_NEW_LOCATION` with base weight $0.55$ and creates a security signal.

### 3. Temporal Clustering
Signals occurring within a sliding 3600-second window are grouped by primary actor (`user-42`). When subsequent file access, USB copy, and egress transfer events occur, they are clustered into a multi-stage candidate chain.

### 4. Promotion Gate & Graph Assembly
Candidate chain meets promotion criteria ($\ge 3$ events, $\ge 2$ stages) and is promoted to incident `inc-001`. The 1-hop neighborhood subgraph is extracted using NetworkX and serialized for the frontend.

---

## 🖥️ Interactive UI & Forensic Elements Walkthrough

### 1. Executive Console & Radial Risk Gauge
Displays primary actor attribution (`user-42`), radial risk gauge (89/100 HIGH), 4-factor formula breakdown, and approved action buttons (`isolate-device`, `disable-session`).

<p align="center">
  <img src="assets/annotated/annotated_01_executive_console.png" alt="Executive Console" width="95%" />
</p>

---

### 2. Chronological Attack Timeline
Reconstructs the attack across 4 discrete stages strictly preserving timestamp monotonicity:
1. **Stage 1 (09:41:12 UTC):** Initial Access via VPN from Bucharest (`evt-003`).
2. **Stage 2 (09:48:33 – 09:50:14 UTC):** Sensitive Resource Collection of payroll & M&A files (`evt-008`, `evt-009`).
3. **Stage 3 (09:52:05 – 09:55:02 UTC):** Removable Media Transfer to USB (`evt-011`, `evt-012`, `evt-013`).
4. **Stage 4 (09:58:45 UTC):** Outbound Network Exfiltration (`evt-015`).

<p align="center">
  <img src="assets/annotated/annotated_02_attack_timeline.png" alt="Attack Timeline" width="95%" />
</p>

---

### 3. Interactive SVG Entity-Relational Graph
Visualizes the 28-node correlated subgraph with dynamic node highlighting, stage filtering, and physics controls.

<p align="center">
  <img src="assets/annotated/annotated_03_entity_graph.png" alt="Entity Graph" width="95%" />
</p>

---

### 4. Forensic Evidence Drawer (Rule #2 Proof)
Clicking any stage card opens the slide-over drawer displaying exact event IDs, raw telemetry JSON, access masks, and timestamps.

<p align="center">
  <img src="assets/annotated/annotated_04_evidence_drawer.png" alt="Evidence Drawer" width="95%" />
</p>

---

### 5. Bounded AI Copilot & Anti-Hallucination Guard
Displays evidence-bounded analyst briefing, green "EVIDENCE VALIDATION PASSED" seal, and built-in evaluator buttons to inject fake event IDs or unauthorized actions to witness real-time verifier interception.

<p align="center">
  <img src="assets/annotated/annotated_05_copilot_verified.png" alt="AI Copilot" width="95%" />
</p>

---

### 6. Replay Lab & Evaluator Benchmarking
Allows evaluators to re-run benchmark datasets from a clean state in under 2 seconds:
- **Canonical Attack:** 1 incident promoted, Risk 89.
- **Benign Admin Noise:** 0 incidents promoted, 2 suppressed.
- **Partial Attack:** 1 incident promoted, Risk 76.

<p align="center">
  <img src="assets/annotated/annotated_06_replay_lab.png" alt="Replay Lab" width="95%" />
</p>

---

### 7. False-Positive Suppression Audit Ledger
Logs all suppressed noise clusters with full audit trails, preserving quiet SOC queues while maintaining compliance.

<p align="center">
  <img src="assets/annotated/annotated_07_suppression_ledger.png" alt="Suppression Ledger" width="95%" />
</p>

---

## 📊 Sample Input & Output Trace

### Representative Input Event (`data/scenarios/attack_insider_usb.jsonl`)
```json
{
  "event_id": "evt-008",
  "timestamp": "2026-10-06T09:48:33Z",
  "source": "windows",
  "event_type": "file_access",
  "action": "read",
  "user_id": "user-42",
  "device_id": "device-17",
  "resource": "Finance/Q4/payroll.xlsx",
  "application": "explorer.exe",
  "attributes": {
    "share_path": "\\\\corp-fs01\\Finance\\Q4\\payroll.xlsx",
    "access_mask": "0x120089",
    "file_extension": "xlsx"
  }
}
```

### Generated Output Incident Object (`/api/incidents/inc-001`)
```json
{
  "incident_id": "inc-001",
  "title": "Multi-Stage Insider Exfiltration: user-42",
  "severity": "HIGH",
  "risk_score": 89,
  "confidence": 0.94,
  "start_time": "2026-10-06T09:41:12Z",
  "end_time": "2026-10-06T09:58:45Z",
  "actor_id": "user-42",
  "device_id": "device-17",
  "stages": [
    {
      "stage_id": "stage-01",
      "stage_name": "initial_access",
      "start_time": "2026-10-06T09:41:12Z",
      "end_time": "2026-10-06T09:41:12Z",
      "evidence_event_ids": ["evt-003"]
    },
    {
      "stage_id": "stage-02",
      "stage_name": "resource_collection",
      "start_time": "2026-10-06T09:48:33Z",
      "end_time": "2026-10-06T09:50:14Z",
      "evidence_event_ids": ["evt-008", "evt-009"]
    },
    {
      "stage_id": "stage-03",
      "stage_name": "removable_media_transfer",
      "start_time": "2026-10-06T09:52:05Z",
      "end_time": "2026-10-06T09:55:02Z",
      "evidence_event_ids": ["evt-011", "evt-012", "evt-013"]
    },
    {
      "stage_id": "stage-04",
      "stage_name": "exfiltration",
      "start_time": "2026-10-06T09:58:45Z",
      "end_time": "2026-10-06T09:58:45Z",
      "evidence_event_ids": ["evt-015"]
    }
  ],
  "recommended_actions": [
    "isolate-device",
    "disable-session",
    "review-resource-access"
  ]
}
```

---

## 📌 Scope Note: MVP vs. Stretch Goals

As required by **Page 3 of the HackNex Submission Guidelines**:

| Feature / Capability | Implementation Scope | Status | Notes |
| :--- | :---: | :---: | :--- |
| **Multi-Source Log Ingestion & Normalization** | **MVP** | **Implemented** | CanonicalEvent-v1 schema with quarantine queue. |
| **Cross-Entity Correlation (User, Device, IP, App, USB)** | **MVP** | **Implemented** | TemporalSequenceCorrelator & NetworkX graph. |
| **Chronological Step-by-Step Attack Reconstruction** | **MVP** | **Implemented** | 4 discrete stages with monotonic timestamp validation. |
| **Proof for Every Stage (Real Telemetry Citations)** | **MVP** | **Implemented** | Every stage backed by immutable event IDs in evidence drawer. |
| **Rule #1 False-Positive Suppression Gate** | **MVP** | **Implemented** | 0 FP incidents on benign admin baseline; suppression ledger active. |
| **Explainable 4-Factor Risk Engine (0–100)** | **MVP** | **Implemented** | 35% Signal, 30% Sequence, 20% Novelty, 15% Anomaly. |
| **Bounded Anti-Hallucination AI Copilot** | **MVP** | **Implemented** | Schema verifier intercepting ungrounded events/actions. |
| **High-Density Next.js 16 SOC Interface** | **MVP** | **Implemented** | Radial risk gauge, SVG graph, drawer, replay lab. |
| **Multivariate Statistical Anomaly Scorer** | **MVP** | **Implemented** | RobustAnomalyScorer z-score deviations across 6 features. |
| **Slow, Multi-Week Low-and-Slow Campaign Tracking** | **Stretch** | **Documented** | Identified in PS03 as advanced stretch; requires cross-month time sliding. |

---

## 📦 Tech Stack & Declared Resources

Under the HackNex **"Declare Your Resources"** rule, all dependencies are fully disclosed:

### Backend Core & Engine (Python 3.11+)
- **FastAPI (0.115.6) & Uvicorn (0.34.0):** Asynchronous REST API framework.
- **Pydantic (2.10.4):** Strict data contract validation for CanonicalEvent-v1.
- **NetworkX (3.4.2):** Bipartite entity-event graph topology and subgraph extraction.
- **NumPy (2.2.1) & Pandas (2.2.3):** Numerical baseline modeling and multivariate $z$-score statistics.
- **PyYAML (6.0.2):** Declarative detection rule parsing.
- **SQLite (Pure-Python):** Local embedded persistence for incidents and suppression audits.
- **Pytest (9.1.1):** Automated testing framework (42 tests).

### Frontend Analyst Console (Next.js 16)
- **Next.js 16.1.6 (React 19, TypeScript):** High-density SOC interface.
- **Tailwind CSS v4:** Bespoke dark SOC telemetry design system.
- **Lucide React (0.475.0):** Specialized security operations iconography.
- **Native SVG:** Interactive entity graph rendering with zero external charting bloat.

### Telemetry Provenance
- `attack_insider_usb.jsonl` (15 events) — Team-generated synthetic canonical attack.
- `benign_admin.jsonl` (10 events) — Team-generated synthetic negative control.
- `attack_partial.jsonl` (7 events) — Team-generated partial degradation scenario.
- `malformed_logs.jsonl` (8 records) — Team-generated quarantine test fixture.
- **Public Datasets Used:** **NONE.** Current MVP uses team-generated deterministic synthetic telemetry with verified SHA-256 hashes.

---

## 🚀 Quick Start & Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### ⚡ Option A: 1-Click Launch (Windows)
Double-click or run from terminal:
```cmd
run.bat
```
This automatically initializes the virtual environment, starts the FastAPI backend (`:8000`), starts the Next.js frontend (`:3000`), and opens `http://localhost:3000` in your browser.

To gracefully stop all services:
```cmd
stop.bat
```

---

### 🛠️ Option B: Manual Setup

#### 1. Backend Server
```bash
cd backend
python -m venv .venv

# Windows:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation available at: `http://127.0.0.1:8000/docs`

#### 2. Frontend Console
```bash
cd frontend
npm install
npm run dev
```
Analyst Console available at: `http://localhost:3000`

---

## 🧪 How to Reproduce Demonstrated Results

### 1. Run Automated Test Suite (42 Tests)
```bash
# Run complete test suite (unit, integration, verifier, negative controls)
pytest backend/tests
```
Expected output: **42 passed in ~1.5 seconds (100% pass rate)**.

### 2. Run Headless Evaluator Verification Script
```bash
python scripts/run_demo.py
```
This automated runner executes the entire pipeline headless:
1. Ingests canonical attack $\to$ verifies 1 incident, 4 stages, Risk 89.
2. Ingests benign noise $\to$ verifies 0 incidents promoted, 2 suppressed clusters.
3. Tests Copilot verifier with fake event `evt-fake-9999` $\to$ verifies interception.

### 3. Run One-Click Verification Batch
```cmd
verify.bat
```

---

## 📑 Presentation Deck & Submission Links

- **PowerPoint Presentation Deck:** [`ThreatWeave_HackNex_Presentation.pptx`](ThreatWeave_HackNex_Presentation.pptx)  
  *12 professional 16:9 widescreen slides with embedded annotated screenshots and complete speaker notes for evaluation pitch.*
- **Official Compliance Matrix:** [`docs/PS03_COMPLIANCE_MATRIX.md`](docs/PS03_COMPLIANCE_MATRIX.md)
- **Dataset Audit Report:** [`docs/DATASET_AUDIT.md`](docs/DATASET_AUDIT.md)
- **Evidence Traceability Report:** [`docs/PS03_EVIDENCE_TRACE.md`](docs/PS03_EVIDENCE_TRACE.md)
- **Final Evaluation Scorecard:** [`docs/PS03_FINAL_SCORECARD.md`](docs/PS03_FINAL_SCORECARD.md)
- **Official GitHub Repository:** [https://github.com/jeromeprince777/Hacknex_PSI03-AI-Powered-Cyber-Threat-Intelligence_Mark-IV-302-.git](https://github.com/jeromeprince777/Hacknex_PSI03-AI-Powered-Cyber-Threat-Intelligence_Mark-IV-302-.git)
