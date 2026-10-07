# THREATWEAVE — Comprehensive Dataset & Telemetry Audit

Authoritative Standard: **HackNex 2026 Qualifier Rules ("Declare Your Resources") & PS03 Requirements**  
Audit Date: **October 7, 2026**

---

## 1. Dataset Inventory & Classification

| Resource | Location | Type | Origin Classification | Used by Runtime? | Purpose | File Hash (SHA-256) |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **`attack_insider_usb.jsonl`** | `data/scenarios/` | JSONL (15 records) | **A. Team-generated synthetic data** | **Yes** (Default demo dataset) | Canonical multi-stage insider threat scenario: unusual VPN login, sensitive file read, USB mount & copy, large outbound transfer. | `a851b19a8e2cec44ab693a8682cb885f006ce7f7912b52e582a3949212c44dc8` |
| **`benign_admin.jsonl`** | `data/scenarios/` | JSONL (10 records) | **A. Team-generated synthetic data** | **Yes** (Replay Lab benchmark) | Negative control demonstrating false-positive suppression gate on routine administrative and IT maintenance tasks. | `abf66478a7758384112210fe935b2b95a3d404178a05a6ea27fed54ed71dbeb2` |
| **`attack_partial.jsonl`** | `data/scenarios/` | JSONL (7 records) | **A. Team-generated synthetic data** | **Yes** (Replay Lab benchmark) | Partial attack scenario with collection but missing data copy/exfil, testing graceful risk degradation. | `c6a89b5778a6258f4ac5813dd42654945aa73029c86eff79e6958ef550901d55` |
| **`malformed_logs.jsonl`** | `data/scenarios/` | JSONL (8 records) | **E. Test fixture / Synthetic anomaly** | **Yes** (Quarantine validation) | Malformed JSON records, invalid timestamps, and missing event IDs to verify ingestion quarantine safety. | `2dbdca395185ca001b2fba8ec8de0cadfd1988b591d5fcaa3eaf75c14f93a162` |
| **`event_schema.json`** | `data/schema/` | JSON Schema | **E. Test fixture / Schema definition** | **No** (Reference contract) | JSON Schema definition defining canonical Event-v1 specification. | `c6e2a2cfa02ef1bb51fc61937dfa818c430e7136006f7bbab351ae2e53efbfe5` |
| **`threatweave.sqlite`** | `backend/data/` | SQLite Database | **Runtime Persistence** | **Yes** (Storage backend) | Local SQLite persistence layer storing ingested events, detected signals, promoted incidents, stages, and suppression audit logs. | *Dynamically mutated by runtime* |

---

## 2. Public Dataset Audit (Phase 9 Verification)

A comprehensive codebase and documentation search was conducted for references to public cybersecurity datasets:
- **DARPA:** 0 occurrences found in code, datasets, or runtime manifests.
- **CICIDS / CIC-IDS:** 0 occurrences found.
- **Kaggle:** 0 occurrences found.
- **UNSW-NB15:** 0 occurrences found.
- **CTF Datasets:** 0 occurrences found.

### Official Finding:
```text
======================================================================
               NO PUBLIC DATASET FOUND IN RUNTIME
 Current MVP uses team-generated deterministic synthetic telemetry.
======================================================================
```
*Note on PRD Mentions:* Early PRD planning documents referenced public dataset options (such as DARPA or CICIDS) as possible future integration targets. However, the runtime codebase and live demonstration rely strictly on team-generated deterministic synthetic JSONL telemetry. No external public dataset files exist in the repository.

---

## 3. Data Generation & Determinism Audit (Phase 10 Verification)

- **Generation Method:** The scenario files in `data/scenarios/` are fixed, committed static files. They are **not** generated dynamically via pseudo-random number generators at runtime.
- **Timestamp Determinism:** All timestamps are fixed ISO-8601 UTC strings (`2026-10-06T08:30:15Z` through `2026-10-06T09:58:45Z`).
- **Identifier Determinism:** All event IDs are fixed canonical strings (`evt-001` through `evt-015`, `ben-001` through `ben-010`).
- **Reproducibility Test:** Running `scripts/seed_demo.py` or `PipelineOrchestrator.run_analysis()` repeatedly produces identical cryptographic SHA-256 hashes, identical detection signals, identical stage counts (4), and identical deterministic Risk Indexes (89/100).

---

## 4. External Network & Undeclared Data Audit (Phase 11 Verification)

A strict inspection of the backend source code (`backend/app/`) verified:
- **Zero outbound HTTP requests:** No runtime calls to external endpoints, public APIs, or remote databases.
- **Zero external model weights downloaded:** No connections to HuggingFace, PyTorch Hub, or cloud model stores.
- **Zero API key requirements:** The platform executes 100% offline in a completely self-contained local environment.
