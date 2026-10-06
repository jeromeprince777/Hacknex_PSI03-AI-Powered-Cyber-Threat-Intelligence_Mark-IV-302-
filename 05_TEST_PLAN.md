# THREATWEAVE — Test Plan & Acceptance Criteria

## 1. Test Philosophy

The qualifier cares about:
- attack-chain correctness;
- false-positive control;
- entity correlation;
- timeline accuracy;
- explainability;
- evidence for every stage.

Tests therefore focus on **behavior**, not only code coverage.

---

## 2. Golden Dataset

Create a fixed scenario file:

`data/scenarios/attack_insider_usb.jsonl`

Required semantic sequence:

```text
T1: user login from first-seen location
T2: unusual access to sensitive resource
T3: USB/removable device connection
T4: resource copied to removable device
```

Optional:
```text
T5: outbound transfer
```

Expected:
- exactly one primary incident;
- ≥3 detected stages for T1–T4;
- evidence IDs point to the correct events;
- events appear in timestamp order;
- the same user is linked throughout;
- relevant device/IP/resource nodes are shown.

---

## 3. Benign Dataset

`data/scenarios/benign_admin.jsonl`

Include:
- routine login from known location;
- routine file access;
- routine backup operation;
- administrator maintenance;
- known device usage.

Expected:
- no high-confidence incident;
- isolated signals may exist;
- suppression reasons are visible.

---

## 4. Unit Tests

### Normalization
- missing optional field;
- malformed timestamp;
- unknown source field;
- duplicate event ID.

### Rule engine
- each rule fires on positive example;
- rule does not fire on near-miss benign event.

### Novelty
- first-seen relationship scores novel;
- known relationship scores low novelty.

### Sequence
- correct event order forms a sequence;
- reversed order does not form the canonical attack;
- missing middle stage reduces score.

### Evidence
- every stage has event IDs;
- nonexistent event ID is rejected.

### Risk
- same inputs produce same risk;
- score always 0–100;
- weights sum to 1.

### Copilot verifier
- unknown evidence ID rejected;
- unknown stage ID rejected;
- unknown action ID rejected;
- valid output accepted.

---

## 5. Integration Tests

### Test 01 — Full attack replay

```text
ingest → normalize → detect → correlate → score → store → API → UI
```

Expected:
- incident exists;
- UI loads it;
- timeline and graph contain the same evidence.

### Test 02 — Clean replay

Expected:
- no high-severity incident.

### Test 03 — Partial attack

Remove USB copy event.

Expected:
- incident risk falls;
- removable-media stage disappears;
- system does not falsely claim completed transfer.

### Test 04 — Conflicting timestamps

Expected:
- invalid data warning;
- no fabricated order.

---

## 6. Frontend Acceptance Tests

Use Playwright.

### Dashboard
- loads without console errors;
- incident count renders;
- high-risk incident appears.

### Incident page
- risk index visible;
- timeline visible;
- graph visible;
- each stage shows evidence;
- evidence drawer opens;
- raw and normalized event data are distinguishable.

### Copilot
- explanation loads;
- evidence references are clickable;
- invalid model output is not displayed as verified.

### Responsive
- desktop layout works;
- laptop width remains usable;
- graph can be inspected without clipping.

---

## 7. False Positive Gate

Before final demo, run:

```text
Scenario A: attack
Scenario B: benign
Scenario C: near-miss benign
Scenario D: partial attack
```

Record:

| Scenario | Expected | Actual | Result |
|---|---|---|---|
| Attack | 1 high-risk incident |  |  |
| Benign | 0 high-risk |  |  |
| Near-miss | 0 high-risk |  |  |
| Partial | degraded/partial chain |  |  |

Do not tune rules against the exact evaluator data.

---

## 8. “No Hallucination” Acceptance Tests

The UI must not display a verified AI explanation when:
- evidence ID is unknown;
- evidence is attached to another incident;
- timestamp contradicts timeline;
- AI introduces an entity that does not exist.

For a failed verification:
```text
AI explanation status: Rejected
Reason: Evidence reference validation failed
```

This is more credible than pretending the AI is perfect.

---

## 9. Regression Checklist

Before submission:
- `pytest` passes.
- frontend build passes.
- backend starts.
- seeded data loads.
- Playwright smoke tests pass.
- no console errors.
- no broken network calls.
- demo path works from a fresh clone.
