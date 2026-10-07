"""
ThreatWeave Post-Audit Hardening Regression Test Suite.
Validates fixes for:
1. RFC 1918 vs RFC 5737 IP handling.
2. evt-015 LARGE_OUTBOUND_TRANSFER detection.
3. 4-Stage canonical attack reconstruction with exfiltration evidence.
4. Deterministic signal IDs & SQLite idempotent storage across repeated runs.
5. Copilot verifier type resilience against malformed inputs (A-G).
6. Copilot provider abstraction and offline deterministic fallback.
7. YAML rule configuration consistency.
Strictly adheres to docs/05_TEST_PLAN.md and AGENTS.md.
"""

import os
from pathlib import Path
import sqlite3
import pytest
import yaml

from app.schemas.events import ThreatWeaveEvent
from app.detectors.rules import (
    AtomicRuleDetector,
    is_external_for_detection,
    is_private_ip,
    is_rfc1918_private_ip,
    load_detection_rule_configs,
)
from app.detectors.sequence import TemporalSequenceCorrelator
from app.ingestion.validator import ingest_jsonl_file
from app.storage.repository import StorageRepository
from app.pipeline import PipelineOrchestrator
from app.copilot.verifier import verify_copilot
from app.copilot.provider import (
    DeterministicCopilotProvider,
    LLMCopilotProvider,
)
from app.copilot.engine import CopilotEngine

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SCENARIOS_DIR = ROOT_DIR / "data" / "scenarios"
CONFIGS_DIR = ROOT_DIR / "configs"


# ==============================================================================
# TEST 1 & 2: RFC 1918 vs RFC 5737 Subnet Semantics
# ==============================================================================

def test_rfc1918_private_ip_behavior():
    """Verify that RFC 1918 subnets and loopbacks are classified as private/internal."""
    # RFC 1918 ranges
    assert is_rfc1918_private_ip("10.0.0.1") is True
    assert is_rfc1918_private_ip("10.10.4.20") is True
    assert is_rfc1918_private_ip("172.16.5.10") is True
    assert is_rfc1918_private_ip("172.31.255.254") is True
    assert is_rfc1918_private_ip("192.168.1.1") is True
    assert is_rfc1918_private_ip("192.168.100.50") is True

    # Loopback / Link-local
    assert is_rfc1918_private_ip("127.0.0.1") is True
    assert is_rfc1918_private_ip("169.254.1.1") is True

    # None / Empty defaults to private
    assert is_rfc1918_private_ip(None) is True
    assert is_rfc1918_private_ip("") is True

    # External & Documentation IPs are NOT RFC 1918
    assert is_rfc1918_private_ip("198.51.100.88") is False
    assert is_rfc1918_private_ip("192.0.2.1") is False
    assert is_rfc1918_private_ip("203.0.113.10") is False
    assert is_rfc1918_private_ip("8.8.8.8") is False

    # Backward compatibility alias
    assert is_private_ip("10.10.4.20") is True
    assert is_private_ip("198.51.100.88") is False


def test_rfc5737_external_detector_behavior():
    """Verify that RFC 5737 benchmark subnets are treated as external for threat detectors."""
    # RFC 5737 TEST-NET subnets
    assert is_external_for_detection("192.0.2.1") is True      # TEST-NET-1
    assert is_external_for_detection("198.51.100.88") is True  # TEST-NET-2 (Demo exfil target)
    assert is_external_for_detection("203.0.113.10") is True   # TEST-NET-3 (Demo external auth)

    # Standard public internet IPs
    assert is_external_for_detection("8.8.8.8") is True
    assert is_external_for_detection("1.1.1.1") is True

    # Internal subnets must NOT be external
    assert is_external_for_detection("10.10.4.20") is False
    assert is_external_for_detection("172.16.1.1") is False
    assert is_external_for_detection("192.168.0.1") is False
    assert is_external_for_detection("127.0.0.1") is False
    assert is_external_for_detection(None) is False


# ==============================================================================
# TEST 3 & 4: evt-015 Detection & 4-Stage Attack Reconstruction
# ==============================================================================

def test_evt015_triggers_large_outbound_transfer():
    """Verify that evt-015 triggers LARGE_OUTBOUND_TRANSFER detector for RFC 5737 destination."""
    ev = ThreatWeaveEvent(
        event_id="evt-015",
        timestamp="2026-10-06T09:58:45Z",
        event_type="outbound_connection",
        source="firewall",
        action="connect",
        user_id="user-42",
        device_id="device-17",
        src_ip="10.10.4.20",
        dst_ip="198.51.100.88",
        application="curl.exe",
        resource="https://198.51.100.88/upload",
        session_id="sess-883",
        attributes={"dst_port": 443, "protocol": "TCP", "bytes": 15065760},
    )

    signals = AtomicRuleDetector.evaluate_event(ev)
    assert len(signals) == 1
    sig = signals[0]
    assert sig.signal_type == "large_outbound_transfer"
    assert sig.stage == "exfiltration"
    assert sig.score == 0.75
    assert sig.reason_code == "LARGE_OUTBOUND_TRANSFER"
    assert sig.signal_id == "sig-evt-015-large_outbound_transfer"


def test_four_stage_attack_reconstruction():
    """Verify that canonical attack reconstructs 4 full attack stages including exfiltration."""
    report = ingest_jsonl_file(SCENARIOS_DIR / "attack_insider_usb.jsonl")
    all_signals = []
    for ev in report.events:
        all_signals.extend(AtomicRuleDetector.evaluate_event(ev))

    clusters = TemporalSequenceCorrelator.cluster_events_and_signals(report.events, all_signals)
    u42_cluster = next((c for c in clusters if c.primary_entity == "user-42"), None)
    assert u42_cluster is not None

    stages = TemporalSequenceCorrelator.build_attack_stages("inc-test", u42_cluster)
    assert len(stages) == 4, f"Expected 4 attack stages, got {len(stages)}: {[s.name for s in stages]}"

    # Verify stage names and chronological sequence
    stage_names = [s.name for s in stages]
    assert "Initial access" in stage_names[0]
    assert "Resource" in stage_names[1]
    assert "Removable-media" in stage_names[2] or "USB" in stage_names[2]
    assert "exfiltration" in stage_names[3].lower()

    # Verify evt-015 appears in the exfiltration stage
    exfil_stage = stages[3]
    assert "evt-015" in exfil_stage.evidence_event_ids
    assert "LARGE_OUTBOUND_TRANSFER" in exfil_stage.reason_codes


# ==============================================================================
# TEST 5, 6, 7: Idempotent Storage, Deterministic Signal IDs, No Duplicates
# ==============================================================================

def test_deterministic_signal_ids():
    """Verify that identical events always generate identical deterministic signal IDs."""
    ev = ThreatWeaveEvent(
        event_id="evt-003",
        timestamp="2026-10-06T09:41:12Z",
        event_type="login_success",
        source="vpn",
        user_id="user-42",
        src_ip="203.0.113.10",
        attributes={"country_code": "RO", "login_location": "Bucharest, Romania"},
    )
    sig1 = AtomicRuleDetector.evaluate_event(ev)[0]
    sig2 = AtomicRuleDetector.evaluate_event(ev)[0]

    assert sig1.signal_id == sig2.signal_id
    assert sig1.signal_id == "sig-evt-003-auth_new_location"


def test_repeated_pipeline_execution_idempotency(tmp_path):
    """
    Verify repeated pipeline runs do not accumulate duplicate rows in SQLite tables.
    Runs pipeline 3 consecutive times and asserts identical record counts.
    """
    db_file = tmp_path / "test_threatweave.sqlite"
    repo = StorageRepository(db_path=str(db_file))
    orchestrator = PipelineOrchestrator(repo=repo)
    attack_file = SCENARIOS_DIR / "attack_insider_usb.jsonl"

    def get_row_counts():
        with sqlite3.connect(db_file) as conn:
            c = conn.cursor()
            counts = {}
            for tbl in ["events", "signals", "incidents", "stages", "stage_evidence"]:
                c.execute(f"SELECT count(*) FROM {tbl}")
                counts[tbl] = c.fetchone()[0]
            return counts

    # Run 1
    r1 = orchestrator.run_analysis(attack_file, dataset_id="run-1")
    c1 = get_row_counts()
    assert r1["incidents_created"] == 1
    assert c1["incidents"] == 1
    assert c1["stages"] == 4
    assert c1["signals"] == 7
    assert c1["events"] == 15

    # Run 2
    r2 = orchestrator.run_analysis(attack_file, dataset_id="run-2")
    c2 = get_row_counts()
    assert c2 == c1, f"Run 2 accumulated duplicate records! {c2} vs {c1}"

    # Run 3
    r3 = orchestrator.run_analysis(attack_file, dataset_id="run-3")
    c3 = get_row_counts()
    assert c3 == c1, f"Run 3 accumulated duplicate records! {c3} vs {c1}"


# ==============================================================================
# TEST 8 & 9: Copilot Verifier Type Resilience (A - G) & Never Crashes
# ==============================================================================

@pytest.fixture
def sample_evidence_pack():
    return {
        "incident": {
            "incident_id": "inc-001",
            "severity": "high",
            "risk_index": 89,
            "risk_components": {"signal_score": 0.71, "sequence_score": 1.0, "entity_novelty": 1.0, "anomaly_score": 0.95},
        },
        "stages": [
            {"stage_id": "stage-01", "name": "Initial access", "evidence_event_ids": ["evt-003"]},
            {"stage_id": "stage-02", "name": "Resource collection", "evidence_event_ids": ["evt-008"]},
        ],
        "timeline": [
            {"event_id": "evt-003", "fact": "VPN login from Bucharest"},
            {"event_id": "evt-008", "fact": "Accessed payroll.xlsx"},
        ],
        "approved_actions": [
            {"action_id": "isolate-device", "label": "Isolate device"},
            {"action_id": "disable-session", "label": "Disable user session"},
        ],
    }


def test_copilot_verifier_type_resilience_cases(sample_evidence_pack):
    """
    Tests all malformed Copilot outputs (A through G).
    Guarantees verifier never crashes and returns structured rejection codes.
    """
    # A. String instead of dict in stage_explanations
    out_a = {
        "summary": "Valid summary",
        "confidence": "high",
        "stage_explanations": ["Initial access occurred via VPN"],
    }
    verified, reason = verify_copilot(out_a, sample_evidence_pack)
    assert verified is False
    assert "invalid_stage_explanation_type" in reason

    # B. Null stage explanation in stage_explanations
    out_b = {
        "summary": "Valid summary",
        "confidence": "high",
        "stage_explanations": [None],
    }
    verified, reason = verify_copilot(out_b, sample_evidence_pack)
    assert verified is False
    assert "invalid_stage_explanation_type" in reason

    # C. Missing evidence_event_ids in stage explanation
    out_c = {
        "summary": "Valid summary",
        "confidence": "high",
        "stage_explanations": [{"stage_id": "stage-01"}],
    }
    verified, reason = verify_copilot(out_c, sample_evidence_pack)
    assert verified is False
    assert "missing_evidence_ids" in reason

    # D. Wrong evidence_event_ids type (string instead of list)
    out_d = {
        "summary": "Valid summary",
        "confidence": "high",
        "stage_explanations": [{"stage_id": "stage-01", "evidence_event_ids": "evt-003"}],
    }
    verified, reason = verify_copilot(out_d, sample_evidence_pack)
    assert verified is False
    assert "invalid_evidence_ids_type" in reason

    # E. Unknown stage
    out_e = {
        "summary": "Valid summary",
        "confidence": "high",
        "stage_explanations": [{"stage_id": "stage-99", "evidence_event_ids": ["evt-003"]}],
    }
    verified, reason = verify_copilot(out_e, sample_evidence_pack)
    assert verified is False
    assert "unknown_stage_id" in reason

    # F. Unknown event
    out_f = {
        "summary": "Valid summary",
        "confidence": "high",
        "stage_explanations": [{"stage_id": "stage-01", "evidence_event_ids": ["evt-phantom-999"]}],
    }
    verified, reason = verify_copilot(out_f, sample_evidence_pack)
    assert verified is False
    assert "unknown_evidence_event_id" in reason

    # G. Unknown action
    out_g = {
        "summary": "Valid summary",
        "confidence": "high",
        "stage_explanations": [{"stage_id": "stage-01", "evidence_event_ids": ["evt-003"]}],
        "recommended_actions": [{"action_id": "launch-retaliatory-strike"}],
    }
    verified, reason = verify_copilot(out_g, sample_evidence_pack)
    assert verified is False
    assert "unknown_action_id" in reason


def test_copilot_verifier_never_crashes_on_garbage():
    """Verify that arbitrary garbage inputs return verified=False without unhandled exceptions."""
    for garbage in [None, 1234, "string", [], True, object()]:
        verified, reason = verify_copilot(garbage, {})
        assert verified is False
        assert reason is not None


# ==============================================================================
# TEST 10: Copilot Provider Abstraction & Offline Fallback
# ==============================================================================

def test_copilot_provider_abstraction_and_fallback(sample_evidence_pack):
    """Verify provider abstraction and clean offline deterministic fallback."""
    # Deterministic provider
    det_provider = DeterministicCopilotProvider()
    resp, name = det_provider.generate(sample_evidence_pack)
    assert name == "deterministic"
    assert "summary" in resp
    assert len(resp["stage_explanations"]) == 2

    # LLM provider with no API key falls back cleanly
    orig_key = os.environ.pop("GEMINI_API_KEY", None)
    try:
        llm_provider = LLMCopilotProvider()
        resp_llm, name_llm = llm_provider.generate(sample_evidence_pack)
        assert "llm-fallback" in name_llm
        assert "summary" in resp_llm

        # Verify through CopilotEngine
        engine_res = CopilotEngine.generate_explanation(sample_evidence_pack, provider=llm_provider)
        assert engine_res["verified"] is True
        assert engine_res["verification_status"] == "VERIFIED"
        assert "llm-fallback" in engine_res["provider"]
    finally:
        if orig_key:
            os.environ["GEMINI_API_KEY"] = orig_key


# ==============================================================================
# TEST 11: YAML Rule Configuration Consistency
# ==============================================================================

def test_yaml_rule_configuration_consistency():
    """
    Verify that configs/detection_rules.yaml matches the runtime detector implementation.
    Rule IDs, stages, and signal types must be synchronized.
    """
    yaml_file = CONFIGS_DIR / "detection_rules.yaml"
    assert yaml_file.is_file(), f"Configuration file {yaml_file} not found!"

    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert "rules" in data
    yaml_rules = {r["id"]: r for r in data["rules"]}

    # Verify loaded runtime configs match YAML
    runtime_configs = AtomicRuleDetector.RULE_CONFIGS

    for rule_id, y_rule in yaml_rules.items():
        assert rule_id in runtime_configs, f"Rule '{rule_id}' in YAML is missing from detector runtime!"
        rt_rule = runtime_configs[rule_id]
        assert rt_rule["stage"] == y_rule["stage"]
        assert rt_rule["signal_type"] == y_rule["signal_type"]
        assert rt_rule["base_score"] == y_rule["base_score"]
