"""
ThreatWeave Baseline & Entity Novelty Engine.
Profiles historical entity associations and evaluates novelty for observed relationships.
Strictly adheres to docs/02_TECHNICAL_PRD.md Section 11.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.events import ThreatWeaveEvent


class BaselineProfile:
    """
    Holds historical interaction graphs for users, devices, IPs, and resources.
    """

    def __init__(self) -> None:
        self.user_ips: Dict[str, Set[str]] = {}
        self.user_devices: Dict[str, Set[str]] = {}
        self.user_resources: Dict[str, Set[str]] = {}
        self.device_usbs: Dict[str, Set[str]] = {}

    def observe(self, event: ThreatWeaveEvent) -> None:
        """Records an event into the baseline history."""
        user = event.user_id
        dev = event.device_id
        ip = event.src_ip
        res = event.resource
        usb = event.attributes.get("removable_media_id")

        if user:
            if ip:
                self.user_ips.setdefault(user, set()).add(ip)
            if dev:
                self.user_devices.setdefault(user, set()).add(dev)
            if res:
                self.user_resources.setdefault(user, set()).add(res)

        if dev and usb:
            self.device_usbs.setdefault(dev, set()).add(usb)

    @classmethod
    def build_default_baseline(cls) -> BaselineProfile:
        """
        Initializes an enterprise baseline reflecting standard known relationships.
        Matches the seeded baseline context described in docs/PRD.md.
        """
        profile = cls()
        # user-42 known standard patterns
        profile.user_ips["user-42"] = {"10.10.4.20"}
        profile.user_devices["user-42"] = {"device-17"}
        profile.user_resources["user-42"] = {
            "HR/attendance.csv",
            "Engineering/docs/specs.md",
            "Shared/Templates/timesheet.xlsx",
        }

        # user-admin known standard patterns
        profile.user_ips["user-admin"] = {"10.10.1.15"}
        profile.user_devices["user-admin"] = {"device-srv01"}
        profile.user_resources["user-admin"] = {
            "Shared/Archived/backup_config.json",
            "C:\\Scripts\\backup_daily.ps1",
        }

        # user-it known patterns
        profile.user_ips["user-it"] = {"10.10.3.50"}
        profile.user_devices["user-it"] = {"device-it01"}
        profile.device_usbs["device-it01"] = {"usb-it-approved-01"}

        # user-88, user-12, user-33 standard workstation patterns
        profile.user_ips["user-88"] = {"10.10.4.105"}
        profile.user_resources["user-88"] = {"Shared/Templates/timesheet.xlsx", "Shared/Announcements/all_hands.pdf"}

        return profile


class EntityNoveltyScorer:
    """
    Calculates novelty scores [0.0, 1.0] for observed events relative to a baseline.
    """

    def __init__(self, baseline: Optional[BaselineProfile] = None) -> None:
        self.baseline = baseline or BaselineProfile.build_default_baseline()

    def score_event(self, event: ThreatWeaveEvent) -> Tuple[float, List[str]]:
        """
        Scores novelty of a single event and returns reasons.
        """
        novelty_score = 0.0
        reasons: List[str] = []

        user = event.user_id
        ip = event.src_ip
        res = event.resource
        dev = event.device_id
        usb = event.attributes.get("removable_media_id")

        if user and ip:
            known_ips = self.baseline.user_ips.get(user, set())
            if known_ips and ip not in known_ips:
                novelty_score += 0.35
                reasons.append(f"Novel IP '{ip}' for user '{user}' (baseline: {list(known_ips)})")

        if user and res:
            known_res = self.baseline.user_resources.get(user, set())
            if known_res and res not in known_res:
                novelty_score += 0.35
                reasons.append(f"First-seen resource access to '{res}' by user '{user}'")

        if dev and usb:
            known_usbs = self.baseline.device_usbs.get(dev, set())
            if usb not in known_usbs:
                novelty_score += 0.30
                reasons.append(f"First-seen removable media '{usb}' connected to device '{dev}'")

        return min(1.0, novelty_score), reasons

    def score_event_cluster(self, events: List[ThreatWeaveEvent]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculates aggregate novelty score for a correlated cluster of events.
        """
        if not events:
            return 0.0, {"reasons": [], "novel_relationships_count": 0}

        aggregated_score = 0.0
        all_reasons: List[str] = []

        has_novel_ip = False
        has_novel_resource = False
        has_novel_usb = False

        for ev in events:
            score, reasons = self.score_event(ev)
            all_reasons.extend(reasons)
            for r in reasons:
                if "Novel IP" in r:
                    has_novel_ip = True
                elif "First-seen resource" in r:
                    has_novel_resource = True
                elif "First-seen removable media" in r:
                    has_novel_usb = True

        if has_novel_ip:
            aggregated_score += 0.35
        if has_novel_resource:
            aggregated_score += 0.35
        if has_novel_usb:
            aggregated_score += 0.30

        clamped = min(1.0, max(0.05, aggregated_score))
        return clamped, {
            "reasons": list(set(all_reasons)),
            "has_novel_ip": has_novel_ip,
            "has_novel_resource": has_novel_resource,
            "has_novel_usb": has_novel_usb,
        }
