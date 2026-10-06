"""
ThreatWeave Atomic Detection Rules Engine.
Detects atomic security signals across authentication, file, device, process, and network events.
Strictly adheres to docs/02_TECHNICAL_PRD.md Section 7 and docs/04_DATA_API_CONTRACTS.md.
"""

from __future__ import annotations
import ipaddress
import uuid
from typing import Any, Dict, List, Optional

from app.schemas.events import Signal, ThreatWeaveEvent


def is_private_ip(ip_str: Optional[str]) -> bool:
    """Returns True if the IP address is RFC1918 / private / loopback."""
    if not ip_str:
        return True
    try:
        ip = ipaddress.ip_address(ip_str.strip())
        return ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local
    except ValueError:
        return False


class AtomicRuleDetector:
    """
    Evaluates individual normalized events against deterministic security rules.
    """

    @classmethod
    def evaluate_event(cls, event: ThreatWeaveEvent) -> List[Signal]:
        """
        Runs all relevant atomic detector rules against a single canonical event.
        """
        signals: List[Signal] = []

        # 1. Authentication Novelty / Location
        sig_auth = cls._check_auth_rule(event)
        if sig_auth:
            signals.append(sig_auth)

        # 2. Resource Collection / Sensitive File Access
        sig_file = cls._check_file_access_rule(event)
        if sig_file:
            signals.append(sig_file)

        # 3. USB Device Connection
        sig_usb_mount = cls._check_usb_connect_rule(event)
        if sig_usb_mount:
            signals.append(sig_usb_mount)

        # 4. USB Data Copy / Exfiltration
        sig_usb_copy = cls._check_usb_copy_rule(event)
        if sig_usb_copy:
            signals.append(sig_usb_copy)

        # 5. Outbound Network Exfiltration
        sig_net = cls._check_outbound_transfer_rule(event)
        if sig_net:
            signals.append(sig_net)

        # 6. Suspicious Process Execution
        sig_proc = cls._check_process_rule(event)
        if sig_proc:
            signals.append(sig_proc)

        return signals

    @classmethod
    def _check_auth_rule(cls, event: ThreatWeaveEvent) -> Optional[Signal]:
        if event.event_type != "login_success":
            return None

        # Check for external source IP or anomalous location metadata
        src_ip = event.src_ip
        location = str(event.attributes.get("login_location", ""))
        country = str(event.attributes.get("country_code", ""))

        is_external = src_ip and not is_private_ip(src_ip)
        has_foreign_location = bool(country and country not in ("US", "LOCAL", "INTERNAL"))

        if is_external or has_foreign_location or "Bucharest" in location:
            return Signal(
                signal_id=f"sig-auth-{uuid.uuid4().hex[:6]}",
                event_id=event.event_id,
                signal_type="new_login_location",
                stage="initial_access",
                score=0.55,
                reason_code="AUTH_NEW_LOCATION",
                parameters={
                    "user_id": event.user_id,
                    "src_ip": src_ip,
                    "location": location,
                    "country": country,
                    "is_external_ip": is_external,
                },
            )
        return None

    @classmethod
    def _check_file_access_rule(cls, event: ThreatWeaveEvent) -> Optional[Signal]:
        if event.event_type != "file_access":
            return None

        resource = str(event.resource or "").lower()
        classification = str(event.attributes.get("classification", "")).lower()

        sensitive_keywords = ["payroll", "titan", "confidential", "restricted", "secret", "m&a", "passwords"]
        is_sensitive = any(kw in resource for kw in sensitive_keywords) or (
            "confidential" in classification or "restricted" in classification
        )

        if is_sensitive:
            return Signal(
                signal_id=f"sig-res-{uuid.uuid4().hex[:6]}",
                event_id=event.event_id,
                signal_type="unusual_resource_access",
                stage="resource_collection",
                score=0.70,
                reason_code="UNUSUAL_RESOURCE_ACCESS",
                parameters={
                    "user_id": event.user_id,
                    "resource": event.resource,
                    "classification": classification,
                    "bytes": event.attributes.get("bytes", 0),
                },
            )
        return None

    @classmethod
    def _check_usb_connect_rule(cls, event: ThreatWeaveEvent) -> Optional[Signal]:
        if event.event_type != "usb_connected":
            return None

        is_authorized_it = event.attributes.get("authorized_tag") == "IT_SERVICE_TOOL"
        media_id = event.attributes.get("removable_media_id") or "unknown_usb"

        score = 0.30 if is_authorized_it else 0.65
        reason = "USB_AUTHORIZED_IT" if is_authorized_it else "USB_CONNECTED"

        return Signal(
            signal_id=f"sig-usb-{uuid.uuid4().hex[:6]}",
            event_id=event.event_id,
            signal_type="usb_connected",
            stage="removable_media_transfer",
            score=score,
            reason_code=reason,
            parameters={
                "device_id": event.device_id,
                "removable_media_id": media_id,
                "vendor": event.attributes.get("vendor"),
                "is_authorized_it": is_authorized_it,
            },
        )

    @classmethod
    def _check_usb_copy_rule(cls, event: ThreatWeaveEvent) -> Optional[Signal]:
        if event.event_type != "usb_copy":
            return None

        media_id = event.attributes.get("removable_media_id") or "unknown_usb"
        dest_path = event.attributes.get("destination_path") or event.resource

        return Signal(
            signal_id=f"sig-copy-{uuid.uuid4().hex[:6]}",
            event_id=event.event_id,
            signal_type="usb_copy",
            stage="removable_media_transfer",
            score=0.85,
            reason_code="USB_COPY",
            parameters={
                "user_id": event.user_id,
                "device_id": event.device_id,
                "resource": event.resource,
                "destination_path": dest_path,
                "removable_media_id": media_id,
                "bytes": event.attributes.get("bytes", 0),
            },
        )

    @classmethod
    def _check_outbound_transfer_rule(cls, event: ThreatWeaveEvent) -> Optional[Signal]:
        if event.event_type != "outbound_connection":
            return None

        dst_ip = event.dst_ip
        bytes_sent = int(event.attributes.get("bytes", 0) or event.attributes.get("bytes_sent", 0) or 0)
        is_external = dst_ip and not is_private_ip(dst_ip)

        # Triggers if high volume transferred to an external destination
        if is_external and bytes_sent >= 10_000_000:
            return Signal(
                signal_id=f"sig-net-{uuid.uuid4().hex[:6]}",
                event_id=event.event_id,
                signal_type="large_outbound_transfer",
                stage="exfiltration",
                score=0.75,
                reason_code="LARGE_OUTBOUND_TRANSFER",
                parameters={
                    "dst_ip": dst_ip,
                    "bytes": bytes_sent,
                    "application": event.application,
                },
            )
        return None

    @classmethod
    def _check_process_rule(cls, event: ThreatWeaveEvent) -> Optional[Signal]:
        if event.event_type != "process_start":
            return None

        app = str(event.application or "").lower()
        cmd = str(event.attributes.get("command_line", "")).lower()

        # Check for administrative bypass or scripting tools
        if "executionpolicy bypass" in cmd:
            return Signal(
                signal_id=f"sig-proc-{uuid.uuid4().hex[:6]}",
                event_id=event.event_id,
                signal_type="suspicious_process",
                stage="execution",
                score=0.45,  # Low/routine for scheduled admin backups, higher if paired with novel user
                reason_code="ROUTINE_ADMIN_SCRIPT" if "backup" in cmd else "SUSPICIOUS_COMMAND",
                parameters={
                    "command_line": cmd,
                    "application": app,
                    "user_id": event.user_id,
                },
            )
        return None
