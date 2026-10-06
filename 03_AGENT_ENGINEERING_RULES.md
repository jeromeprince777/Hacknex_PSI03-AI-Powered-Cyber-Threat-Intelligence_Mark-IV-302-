# THREATWEAVE — Antigravity Agent Engineering Rules

Place the core of this document in `AGENTS.md` at the repository root.

## 0. Mission

Build ThreatWeave for the HackNex 2026 internal qualifier, problem HNX26PSI03.

The system must reconstruct coordinated security incidents from logs across users, devices, IPs and applications. The final output must include an ordered attack timeline, attack stages, evidence for every stage, risk, and recommended actions.

The qualifier explicitly rewards evidence-backed analysis and penalizes excessive false positives.

---

## 1. Non-Negotiable Rules

### Rule A — Never invent evidence
Never create fake event IDs, timestamps, users, IPs, devices, applications, resources, attack stages or observations.

### Rule B — Never use the LLM as the detector of truth
Detection facts come from code, rules, graph relationships, statistics and stored logs.

### Rule C — Every stage needs evidence
No `stage.status = detected` unless `stage.evidence_event_ids.length > 0`.

### Rule D — Every score needs components
Never output a bare score.

### Rule E — Prefer deterministic behavior
For a fixed dataset + config + version, detection must be reproducible.

### Rule F — Clean logs must stay mostly quiet
Do not increase alert volume just to make the dashboard look active.

### Rule G — No placeholder code
Do not leave TODOs, fake imports, mocked functions disguised as production paths, or invented package APIs.

### Rule H — Verify before presenting
After every major feature:
1. run unit tests;
2. run the application;
3. exercise the API;
4. run Playwright smoke test;
5. inspect browser console;
6. inspect network errors.

### Rule I — Keep external resources explicit
Every API, dataset, pretrained model or third-party component must be documented in README.

### Rule J — Do not overengineer the infrastructure
A robust local demo beats an unfinished distributed architecture.

---

## 2. Anti-AI-Slop UI Rules

Do not generate:
- generic SaaS dashboard layouts;
- giant hero gradients;
- random glassmorphism;
- meaningless KPI cards;
- excessive rounded cards;
- lorem ipsum;
- “AI-powered next generation” marketing copy;
- fake charts with arbitrary numbers;
- glowing decorations unrelated to security operations.

Design for a SOC analyst.

The interface should feel like an actual investigation tool:
- dense but readable;
- evidence-oriented;
- strong hierarchy;
- consistent severity semantics;
- timeline and graph are primary visuals;
- metadata is visible;
- empty states explain what to do;
- no visual element should imply certainty the data does not support.

Use the installed `hallmark`, `industrial-brutalist-ui`, `frontend-design`, `design-taste-frontend`, `high-end-visual-design`, and `web-design-guidelines` skills as appropriate.

---

## 3. Frontend Constraints

Prefer:
- Next.js
- TypeScript
- Tailwind
- shadcn/ui
- Cytoscape.js or React Flow

Components must consume typed API contracts.

Never hardcode production incident values into visual components.

For the seeded demo, data comes from the dataset/API.

---

## 4. Backend Constraints

Prefer:
- FastAPI
- Pydantic
- NetworkX
- pandas
- scikit-learn
- SQLite

Write small modules with clear responsibilities.

Recommended boundaries:

```text
ingestion
normalization
validation
detectors
graph
correlation
scoring
evidence
copilot
verification
storage
```

No detector should query the database through the UI layer.

---

## 5. Detection Rules Must Be Data-Driven

Use config files where practical.

Example:

```yaml
- id: AUTH_NEW_LOCATION
  event_type: login_success
  stage: initial_access
  weight: 0.55
  reason: "Successful login from a first-seen location relationship"
```

Rules must output structured reason codes.

---

## 6. Evidence Contract

Any detector output must contain:

```json
{
  "event_id": "evt-123",
  "signal_type": "string",
  "stage": "string",
  "reason_code": "string",
  "score": 0.0
}
```

No free-floating detection strings.

---

## 7. Correlation Rules

Correlate using explicit keys and windows:
- same user
- same device
- same session
- same source IP
- related resource
- time window

Do not correlate everything to everything.

Every correlation must be explainable.

---

## 8. LLM Rules

The LLM gets a bounded evidence pack.

The LLM can:
- summarize;
- explain;
- select approved actions;
- state limitations.

The LLM cannot:
- retrieve arbitrary secrets;
- browse the network by default;
- execute remediation;
- fabricate missing evidence;
- create new incident facts.

Validate output with Pydantic/Zod before returning it to the UI.

---

## 9. Tool Use in Antigravity

For the initial implementation:
- use `/plan`;
- use `brainstorming` before major product decisions;
- use `codebase-design` for architecture;
- use `full-output-enforcement` when generating larger modules;
- use `webapp-testing` and Playwright after UI work;
- use `diagnosing-bugs` for regressions;
- use `hallmark` and `frontend-design` for visual audit;
- use `vercel-react-best-practices` before final frontend optimization.

Do not ask an agent to “build the whole thing” in one uncontrolled pass.

Prefer small, testable milestones.

---

## 10. Commit Strategy

Use commits such as:

```text
feat(ingestion): add canonical event schema
feat(detectors): add authentication novelty detector
feat(correlation): build stage sequence correlator
feat(scoring): add explainable risk index
feat(ui): add incident investigation view
feat(copilot): add evidence-bounded analyst explanation
test: add clean-vs-attack scenarios
docs: add reproducible demo instructions
```

---

## 11. Definition of Done for a Module

A module is done only when:
- source code exists;
- types/schemas exist;
- tests exist;
- errors are handled;
- no placeholder behavior remains;
- it is integrated into the actual execution path;
- README/docs are updated if behavior is externally visible.

