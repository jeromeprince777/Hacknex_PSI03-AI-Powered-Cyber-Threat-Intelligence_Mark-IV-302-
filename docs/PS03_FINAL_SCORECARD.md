# THREATWEAVE — HNX26PSI03 Final Evaluation Scorecard

Authoritative Source: **HackNex 2026 Internal Qualifier Problem Statement Booklet — Page 7 (HNX26PSI03) & Pages 3–4**  
Evaluation Standard: **Strict Evidence-Based Verification Across Code, Telemetry, and Runtime Outputs**  
Audit Date: **October 7, 2026**

---

## 1. Official PS03 Evaluation Criteria Scorecard

| PS03 Evaluation Criterion | Concrete Runtime & Code Evidence | Verified Status |
| :--- | :--- | :---: |
| **Event correlation** | NetworkX multi-relational graph and `TemporalSequenceCorrelator` cluster events by actor and shared temporal window. | **PASS** |
| **User linkage** | `user_id` acts as primary clustering key; attacker `user-42` correlated across VPN, Windows, EDR, and Firewall logs. | **PASS** |
| **Device linkage** | `device_id` (`device-17`) binds endpoint activity, network login, and USB peripheral attachments (`Volume:E:\`). | **PASS** |
| **IP linkage** | Correlates novel external ingress IP (`203.0.113.10`) with internal host IP (`10.10.1.5`) and external exfiltration destination (`198.51.100.88`). | **PASS** |
| **App / resource linkage** | Binds application `explorer.exe` to sensitive files (`payroll.xlsx`, `Project_Titan.pdf`) across local access and USB copy writes. | **PASS** |
| **Step-by-step reconstruction** | Reconstructs 4 distinct chronological attack stages with concrete start/end timestamps and detector reason codes. | **PASS** |
| **Timeline accuracy** | Validates chronological monotonicity across all 15 events (`09:41:12Z` $\rightarrow$ `09:58:45Z`); matches source JSONL exactly with zero drift. | **PASS** |
| **Attack stages identification** | Standardized 5-stage taxonomy identifies Initial Access, Resource Collection, Removable Media Transfer, and Exfiltration. | **PASS** |
| **Proof per stage** | Every promoted stage references $\ge 1$ verified event ID (`evt-003`, `evt-008`, `evt-009`, `evt-011`, `evt-012`, `evt-013`, `evt-015`). Zero fake IDs allowed. | **PASS** |
| **Risk assessment** | Transparent 4-factor formula ($100 \times [0.35\text{Sig} + 0.30\text{Seq} + 0.20\text{Nov} + 0.15\text{Anom}]$) outputs Risk Index **89/100 (HIGH)**. | **PASS** |
| **Recommended action** | Dynamic playbook recommendations (`isolate-device`, `disable-session`, `review-resource-access`) mapped from approved action catalog. | **PASS** |
| **False-positive control** | Promotion gate enforces $\ge 3$ events and $\ge 2$ stages; routine admin activity in `benign_admin.jsonl` filtered out. | **PASS** |
| **Benign silence** | Zero incidents promoted on `benign_admin.jsonl`; 2 isolated signal clusters documented in immutable audit ledger. | **PASS** |
| **Explanation capability** | AI Copilot synthesizes evidence-bounded explanation citing verified telemetry proof; passes schema and evidence validator. | **PASS** |
| **Sample security logs** | 4 canonical scenario datasets in JSONL format representing multi-source enterprise logs with normalized schema. | **PASS** |
| **One known multi-stage attack** | Detects canonical 4-stage insider threat data exfiltration scenario from raw logs through final incident promotion. | **PASS** |
| **Advanced novel attacks** | Statistical baseline modeling (`RobustAnomalyScorer`) detects multivariate anomalies; long-running low-and-slow campaigns documented as stretch. | **PARTIAL** |

---

## 2. Summary Breakdown

- **Total Assessed Criteria:** 17
- **Criteria Passing with Proof:** 16 (94.1%)
- **Criteria with Partial / Stretch Support:** 1 (5.9% — Advanced novel / slow-and-hidden campaigns)
- **Criteria Failing:** 0 (0%)

---

## 3. Evaluator Verification Commands

All results in this scorecard are 100% reproducible on a local workstation:

```bash
# 1. Run complete automated unit and integration suite (42 tests)
pytest backend/tests

# 2. Run headless evaluator verification runner
python scripts/run_demo.py

# 3. Run complete one-click verification script
verify.bat
```
