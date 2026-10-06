# THREATWEAVE — 24-Hour Hackathon Execution Plan

## Objective

Finish a **reliable, visually strong, evidence-first MVP** before adding ambitious features.

---

## Hour 0–1 — Lock scope

Deliver:
- product name;
- PRD accepted by team;
- architecture;
- event schema;
- attack scenario;
- benign scenario.

Use Antigravity:
```text
/plan
```

Then ask the agent to generate the repository skeleton only.

---

## Hour 1–3 — Dataset + schema

Build:
- canonical schema;
- sample generator;
- attack dataset;
- benign dataset;
- validator;
- normalization.

Acceptance:
```bash
python scripts/seed_demo.py
pytest backend/tests/test_schema.py
```

---

## Hour 3–6 — Detection core

Build in this order:
1. atomic signal rules;
2. entity novelty;
3. sequence correlation;
4. graph construction;
5. risk scoring;
6. suppression logic.

Do not touch the fancy UI until the backend can print:

```text
Incident: inc-001
Risk Index: 84
Stages:
  1. Initial access → evt-003
  2. Resource collection → evt-008, evt-009
  3. Removable-media transfer → evt-011, evt-012
```

---

## Hour 6–8 — API

Implement:
- `/health`
- `/datasets/ingest`
- `/analysis/run`
- `/incidents`
- `/incidents/{id}`
- `/incidents/{id}/evidence`

Test with curl/Postman/browser.

---

## Hour 8–12 — Premium UI

Build in this order:

### 1. Incident header
- severity;
- risk index;
- users/devices/IPs;
- incident status.

### 2. Timeline
- timestamp;
- stage;
- event ID;
- source;
- click-to-evidence.

### 3. Entity graph
- user/device/IP/resource/app;
- edges;
- selected-stage highlighting.

### 4. Risk breakdown
- four component bars;
- exact values;
- formula hint.

### 5. Evidence drawer
- raw event;
- normalized event;
- detector reasons.

Avoid decorative dashboards.

---

## Hour 12–14 — Copilot

Implement:
- evidence pack;
- system prompt;
- structured output;
- verifier;
- UI status badge.

Demo question:
> “Why is this incident high risk?”

The answer should cite the real event IDs.

---

## Hour 14–16 — Testing

Use:
- pytest;
- Playwright;
- browser console;
- network inspection.

Run attack + benign + partial attack.

---

## Hour 16–18 — Visual polish

Use:
- `hallmark`
- `frontend-design`
- `high-end-visual-design`
- `web-design-guidelines`

Polish:
- typography;
- spacing;
- timeline hierarchy;
- graph labels;
- loading states;
- empty states;
- error states.

Do not redesign functional components from scratch unless needed.

---

## Hour 18–20 — Reliability pass

Freeze detection logic.

Do not add new ML models.

Check:
- fresh clone;
- one-command startup;
- demo data;
- no secret keys committed;
- API failure states;
- slow model response;
- missing fields.

---

## Hour 20–22 — Demo rehearsal

Practice a 3-minute story:

1. Here is the event flood.
2. ThreatWeave correlates it.
3. One incident emerges.
4. This is the timeline.
5. These are the entities.
6. These are the three attack stages.
7. This is the evidence for each stage.
8. This is the risk breakdown.
9. This is why benign activity was suppressed.
10. This is the evidence-bounded AI explanation.

---

## Hour 22–23 — Documentation

README must include:
- problem;
- solution;
- architecture;
- setup;
- dataset;
- run commands;
- screenshots;
- model/API list;
- limitations;
- MVP vs stretch;
- resource declaration.

---

## Hour 23–24 — Freeze

No feature additions.

Only:
- bug fixes;
- build fixes;
- demo rehearsal;
- backup;
- Git push;
- final verification.

Create a backup branch/tag:

```text
qualifier-final
```

---

## Team Split

### Person A — Backend / detection
- schema
- normalization
- rules
- sequence
- risk
- tests

### Person B — Frontend
- incident UI
- timeline
- graph
- evidence

### Person C — AI / data
- datasets
- anomaly score
- evidence pack
- copilot verifier

### Person D — Integration / demo / docs
- API integration
- Playwright
- README
- screenshots
- demo script

If only 2 people:
- Person A = backend + data
- Person B = frontend + AI
- share testing/docs.

