# THREATWEAVE — Data, API & AI Contracts

## 1. Canonical Event JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ThreatWeaveEvent",
  "type": "object",
  "required": ["event_id", "timestamp", "event_type", "source"],
  "properties": {
    "event_id": {"type": "string"},
    "timestamp": {"type": "string", "format": "date-time"},
    "event_type": {"type": "string"},
    "source": {"type": "string"},
    "action": {"type": ["string", "null"]},
    "user_id": {"type": ["string", "null"]},
    "device_id": {"type": ["string", "null"]},
    "src_ip": {"type": ["string", "null"]},
    "dst_ip": {"type": ["string", "null"]},
    "application": {"type": ["string", "null"]},
    "resource": {"type": ["string", "null"]},
    "session_id": {"type": ["string", "null"]},
    "attributes": {"type": "object"},
    "raw": {"type": "object"}
  }
}
```

---

## 2. Signal Contract

```json
{
  "signal_id": "sig-001",
  "event_id": "evt-001",
  "signal_type": "new_login_location",
  "stage": "initial_access",
  "score": 0.55,
  "reason_code": "AUTH_NEW_LOCATION",
  "parameters": {
    "baseline_key": "user:user-42",
    "observed_value": "203.0.113.10",
    "baseline_match": false
  }
}
```

---

## 3. Incident Contract

```json
{
  "incident_id": "inc-001",
  "status": "open",
  "severity": "high",
  "risk_index": 84,
  "risk_components": {
    "signal_score": 0.86,
    "sequence_score": 0.92,
    "entity_novelty": 0.78,
    "anomaly_score": 0.71
  },
  "entity_ids": ["user-42", "device-17", "203.0.113.10"],
  "stage_ids": ["stage-001", "stage-002", "stage-003"],
  "evidence_event_ids": ["evt-003", "evt-008", "evt-011"],
  "analysis_version": "0.1.0",
  "rule_version": "demo-2026-01"
}
```

---

## 4. Stage Contract

```json
{
  "stage_id": "stage-001",
  "incident_id": "inc-001",
  "name": "Initial access",
  "sequence_index": 1,
  "start_time": "2026-10-06T09:41:12Z",
  "end_time": "2026-10-06T09:41:12Z",
  "evidence_event_ids": ["evt-003"],
  "reason_codes": ["AUTH_NEW_LOCATION"]
}
```

---

## 5. Evidence Contract

```json
{
  "event_id": "evt-003",
  "timestamp": "2026-10-06T09:41:12Z",
  "source": "vpn",
  "raw": {},
  "normalized": {},
  "detectors": [
    {
      "reason_code": "AUTH_NEW_LOCATION",
      "signal_type": "new_login_location"
    }
  ],
  "linked_entities": [
    "user-42",
    "device-17",
    "203.0.113.10"
  ]
}
```

---

## 6. Copilot Request/Response

### Request

```json
{
  "incident_id": "inc-001",
  "question": "Why is this incident high risk?"
}
```

### Evidence pack

```json
{
  "incident": {
    "incident_id": "inc-001",
    "risk_index": 84,
    "severity": "high"
  },
  "timeline": [
    {
      "event_id": "evt-003",
      "timestamp": "...",
      "stage_id": "stage-001",
      "fact": "Successful login with a first-seen relationship"
    }
  ],
  "stages": [],
  "approved_actions": []
}
```

### Required response

```json
{
  "summary": "The Risk Index is high because ...",
  "confidence": "high",
  "stage_explanations": [],
  "recommended_actions": [],
  "limitations": []
}
```

---

## 7. Verification Function

Pseudo-logic:

```python
def verify_copilot(output, evidence_pack):
    assert output["confidence"] in {"low", "medium", "high"}

    valid_events = {
        e["event_id"] for e in evidence_pack["timeline"]
    }

    valid_stages = {
        s["stage_id"] for s in evidence_pack["stages"]
    }

    valid_actions = {
        a["action_id"] for a in evidence_pack["approved_actions"]
    }

    for stage in output["stage_explanations"]:
        if stage["stage_id"] not in valid_stages:
            return False, "unknown_stage_id"

        for event_id in stage["evidence_event_ids"]:
            if event_id not in valid_events:
                return False, "unknown_evidence_event_id"

    for action in output["recommended_actions"]:
        if action["action_id"] not in valid_actions:
            return False, "unknown_action_id"

    return True, None
```

Never trust model output before verification.

