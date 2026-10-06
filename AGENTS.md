# THREATWEAVE — Repository Agent Rules

This repository implements HNX26PSI03: AI-Powered Cyber Threat Intelligence.

Read `docs/AGENT_ENGINEERING_RULES.md` and the full PRD/technical PRD before modifying the project.

Non-negotiable:
- Never invent evidence, APIs, imports, data, timestamps, entities or results.
- Detection facts come from code/data, not the LLM.
- Every detected attack stage must reference real event IDs.
- Every score must expose its components.
- Fixed dataset + fixed config must produce reproducible detection.
- Prefer conservative correlation and false-positive suppression.
- AI may summarize only a bounded evidence pack and must pass schema/evidence validation.
- No placeholder code or fake implementations.
- Test actual end-to-end behavior before claiming completion.
- Keep the UI evidence-first and avoid generic AI-SaaS visuals.
