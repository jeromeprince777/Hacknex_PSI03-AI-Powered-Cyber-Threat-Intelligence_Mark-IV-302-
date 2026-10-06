"""
Tests for Entity Graph Builder, Risk Engine, Evidence Pack, and SQLite Persistence.
Verifies compliance with docs/02_TECHNICAL_PRD.md and docs/04_DATA_API_CONTRACTS.md.
"""

from pathlib import Path
import tempfile
import pytest

from app.schemas.events import (
    Incident,
    RiskComponents,
    Signal,
    Stage,
    SuppressionRecord,
    ThreatWeaveEvent,
)
from app.ingestion.validator import ingest_jsonl_file
from app.detectors.rules import AtomicRuleDetector
from app.detectors.novelty import EntityNoveltyScorer
from app.detectors.sequence import TemporalSequenceCorrelator
from app.graph.builder import EntityGraphBuilder
from app.scoring.risk import RiskEngine, RobustAnomalyScorer as AnomalyScorer
from app.evidence.pack import EvidencePackBuilder, APPROVED_ACTION_CATALOG
from app.storage.repository import StorageRepository

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "scenarios"


def test_entity_graph_builder_and_subgraph():
    """Verify NetworkX entity graph construction and focused 1-hop subgraph extraction."""
    report = ingest_jsonl_file(DATA_DIR / "attack_insider_usb.jsonl")
    builder = EntityGraphBuilder()
    builder.add_events_batch(report.events)

    # Check that key entity nodes exist
    assert builder.graph.has_node("user:user-42")
    assert builder.graph.has_node("device:device-17")
    assert builder.graph.has_node("ip:203.0.113.10")
    assert builder.graph.has_node("resource:Finance/Q4/payroll.xlsx")
    assert builder.graph.has_node("removable:usb-kingston-992")

    # Correlate stages for incident
    signals = []
    for ev in report.events:
        signals.extend(AtomicRuleDetector.evaluate_event(ev))
    clusters = TemporalSequenceCorrelator.cluster_events_and_signals(report.events, signals)
    u42_cluster = next(c for c in clusters if c.primary_entity == "user-42")
    stages = TemporalSequenceCorrelator.build_attack_stages("inc-001", u42_cluster)

    # Extract 1-hop incident subgraph
    subgraph = builder.extract_incident_subgraph("inc-001", stages, u42_cluster.events)
    assert subgraph["incident_id"] == "inc-001"
    assert subgraph["total_nodes"] > 5
    assert subgraph["total_edges"] > 5

    node_types = {n["type"] for n in subgraph["nodes"]}
    assert "Incident" in node_types
    assert "Stage" in node_types
    assert "User" in node_types
    assert "Device" in node_types


def test_risk_engine_calculation():
    """Verify deterministic Risk Index computation and component weighting."""
    report = ingest_jsonl_file(DATA_DIR / "attack_insider_usb.jsonl")
    signals = []
    for ev in report.events:
        signals.extend(AtomicRuleDetector.evaluate_event(ev))

    clusters = TemporalSequenceCorrelator.cluster_events_and_signals(report.events, signals)
    u42_cluster = next(c for c in clusters if c.primary_entity == "user-42")
    stages = TemporalSequenceCorrelator.build_attack_stages("inc-001", u42_cluster)

    seq_score = TemporalSequenceCorrelator.calculate_sequence_score(stages, u42_cluster.events)
    novelty_scorer = EntityNoveltyScorer()
    nov_score, _ = novelty_scorer.score_event_cluster(u42_cluster.events)

    engine = RiskEngine()
    risk_idx, severity, components = engine.calculate_risk(
        signals=u42_cluster.signals,
        sequence_score=seq_score,
        entity_novelty=nov_score,
        events=u42_cluster.events,
    )

    # Canonical insider attack should land in High severity (>= 75)
    assert 75 <= risk_idx <= 100
    assert severity == "high"
    assert components.signal_score >= 0.70
    assert components.sequence_score >= 0.85
    assert components.entity_novelty >= 0.70
    assert components.anomaly_score >= 0.60


def test_anomaly_scorer_isolation_forest():
    """Verify statistical anomaly detection distinguishes normal from attack sequences."""
    scorer = AnomalyScorer()

    benign_report = ingest_jsonl_file(DATA_DIR / "benign_admin.jsonl")
    attack_report = ingest_jsonl_file(DATA_DIR / "attack_insider_usb.jsonl")

    benign_score = scorer.calculate_anomaly_score(benign_report.events)
    attack_score = scorer.calculate_anomaly_score(attack_report.events)

    assert attack_score > benign_score
    assert attack_score >= 0.60


def test_evidence_pack_builder():
    """Verify bounded evidence pack structure, action catalog filtering, and timeline facts."""
    report = ingest_jsonl_file(DATA_DIR / "attack_insider_usb.jsonl")
    signals = []
    for ev in report.events:
        signals.extend(AtomicRuleDetector.evaluate_event(ev))

    clusters = TemporalSequenceCorrelator.cluster_events_and_signals(report.events, signals)
    u42_cluster = next(c for c in clusters if c.primary_entity == "user-42")
    stages = TemporalSequenceCorrelator.build_attack_stages("inc-001", u42_cluster)

    inc = Incident(
        incident_id="inc-001",
        status="open",
        severity="high",
        risk_index=88,
        risk_components=RiskComponents(
            signal_score=0.86,
            sequence_score=0.92,
            entity_novelty=0.78,
            anomaly_score=0.71,
        ),
        entity_ids=["user-42", "device-17", "203.0.113.10"],
        stage_ids=[s.stage_id for s in stages],
        evidence_event_ids=list(dict.fromkeys(e.event_id for e in u42_cluster.events)),
    )

    pack = EvidencePackBuilder.build_evidence_pack(
        incident=inc,
        stages=stages,
        evidence_events=u42_cluster.events,
        signals=u42_cluster.signals,
    )

    assert pack["incident"]["incident_id"] == "inc-001"
    assert len(pack["timeline"]) == len(u42_cluster.events)
    assert len(pack["stages"]) == len(stages)
    assert len(pack["approved_actions"]) >= 2

    # Verify approved action IDs match catalog
    valid_action_ids = {a["action_id"] for a in APPROVED_ACTION_CATALOG}
    for action in pack["approved_actions"]:
        assert action["action_id"] in valid_action_ids

    # Verify timeline facts cite real entities
    first_fact = pack["timeline"][0]["fact"]
    assert "user-42" in first_fact


def test_sqlite_repository_persistence():
    """Verify SQLite repository schema creation, insert, and query round-trip."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tf:
        temp_db_path = tf.name

    repo = StorageRepository(db_path=temp_db_path)

    report = ingest_jsonl_file(DATA_DIR / "attack_insider_usb.jsonl")
    repo.save_events(report.events)

    events_retrieved = repo.get_events_by_ids(["evt-001", "evt-003", "evt-011"])
    assert len(events_retrieved) == 3
    assert {e.event_id for e in events_retrieved} == {"evt-001", "evt-003", "evt-011"}

    # Save incident and stages
    stage1 = Stage(
        stage_id="stage-01",
        incident_id="inc-test-01",
        name="Initial Access",
        sequence_index=1,
        start_time="2026-10-06T09:41:12Z",
        end_time="2026-10-06T09:41:12Z",
        evidence_event_ids=["evt-003"],
        reason_codes=["AUTH_NEW_LOCATION"],
    )
    inc = Incident(
        incident_id="inc-test-01",
        status="open",
        severity="high",
        risk_index=85,
        risk_components=RiskComponents(
            signal_score=0.8,
            sequence_score=0.9,
            entity_novelty=0.8,
            anomaly_score=0.7,
        ),
        entity_ids=["user-42", "device-17"],
        stage_ids=["stage-01"],
        evidence_event_ids=["evt-003"],
    )
    repo.save_incident(inc, [stage1])

    inc_fetched = repo.get_incident("inc-test-01")
    assert inc_fetched is not None
    assert inc_fetched.risk_index == 85
    assert inc_fetched.severity == "high"

    stages_fetched = repo.get_incident_stages("inc-test-01")
    assert len(stages_fetched) == 1
    assert stages_fetched[0].stage_id == "stage-01"
    assert stages_fetched[0].evidence_event_ids == ["evt-003"]

    # Save suppression record
    sup = SuppressionRecord(
        suppression_id="sup-test-01",
        target_id="cluster-99",
        reason_code="INSUFFICIENT_CHAIN_EVIDENCE",
        missing_requirements=["requires >= 2 distinct attack stages"],
        details={"events_count": 1},
    )
    repo.save_suppression_record(sup)

    sups_fetched = repo.list_suppression_records()
    assert len(sups_fetched) >= 1
    assert sups_fetched[0].suppression_id == "sup-test-01"
