"""
ThreatWeave Multi-Source Normalization Pipeline.
Converts heterogeneous security logs (Windows EventLog, Linux syslog, VPN, EDR, Firewall)
into the Canonical ThreatWeaveEvent schema.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.events import ThreatWeaveEvent


class LogNormalizer:
    """
    Adapter engine that translates heterogeneous vendor/OS logs into canonical events.
    """

    @staticmethod
    def _parse_timestamp(val: Any) -> str:
        if not val:
            return datetime.now(timezone.utc).isoformat()
        if isinstance(val, (int, float)):
            return datetime.fromtimestamp(val, tz=timezone.utc).isoformat()
        s = str(val).strip()
        try:
            # Replace Z with +00:00 for fromisoformat compatibility
            ts = s.replace("Z", "+00:00")
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()

    @classmethod
    def normalize_windows_event(cls, raw: Dict[str, Any]) -> ThreatWeaveEvent:
        """
        Normalizes Windows Security EventLog (EventCode 4624, 4663, 4672, 7045, etc.).
        """
        code = raw.get("EventCode") or raw.get("event_code") or raw.get("id")
        event_id = raw.get("event_id") or f"win-{uuid.uuid4().hex[:8]}"
        timestamp = cls._parse_timestamp(raw.get("timestamp") or raw.get("TimeCreated"))

        event_type = "windows_event"
        action = "observe"
        user_id = raw.get("TargetUserName") or raw.get("user_id") or raw.get("SubjectUserName")
        device_id = raw.get("Computer") or raw.get("device_id") or raw.get("WorkstationName")
        src_ip = raw.get("IpAddress") or raw.get("src_ip")
        if src_ip in ("-", "::1", "127.0.0.1"):
            src_ip = None

        resource = raw.get("ObjectName") or raw.get("resource") or raw.get("RelativeTargetName")
        application = raw.get("ProcessName") or raw.get("application")
        session_id = raw.get("TargetLogonId") or raw.get("session_id")

        if code in (4624, "4624"):
            event_type = "login_success"
            action = "authenticate"
        elif code in (4625, "4625"):
            event_type = "login_failure"
            action = "authenticate"
        elif code in (4663, "4663"):
            event_type = "file_access"
            action = "read" if "READ" in str(raw.get("AccessList", "")).upper() else "write"
        elif code in (4688, "4688", 1, "1"):
            event_type = "process_start"
            action = "execute"
            application = raw.get("NewProcessName") or raw.get("Image") or application

        attributes = {k: v for k, v in raw.items() if k not in {
            "event_id", "timestamp", "EventCode", "TargetUserName", "Computer", "IpAddress", "ObjectName"
        }}

        return ThreatWeaveEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            source="windows",
            action=action,
            user_id=user_id,
            device_id=device_id,
            src_ip=src_ip,
            dst_ip=raw.get("dst_ip"),
            application=application,
            resource=resource,
            session_id=session_id,
            attributes=attributes,
            raw=raw,
        )

    @classmethod
    def normalize_vpn_event(cls, raw: Dict[str, Any]) -> ThreatWeaveEvent:
        """
        Normalizes VPN / Remote Access gateway telemetry.
        """
        event_id = raw.get("event_id") or f"vpn-{uuid.uuid4().hex[:8]}"
        timestamp = cls._parse_timestamp(raw.get("timestamp") or raw.get("time"))
        user_id = raw.get("user") or raw.get("username") or raw.get("user_id")
        src_ip = raw.get("client_ip") or raw.get("src_ip") or raw.get("remote_ip")
        dst_ip = raw.get("gateway_ip") or raw.get("dst_ip")

        status = str(raw.get("status") or raw.get("event") or "").upper()
        if "SUCCESS" in status or "CONNECT" in status:
            event_type = "login_success"
            action = "authenticate"
        else:
            event_type = "login_failure"
            action = "authenticate"

        attributes = {
            "login_location": raw.get("location") or raw.get("geo") or raw.get("login_location"),
            "country_code": raw.get("country") or raw.get("country_code"),
            "client_version": raw.get("client_version"),
        }

        return ThreatWeaveEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            source="vpn",
            action=action,
            user_id=user_id,
            device_id=raw.get("device_id") or raw.get("workstation"),
            src_ip=src_ip,
            dst_ip=dst_ip,
            application="OpenVPN",
            resource=None,
            session_id=raw.get("session_id") or raw.get("tunnel_id"),
            attributes=attributes,
            raw=raw,
        )

    @classmethod
    def normalize_edr_event(cls, raw: Dict[str, Any]) -> ThreatWeaveEvent:
        """
        Normalizes Endpoint Detection & Response telemetry (USB, process injection, suspicious command).
        """
        event_id = raw.get("event_id") or f"edr-{uuid.uuid4().hex[:8]}"
        timestamp = cls._parse_timestamp(raw.get("timestamp"))
        event_type = raw.get("event_type") or "edr_activity"
        action = raw.get("action") or "observe"

        return ThreatWeaveEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            source="edr",
            action=action,
            user_id=raw.get("user_id"),
            device_id=raw.get("device_id"),
            src_ip=raw.get("src_ip"),
            dst_ip=raw.get("dst_ip"),
            application=raw.get("application"),
            resource=raw.get("resource"),
            session_id=raw.get("session_id"),
            attributes=raw.get("attributes", {}),
            raw=raw,
        )

    @classmethod
    def normalize_auto(cls, raw: Dict[str, Any]) -> ThreatWeaveEvent:
        """
        Automatic source detection and dispatch.
        If already canonical, returns as ThreatWeaveEvent directly.
        """
        # If it already has required canonical fields
        if all(k in raw for k in ("event_id", "timestamp", "event_type", "source")):
            return ThreatWeaveEvent(**raw)

        source = str(raw.get("source", "")).lower()
        if source == "windows" or "EventCode" in raw:
            return cls.normalize_windows_event(raw)
        elif source == "vpn" or "client_ip" in raw or "tunnel_id" in raw:
            return cls.normalize_vpn_event(raw)
        elif source in ("edr", "crowdstrike", "sentinel"):
            return cls.normalize_edr_event(raw)
        else:
            # Fallback best-effort mapping
            event_id = raw.get("event_id") or f"evt-{uuid.uuid4().hex[:8]}"
            timestamp = cls._parse_timestamp(raw.get("timestamp"))
            event_type = raw.get("event_type") or "unknown"
            return ThreatWeaveEvent(
                event_id=event_id,
                timestamp=timestamp,
                event_type=event_type,
                source=source or "generic",
                action=raw.get("action"),
                user_id=raw.get("user_id"),
                device_id=raw.get("device_id"),
                src_ip=raw.get("src_ip"),
                dst_ip=raw.get("dst_ip"),
                application=raw.get("application"),
                resource=raw.get("resource"),
                session_id=raw.get("session_id"),
                attributes=raw.get("attributes", {}),
                raw=raw,
            )
