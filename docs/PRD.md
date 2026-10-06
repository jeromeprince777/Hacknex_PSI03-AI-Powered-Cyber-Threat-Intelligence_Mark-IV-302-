# THREATWEAVE — Product Requirements Document (PRD)

**HackNex 2026 Internal Qualifier — HNX26PSI03: AI-Powered Cyber Threat Intelligence**  
**Product type:** Evidence-first cyber threat investigation and attack-chain reconstruction system  
**Working name:** ThreatWeave  
**Primary goal:** Reconstruct coordinated attacks from security logs across users, devices, IPs and applications while minimizing false alarms and showing proof for every stage.

---

## 1. Product North Star

ThreatWeave should make a messy pile of security events answer one operational question:

> **“What happened, who/what was involved, how did the attack progress, what proves each stage, how risky is it, and what should an analyst do next?”**

The product must prefer **verifiable evidence over impressive language**.

A detection is not considered valid merely because an AI model says it looks malicious. A stage must point to one or more real events. A chain must be built from correlated events in time and across shared entities.

---

## 2. Problem

Security systems generate large volumes of authentication, endpoint, file, application and network logs. Individual events can look harmless, while the combination of events can reveal a coordinated attack.

The qualifier specifically asks teams to connect events across users, devices, IP addresses and applications, reconstruct the attack step-by-step, show a timeline, identify stages, provide proof for each stage, estimate risk, and recommend action.

The evaluation also explicitly penalizes excessive false alarms and unsupported claims.

---

## 3. Target Users

### Primary
**Security analyst / SOC analyst**
- Investigates suspicious activity.
- Needs fast attack reconstruction.
- Needs evidence that can be audited.

### Secondary
**Security lead / incident responder**
- Wants a compact incident case view.
- Needs prioritized risk and recommended response actions.

### Demo/evaluator
- Needs to see the full reasoning path from raw log → correlation → attack chain → evidence → risk → action.

---

## 4. Product Scope

### MVP — mandatory for the 24-hour qualifier

1. Ingest security logs from JSONL/CSV.
2. Normalize different event formats into one internal schema.
3. Create entities for:
   - users
   - devices
   - IP addresses
   - applications
   - files/resources
4. Build an event/entity graph.
5. Detect one known multi-stage attack.
6. Correlate events into an ordered attack chain.
7. Show an incident timeline.
8. Identify attack stages.
9. Attach evidence event IDs to every stage.
10. Calculate a risk score with an explainable component breakdown.
11. Suppress weak/isolated signals to reduce false positives.
12. Show recommended actions from a controlled action library.
13. Provide an AI analyst explanation grounded only in retrieved evidence.
14. Include at least one benign scenario demonstrating that the system stays quiet.
15. Include a replayable seeded demo dataset.
16. Provide README + setup + reproduction instructions.

### Stretch

- Multiple simultaneous incidents.
- Additional attack patterns.
- Cross-host lateral movement.
- Long-running / low-and-slow chains.
- Analyst feedback loop.
- ATT&CK-style technique mapping.
- Natural-language investigation queries.
- Real-time streaming.
- External threat-intelligence enrichment.
- Persistent case management.

---

## 5. Core User Journey

### Journey A — SOC triage

1. Analyst opens dashboard.
2. Dashboard shows current incidents and signal volume.
3. Analyst opens a high-risk incident.
4. ThreatWeave displays:
   - risk score
   - attack summary
   - timeline
   - entity graph
   - stage cards
   - evidence
   - recommended actions
5. Analyst clicks a stage.
6. UI highlights the exact supporting events.
7. Analyst clicks an event.
8. UI displays the raw source log and normalized representation.
9. Analyst asks the Copilot why the incident is high risk.
10. Copilot answers only using the evidence pack.

### Journey B — Benign activity

1. Analyst loads a clean dataset.
2. Normal admin activity generates some low-level signals.
3. ThreatWeave should not create a high-confidence attack chain.
4. Dashboard shows suppressed/low-risk signals and why they were not escalated.

---

## 6. Product Principles

### Principle 1 — Evidence before explanation
Every claim must reference event IDs.

### Principle 2 — Correlation before escalation
A single odd event should normally remain a signal, not an attack.

### Principle 3 — Deterministic core, bounded AI
The detection engine determines facts. The LLM may summarize, organize, and recommend from a controlled evidence set. It must not invent facts.

### Principle 4 — Silence is a feature
A clean dataset should produce few or no high-severity incidents.

### Principle 5 — Every score is inspectable
The UI should expose the factors contributing to risk.

### Principle 6 — Reproducible demo
One command should load the same dataset and reproduce the same incident.

---

## 7. Functional Requirements

### FR-01: Log ingestion
The system shall accept normalized and raw sample security logs in JSONL or CSV.

### FR-02: Validation
Invalid events shall be rejected or quarantined with a visible validation reason.

### FR-03: Normalization
The system shall map raw sources to a canonical event schema.

### FR-04: Entity extraction
The system shall extract user, device, source IP, destination IP, application, resource/file and session identifiers when present.

### FR-05: Correlation
Events sharing meaningful entity relationships and occurring within configurable time windows shall be correlated.

### FR-06: Stage detection
The engine shall classify supported event patterns into attack stages.

### FR-07: Sequence detection
Supported stage transitions shall form attack-chain candidates.

### FR-08: Evidence
Every stage and chain transition shall include references to source event IDs.

### FR-09: Risk scoring
Each incident shall have a 0–100 risk score plus a factor breakdown.

### FR-10: False-positive suppression
The engine shall avoid escalating isolated low-confidence signals and shall require configurable correlation evidence for a high-confidence incident.

### FR-11: Timeline
Events shall be displayed in time order with stage markers.

### FR-12: Graph
The graph shall show relevant entities and relationships only; unrelated events should be filterable away.

### FR-13: Recommended response
The engine shall map detected stages to predefined response actions.

### FR-14: AI explanation
The AI layer shall receive only the evidence pack and structured incident facts.

### FR-15: Hallucination guard
Any AI evidence reference not present in the supplied evidence pack shall be rejected by the verifier.

### FR-16: Reproducibility
A seeded attack dataset shall reproduce the same incident chain and risk components.

### FR-17: Audit trail
The UI/API shall expose which detector/rule produced each signal and when the analysis was run.

---

## 8. Non-Functional Requirements

### Reliability
- No frontend crash on malformed input.
- Backend returns structured errors.
- Detection output is deterministic for a fixed dataset and configuration.

### Explainability
- No alert without a reason.
- No attack stage without evidence.
- Risk score must expose components.

### Performance
Target for the demo:
- Load 10k–50k sample events in a few seconds locally.
- Incident investigation page should render the selected chain quickly.
- Detection pipeline should be suitable for repeated replay.

### Security
- Never execute values from logs as code.
- Sanitize HTML/log rendering.
- API keys must be environment variables.
- Do not send raw logs to an LLM unless explicitly configured.
- Redact secrets/tokens/password-like fields before AI processing.

### Usability
- The primary incident story should be understandable in under 60 seconds.
- Evidence should be one click away.
- Colors/icons must not be the only indication of severity.

---

## 9. Success Criteria

ThreatWeave is successful when a reviewer can take one seeded attack and answer all of these from the UI:

1. Who is involved?
2. Which device(s)?
3. Which IP(s)?
4. Which application(s)?
5. What happened first?
6. What happened next?
7. Which attack stages were detected?
8. What proves each stage?
9. Why is the chain risky?
10. What should be done now?
11. Why was benign activity not escalated?

---

## 10. Primary Demo Attack

Use the qualifier's own style of scenario as the canonical demo:

**Stage 1 — unusual authentication**
- User logs in from a previously unseen location/IP.

**Stage 2 — unusual resource access**
- Same user accesses files/resources they have not previously touched.

**Stage 3 — removable-media transfer**
- The user copies selected resources to a USB/removable device.

ThreatWeave should correlate these through the same user and relevant device/session context and show a single ordered incident instead of three unrelated alerts.

Add a fourth event as an optional enrichment:
- outbound connection after the local collection/copy action.

---

## 11. Risk Model

Do not pretend the score is a probability.

Use a deterministic **Risk Index (0–100)**.

Recommended MVP formula:

`Risk = clamp(100 * (0.35 * SignalScore + 0.30 * SequenceScore + 0.20 * EntityNovelty + 0.15 * AnomalyScore))`

Where:
- **SignalScore:** weighted severity of observed event patterns.
- **SequenceScore:** strength of supported stage transitions.
- **EntityNovelty:** unusual user/device/IP/resource relationship.
- **AnomalyScore:** normalized statistical outlier signal.

Display all four components.

Example:
- SignalScore = 0.86
- SequenceScore = 0.92
- EntityNovelty = 0.78
- AnomalyScore = 0.71
- Risk Index = 84

Label the result:
- 0–24: Informational
- 25–49: Low
- 50–74: Medium
- 75–100: High

The thresholds are product configuration, not universal security standards.

---

## 12. False Positive Strategy

A detection should have three levels:

### Signal
A potentially interesting event.

### Cluster
Multiple related signals connected by user/device/IP/app/resource.

### Incident
A sufficiently strong multi-stage chain.

Suggested escalation rule for MVP:

`Incident = at least 3 evidence events + at least 2 distinct stages + meaningful entity link + sequence consistency`

Allow a small number of critical-event overrides only when explicitly defined in code.

This is deliberately conservative because the qualifier states that too many false alarms can cap the score.

---

## 13. AI Guardrails

The LLM is not the source of truth.

### Allowed
- Summarize verified facts.
- Explain the score using supplied factors.
- Select from approved response actions.
- Write a human-readable incident report.
- Ask for clarification when evidence is insufficient.

### Not allowed
- Invent timestamps.
- Invent IPs/users/devices.
- Invent evidence IDs.
- Claim a stage without evidence.
- Create new response actions outside the approved action library.
- Turn uncertainty into certainty.
- Infer facts that were not retrieved.

### Required AI output

```json
{
  "summary": "string",
  "confidence": "low|medium|high",
  "stage_explanations": [
    {
      "stage_id": "stage-1",
      "explanation": "string",
      "evidence_event_ids": ["evt-001", "evt-002"]
    }
  ],
  "recommended_actions": [
    {
      "action_id": "isolate-device",
      "reason": "string"
    }
  ],
  "limitations": ["string"]
}
```

The verifier rejects output if:
- an event ID does not exist,
- a stage ID does not exist,
- an action ID does not exist,
- the explanation contradicts verified facts.

---

## 14. Key Screens

### Dashboard
- incident count
- high-risk incidents
- unresolved incidents
- event volume
- false-positive / suppression summary
- recent incidents

### Incident detail
- score + factor breakdown
- attack summary
- timeline
- entity graph
- attack stages
- evidence drawer
- recommended actions
- AI analyst explanation
- analysis metadata

### Evidence drawer
- event ID
- timestamp
- source
- raw log
- normalized event
- detector reason
- linked entities

### Data replay
- dataset selector
- event count
- run detection
- run comparison
- clean vs attack scenario

---

## 15. MVP Out of Scope

Do not attempt during the 24-hour build:
- full SIEM replacement
- live enterprise log ingestion
- autonomous remediation that changes machines
- real credential collection
- exploit execution
- offensive security operations
- broad threat-intelligence crawling
- training a custom deep-learning cybersecurity model from scratch

---

## 16. Release Definition

The MVP is done when:
- a fresh clone starts successfully;
- the seeded dataset loads;
- the canonical attack is detected;
- the three attack stages are shown;
- every stage points to evidence;
- timeline and graph agree with the underlying events;
- risk score is reproducible;
- clean logs do not create a high-confidence incident;
- AI explanation passes evidence validation;
- README can reproduce the demo.

