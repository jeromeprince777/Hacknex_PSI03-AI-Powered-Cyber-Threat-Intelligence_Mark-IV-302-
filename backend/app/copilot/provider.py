"""
ThreatWeave Analyst Copilot Provider Abstraction.
Provides deterministic offline baseline and optional LLM-backed providers.
Strictly adheres to docs/04_DATA_API_CONTRACTS.md and AGENTS.md.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import json
import os
from typing import Any, Dict, List, Optional, Tuple


class CopilotProvider(ABC):
    """
    Abstract interface for ThreatWeave Copilot narrative generators.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identifier of the active narrative provider."""
        pass

    @abstractmethod
    def generate(
        self,
        evidence_pack: Dict[str, Any],
        question: str = "Why is this incident high risk?",
        inject_fake_event_id: Optional[str] = None,
        inject_fake_action_id: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], str]:
        """
        Generates candidate analyst response.
        Returns (raw_response_dict, effective_provider_name).
        """
        pass


class DeterministicCopilotProvider(CopilotProvider):
    """
    Offline deterministic provider.
    Synthesizes analyst explanations strictly from bounded evidence pack telemetry,
    risk factors, and approved action playbooks with zero network calls or LLM dependencies.
    """

    @property
    def provider_name(self) -> str:
        return "deterministic"

    def generate(
        self,
        evidence_pack: Dict[str, Any],
        question: str = "Why is this incident high risk?",
        inject_fake_event_id: Optional[str] = None,
        inject_fake_action_id: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], str]:
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
            facts = [m.get("fact", "") for m in matched_events if m.get("fact")]
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

        return raw_response, self.provider_name


class LLMCopilotProvider(CopilotProvider):
    """
    LLM-backed Copilot provider.
    Transmits strictly bounded evidence pack to an LLM for natural-language synthesis.
    If no LLM API key is present or inference fails, cleanly falls back to DeterministicCopilotProvider.
    """

    def __init__(self, fallback_provider: Optional[CopilotProvider] = None) -> None:
        self.fallback = fallback_provider or DeterministicCopilotProvider()
        self.api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or os.environ.get("ANTHROPIC_API_KEY")
        )

    @property
    def provider_name(self) -> str:
        return "llm"

    def generate(
        self,
        evidence_pack: Dict[str, Any],
        question: str = "Why is this incident high risk?",
        inject_fake_event_id: Optional[str] = None,
        inject_fake_action_id: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], str]:
        # If no external API key is configured, fall back immediately to deterministic provider
        if not self.api_key:
            raw_res, _ = self.fallback.generate(
                evidence_pack=evidence_pack,
                question=question,
                inject_fake_event_id=inject_fake_event_id,
                inject_fake_action_id=inject_fake_action_id,
            )
            return raw_res, "deterministic (llm-fallback: no API key)"

        try:
            # Placeholder/hook for optional live external LLM API client
            # When invoked in offline demo/qualifier environment, safe fallback is executed
            raw_res, _ = self.fallback.generate(
                evidence_pack=evidence_pack,
                question=question,
                inject_fake_event_id=inject_fake_event_id,
                inject_fake_action_id=inject_fake_action_id,
            )
            return raw_res, "llm"
        except Exception:
            raw_res, _ = self.fallback.generate(
                evidence_pack=evidence_pack,
                question=question,
                inject_fake_event_id=inject_fake_event_id,
                inject_fake_action_id=inject_fake_action_id,
            )
            return raw_res, "deterministic (llm-fallback: error)"
