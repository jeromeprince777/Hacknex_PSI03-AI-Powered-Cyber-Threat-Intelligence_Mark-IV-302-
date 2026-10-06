"""
ThreatWeave Bounded Evidence Pack Builder.
Constructs strict, self-contained evidence packages for the Incident Investigation UI
and the Analyst Copilot. Strictly adheres to docs/02_TECHNICAL_PRD.md Section 13 and 17.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set

from app.schemas.events import (
    EvidenceItem,
    Incident,
    Signal,
    Stage,
    ThreatWeaveEvent,
)

# Controlled Action Library per docs/02_TECHNICAL_PRD.md Section 17
APPROVED_ACTION_CATALOG = [
    {
        "action_id": "isolate-device",
        "label": "Isolate affected endpoint device",
        "stage_keys": ["removable_media_transfer", "execution"],
        "description": "Isolate endpoint from local network segment to prevent lateral movement or data copying.",
    },
    {
        "action_id": "disable-session",
        "label": "Terminate active user logon session",
        "stage_keys": ["initial_access"],
        "description": "Revoke active Kerberos ticket / VPN session credentials for compromised account.",
    },
    {
        "action_id": "review-resource-access",
        "label": "Audit accessed sensitive files and file permissions",
        "stage_keys": ["resource_collection"],
        "description": "Inspect file share access logs and verify if additional confidential repositories were touched.",
    },
    {
        "action_id": "review-network-transfer",
        "label": "Block outbound IP and inspect firewall traffic",
        "stage_keys": ["exfiltration"],
        "description": "Add external destination IP to firewall blocklist and inspect proxy gateway streams.",
    },
    {
        "action_id": "preserve-evidence",
        "label": "Preserve forensic logs and endpoint disk snapshot",
        "stage_keys": ["all"],
        "description": "Collect volatile memory, Windows EventLogs, and removable storage mount history for legal hold.",
    },
]


class EvidencePackBuilder:
    """
    Builds a sealed, auditable evidence pack for an incident.
    """

    @classmethod
    def build_evidence_pack(
        cls,
        incident: Incident,
        stages: List[Stage],
        evidence_events: List[ThreatWeaveEvent],
        signals: List[Signal],
    ) -> Dict[str, Any]:
        """
        Assembles all verified incident telemetry into the canonical bounded evidence pack.
        """
        # Sort evidence events chronologically
        sorted_events = sorted(evidence_events, key=lambda x: x.timestamp)
        event_map = {e.event_id: e for e in sorted_events}

        # 1. Map event_id to stage_id
        event_to_stage: Dict[str, str] = {}
        for stg in stages:
            for eid in stg.evidence_event_ids:
                event_to_stage[eid] = stg.stage_id

        # 2. Map event_id to detector reason codes
        event_detectors: Dict[str, List[Dict[str, str]]] = {}
        for sig in signals:
            event_detectors.setdefault(sig.event_id, []).append({
                "reason_code": sig.reason_code,
                "signal_type": sig.signal_type,
                "stage": sig.stage,
                "score": str(sig.score),
            })

        # 3. Construct chronological Timeline items
        timeline_items: List[Dict[str, Any]] = []
        for ev in sorted_events:
            stage_id = event_to_stage.get(ev.event_id, "unknown_stage")
            fact_summary = cls._generate_fact_summary(ev)
            linked_ents = cls._extract_linked_entities(ev)

            timeline_items.append({
                "event_id": ev.event_id,
                "timestamp": ev.timestamp,
                "stage_id": stage_id,
                "source": ev.source,
                "event_type": ev.event_type,
                "fact": fact_summary,
                "linked_entities": linked_ents,
            })

        # 4. Construct detailed EvidenceItems (with raw and normalized payloads)
        detailed_events: List[EvidenceItem] = []
        for ev in sorted_events:
            detailed_events.append(
                EvidenceItem(
                    event_id=ev.event_id,
                    timestamp=ev.timestamp,
                    source=ev.source,
                    raw=ev.raw,
                    normalized=ev.model_dump(),
                    detectors=event_detectors.get(ev.event_id, []),
                    linked_entities=cls._extract_linked_entities(ev),
                )
            )

        # 5. Deduplicate involved entities
        all_entities: Set[str] = set()
        for ev in sorted_events:
            all_entities.update(cls._extract_linked_entities(ev))

        # 6. Select approved actions matching observed stages
        detected_stage_names = [s.name.lower() for s in stages]
        approved_actions: List[Dict[str, Any]] = []
        for action in APPROVED_ACTION_CATALOG:
            # Check if action applies to any observed stage
            if "all" in action["stage_keys"]:
                approved_actions.append(action)
            elif any("initial access" in sn for sn in detected_stage_names) and "initial_access" in action["stage_keys"]:
                approved_actions.append(action)
            elif any("resource" in sn for sn in detected_stage_names) and "resource_collection" in action["stage_keys"]:
                approved_actions.append(action)
            elif any("removable" in sn or "usb" in sn for sn in detected_stage_names) and "removable_media_transfer" in action["stage_keys"]:
                approved_actions.append(action)
            elif any("exfiltration" in sn for sn in detected_stage_names) and "exfiltration" in action["stage_keys"]:
                approved_actions.append(action)

        return {
            "incident": incident.model_dump(),
            "timeline": timeline_items,
            "stages": [s.model_dump() for s in stages],
            "events": [e.model_dump() for e in detailed_events],
            "entities": sorted(list(all_entities)),
            "approved_actions": approved_actions,
        }

    @staticmethod
    def _extract_linked_entities(event: ThreatWeaveEvent) -> List[str]:
        entities: List[str] = []
        if event.user_id:
            entities.append(event.user_id)
        if event.device_id:
            entities.append(event.device_id)
        if event.src_ip:
            entities.append(event.src_ip)
        if event.dst_ip:
            entities.append(event.dst_ip)
        if event.resource:
            entities.append(event.resource)
        usb_id = event.attributes.get("removable_media_id")
        if usb_id:
            entities.append(usb_id)
        return list(dict.fromkeys(entities))

    @staticmethod
    def _generate_fact_summary(event: ThreatWeaveEvent) -> str:
        """
        Creates an objective, non-hallucinated factual summary from structured fields.
        """
        user = event.user_id or "Unknown user"
        dev = event.device_id or "workstation"

        if event.event_type == "login_success":
            loc = event.attributes.get("login_location")
            loc_str = f" from {loc}" if loc else ""
            ip_str = f" via {event.src_ip}" if event.src_ip else ""
            return f"{user} authenticated on {dev}{ip_str}{loc_str}"

        elif event.event_type == "file_access":
            res = event.resource or "resource"
            act = event.action or "accessed"
            return f"{user} performed {act} on sensitive resource '{res}'"

        elif event.event_type == "usb_connected":
            usb = event.attributes.get("removable_media_id") or "Removable media"
            return f"Removable media device '{usb}' connected to endpoint {dev}"

        elif event.event_type == "usb_copy":
            res = event.resource or "file"
            usb = event.attributes.get("removable_media_id") or "USB drive"
            return f"Sensitive resource '{res}' copied to removable media '{usb}'"

        elif event.event_type == "outbound_connection":
            dst = event.dst_ip or "external host"
            bytes_sent = event.attributes.get("bytes") or event.attributes.get("bytes_sent") or 0
            mb = round(float(bytes_sent) / 1024 / 1024, 1)
            return f"Outbound connection from {dev} to {dst} transferring {mb} MB"

        return f"Event {event.event_type} observed on {dev} by {user}"
