"""
ThreatWeave Canonical Data Schemas & API Contracts.
Strictly adheres to docs/04_DATA_API_CONTRACTS.md and AGENTS.md.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ThreatWeaveEvent(BaseModel):
    """
    Canonical Event Model representing normalized security log telemetry.
    """
    event_id: str = Field(..., description="Unique event identifier (e.g. evt-001)")
    timestamp: str = Field(..., description="ISO-8601 UTC timestamp")
    event_type: str = Field(..., description="Normalized event category")
    source: str = Field(..., description="Log source system (e.g. windows, vpn, edr)")
    action: Optional[str] = Field(default=None, description="Action taken (e.g. read, write, authenticate)")
    user_id: Optional[str] = Field(default=None, description="Associated user identity")
    device_id: Optional[str] = Field(default=None, description="Host or device identity")
    src_ip: Optional[str] = Field(default=None, description="Source IP address")
    dst_ip: Optional[str] = Field(default=None, description="Destination IP address")
    application: Optional[str] = Field(default=None, description="Application or executable name")
    resource: Optional[str] = Field(default=None, description="Target resource, file, or endpoint")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Source-specific key-value metadata")
    raw: Dict[str, Any] = Field(default_factory=dict, description="Original unparsed log record")

    @field_validator("event_id")
    @classmethod
    def validate_event_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("event_id cannot be empty")
        return v.strip()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("timestamp cannot be empty")
        # Ensure it conforms to ISO-8601
        try:
            # Handle Z suffix
            ts = v.replace("Z", "+00:00")
            datetime.fromisoformat(ts)
        except Exception as e:
            raise ValueError(f"timestamp must be a valid ISO-8601 string: {e}")
        return v.strip()

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("event_type cannot be empty")
        return v.strip()

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("source cannot be empty")
        return v.strip()


class Signal(BaseModel):
    """
    Atomic detection signal emitted by deterministic rules or baseline anomaly detectors.
    """
    signal_id: str
    event_id: str
    signal_type: str
    stage: str
    score: float = Field(..., ge=0.0, le=1.0)
    reason_code: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Stage(BaseModel):
    """
    Reconstructed attack chain stage backed by concrete event evidence IDs.
    """
    stage_id: str
    incident_id: str
    name: str
    sequence_index: int
    start_time: str
    end_time: str
    evidence_event_ids: List[str] = Field(..., min_length=1)
    reason_codes: List[str] = Field(default_factory=list)


class RiskComponents(BaseModel):
    """
    Transparent factor breakdown composing the deterministic Risk Index.
    Formula: clamp(100 * (0.35 * signal + 0.30 * sequence + 0.20 * novelty + 0.15 * anomaly))
    """
    signal_score: float = Field(..., ge=0.0, le=1.0)
    sequence_score: float = Field(..., ge=0.0, le=1.0)
    entity_novelty: float = Field(..., ge=0.0, le=1.0)
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "signal": 0.35,
            "sequence": 0.30,
            "novelty": 0.20,
            "anomaly": 0.15,
        }
    )


class Incident(BaseModel):
    """
    Correlated multi-stage security incident.
    """
    incident_id: str
    status: str = "open"
    severity: str = Field(..., pattern="^(informational|low|medium|high)$")
    risk_index: int = Field(..., ge=0, le=100)
    risk_components: RiskComponents
    entity_ids: List[str] = Field(default_factory=list)
    stage_ids: List[str] = Field(default_factory=list)
    evidence_event_ids: List[str] = Field(default_factory=list)
    analysis_version: str = "0.1.0"
    rule_version: str = "demo-2026-01"


class SuppressionRecord(BaseModel):
    """
    Audit record documenting why an isolated signal or cluster was not escalated to an incident.
    """
    suppression_id: str
    target_id: str
    reason_code: str
    missing_requirements: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)


class EvidenceItem(BaseModel):
    """
    Fully resolved evidence record linking normalized event to detector reasons and entities.
    """
    event_id: str
    timestamp: str
    source: str
    raw: Dict[str, Any] = Field(default_factory=dict)
    normalized: Dict[str, Any] = Field(default_factory=dict)
    detectors: List[Dict[str, str]] = Field(default_factory=list)
    linked_entities: List[str] = Field(default_factory=list)


class StageExplanation(BaseModel):
    stage_id: str
    explanation: str
    evidence_event_ids: List[str]


class RecommendedAction(BaseModel):
    action_id: str
    reason: str


class CopilotExplanation(BaseModel):
    """
    Strict schema contract for AI Analyst Copilot responses.
    """
    summary: str
    confidence: str = Field(..., pattern="^(low|medium|high)$")
    stage_explanations: List[StageExplanation] = Field(default_factory=list)
    recommended_actions: List[RecommendedAction] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
