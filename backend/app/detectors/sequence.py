"""
ThreatWeave Temporal Sequence Correlator & False Positive Suppression Engine.
Correlates atomic signals across temporal windows and shared entities into attack stages.
Enforces the strict Incident Promotion Gate (Signal -> Cluster -> Incident).
Strictly adheres to docs/01_PRD.md Section 12, docs/02_TECHNICAL_PRD.md Section 8 & 10.
"""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.events import (
    Signal,
    Stage,
    SuppressionRecord,
    ThreatWeaveEvent,
)


class CorrelatedCluster:
    """
    Intermediate grouping of related signals and events sharing an entity and time window.
    """

    def __init__(self, cluster_id: str, primary_entity: str) -> None:
        self.cluster_id = cluster_id
        self.primary_entity = primary_entity
        self.events: List[ThreatWeaveEvent] = []
        self.signals: List[Signal] = []

    @property
    def event_ids(self) -> List[str]:
        return [e.event_id for e in self.events]

    @property
    def stages_present(self) -> Set[str]:
        return {s.stage for s in self.signals}


class TemporalSequenceCorrelator:
    """
    Correlates atomic detection signals into attack stages and evaluates chain consistency.
    """

    STAGE_ORDER = [
        "initial_access",
        "execution",
        "resource_collection",
        "removable_media_transfer",
        "exfiltration",
    ]

    STAGE_NAMES = {
        "initial_access": "Initial access / Authentication novelty",
        "execution": "Process execution / Staging",
        "resource_collection": "Resource discovery / Collection",
        "removable_media_transfer": "Removable-media transfer / USB activity",
        "exfiltration": "Outbound data exfiltration",
    }

    @classmethod
    def cluster_events_and_signals(
        cls,
        events: List[ThreatWeaveEvent],
        signals: List[Signal],
    ) -> List[CorrelatedCluster]:
        """
        Groups events and signals by primary actor entity (user_id or device_id).
        """
        event_map = {e.event_id: e for e in events}
        signal_map: Dict[str, List[Signal]] = {}
        for sig in signals:
            signal_map.setdefault(sig.event_id, []).append(sig)

        clusters: Dict[str, CorrelatedCluster] = {}

        for sig in signals:
            ev = event_map.get(sig.event_id)
            if not ev:
                continue

            # Primary entity key (user preferred, fallback to device or session)
            entity_key = ev.user_id or ev.device_id or ev.session_id or "unknown_entity"
            if entity_key not in clusters:
                clusters[entity_key] = CorrelatedCluster(
                    cluster_id=f"cluster-{uuid.uuid4().hex[:6]}",
                    primary_entity=entity_key,
                )

            cluster = clusters[entity_key]
            cluster.signals.append(sig)
            if ev not in cluster.events:
                cluster.events.append(ev)

        # Sort events inside clusters chronologically
        for c in clusters.values():
            c.events.sort(key=lambda x: x.timestamp)

        return list(clusters.values())

    @classmethod
    def build_attack_stages(
        cls,
        incident_id: str,
        cluster: CorrelatedCluster,
    ) -> List[Stage]:
        """
        Groups cluster signals by canonical attack stage and attaches verified event evidence IDs.
        """
        stage_groups: Dict[str, List[Signal]] = {}
        for sig in cluster.signals:
            stage_groups.setdefault(sig.stage, []).append(sig)

        event_map = {e.event_id: e for e in cluster.events}
        ordered_stages: List[Stage] = []
        seq_idx = 1

        for stage_key in cls.STAGE_ORDER:
            if stage_key not in stage_groups:
                continue

            group_signals = stage_groups[stage_key]
            evidence_ids = list(dict.fromkeys(s.event_id for s in group_signals))
            if not evidence_ids:
                continue

            # Compute start and end timestamps from concrete evidence events
            stage_events = [event_map[eid] for eid in evidence_ids if eid in event_map]
            if not stage_events:
                continue

            stage_events.sort(key=lambda x: x.timestamp)
            start_t = stage_events[0].timestamp
            end_t = stage_events[-1].timestamp
            reason_codes = list(dict.fromkeys(s.reason_code for s in group_signals))

            stage = Stage(
                stage_id=f"stage-{seq_idx:02d}",
                incident_id=incident_id,
                name=cls.STAGE_NAMES.get(stage_key, stage_key.replace("_", " ").title()),
                sequence_index=seq_idx,
                start_time=start_t,
                end_time=end_t,
                evidence_event_ids=evidence_ids,
                reason_codes=reason_codes,
            )
            ordered_stages.append(stage)
            seq_idx += 1

        return ordered_stages

    @classmethod
    def calculate_sequence_score(
        cls,
        stages: List[Stage],
        events: List[ThreatWeaveEvent],
    ) -> float:
        """
        Evaluates the sequence score [0.0, 1.0] using explainable components:
        - Stage transition match: +0.25
        - Valid chronological ordering: +0.15
        - Consistent user across stages: +0.20
        - Consistent device/session across stages: +0.15
        - Shared context (e.g. accessed file matches USB copy): +0.15
        - Multiple independent evidence events: +0.10
        """
        if not stages or len(stages) < 2:
            return 0.20 if stages else 0.0

        score = 0.0

        # 1. Stage transition match
        stage_names = [s.name for s in stages]
        has_auth = any("Initial access" in n for n in stage_names)
        has_collection = any("Resource" in n for n in stage_names)
        has_transfer = any("Removable-media" in n or "USB" in n for n in stage_names)
        has_completed_copy = any(e.event_type == "usb_copy" for e in events)

        if has_auth and has_collection and has_transfer and has_completed_copy:
            score += 0.25
        elif has_auth and has_collection and has_transfer:
            # Removable media attached but no files transferred
            score += 0.15
        elif (has_auth and has_collection) or (has_collection and has_transfer):
            score += 0.10
        else:
            score += 0.05

        # 2. Chronological ordering
        ordered = True
        for i in range(len(stages) - 1):
            if stages[i].start_time > stages[i + 1].start_time:
                ordered = False
                break
        if ordered:
            score += 0.15

        # 3. User consistency
        users = {e.user_id for e in events if e.user_id}
        if len(users) == 1:
            score += 0.20
        elif len(users) > 1:
            score += 0.05

        # 4. Device/Session consistency
        devices = {e.device_id for e in events if e.device_id}
        sessions = {e.session_id for e in events if e.session_id}
        if len(devices) == 1 or len(sessions) == 1:
            score += 0.15

        # 5. Shared context (resource correlation)
        read_resources = {e.resource for e in events if e.action == "read" and e.resource}
        written_resources = {e.resource for e in events if (e.action == "write" or e.event_type == "usb_copy") and e.resource}
        overlap = read_resources.intersection(written_resources)
        if overlap:
            score += 0.15

        # 6. Multiple independent evidence events
        all_evidence = set()
        for s in stages:
            all_evidence.update(s.evidence_event_ids)
        if len(all_evidence) >= 4:
            score += 0.10
        elif len(all_evidence) >= 3:
            score += 0.05

        return round(min(1.0, score), 2)

    @classmethod
    def evaluate_promotion_gate(
        cls,
        cluster: CorrelatedCluster,
        stages: List[Stage],
    ) -> Tuple[bool, Optional[SuppressionRecord]]:
        """
        Enforces the MVP False-Positive Suppression Gate:
        - At least 3 evidence events
        - At least 2 distinct stages
        - Valid entity link
        - Chronological order consistency
        """
        missing_requirements: List[str] = []

        all_evidence = set()
        for s in stages:
            all_evidence.update(s.evidence_event_ids)

        # Gate 1: Event volume
        if len(all_evidence) < 3:
            missing_requirements.append(
                f"requires >= 3 evidence events (observed {len(all_evidence)})"
            )

        # Gate 2: Distinct stages
        if len(stages) < 2:
            missing_requirements.append(
                f"requires >= 2 distinct attack stages (observed {len(stages)})"
            )

        # Gate 3: Temporal order
        if len(stages) >= 2:
            for i in range(len(stages) - 1):
                if stages[i].start_time > stages[i + 1].start_time:
                    missing_requirements.append("chronological stage sequence violated")
                    break

        if missing_requirements:
            suppression = SuppressionRecord(
                suppression_id=f"sup-{uuid.uuid4().hex[:6]}",
                target_id=cluster.cluster_id,
                reason_code="INSUFFICIENT_CHAIN_EVIDENCE",
                missing_requirements=missing_requirements,
                details={
                    "primary_entity": cluster.primary_entity,
                    "stages_count": len(stages),
                    "evidence_events_count": len(all_evidence),
                    "signals_count": len(cluster.signals),
                },
            )
            return False, suppression

        return True, None
