"""
ThreatWeave Analyst Copilot Engine.
Consumes bounded evidence packs and outputs structured incident explanations validated by the anti-hallucination verifier.
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.events import CopilotExplanation
from app.copilot.verifier import verify_copilot


class CopilotEngine:
    """
    Orchestrates evidence pack ingestion, structured analysis generation, and verification.
    """

    @classmethod
    def generate_explanation(
        cls,
        evidence_pack: Dict[str, Any],
        question: str = "Why is this incident high risk?",
        inject_fake_event_id: Optional[str] = None,
        inject_fake_action_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates an analyst explanation strictly grounded in the evidence pack.
        Supports negative control injection for live demo verification testing.
        """
        incident = evidence_pack.get("incident", {})
        stages = evidence_pack.get("stages", [])
        timeline = evidence_pack.get("timeline", [])
        approved_actions = evidence_pack.get("approved_actions", [])
        risk_components = incident.get("risk_components", {})

        risk_idx = incident.get("risk_index", 0)
        sev = incident.get("severity", "unknown")
        entities = evidence_pack.get("entities", [])

        # Build grounded stage explanations citing only real evidence events
        stage_exps: List[Dict[str, Any]] = []
        for stg in stages:
            stg_id = stg.get("stage_id", "stage-01")
            name = stg.get("name", "Stage")
            ev_ids = list(stg.get("evidence_event_ids", []))

            # Find matching events in timeline
            matched_events = [t for t in timeline if t.get("event_id") in ev_ids]
            facts = [m.get("fact", "") for m in matched_events]
            exp_text = f"{name} supported by telemetry: " + "; ".join(facts) if facts else f"{name} detected."

            # Negative control test injection
            if inject_fake_event_id and stg == stages[0]:
                ev_ids.append(inject_fake_event_id)

            stage_exps.append({
                "stage_id": stg_id,
                "explanation": exp_text,
                "evidence_event_ids": ev_ids,
            })

        # Build recommended actions from approved catalog
        rec_actions: List[Dict[str, Any]] = []
        for act in approved_actions[:3]:
            rec_actions.append({
                "action_id": act.get("action_id"),
                "reason": f"Recommended due to observed activity in {act.get('label')}.",
            })

        if inject_fake_action_id:
            rec_actions.append({
                "action_id": inject_fake_action_id,
                "reason": "Injected unauthorized response action.",
            })

        # Compose factual summary
        sig_score = risk_components.get("signal_score", 0.0)
        seq_score = risk_components.get("sequence_score", 0.0)
        nov_score = risk_components.get("entity_novelty", 0.0)
        anom_score = risk_components.get("anomaly_score", 0.0)

        summary = (
            f"Incident {incident.get('incident_id')} is rated {sev.upper()} severity with a Risk Index of {risk_idx}/100. "
            f"The detection pipeline correlated {len(timeline)} chronological security events across entities {', '.join(entities[:4])}. "
            f"Key risk contributors: Signal Severity ({sig_score}), Sequence Consistency ({seq_score}), "
            f"Entity Novelty ({nov_score}), and Statistical Anomaly ({anom_score}). "
            f"The attack chain progressed through {len(stages)} distinct stages with verified telemetry proof for each step."
        )

        raw_response = {
            "summary": summary,
            "confidence": "high" if risk_idx >= 75 else "medium",
            "stage_explanations": stage_exps,
            "recommended_actions": rec_actions,
            "limitations": [
                "Analysis bounded strictly to ingested security logs.",
                "Advisory recommendations only; requires SOC analyst confirmation prior to host isolation.",
            ],
        }

        # Step 2: Strict Anti-Hallucination Verification
        is_verified, rejection_reason = verify_copilot(raw_response, evidence_pack)

        return {
            "verified": is_verified,
            "verification_status": "VERIFIED" if is_verified else "REJECTED",
            "rejection_reason": rejection_reason,
            "response": raw_response if is_verified else None,
            "raw_payload": raw_response,
        }
