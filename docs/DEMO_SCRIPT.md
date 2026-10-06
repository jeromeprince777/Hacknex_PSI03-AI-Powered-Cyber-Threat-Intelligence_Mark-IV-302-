# THREATWEAVE — 3-Minute Qualifier Demo Script

## 0:00 — Problem

“Security logs rarely look like an attack one line at a time. ThreatWeave connects events across users, devices, IPs and applications and reconstructs the attack chain.”

---

## 0:20 — Raw event view

Show the dataset replay.

Say:

“Here we have normal activity mixed with a sequence that should not be looked at independently.”

---

## 0:35 — Incident detection

Run analysis.

Show:
- one high-risk incident;
- Risk Index;
- involved user/device/IP.

Say:

“Instead of producing five disconnected alerts, the engine promotes the related signals into one evidence-backed incident.”

---

## 0:50 — Timeline

Show the timeline.

Highlight:

1. unusual login relationship;
2. sensitive/unusual resource access;
3. USB connection/copy.

Say:

“The order is preserved from the actual event timestamps.”

---

## 1:15 — Graph

Show the entity graph.

Say:

“The graph makes the correlation explicit: the same user connects the authentication event to the device, accessed resource and removable device.”

---

## 1:35 — Evidence

Click each stage.

Say:

“Every stage has proof. When I click a stage, these are the exact event IDs and source records that support it.”

This is one of the most important moments.

---

## 1:55 — Risk explanation

Show the score breakdown.

Say:

“This is not a magic probability. It is a Risk Index composed of signal strength, sequence consistency, entity novelty and statistical anomaly.”

---

## 2:10 — False-positive control

Switch to benign dataset.

Say:

“Now we replay routine administrator activity. We may still see individual signals, but the chain does not meet our promotion requirements, so we do not raise a high-confidence incident.”

---

## 2:30 — AI copilot

Ask:

> “Why is this incident high risk?”

Show verified response.

Say:

“The AI does not decide what happened. It receives a bounded evidence pack and can only reference evidence IDs that exist. The verifier rejects unsupported references.”

---

## 2:50 — Close

“ThreatWeave is designed around one principle: no evidence, no claim. That makes the output useful to an analyst and auditable to an evaluator.”

