"""
Incident Investigation & Telemetry API Routes.
Provides auditable endpoints for case management, timeline inspection, graph visualization, and evidence.
"""

from fastapi import APIRouter, HTTPException

from app.storage.repository import StorageRepository
from app.graph.builder import EntityGraphBuilder
from app.evidence.pack import EvidencePackBuilder

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("")
def list_incidents():
    """Returns all ranked incidents from storage."""
    repo = StorageRepository()
    incidents = repo.list_incidents()
    return {
        "total_incidents": len(incidents),
        "incidents": [inc.model_dump() for inc in incidents],
    }


@router.get("/suppression")
def list_suppression_records():
    """Returns false-positive suppression audit records."""
    repo = StorageRepository()
    records = repo.list_suppression_records()
    return {
        "total_suppressed": len(records),
        "suppression_records": [r.model_dump() for r in records],
    }


@router.get("/{incident_id}")
def get_incident_detail(incident_id: str):
    """Returns incident header, risk breakdown, and stages."""
    repo = StorageRepository()
    incident = repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    stages = repo.get_incident_stages(incident_id)
    return {
        "incident": incident.model_dump(),
        "stages": [s.model_dump() for s in stages],
    }


@router.get("/{incident_id}/evidence")
def get_incident_evidence_pack(incident_id: str):
    """
    Returns the complete sealed Evidence Pack for an incident,
    including timeline, raw & normalized telemetry, linked entities, and approved actions.
    """
    repo = StorageRepository()
    incident = repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    stages = repo.get_incident_stages(incident_id)
    all_evidence_ids = incident.evidence_event_ids
    events = repo.get_events_by_ids(all_evidence_ids)
    signals = repo.get_signals_by_event_ids(all_evidence_ids)

    evidence_pack = EvidencePackBuilder.build_evidence_pack(
        incident=incident,
        stages=stages,
        evidence_events=events,
        signals=signals,
    )
    return evidence_pack


@router.get("/{incident_id}/graph")
def get_incident_entity_graph(incident_id: str):
    """
    Returns a clean, focused 1-hop incident subgraph in Cytoscape.js / React Flow format.
    """
    repo = StorageRepository()
    incident = repo.get_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found.")

    stages = repo.get_incident_stages(incident_id)
    events = repo.get_events_by_ids(incident.evidence_event_ids)

    builder = EntityGraphBuilder()
    builder.add_events_batch(events)

    subgraph = builder.extract_incident_subgraph(
        incident_id=incident_id,
        stages=stages,
        evidence_events=events,
    )
    return subgraph
