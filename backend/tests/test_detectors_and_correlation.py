"""
Tests for Atomic Detectors, Entity Novelty, Temporal Correlation, and FP Suppression Gate.
Verifies compliance with docs/05_TEST_PLAN.md (Tests 1, 2, 3, 4) and AGENTS.md.
"""

from pathlib import Path
import pytest

from app.schemas.events import ThreatWeaveEvent
from app.ingestion.validator import ingest_jsonl_file
from app.detectors.rules import AtomicRuleDetector
from app.detectors.novelty import BaselineProfile, EntityNoveltyScorer
from app.detectors.sequence import TemporalSequenceCorrelator

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "scenarios"


def test_atomic_rules_positive_cases():
    """Verify that all atomic detection rules fire accurately on positive indicators."""
    # 1. External / Foreign Login
    ev_auth = ThreatWeaveEvent(
        event_id="evt-auth-1",
        timestamp="2026-10-06T09:41:12Z",
        event_type="login_success",
        source="vpn",
        user_id="user-42",
        src_ip="203.0.113.10",
        attributes={"login_location": "Bucharest, Romania", "country_code": "RO"},
    )
    sig_auth = AtomicRuleDetector.evaluate_event(ev_auth)
    assert len(sig_auth) == 1
    assert sig_auth[0].reason_code == "AUTH_NEW_LOCATION"
    assert sig_auth[0].stage == "initial_access"
    assert sig_auth[0].score == 0.55

    # 2. Sensitive Resource Access
    ev_file = ThreatWeaveEvent(
        event_id="evt-file-1",
        timestamp="2026-10-06T09:48:33Z",
        event_type="file_access",
        source="windows",
        action="read",
        user_id="user-42",
        resource="Finance/Q4/payroll.xlsx",
        attributes={"classification": "restricted_confidential"},
    )
    sig_file = AtomicRuleDetector.evaluate_event(ev_file)
    assert len(sig_file) == 1
    assert sig_file[0].reason_code == "UNUSUAL_RESOURCE_ACCESS"
    assert sig_file[0].stage == "resource_collection"
    assert sig_file[0].score == 0.70

    # 3. Removable Media Connect
    ev_usb = ThreatWeaveEvent(
        event_id="evt-usb-1",
        timestamp="2026-10-06T09:52:05Z",
        event_type="usb_connected",
        source="edr",
        device_id="device-17",
        attributes={"removable_media_id": "usb-kingston-992"},
    )
    sig_usb = AtomicRuleDetector.evaluate_event(ev_usb)
    assert len(sig_usb) == 1
    assert sig_usb[0].reason_code == "USB_CONNECTED"
    assert sig_usb[0].stage == "removable_media_transfer"

    # 4. USB Copy
    ev_copy = ThreatWeaveEvent(
        event_id="evt-copy-1",
        timestamp="2026-10-06T09:54:20Z",
        event_type="usb_copy",
        source="edr",
        user_id="user-42",
        device_id="device-17",
        resource="Finance/Q4/payroll.xlsx",
        attributes={"removable_media_id": "usb-kingston-992"},
    )
    sig_copy = AtomicRuleDetector.evaluate_event(ev_copy)
    assert len(sig_copy) == 1
    assert sig_copy[0].reason_code == "USB_COPY"
    assert sig_copy[0].stage == "removable_media_transfer"
    assert sig_copy[0].score == 0.85


def test_atomic_rules_negative_and_benign_cases():
    """Verify that routine benign events do not trigger malicious alerts."""
    # Routine internal workstation login
    ev_routine_login = ThreatWeaveEvent(
        event_id="ben-auth-1",
        timestamp="2026-10-06T08:30:15Z",
        event_type="login_success",
        source="windows",
        user_id="user-88",
        device_id="device-04",
        src_ip="10.10.4.105",
        attributes={"auth_method": "kerberos"},
    )
    sig_routine = AtomicRuleDetector.evaluate_event(ev_routine_login)
    assert len(sig_routine) == 0

    # Routine template file read
    ev_routine_file = ThreatWeaveEvent(
        event_id="ben-file-1",
        timestamp="2026-10-06T08:45:00Z",
        event_type="file_access",
        source="file_server",
        action="read",
        user_id="user-88",
        resource="Shared/Templates/timesheet.xlsx",
    )
    sig_file = AtomicRuleDetector.evaluate_event(ev_routine_file)
    assert len(sig_file) == 0


def test_entity_novelty_scorer():
    """Verify baseline comparison and entity novelty calculation."""
    scorer = EntityNoveltyScorer()

    # Known relationship: user-42 accessing HR/attendance.csv from 10.10.4.20
    ev_known = ThreatWeaveEvent(
        event_id="ev-k1",
        timestamp="2026-10-06T09:00:00Z",
        event_type="file_access",
        source="windows",
        user_id="user-42",
        src_ip="10.10.4.20",
        resource="HR/attendance.csv",
    )
    score_known, reasons_known = scorer.score_event(ev_known)
    assert score_known == 0.0
    assert len(reasons_known) == 0

    # Novel relationship: user-42 accessing Finance/Q4/payroll.xlsx from 203.0.113.10
    ev_novel = ThreatWeaveEvent(
        event_id="ev-n1",
        timestamp="2026-10-06T09:41:12Z",
        event_type="file_access",
        source="windows",
        user_id="user-42",
        src_ip="203.0.113.10",
        resource="Finance/Q4/payroll.xlsx",
    )
    score_novel, reasons_novel = scorer.score_event(ev_novel)
    assert score_novel >= 0.70
    assert any("Novel IP" in r for r in reasons_novel)
    assert any("First-seen resource" in r for r in reasons_novel)


def test_canonical_attack_promotion_gate():
    """
    TEST 1: Canonical attack replay.
    Expectation: Correlates into 1 promoted incident candidate with >= 3 stages and high sequence score.
    """
    report = ingest_jsonl_file(DATA_DIR / "attack_insider_usb.jsonl")
    all_signals = []
    for ev in report.events:
        all_signals.extend(AtomicRuleDetector.evaluate_event(ev))

    clusters = TemporalSequenceCorrelator.cluster_events_and_signals(report.events, all_signals)
    assert len(clusters) > 0

    # Locate user-42 cluster
    u42_cluster = next((c for c in clusters if c.primary_entity == "user-42"), None)
    assert u42_cluster is not None

    stages = TemporalSequenceCorrelator.build_attack_stages("inc-001", u42_cluster)
    assert len(stages) >= 3  # Initial access, Resource collection, Removable-media transfer, Exfil

    # Verify stage names and order
    stage_names = [s.name for s in stages]
    assert any("Initial access" in n for n in stage_names)
    assert any("Resource" in n for n in stage_names)
    assert any("Removable-media" in n or "USB" in n for n in stage_names)

    # Sequence score
    seq_score = TemporalSequenceCorrelator.calculate_sequence_score(stages, u42_cluster.events)
    assert seq_score >= 0.85

    # Promotion Gate
    promoted, suppression = TemporalSequenceCorrelator.evaluate_promotion_gate(u42_cluster, stages)
    assert promoted is True
    assert suppression is None


def test_benign_scenario_suppression_gate():
    """
    TEST 2: Benign admin activity replay.
    Expectation: Zero high-confidence incidents. Clusters are suppressed with visible reasons.
    """
    report = ingest_jsonl_file(DATA_DIR / "benign_admin.jsonl")
    all_signals = []
    for ev in report.events:
        all_signals.extend(AtomicRuleDetector.evaluate_event(ev))

    clusters = TemporalSequenceCorrelator.cluster_events_and_signals(report.events, all_signals)

    # For any cluster in benign dataset, verify it does NOT pass the promotion gate
    promoted_incidents = 0
    suppression_records = []

    for cluster in clusters:
        stages = TemporalSequenceCorrelator.build_attack_stages(f"inc-candidate-{cluster.cluster_id}", cluster)
        promoted, suppression = TemporalSequenceCorrelator.evaluate_promotion_gate(cluster, stages)
        if promoted:
            promoted_incidents += 1
        elif suppression:
            suppression_records.append(suppression)

    assert promoted_incidents == 0, "Benign dataset must NOT generate high-confidence incidents!"
    assert len(suppression_records) > 0
    for s in suppression_records:
        assert s.reason_code == "INSUFFICIENT_CHAIN_EVIDENCE"
        assert len(s.missing_requirements) > 0


def test_partial_attack_degradation():
    """
    TEST 3: Partial attack (missing USB copy).
    Expectation: Removable-media copy stage is absent and sequence score is reduced.
    """
    report = ingest_jsonl_file(DATA_DIR / "attack_partial.jsonl")
    all_signals = []
    for ev in report.events:
        all_signals.extend(AtomicRuleDetector.evaluate_event(ev))

    clusters = TemporalSequenceCorrelator.cluster_events_and_signals(report.events, all_signals)
    u42_cluster = next((c for c in clusters if c.primary_entity == "user-42"), None)
    assert u42_cluster is not None

    stages = TemporalSequenceCorrelator.build_attack_stages("inc-partial", u42_cluster)
    seq_score = TemporalSequenceCorrelator.calculate_sequence_score(stages, u42_cluster.events)

    # Exfiltration / USB copy was omitted, so score is lower than full attack (0.9+)
    assert seq_score < 0.85
    # Verify no stage claims completed USB copy
    all_reasons = []
    for s in stages:
        all_reasons.extend(s.reason_codes)
    assert "USB_COPY" not in all_reasons


def test_reversed_event_order_penalized():
    """
    TEST 4: Reversed event order.
    Expectation: Sequence score drops and promotion gate catches the temporal inconsistency.
    """
    report = ingest_jsonl_file(DATA_DIR / "attack_insider_usb.jsonl")
    all_signals = []
    for ev in report.events:
        all_signals.extend(AtomicRuleDetector.evaluate_event(ev))

    clusters = TemporalSequenceCorrelator.cluster_events_and_signals(report.events, all_signals)
    u42_cluster = next((c for c in clusters if c.primary_entity == "user-42"), None)
    assert u42_cluster is not None

    stages = TemporalSequenceCorrelator.build_attack_stages("inc-reversed", u42_cluster)
    # Manually reverse stages
    reversed_stages = list(reversed(stages))

    promoted, suppression = TemporalSequenceCorrelator.evaluate_promotion_gate(u42_cluster, reversed_stages)
    assert promoted is False
    assert suppression is not None
    assert any("chronological" in r for r in suppression.missing_requirements)
