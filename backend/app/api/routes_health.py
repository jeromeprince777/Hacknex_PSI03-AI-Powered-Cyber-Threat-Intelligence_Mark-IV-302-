"""
Health & Service Diagnostic API Routes.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Returns platform operational health and engine versions."""
    return {
        "status": "ok",
        "service": "ThreatWeave",
        "version": "0.1.0",
        "analysis_version": "0.1.0",
        "rule_version": "demo-2026-01",
        "schema_version": "event-v1",
        "prompt_version": "copilot-v1",
    }
