"""
Analyst Copilot API Routes.
Provides evidence-bounded AI explanations with deterministic anti-hallucination verification.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.storage.repository import StorageRepository
from app.evidence.pack import EvidencePackBuilder
from app.copilot.engine import CopilotEngine

router = APIRouter(prefix="/copilot", tags=["Copilot"])


class CopilotExplainRequest(BaseModel):
    incident_id: str
    question: str = "Why is this incident high risk?"
    inject_fake_event_id: Optional[str] = None
    inject_fake_action_id: Optional[str] = None


@router.post("/explain")
def explain_incident(req: CopilotExplainRequest):
    """
    Produces an evidence-grounded AI Analyst explanation for an incident.
    Always validated by the anti-hallucination verifier prior to return.
    """
    repo = StorageRepository()
    incident = repo.get_incident(req.incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident '{req.incident_id}' not found.")

    stages = repo.get_incident_stages(req.incident_id)
    all_evidence_ids = incident.evidence_event_ids
    events = repo.get_events_by_ids(all_evidence_ids)
    signals = repo.get_signals_by_event_ids(all_evidence_ids)

    evidence_pack = EvidencePackBuilder.build_evidence_pack(
        incident=incident,
        stages=stages,
        evidence_events=events,
        signals=signals,
    )

    result = CopilotEngine.generate_explanation(
        evidence_pack=evidence_pack,
        question=req.question,
        inject_fake_event_id=req.inject_fake_event_id,
        inject_fake_action_id=req.inject_fake_action_id,
    )

    return {
        "incident_id": req.incident_id,
        "question": req.question,
        "provider": result.get("provider", "deterministic"),
        "verified": result["verified"],
        "verification_status": result["verification_status"],
        "rejection_reason": result["rejection_reason"],
        "explanation": result["response"],
        "evidence_pack": evidence_pack if result["verified"] else None,
    }
