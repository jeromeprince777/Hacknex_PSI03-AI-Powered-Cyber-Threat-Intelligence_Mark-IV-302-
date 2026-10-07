"""
ThreatWeave Analyst Copilot Engine.
Consumes bounded evidence packs and outputs structured incident explanations validated by the anti-hallucination verifier.
Strictly adheres to docs/04_DATA_API_CONTRACTS.md and AGENTS.md.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.events import CopilotExplanation
from app.copilot.verifier import verify_copilot
from app.copilot.provider import CopilotProvider, DeterministicCopilotProvider, LLMCopilotProvider


class CopilotEngine:
    """
    Orchestrates evidence pack ingestion, structured analysis generation via
    provider abstraction, and deterministic anti-hallucination verification.
    """

    @classmethod
    def get_provider(cls) -> CopilotProvider:
        """Resolves configured CopilotProvider from environment."""
        provider_mode = os.environ.get("COPILOT_PROVIDER", "deterministic").strip().lower()
        if provider_mode == "llm":
            return LLMCopilotProvider()
        return DeterministicCopilotProvider()

    @classmethod
    def generate_explanation(
        cls,
        evidence_pack: Dict[str, Any],
        question: str = "Why is this incident high risk?",
        inject_fake_event_id: Optional[str] = None,
        inject_fake_action_id: Optional[str] = None,
        provider: Optional[CopilotProvider] = None,
    ) -> Dict[str, Any]:
        """
        Generates an analyst explanation strictly grounded in the evidence pack.
        Delegates synthesis to the active CopilotProvider, then runs mandatory
        anti-hallucination verification against the bounded evidence pack.
        """
        active_provider = provider or cls.get_provider()

        raw_response, effective_provider = active_provider.generate(
            evidence_pack=evidence_pack,
            question=question,
            inject_fake_event_id=inject_fake_event_id,
            inject_fake_action_id=inject_fake_action_id,
        )

        # Step 2: Strict Anti-Hallucination Verification
        is_verified, rejection_reason = verify_copilot(raw_response, evidence_pack)

        return {
            "provider": effective_provider,
            "verified": is_verified,
            "verification_status": "VERIFIED" if is_verified else "REJECTED",
            "rejection_reason": rejection_reason,
            "response": raw_response if is_verified else None,
            "raw_payload": raw_response,
        }
