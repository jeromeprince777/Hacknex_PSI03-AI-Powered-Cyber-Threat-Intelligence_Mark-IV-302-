"""
Unit tests for ThreatWeave Canonical Event Schema, Normalization, and Seed Datasets.
Verifies compliance with docs/04_DATA_API_CONTRACTS.md and docs/05_TEST_PLAN.md.
"""

from pathlib import Path
import pytest
from pydantic import ValidationError

from app.schemas.events import (
    ThreatWeaveEvent,
    Signal,
    Stage,
    Incident,
    RiskComponents,
    CopilotExplanation,
)
from app.ingestion.validator import (
    ingest_jsonl_content,
    ingest_jsonl_file,
    validate_dict_event,
)
from app.ingestion.normalizer import LogNormalizer

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "scenarios"


def test_canonical_event_valid():
    """Verify that a compliant event dictionary instantiates without errors."""
    event_data = {
        "event_id": "evt-100",
        "timestamp": "2026-10-06T12:00:00Z",
        "event_type": "file_access",
        "source": "windows",
        "action": "read",
        "user_id": "user-42",
        "device_id": "device-17",
        "src_ip": "10.10.4.20",
        "dst_ip": None,
        "application": "FileExplorer",
        "resource": "Finance/Q4/payroll.xlsx",
        "session_id": "sess-883",
        "attributes": {"bytes": 1024},
        "raw": {"RawEventId": 4663},
    }
    event = ThreatWeaveEvent(**event_data)
    assert event.event_id == "evt-100"
    assert event.timestamp == "2026-10-06T12:00:00Z"
    assert event.user_id == "user-42"
    assert event.attributes["bytes"] == 1024
    assert event.raw["RawEventId"] == 4663


def test_canonical_event_invalid_missing_required():
    """Verify that omitting required fields raises ValidationError."""
    # Missing source
    with pytest.raises(ValidationError):
        ThreatWeaveEvent(
            event_id="evt-101",
            timestamp="2026-10-06T12:00:00Z",
            event_type="login_success",
            source="",  # empty string rejected
        )

    # Missing event_type
    with pytest.raises(ValidationError):
        ThreatWeaveEvent(
            event_id="evt-102",
            timestamp="2026-10-06T12:00:00Z",
            event_type="",
            source="windows",
        )


def test_canonical_event_invalid_timestamp():
    """Verify that non-ISO timestamp raises ValidationError."""
    with pytest.raises(ValidationError):
        ThreatWeaveEvent(
            event_id="evt-103",
            timestamp="not-a-valid-timestamp",
            event_type="login_success",
            source="windows",
        )


def test_attack_insider_usb_scenario():
    """
    Verify the canonical attack dataset (attack_insider_usb.jsonl).
    Must parse completely with 0 quarantine records and preserve the 4+ stage progression.
    """
    scenario_path = DATA_DIR / "attack_insider_usb.jsonl"
    assert scenario_path.is_file(), f"Scenario file not found at {scenario_path}"

    report = ingest_jsonl_file(scenario_path)
    assert report.total_records == 15
    assert report.valid_records == 15
    assert report.quarantined_records == 0
    assert report.duplicate_records == 0

    event_ids = [e.event_id for e in report.events]
    assert "evt-001" in event_ids
    assert "evt-003" in event_ids  # Initial access (VPN Bucharest)
    assert "evt-008" in event_ids  # Collection (payroll.xlsx)
    assert "evt-009" in event_ids  # Collection (Project_Titan.pdf)
    assert "evt-011" in event_ids  # Device (USB connected)
    assert "evt-012" in event_ids  # Exfil (USB copy payroll)
    assert "evt-013" in event_ids  # Exfil (USB copy Project_Titan)
    assert "evt-015" in event_ids  # Outbound network transfer

    # Verify key attack entity bindings
    evt_auth = next(e for e in report.events if e.event_id == "evt-003")
    assert evt_auth.user_id == "user-42"
    assert evt_auth.src_ip == "203.0.113.10"
    assert evt_auth.attributes.get("login_location") == "Bucharest, Romania"

    evt_usb_connect = next(e for e in report.events if e.event_id == "evt-011")
    assert evt_usb_connect.device_id == "device-17"
    assert evt_usb_connect.attributes.get("removable_media_id") == "usb-kingston-992"

    evt_usb_copy = next(e for e in report.events if e.event_id == "evt-012")
    assert evt_usb_copy.resource == "Finance/Q4/payroll.xlsx"
    assert evt_usb_copy.attributes.get("removable_media_id") == "usb-kingston-992"


def test_benign_admin_scenario():
    """
    Verify the benign scenario dataset (benign_admin.jsonl).
    Must parse completely with 0 quarantine records.
    """
    scenario_path = DATA_DIR / "benign_admin.jsonl"
    assert scenario_path.is_file()

    report = ingest_jsonl_file(scenario_path)
    assert report.total_records == 10
    assert report.valid_records == 10
    assert report.quarantined_records == 0


def test_attack_partial_scenario():
    """
    Verify the partial attack dataset (attack_partial.jsonl).
    Lacks USB file copy events.
    """
    scenario_path = DATA_DIR / "attack_partial.jsonl"
    assert scenario_path.is_file()

    report = ingest_jsonl_file(scenario_path)
    assert report.total_records == 7
    assert report.valid_records == 7
    assert report.quarantined_records == 0

    event_types = [e.event_type for e in report.events]
    assert "usb_copy" not in event_types


def test_malformed_logs_quarantine():
    """
    Verify that malformed logs are quarantined with structured error codes
    and valid records in the same stream are preserved.
    """
    scenario_path = DATA_DIR / "malformed_logs.jsonl"
    assert scenario_path.is_file()

    report = ingest_jsonl_file(scenario_path)
    assert report.total_records == 8
    # mal-001 and first evt-dup-01 are valid
    assert report.valid_records == 2
    # 6 quarantined: missing id, missing time, bad time, missing type, duplicate id, invalid json
    assert report.quarantined_records == 6
    assert report.duplicate_records == 1

    reason_codes = {q.reason_code for q in report.quarantine}
    assert "INVALID_JSON" in reason_codes
    assert "MISSING_EVENT_ID" in reason_codes
    assert "SCHEMA_VALIDATION_ERROR" in reason_codes
    assert "DUPLICATE_EVENT_ID" in reason_codes


def test_normalizer_windows_event():
    """Verify conversion of raw Windows EventLog record."""
    raw_win = {
        "EventCode": 4624,
        "TimeCreated": "2026-10-06T09:00:00Z",
        "TargetUserName": "user-test",
        "Computer": "WKST-001",
        "IpAddress": "10.10.4.55",
        "TargetLogonId": "0x12a4f",
    }
    event = LogNormalizer.normalize_windows_event(raw_win)
    assert event.event_type == "login_success"
    assert event.user_id == "user-test"
    assert event.device_id == "WKST-001"
    assert event.src_ip == "10.10.4.55"
    assert event.session_id == "0x12a4f"
    assert event.source == "windows"


def test_normalizer_vpn_event():
    """Verify conversion of raw VPN connection log."""
    raw_vpn = {
        "event": "AUTH_SUCCESS",
        "time": "2026-10-06T09:15:00Z",
        "username": "user-remote",
        "client_ip": "198.51.100.12",
        "location": "Warsaw, Poland",
    }
    event = LogNormalizer.normalize_vpn_event(raw_vpn)
    assert event.event_type == "login_success"
    assert event.user_id == "user-remote"
    assert event.src_ip == "198.51.100.12"
    assert event.attributes["login_location"] == "Warsaw, Poland"
    assert event.source == "vpn"


def test_risk_components_contract():
    """Verify RiskComponents formula and weight constraints."""
    rc = RiskComponents(
        signal_score=0.86,
        sequence_score=0.92,
        entity_novelty=0.78,
        anomaly_score=0.71,
    )
    # Risk = clamp(100 * (0.35 * 0.86 + 0.30 * 0.92 + 0.20 * 0.78 + 0.15 * 0.71))
    # 0.35*0.86 = 0.301
    # 0.30*0.92 = 0.276
    # 0.20*0.78 = 0.156
    # 0.15*0.71 = 0.1065
    # sum = 0.8395 -> round(83.95) = 84
    weighted_sum = (
        rc.weights["signal"] * rc.signal_score
        + rc.weights["sequence"] * rc.sequence_score
        + rc.weights["novelty"] * rc.entity_novelty
        + rc.weights["anomaly"] * rc.anomaly_score
    )
    risk_index = round(100 * weighted_sum)
    assert risk_index == 84
