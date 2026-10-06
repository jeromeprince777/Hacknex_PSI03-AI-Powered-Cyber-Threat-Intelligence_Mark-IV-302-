"""
Tests for FastAPI Endpoints, Copilot Generation, and Anti-Hallucination Verification.
Verifies compliance with docs/05_TEST_PLAN.md (Tests 1, 2, 5, 6) and docs/04_DATA_API_CONTRACTS.md.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_health():
    """Verify health endpoint returns 200 and version info."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "ThreatWeave"
    assert data["analysis_version"] == "0.1.0"


def test_api_scenarios_catalog():
    """Verify scenarios catalog lists pre-packaged scenarios."""
    resp = client.get("/api/datasets/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scenarios"]) >= 4
    sc_ids = [s["id"] for s in data["scenarios"]]
    assert "attack_insider_usb" in sc_ids
    assert "benign_admin" in sc_ids


def test_api_run_analysis_canonical_attack():
    """Verify running analysis on canonical attack creates incident and returns metrics."""
    resp = client.post("/api/analysis/run", json={"scenario_name": "attack_insider_usb.jsonl"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["valid_events"] == 15
    assert data["incidents_created"] >= 1


def test_api_get_incidents():
    """Verify fetching ranked incidents."""
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_incidents"] >= 1
    first_inc = data["incidents"][0]
    assert first_inc["risk_index"] >= 75
    assert first_inc["severity"] == "high"
    assert "signal_score" in first_inc["risk_components"]
    assert "sequence_score" in first_inc["risk_components"]


def test_api_get_incident_detail_and_evidence():
    """Verify fetching incident details, timeline, and evidence pack."""
    inc_list = client.get("/api/incidents").json()
    inc_id = inc_list["incidents"][0]["incident_id"]

    # Incident detail
    det_resp = client.get(f"/api/incidents/{inc_id}")
    assert det_resp.status_code == 200
    det_data = det_resp.json()
    assert len(det_data["stages"]) >= 3

    # Evidence pack
    ev_resp = client.get(f"/api/incidents/{inc_id}/evidence")
    assert ev_resp.status_code == 200
    ev_data = ev_resp.json()
    assert len(ev_data["timeline"]) >= 3
    assert len(ev_data["approved_actions"]) >= 2
    assert "user-42" in ev_data["entities"]


def test_api_get_incident_graph():
    """Verify fetching 1-hop subgraph in Cytoscape/React Flow format."""
    inc_list = client.get("/api/incidents").json()
    inc_id = inc_list["incidents"][0]["incident_id"]

    graph_resp = client.get(f"/api/incidents/{inc_id}/graph")
    assert graph_resp.status_code == 200
    graph_data = graph_resp.json()
    assert graph_data["total_nodes"] > 5
    assert graph_data["total_edges"] > 5
    assert any(n["type"] == "Incident" for n in graph_data["nodes"])
    assert any(n["type"] == "Stage" for n in graph_data["nodes"])


def test_api_copilot_verified_explanation():
    """Verify Copilot generates a verified explanation citing real event IDs."""
    inc_list = client.get("/api/incidents").json()
    inc_id = inc_list["incidents"][0]["incident_id"]

    resp = client.post("/api/copilot/explain", json={
        "incident_id": inc_id,
        "question": "Why is this incident high risk?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["verified"] is True
    assert data["verification_status"] == "VERIFIED"
    assert data["rejection_reason"] is None
    assert data["explanation"] is not None

    exp = data["explanation"]
    assert exp["confidence"] in {"low", "medium", "high"}
    assert len(exp["stage_explanations"]) >= 2
    # Verify citations are real event IDs
    all_cited = [eid for stg in exp["stage_explanations"] for eid in stg["evidence_event_ids"]]
    assert "evt-003" in all_cited or "evt-008" in all_cited


def test_copilot_hallucinated_event_id_rejected():
    """
    TEST 5 from docs/05_TEST_PLAN.md:
    Inject a hallucinated event ID into Copilot output.
    Expectation: Verifier REJECTS the response and displays rejection reason.
    """
    inc_list = client.get("/api/incidents").json()
    inc_id = inc_list["incidents"][0]["incident_id"]

    resp = client.post("/api/copilot/explain", json={
        "incident_id": inc_id,
        "question": "Why is this incident high risk?",
        "inject_fake_event_id": "evt-fake-9999",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["verified"] is False
    assert data["verification_status"] == "REJECTED"
    assert "unknown_evidence_event_id" in data["rejection_reason"]
    assert "evt-fake-9999" in data["rejection_reason"]
    assert data["explanation"] is None  # Never display rejected explanation as verified!


def test_copilot_hallucinated_action_id_rejected():
    """
    TEST 6 from docs/05_TEST_PLAN.md:
    Inject an unauthorized response action ID into Copilot output.
    Expectation: Verifier REJECTS the response.
    """
    inc_list = client.get("/api/incidents").json()
    inc_id = inc_list["incidents"][0]["incident_id"]

    resp = client.post("/api/copilot/explain", json={
        "incident_id": inc_id,
        "question": "What actions should we take?",
        "inject_fake_action_id": "nuke-all-infrastructure",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["verified"] is False
    assert data["verification_status"] == "REJECTED"
    assert "unknown_action_id" in data["rejection_reason"]
    assert "nuke-all-infrastructure" in data["rejection_reason"]
    assert data["explanation"] is None


def test_api_benign_scenario_no_high_risk_and_suppression():
    """
    TEST 2: Benign scenario replay via API.
    Expectation: 0 high-risk incidents created, suppression records stored and visible.
    """
    resp = client.post("/api/analysis/run", json={"scenario_name": "benign_admin.jsonl"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["incidents_created"] == 0
    assert data["suppressed_clusters"] >= 1

    # Check suppression endpoint
    sup_resp = client.get("/api/incidents/suppression")
    assert sup_resp.status_code == 200
    sup_data = sup_resp.json()
    assert sup_data["total_suppressed"] >= 1
    assert any("INSUFFICIENT_CHAIN_EVIDENCE" in s["reason_code"] for s in sup_data["suppression_records"])
