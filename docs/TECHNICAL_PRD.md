# THREATWEAVE — Detailed Technical PRD

## 1. Architecture Decision

Use a **hybrid evidence-first architecture**:

```text
                ┌─────────────────────────┐
                │     Next.js Frontend    │
                │ Dashboard / Case / Graph│
                └────────────┬────────────┘
                             │ REST/JSON
                ┌────────────▼────────────┐
                │      FastAPI Backend    │
                │ ingestion / analysis API│
                └──────┬────────┬─────────┘
                       │        │
          ┌────────────▼──┐  ┌──▼──────────────────┐
          │ Deterministic │  │ Statistical anomaly │
          │ detection core│  │ scorer               │
          │ rules + graph │  │ Isolation Forest     │
          └───────┬───────┘  └──────────┬───────────┘
                  │                     │
                  └──────────┬──────────┘
                             ▼
                   ┌────────────────────┐
                   │ Incident/Evidence  │
                   │ canonical objects  │
                   └─────────┬──────────┘
                             │
                      bounded context
                             ▼
                   ┌────────────────────┐
                   │ Analyst Copilot LLM │
                   │ explain/summarize   │
                   └─────────┬──────────┘
                             │
                       schema verifier
                             ▼
                   ┌────────────────────┐
                   │ Verified AI output  │
                   └────────────────────┘
```

### Recommended stack

**Frontend**
- Next.js + TypeScript
- Tailwind CSS
- shadcn/ui
- Cytoscape.js or React Flow for graph visualization
- lightweight chart library for risk/signal views

**Backend**
- Python + FastAPI
- Pydantic
- NetworkX
- scikit-learn
- pandas
- SQLite for MVP persistence

**Testing**
- pytest
- Playwright

**Optional**
- Supabase/Postgres only if the team already has a working connection and wants hosted persistence.
- Vercel for frontend deployment after the local MVP is stable.

The 24-hour priority is a reliable local demo, not infrastructure complexity.

---

## 2. Repository Layout

```text
threatweave/
├── README.md
├── AGENTS.md
├── .env.example
├── docker-compose.yml              # optional
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── incidents/
│   │   ├── datasets/
│   │   └── api/
│   ├── components/
│   │   ├── IncidentHeader.tsx
│   │   ├── AttackTimeline.tsx
│   │   ├── EntityGraph.tsx
│   │   ├── EvidencePanel.tsx
│   │   ├── RiskBreakdown.tsx
│   │   └── AnalystCopilot.tsx
│   └── lib/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes_ingest.py
│   │   │   ├── routes_analysis.py
│   │   │   ├── routes_incidents.py
│   │   │   └── routes_copilot.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── detectors/
│   │   │   ├── rules.py
│   │   │   ├── sequence.py
│   │   │   ├── novelty.py
│   │   │   └── anomaly.py
│   │   ├── graph/
│   │   │   └── builder.py
│   │   ├── scoring/
│   │   │   └── risk.py
│   │   ├── evidence/
│   │   │   └── pack.py
│   │   ├── copilot/
│   │   │   ├── prompt.py
│   │   │   └── verifier.py
│   │   └── storage/
│   │       └── repository.py
│   └── tests/
├── data/
│   ├── raw/
│   ├── normalized/
│   ├── scenarios/
│   │   ├── attack_insider_usb.jsonl
│   │   ├── benign_admin.jsonl
│   │   └── attack_credential_chain.jsonl
│   └── schema/
├── configs/
│   ├── detection_rules.yaml
│   ├── thresholds.yaml
│   └── response_actions.yaml
├── scripts/
│   ├── seed_demo.py
│   ├── normalize_logs.py
│   └── run_demo.py
├── docs/
│   ├── PRD.md
│   ├── TECHNICAL_PRD.md
│   ├── AGENT_RULES.md
│   ├── TEST_PLAN.md
│   └── DEMO_SCRIPT.md
└── artifacts/
    └── screenshots/
```

---

## 3. Canonical Event Schema

Every input record must become this shape:

```json
{
  "event_id": "evt-000123",
  "timestamp": "2026-10-06T09:41:12Z",
  "event_type": "file_access",
  "source": "windows",
  "action": "read",
  "user_id": "user-42",
  "device_id": "device-17",
  "src_ip": "10.10.4.20",
  "dst_ip": null,
  "application": "FileExplorer",
  "resource": "Finance/Q4/payroll.xlsx",
  "session_id": "sess-883",
  "attributes": {},
  "raw": {}
}
```

### Required fields
- event_id
- timestamp
- event_type
- source

### Strongly recommended identity fields
- user_id
- device_id
- src_ip
- dst_ip
- application
- resource
- session_id

### Attributes
Use a dictionary for source-specific properties:
- login_location
- device_trust
- removable_media_id
- bytes
- auth_result
- process_name
- command_hash

Never assume an optional field exists.

---

## 4. Event Types for MVP

Keep the first implementation intentionally narrow:

### Authentication
- login_success
- login_failure
- privilege_grant

### Resource/File
- file_access
- archive_created
- sensitive_resource_access

### Device
- usb_connected
- usb_copy

### Network
- outbound_connection
- large_transfer

### Application/Endpoint
- process_start
- suspicious_command

This is enough to construct the canonical scenario and demonstrate entity correlation.

---

## 5. Normalization Pipeline

```text
raw record
  → parse
  → field mapping
  → timestamp normalization
  → identity normalization
  → event type classification
  → validation
  → canonical event
  → persistence
```

### Rules
- Never silently drop required information.
- Preserve the original raw record.
- Store `normalization_warnings`.
- Record the source adapter.

---

## 6. Entity Graph

### Node types
- User
- Device
- IP
- Application
- Resource
- RemovableDevice
- Session
- Incident

### Edge examples
```text
User ─AUTHENTICATED_FROM─> IP
User ─USED─> Device
Device ─GENERATED─> Event
User ─ACCESSED─> Resource
User ─RAN─> Application
Device ─CONNECTED_TO─> RemovableDevice
Event ─SUPPORTS─> Stage
Stage ─BELONGS_TO─> Incident
```

### Graph filtering
Do not render every entity in the entire dataset.
For an incident:
1. start with incident evidence events;
2. include their direct entities;
3. include one-hop relationships;
4. allow expansion on click.

This keeps the graph readable.

---

## 7. Deterministic Detection Engine

### Detector layers

#### Layer A — Atomic signals
Each rule emits:

```json
{
  "signal_id": "sig-017",
  "event_id": "evt-011",
  "signal_type": "new_login_location",
  "stage": "initial_access",
  "weight": 0.55,
  "reason_code": "AUTH_NEW_LOCATION",
  "parameters": {
    "new_location": "..."
  }
}
```

#### Layer B — Entity novelty
Calculate whether a relationship is unusual for the observed baseline.

Examples:
- first-seen user→country
- first-seen user→device
- first-seen user→resource
- first-seen device→USB

Use a known baseline period in the seeded demo.

#### Layer C — Sequence correlation
Match supported stage transitions inside configurable windows.

Canonical sequence:

```text
new_login_location
        ↓
unusual_resource_access
        ↓
usb_copy
        ↓
(optional) outbound_transfer
```

#### Layer D — anomaly score
Use Isolation Forest or robust standardized deviation over a compact feature vector.

Features can include:
- login novelty
- resource novelty count
- file count
- transfer volume
- events per session
- new device relation
- new IP relation
- time-of-day deviation

Normalize to 0–1.

The anomaly model is a supporting signal, not the sole reason for an incident.

---

## 8. Attack Chain Construction

A chain object:

```json
{
  "incident_id": "inc-001",
  "status": "open",
  "risk_index": 84,
  "severity": "high",
  "entities": {
    "users": ["user-42"],
    "devices": ["device-17"],
    "ips": ["203.0.113.10"],
    "applications": ["FileExplorer"],
    "resources": ["Finance/Q4/payroll.xlsx"]
  },
  "stages": [
    {
      "stage_id": "stage-01",
      "name": "Initial access",
      "timestamp_start": "...",
      "timestamp_end": "...",
      "evidence_event_ids": ["evt-003"]
    },
    {
      "stage_id": "stage-02",
      "name": "Resource discovery/collection",
      "timestamp_start": "...",
      "timestamp_end": "...",
      "evidence_event_ids": ["evt-008", "evt-009"]
    },
    {
      "stage_id": "stage-03",
      "name": "Removable-media transfer",
      "timestamp_start": "...",
      "timestamp_end": "...",
      "evidence_event_ids": ["evt-011", "evt-012"]
    }
  ]
}
```

---

## 9. Risk Calculation

Each component returns a normalized 0–1 value and explanation.

```python
risk_index = round(
    100 * (
        0.35 * signal_score +
        0.30 * sequence_score +
        0.20 * entity_novelty +
        0.15 * anomaly_score
    )
)
```

### Important implementation detail

The exact input values used for a score must be persisted with the incident:

```json
{
  "signal_score": 0.86,
  "sequence_score": 0.92,
  "entity_novelty": 0.78,
  "anomaly_score": 0.71,
  "weights": {
    "signal": 0.35,
    "sequence": 0.30,
    "novelty": 0.20,
    "anomaly": 0.15
  }
}
```

This makes the UI and README auditable.

---

## 10. Sequence Scoring

A simple explainable approach:

- stage match = +0.25
- valid temporal ordering = +0.15
- same user across stages = +0.20
- same device/session across stages = +0.15
- shared IP/context = +0.10
- multiple independent evidence events = +0.15

Cap at 1.0.

Do not claim this is a calibrated probability.

---

## 11. Baseline & Novelty

For MVP:
- baseline = prior events before the incident window;
- calculate seen relationships;
- classify first-seen relationships as novel.

Example:

```text
user-42 has accessed:
  HR/attendance.csv     48 times
  Finance/Q4/payroll.xlsx 0 times

Current event:
  user-42 → Finance/Q4/payroll.xlsx

Novelty = high
```

The baseline must be computed from the provided dataset, not invented.

---

## 12. False-Positive Suppression

Implement a `candidate → incident` promotion model.

```text
Signal
  |
  | weak/isolated
  v
Suppressed signal
```

```text
Signal + related signal
        |
        v
Cluster
        |
        | ≥ 3 evidence events
        | ≥ 2 stages
        | entity relationship
        | temporal consistency
        v
Incident
```

Store the reason for suppression:

```json
{
  "suppressed": true,
  "reason_code": "INSUFFICIENT_CHAIN_EVIDENCE",
  "missing_requirements": [
    "second_stage",
    "third_evidence_event"
  ]
}
```

This directly supports the qualifier's false-positive requirement.

---

## 13. Evidence Pack

Before calling the LLM, generate a strict evidence object:

```json
{
  "incident": {...},
  "timeline": [...],
  "stages": [...],
  "events": [...],
  "entities": [...],
  "risk_breakdown": {...},
  "approved_actions": [...]
}
```

No raw database queries should be exposed to the LLM.

---

## 14. Copilot Tool Contract

The Copilot can use only these backend functions:

```text
get_incident(incident_id)
get_incident_evidence(incident_id)
get_event(event_id)
get_related_entities(incident_id)
get_risk_breakdown(incident_id)
list_approved_actions()
```

Tool outputs are structured JSON.

### Copilot flow

```text
Question
  ↓
Intent classification
  ↓
Retrieve evidence
  ↓
Construct bounded evidence pack
  ↓
LLM structured response
  ↓
Schema validation
  ↓
Evidence-reference validation
  ↓
Contradiction check
  ↓
Display or reject
```

---

## 15. LLM Prompt Contract

System instruction:

```text
You are the ThreatWeave security analyst copilot.

You are not the source of truth.
The supplied evidence pack is the complete factual context for this response.

Rules:
1. Use only facts present in the evidence pack.
2. Every incident/stage claim must reference existing evidence_event_ids.
3. Never invent timestamps, users, devices, IPs, applications, resources, or actions.
4. Never create an evidence ID.
5. Never state a probability unless it is supplied by the evidence pack.
6. Use the term "Risk Index" for the displayed risk score.
7. Clearly state uncertainty when evidence is incomplete.
8. Recommended actions must use only action IDs in approved_actions.
9. If the evidence is insufficient, say "Insufficient evidence" and explain what is missing.
10. Return JSON matching the supplied schema.
```

---

## 16. AI Verification

Verification steps:
1. JSON schema validation.
2. All referenced event IDs exist.
3. All referenced stage IDs exist.
4. All action IDs exist.
5. Evidence is attached to the claimed stage.
6. No unknown entities are introduced.
7. Numeric score claims match stored score.
8. If any check fails, do not display the generated explanation as verified.

UI state:
- `Verified`
- `Rejected — requires review`

---

## 17. Response Action Library

Keep this controlled:

```yaml
actions:
  - id: isolate-device
    label: Isolate affected device
    stage_types: [removable_media_transfer, suspicious_endpoint]
  - id: disable-session
    label: Terminate suspicious session
    stage_types: [initial_access, credential_activity]
  - id: review-resource-access
    label: Review accessed resources
    stage_types: [resource_collection]
  - id: review-network-transfer
    label: Review outbound transfer
    stage_types: [exfiltration]
  - id: preserve-evidence
    label: Preserve affected logs and endpoint evidence
    stage_types: [all]
```

For a hackathon demo, these are **recommendations only**. Do not execute real remediation.

---

## 18. API

### `POST /api/datasets/ingest`
Input:
- file or JSON records

Output:
```json
{
  "dataset_id": "demo-attack-01",
  "accepted_events": 5000,
  "rejected_events": 3,
  "warnings": 2
}
```

### `POST /api/analysis/run`
```json
{
  "dataset_id": "demo-attack-01",
  "mode": "full"
}
```

### `GET /api/incidents`
Returns ranked incidents.

### `GET /api/incidents/{id}`
Returns incident + stages + risk + entities.

### `GET /api/incidents/{id}/evidence`
Returns stage-linked events.

### `POST /api/copilot/explain`
```json
{
  "incident_id": "inc-001",
  "question": "Why is this high risk?"
}
```

### `GET /api/health`
Must return service health.

---

## 19. Database Tables

### events
- event_id
- timestamp
- event_type
- source
- user_id
- device_id
- src_ip
- dst_ip
- application
- resource
- session_id
- attributes_json
- raw_json

### signals
- signal_id
- event_id
- signal_type
- stage
- weight
- reason_code
- parameters_json

### incidents
- incident_id
- status
- risk_index
- severity
- created_at
- analysis_version

### stages
- stage_id
- incident_id
- name
- start_time
- end_time
- sequence_index

### stage_evidence
- stage_id
- event_id

### incident_entities
- incident_id
- entity_type
- entity_id

### suppression_records
- id
- event/cluster reference
- reason_code
- details_json

---

## 20. Observability

Log every analysis with:
- dataset_id
- analysis_version
- rule_version
- number of events
- number of signals
- number of clusters
- number of incidents
- runtime_ms
- model name/version if AI is used

This helps the team explain exactly what happened during the demo.

---

## 21. Version Everything Important

Use explicit versions:

```text
analysis_version = "0.1.0"
rule_version = "demo-2026-01"
prompt_version = "copilot-v1"
schema_version = "event-v1"
```

Avoid changing scoring logic during the demo without recording the new version.

