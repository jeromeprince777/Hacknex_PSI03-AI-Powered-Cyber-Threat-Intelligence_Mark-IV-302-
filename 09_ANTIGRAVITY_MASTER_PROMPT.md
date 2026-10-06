# THREATWEAVE — Master Prompt for Antigravity

You are the lead engineer building **ThreatWeave** for the HackNex 2026 Internal Qualifier, problem statement **HNX26PSI03: AI-Powered Cyber Threat Intelligence**.

The project must reconstruct coordinated attacks from security logs across users, devices, IP addresses and applications.

## FIRST: READ THESE FILES

Read:
- `docs/PRD.md`
- `docs/TECHNICAL_PRD.md`
- `docs/AGENT_RULES.md`
- `docs/DATA_API_CONTRACTS.md`
- `docs/TEST_PLAN.md`
- `docs/24_HOUR_EXECUTION_PLAN.md`
- `docs/DEMO_SCRIPT.md`

Also inspect the repository before making architecture assumptions.

## HARD RULES

1. Do not invent APIs, imports, package names, data fields or framework behavior.
2. Do not invent cybersecurity evidence.
3. Do not make the LLM responsible for factual detection.
4. Every attack stage must have evidence event IDs.
5. Every risk score must expose components.
6. Prefer deterministic detection rules + graph correlation + statistical anomaly scoring.
7. AI may summarize only a bounded evidence pack.
8. Validate every AI evidence reference before displaying it as verified.
9. Do not use fake dashboard numbers.
10. Do not leave placeholder functions, TODOs or fake implementations.
11. Do not overbuild cloud infrastructure until the local demo is stable.
12. Keep the project explainable enough that every team member can defend the implementation.

## STACK

Preferred:
- Next.js + TypeScript + Tailwind + shadcn/ui
- Cytoscape.js or React Flow
- FastAPI + Python
- Pydantic
- NetworkX
- pandas
- scikit-learn
- SQLite
- pytest
- Playwright

Use existing repository choices where they already work.

## PRODUCT

Build these screens:

### Dashboard
- incident list;
- severity;
- Risk Index;
- event volume;
- suppression summary.

### Incident Investigation
- incident header;
- risk breakdown;
- timeline;
- entity graph;
- attack stages;
- evidence panel;
- recommended actions;
- verified AI Copilot.

### Dataset Replay
- select scenario;
- run analysis;
- show results;
- compare attack vs benign.

## IMPLEMENTATION ORDER

### Phase 1
Repository structure + schemas + seed datasets.

### Phase 2
Normalization + validation.

### Phase 3
Atomic detection rules.

### Phase 4
Entity novelty.

### Phase 5
Sequence correlation.

### Phase 6
Graph construction.

### Phase 7
Risk scoring.

### Phase 8
Evidence pack + API.

### Phase 9
Frontend investigation page.

### Phase 10
AI copilot + verifier.

### Phase 11
Tests.

### Phase 12
Visual polish.

## CANONICAL DEMO

Implement the qualifier-style attack:

1. Successful user login from an unusual/first-seen location relationship.
2. The same user accesses resources they have not previously touched.
3. A removable device is connected.
4. The user copies selected resources to that device.
5. Optional outbound transfer enrichment.

The exact event records must be present in the seed data and referenced by IDs.

## FALSE-POSITIVE DEMO

Create routine administrator activity that contains one or two suspicious-looking atomic events but does not form a supported multi-stage chain.

Expected:
- low-level signals may exist;
- no high-confidence incident.

## RISK INDEX

Use:

`Risk = clamp(100 * (0.35 * SignalScore + 0.30 * SequenceScore + 0.20 * EntityNovelty + 0.15 * AnomalyScore))`

This is a product score, not a probability.

## INCIDENT PROMOTION

Default MVP gate:

- at least 3 evidence events;
- at least 2 distinct stages;
- meaningful entity link;
- temporal order consistency.

Store a suppression reason when the gate fails.

## UI STYLE

Use the installed visual design skills.

Target feeling:
- analyst console;
- evidence-first;
- high information density;
- premium but restrained;
- technical;
- not a generic AI SaaS dashboard.

Avoid:
- giant gradients;
- excessive glassmorphism;
- random decorative blobs;
- fake analytics;
- meaningless animated numbers.

Use motion only where it helps investigation flow.

## TESTING

After every major integration:
1. backend unit tests;
2. integration test;
3. run frontend;
4. Playwright smoke test;
5. browser console check;
6. network check.

Do not call work complete until the actual flow works end-to-end.

## AGENT WORKFLOW

Start with:

`/plan`

Then work in small milestones.

Use:
- `brainstorming`
- `codebase-design`
- `full-output-enforcement`
- `webapp-testing`
- `diagnosing-bugs`
- `hallmark`
- `frontend-design`
- `web-design-guidelines`
- `vercel-react-best-practices`

Use `/goal` only for a clearly bounded long task with explicit acceptance criteria.

## REQUIRED OUTPUT AFTER EACH MILESTONE

Return:
1. what changed;
2. files changed;
3. tests run;
4. actual test result;
5. remaining blocker(s);
6. next smallest milestone.

Never report “done” without evidence from commands/tests.
