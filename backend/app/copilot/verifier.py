"""
ThreatWeave Anti-Hallucination Schema & Evidence Verifier.
Strictly verifies that any AI Analyst Copilot output references only real event IDs,
real stage IDs, and approved response actions present in the bounded evidence pack.
Strictly adheres to docs/04_DATA_API_CONTRACTS.md Section 7 and AGENTS.md Rule A & H.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple


def verify_copilot(
    output: Any,
    evidence_pack: Any,
) -> Tuple[bool, Optional[str]]:
    """
    Deterministically validates model output against the supplied bounded evidence pack.
    Returns (True, None) if verified, or (False, rejection_reason) if rejected.
    Guaranteed never to raise uncaught exceptions on malformed model outputs.
    """
    try:
        # Validate root payload types
        if not isinstance(output, dict):
            return False, "invalid_payload_type: Output is not a valid dictionary"

        if not isinstance(evidence_pack, dict):
            return False, "invalid_evidence_pack: Evidence pack is not a valid dictionary"

        # 1. Summary validation
        summary = output.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            return False, "missing_summary: Summary must be a non-empty string"

        # 2. Confidence validation
        confidence = output.get("confidence")
        if confidence not in {"low", "medium", "high"}:
            return False, f"invalid_confidence: Invalid confidence level '{confidence}' (must be low, medium, or high)"

        # 3. Extract verified universe from evidence pack
        timeline_events = evidence_pack.get("timeline")
        if not isinstance(timeline_events, list):
            timeline_events = []
        valid_event_ids: Set[str] = {
            e["event_id"]
            for e in timeline_events
            if isinstance(e, dict) and "event_id" in e and isinstance(e["event_id"], str)
        }

        stages = evidence_pack.get("stages")
        if not isinstance(stages, list):
            stages = []
        valid_stage_ids: Set[str] = {
            s["stage_id"]
            for s in stages
            if isinstance(s, dict) and "stage_id" in s and isinstance(s["stage_id"], str)
        }

        # Map stage_id to authorized evidence event_ids
        stage_to_events: Dict[str, Set[str]] = {}
        for s in stages:
            if isinstance(s, dict) and "stage_id" in s and isinstance(s["stage_id"], str):
                stg_id = s["stage_id"]
                ev_ids = s.get("evidence_event_ids", [])
                if isinstance(ev_ids, list):
                    stage_to_events[stg_id] = {eid for eid in ev_ids if isinstance(eid, str)}
                else:
                    stage_to_events[stg_id] = set()

        approved_actions = evidence_pack.get("approved_actions")
        if not isinstance(approved_actions, list):
            approved_actions = []
        valid_action_ids: Set[str] = {
            a["action_id"]
            for a in approved_actions
            if isinstance(a, dict) and "action_id" in a and isinstance(a["action_id"], str)
        }

        # 4. Validate stage explanations
        if "stage_explanations" not in output:
            return False, "missing_stage_explanations: Output is missing 'stage_explanations' field"

        stage_explanations = output.get("stage_explanations")
        if not isinstance(stage_explanations, list):
            return False, f"invalid_stage_explanations_type: stage_explanations must be a list, got {type(stage_explanations).__name__}"

        for stg_exp in stage_explanations:
            # Check A & B: string instead of dict, or null stage explanation
            if not isinstance(stg_exp, dict):
                return False, f"invalid_stage_explanation_type: Each stage explanation must be a dictionary, got {type(stg_exp).__name__}"

            # Check E: unknown stage
            stage_id = stg_exp.get("stage_id")
            if not stage_id or not isinstance(stage_id, str) or stage_id not in valid_stage_ids:
                return False, f"unknown_stage_id: Stage '{stage_id}' does not exist in incident evidence"

            # Check C: missing evidence_event_ids
            if "evidence_event_ids" not in stg_exp:
                return False, f"missing_evidence_ids: Stage '{stage_id}' is missing 'evidence_event_ids' field"

            # Check D: wrong evidence_event_ids type
            evidence_event_ids = stg_exp.get("evidence_event_ids")
            if not isinstance(evidence_event_ids, list):
                return False, f"invalid_evidence_ids_type: Stage '{stage_id}' evidence_event_ids must be a list, got {type(evidence_event_ids).__name__}"

            if not evidence_event_ids:
                return False, f"missing_evidence_ids: Stage '{stage_id}' has an empty evidence event list"

            # Check F: unknown event & misattributed event
            for eid in evidence_event_ids:
                if not isinstance(eid, str):
                    return False, f"invalid_evidence_id_type: Evidence event ID must be a string, got {type(eid).__name__}"
                if eid not in valid_event_ids:
                    return False, f"unknown_evidence_event_id: Event '{eid}' was never observed in telemetry"
                if eid not in stage_to_events.get(stage_id, set()):
                    return False, f"misattributed_evidence: Event '{eid}' is not associated with stage '{stage_id}'"

        # 5. Validate recommended actions
        recommended_actions = output.get("recommended_actions")
        if recommended_actions is not None:
            if not isinstance(recommended_actions, list):
                return False, f"invalid_recommended_actions_type: recommended_actions must be a list, got {type(recommended_actions).__name__}"

            for act in recommended_actions:
                if not isinstance(act, dict):
                    return False, f"invalid_recommended_action_type: Each recommended action must be a dictionary, got {type(act).__name__}"

                # Check G: unknown action
                action_id = act.get("action_id")
                if not action_id or not isinstance(action_id, str) or action_id not in valid_action_ids:
                    return False, f"unknown_action_id: Action '{action_id}' is not in the approved response catalog"

        return True, None

    except Exception as exc:
        return False, f"verifier_internal_error: {str(exc)}"
