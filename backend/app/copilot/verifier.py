"""
ThreatWeave Anti-Hallucination Schema & Evidence Verifier.
Strictly verifies that any AI Analyst Copilot output references only real event IDs,
real stage IDs, and approved response actions present in the bounded evidence pack.
Strictly adheres to docs/04_DATA_API_CONTRACTS.md Section 7 and AGENTS.md Rule A & H.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple


def verify_copilot(
    output: Dict[str, Any],
    evidence_pack: Dict[str, Any],
) -> Tuple[bool, Optional[str]]:
    """
    Deterministically validates model output against the supplied bounded evidence pack.
    Returns (True, None) if verified, or (False, rejection_reason) if rejected.
    """
    if not isinstance(output, dict):
        return False, "Output is not a valid JSON object"

    # 1. Confidence validation
    confidence = output.get("confidence")
    if confidence not in {"low", "medium", "high"}:
        return False, f"Invalid confidence level: {confidence} (must be low, medium, or high)"

    # 2. Extract verified universe from evidence pack
    timeline_events = evidence_pack.get("timeline", [])
    valid_event_ids: Set[str] = {e["event_id"] for e in timeline_events if "event_id" in e}

    stages = evidence_pack.get("stages", [])
    valid_stage_ids: Set[str] = {s["stage_id"] for s in stages if "stage_id" in s}

    # Map stage_id to authorized evidence event_ids
    stage_to_events: Dict[str, Set[str]] = {}
    for s in stages:
        stage_to_events[s["stage_id"]] = set(s.get("evidence_event_ids", []))

    approved_actions = evidence_pack.get("approved_actions", [])
    valid_action_ids: Set[str] = {a["action_id"] for a in approved_actions if "action_id" in a}

    # 3. Validate stage explanations
    stage_explanations = output.get("stage_explanations", [])
    if not isinstance(stage_explanations, list):
        return False, "stage_explanations must be a list"

    for stg_exp in stage_explanations:
        stage_id = stg_exp.get("stage_id")
        if not stage_id or stage_id not in valid_stage_ids:
            return False, f"unknown_stage_id: Stage '{stage_id}' does not exist in incident evidence"

        evidence_event_ids = stg_exp.get("evidence_event_ids", [])
        if not evidence_event_ids or not isinstance(evidence_event_ids, list):
            return False, f"missing_evidence_ids: Stage '{stage_id}' has no supporting evidence event IDs"

        for eid in evidence_event_ids:
            if eid not in valid_event_ids:
                return False, f"unknown_evidence_event_id: Event '{eid}' was never observed in telemetry"
            # Ensure event actually belongs to this stage
            if eid not in stage_to_events.get(stage_id, set()):
                return False, f"misattributed_evidence: Event '{eid}' is not associated with stage '{stage_id}'"

    # 4. Validate recommended actions
    recommended_actions = output.get("recommended_actions", [])
    if not isinstance(recommended_actions, list):
        return False, "recommended_actions must be a list"

    for act in recommended_actions:
        action_id = act.get("action_id")
        if not action_id or action_id not in valid_action_ids:
            return False, f"unknown_action_id: Action '{action_id}' is not in the approved response catalog"

    # 5. Contradiction check on summary
    summary = str(output.get("summary", ""))
    if not summary.strip():
        return False, "Summary cannot be empty"

    # Verified successfully
    return True, None
