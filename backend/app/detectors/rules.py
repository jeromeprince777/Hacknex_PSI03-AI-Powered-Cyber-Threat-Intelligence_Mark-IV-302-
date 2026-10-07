"""
ThreatWeave Atomic Detection Rules Engine.
Detects atomic security signals across authentication, file, device, process, and network events.
Strictly adheres to docs/02_TECHNICAL_PRD.md Section 7 and docs/04_DATA_API_CONTRACTS.md.
"""

from __future__ import annotations
import ipaddress
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from app.schemas.events import Signal, ThreatWeaveEvent

# RFC 1918 Private Enterprise subnets
RFC1918_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]

# RFC 5737 Documentation and Benchmark subnets (TEST-NET-1, TEST-NET-2, TEST-NET-3)
RFC5737_TEST_NETWORKS = [
    ipaddress.ip_network("192.0.2.0/24"),    # TEST-NET-1
    ipaddress.ip_network("198.51.100.0/24"), # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3
]


def is_rfc1918_private_ip(ip_str: Optional[str]) -> bool:
    """
    Returns True if the IP address belongs strictly to RFC 1918 private subnets
    (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) or standard loopback/link-local ranges.
    Returns False for external/public addresses and documentation test networks.
    """
    if not ip_str:
        return True
    try:
        ip = ipaddress.ip_address(ip_str.strip())
        if ip.is_loopback or ip.is_link_local:
            return True
        return any(ip in net for net in RFC1918_NETWORKS)
    except ValueError:
        return False


def is_external_for_detection(ip_str: Optional[str]) -> bool:
    """
    Evaluates whether an IP address should be treated as external for threat detection.
    
    Distinguishes RFC 1918 private enterprise subnets from external/public networks.
    RFC 5737 documentation ranges (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24)
    are designated for documentation and synthetic simulation, and are explicitly classified
    as external target destinations in ThreatWeave detection scenarios.
    """
    if not ip_str:
        return False
    try:
        ip = ipaddress.ip_address(ip_str.strip())
        if ip.is_loopback or ip.is_link_local:
            return False
        if any(ip in net for net in RFC1918_NETWORKS):
            return False
        if any(ip in net for net in RFC5737_TEST_NETWORKS):
            return True
        # For general addresses: if not private, treat as external
        return not ip.is_private
    except ValueError:
        return False


def is_private_ip(ip_str: Optional[str]) -> bool:
    """
    Legacy helper maintained for backward compatibility.
    Equivalent to is_rfc1918_private_ip(ip_str).
    """
    return is_rfc1918_private_ip(ip_str)


def load_detection_rule_configs() -> Dict[str, Dict[str, Any]]:
    """
    Loads rule metadata from configs/detection_rules.yaml if available,
    falling back to robust defaults matching the contract.
    """
    config_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "configs" / "detection_rules.yaml",
        Path("configs/detection_rules.yaml"),
    ]
    for p in config_paths:
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and "rules" in data:
                        return {r["id"]: r for r in data["rules"] if "id" in r}
            except Exception:
                pass

    return {
        "AUTH_NEW_LOCATION": {
            "id": "AUTH_NEW_LOCATION",
            "event_type": "login_success",
            "stage": "initial_access",
            "signal_type": "new_login_location",
            "base_score": 0.55,
            "description": "Successful authentication from a foreign country or previously unseen IP/location",
        },
        "UNUSUAL_RESOURCE_ACCESS": {
            "id": "UNUSUAL_RESOURCE_ACCESS",
            "event_type": "file_access",
            "stage": "resource_collection",
            "signal_type": "unusual_resource_access",
            "base_score": 0.70,
            "description": "Read or access to confidential, financial, or sensitive enterprise resources",
            "conditions": {
                "sensitive_keywords": ["confidential", "restricted", "payroll", "titan", "m&a", "secret"]
            },
        },
        "USB_CONNECTED": {
            "id": "USB_CONNECTED",
            "event_type": "usb_connected",
            "stage": "removable_media_transfer",
            "signal_type": "usb_connected",
            "base_score": 0.65,
            "description": "Removable media or USB storage device attached to corporate endpoint",
        },
        "USB_COPY": {
            "id": "USB_COPY",
            "event_type": "usb_copy",
            "stage": "removable_media_transfer",
            "signal_type": "usb_copy",
            "base_score": 0.85,
            "description": "File write or data transfer directed to removable USB storage media",
        },
        "LARGE_OUTBOUND_TRANSFER": {
            "id": "LARGE_OUTBOUND_TRANSFER",
            "event_type": "outbound_connection",
            "stage": "exfiltration",
            "signal_type": "large_outbound_transfer",
            "base_score": 0.75,
            "description": "Significant outbound network traffic following local staging or collection",
            "conditions": {"min_bytes": 10000000},
        },
        "SUSPICIOUS_PROCESS": {
            "id": "SUSPICIOUS_PROCESS",
            "event_type": "process_start",
            "stage": "execution",
            "signal_type": "suspicious_process",
            "base_score": 0.60,
            "description": "Execution of script engine or utility with execution bypass or transfer flags",
            "conditions": {
                "suspicious_tools": ["curl.exe", "powershell.exe", "certutil.exe", "scp.exe"]
            },
        },
    }


class AtomicRuleDetector:
    """
    Evaluates individual normalized events against deterministic security rules.
    Rule parameters and scores are aligned with configs/detection_rules.yaml.
    Signal IDs are deterministically generated from (event_id, rule_id).
    """

    RULE_CONFIGS: Dict[str, Dict[str, Any]] = load_detection_rule_configs()

    @classmethod
    def reload_rules(cls) -> None:
        """Reloads rule configuration dictionary from configs/detection_rules.yaml."""
        cls.RULE_CONFIGS = load_detection_rule_configs()

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

        cfg = cls.RULE_CONFIGS.get("AUTH_NEW_LOCATION", {})
        base_score = float(cfg.get("base_score", 0.55))
        stage = str(cfg.get("stage", "initial_access"))
        signal_type = str(cfg.get("signal_type", "new_login_location"))

        src_ip = event.src_ip
        location = str(event.attributes.get("login_location", ""))
        country = str(event.attributes.get("country_code", ""))

        is_external = bool(src_ip and is_external_for_detection(src_ip))
        has_foreign_location = bool(country and country not in ("US", "LOCAL", "INTERNAL"))

        if is_external or has_foreign_location or "Bucharest" in location:
            return Signal(
                signal_id=f"sig-{event.event_id}-auth_new_location",
                event_id=event.event_id,
                signal_type=signal_type,
                stage=stage,
                score=base_score,
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

        cfg = cls.RULE_CONFIGS.get("UNUSUAL_RESOURCE_ACCESS", {})
        base_score = float(cfg.get("base_score", 0.70))
        stage = str(cfg.get("stage", "resource_collection"))
        signal_type = str(cfg.get("signal_type", "unusual_resource_access"))

        resource = str(event.resource or "").lower()
        classification = str(event.attributes.get("classification", "")).lower()

        sensitive_keywords = cfg.get("conditions", {}).get(
            "sensitive_keywords",
            ["payroll", "titan", "confidential", "restricted", "secret", "m&a", "passwords"]
        )
        is_sensitive = any(kw in resource for kw in sensitive_keywords) or (
            "confidential" in classification or "restricted" in classification
        )

        if is_sensitive:
            return Signal(
                signal_id=f"sig-{event.event_id}-unusual_resource_access",
                event_id=event.event_id,
                signal_type=signal_type,
                stage=stage,
                score=base_score,
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

        cfg = cls.RULE_CONFIGS.get("USB_CONNECTED", {})
        base_score = float(cfg.get("base_score", 0.65))
        stage = str(cfg.get("stage", "removable_media_transfer"))
        signal_type = str(cfg.get("signal_type", "usb_connected"))

        is_authorized_it = event.attributes.get("authorized_tag") == "IT_SERVICE_TOOL"
        media_id = event.attributes.get("removable_media_id") or "unknown_usb"

        score = 0.30 if is_authorized_it else base_score
        reason = "USB_AUTHORIZED_IT" if is_authorized_it else "USB_CONNECTED"

        return Signal(
            signal_id=f"sig-{event.event_id}-{reason.lower()}",
            event_id=event.event_id,
            signal_type=signal_type,
            stage=stage,
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

        cfg = cls.RULE_CONFIGS.get("USB_COPY", {})
        base_score = float(cfg.get("base_score", 0.85))
        stage = str(cfg.get("stage", "removable_media_transfer"))
        signal_type = str(cfg.get("signal_type", "usb_copy"))

        media_id = event.attributes.get("removable_media_id") or "unknown_usb"
        dest_path = event.attributes.get("destination_path") or event.resource

        return Signal(
            signal_id=f"sig-{event.event_id}-usb_copy",
            event_id=event.event_id,
            signal_type=signal_type,
            stage=stage,
            score=base_score,
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

        cfg = cls.RULE_CONFIGS.get("LARGE_OUTBOUND_TRANSFER", {})
        base_score = float(cfg.get("base_score", 0.75))
        stage = str(cfg.get("stage", "exfiltration"))
        signal_type = str(cfg.get("signal_type", "large_outbound_transfer"))
        min_bytes = int(cfg.get("conditions", {}).get("min_bytes", 10000000))

        dst_ip = event.dst_ip
        bytes_sent = int(event.attributes.get("bytes", 0) or event.attributes.get("bytes_sent", 0) or 0)
        is_external = bool(dst_ip and is_external_for_detection(dst_ip))

        # Triggers if high volume transferred to an external destination (including RFC 5737 demo destinations)
        if is_external and bytes_sent >= min_bytes:
            return Signal(
                signal_id=f"sig-{event.event_id}-large_outbound_transfer",
                event_id=event.event_id,
                signal_type=signal_type,
                stage=stage,
                score=base_score,
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

        cfg = cls.RULE_CONFIGS.get("SUSPICIOUS_PROCESS", {})
        base_score = float(cfg.get("base_score", 0.60))
        stage = str(cfg.get("stage", "execution"))
        signal_type = str(cfg.get("signal_type", "suspicious_process"))

        app = str(event.application or "").lower()
        cmd = str(event.attributes.get("command_line", "")).lower()

        # Check for administrative bypass or scripting tools
        if "executionpolicy bypass" in cmd:
            is_backup = "backup" in cmd
            reason_code = "ROUTINE_ADMIN_SCRIPT" if is_backup else "SUSPICIOUS_COMMAND"
            score = 0.45 if is_backup else base_score

            return Signal(
                signal_id=f"sig-{event.event_id}-{reason_code.lower()}",
                event_id=event.event_id,
                signal_type=signal_type,
                stage=stage,
                score=score,
                reason_code=reason_code,
                parameters={
                    "command_line": cmd,
                    "application": app,
                    "user_id": event.user_id,
                },
            )
        return None
