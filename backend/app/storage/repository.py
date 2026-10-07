"""
ThreatWeave SQLite Persistence Repository.
Provides local, deterministic storage for events, signals, incidents, stages, evidence links, and suppression records.
Strictly adheres to docs/02_TECHNICAL_PRD.md Section 19.
"""

from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.schemas.events import (
    Incident,
    RiskComponents,
    Signal,
    Stage,
    SuppressionRecord,
    ThreatWeaveEvent,
)


class StorageRepository:
    """
    Thread-safe SQLite storage for the ThreatWeave platform.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_dir = Path(__file__).resolve().parent.parent.parent / "data"
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(db_dir / "threatweave.sqlite")
        else:
            self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Events Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    action TEXT,
                    user_id TEXT,
                    device_id TEXT,
                    src_ip TEXT,
                    dst_ip TEXT,
                    application TEXT,
                    resource TEXT,
                    session_id TEXT,
                    attributes_json TEXT,
                    raw_json TEXT
                )
            """)

            # 2. Signals Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    signal_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    score REAL NOT NULL,
                    reason_code TEXT NOT NULL,
                    parameters_json TEXT,
                    UNIQUE(event_id, reason_code)
                )
            """)

            # 3. Incidents Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    risk_index INTEGER NOT NULL,
                    risk_components_json TEXT NOT NULL,
                    entity_ids_json TEXT NOT NULL,
                    stage_ids_json TEXT NOT NULL,
                    evidence_event_ids_json TEXT NOT NULL,
                    analysis_version TEXT NOT NULL,
                    rule_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 4. Stages Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stages (
                    stage_id TEXT NOT NULL,
                    incident_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    sequence_index INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    reason_codes_json TEXT NOT NULL,
                    PRIMARY KEY (stage_id, incident_id)
                )
            """)

            # 5. Stage Evidence Mapping Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stage_evidence (
                    stage_id TEXT NOT NULL,
                    incident_id TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    PRIMARY KEY (stage_id, incident_id, event_id)
                )
            """)

            # 6. Suppression Records Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppression_records (
                    suppression_id TEXT PRIMARY KEY,
                    target_id TEXT NOT NULL,
                    reason_code TEXT NOT NULL,
                    missing_requirements_json TEXT NOT NULL,
                    details_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_events(self, events: List[ThreatWeaveEvent]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for ev in events:
                cursor.execute("""
                    INSERT OR REPLACE INTO events (
                        event_id, timestamp, event_type, source, action,
                        user_id, device_id, src_ip, dst_ip, application,
                        resource, session_id, attributes_json, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ev.event_id,
                    ev.timestamp,
                    ev.event_type,
                    ev.source,
                    ev.action,
                    ev.user_id,
                    ev.device_id,
                    ev.src_ip,
                    ev.dst_ip,
                    ev.application,
                    ev.resource,
                    ev.session_id,
                    json.dumps(ev.attributes),
                    json.dumps(ev.raw),
                ))
            conn.commit()

    def save_signals(self, signals: List[Signal]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for sig in signals:
                cursor.execute("""
                    INSERT OR REPLACE INTO signals (
                        signal_id, event_id, signal_type, stage, score, reason_code, parameters_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sig.signal_id,
                    sig.event_id,
                    sig.signal_type,
                    sig.stage,
                    sig.score,
                    sig.reason_code,
                    json.dumps(sig.parameters),
                ))
            conn.commit()

    def save_incident(self, incident: Incident, stages: List[Stage]) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO incidents (
                    incident_id, status, severity, risk_index,
                    risk_components_json, entity_ids_json, stage_ids_json,
                    evidence_event_ids_json, analysis_version, rule_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                incident.incident_id,
                incident.status,
                incident.severity,
                incident.risk_index,
                json.dumps(incident.risk_components.model_dump()),
                json.dumps(incident.entity_ids),
                json.dumps(incident.stage_ids),
                json.dumps(incident.evidence_event_ids),
                incident.analysis_version,
                incident.rule_version,
                now_iso,
            ))

            # Clean prior stages and stage_evidence for this incident to maintain idempotency
            cursor.execute("DELETE FROM stage_evidence WHERE incident_id = ?", (incident.incident_id,))
            cursor.execute("DELETE FROM stages WHERE incident_id = ?", (incident.incident_id,))

            for stg in stages:
                cursor.execute("""
                    INSERT OR REPLACE INTO stages (
                        stage_id, incident_id, name, sequence_index,
                        start_time, end_time, reason_codes_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    stg.stage_id,
                    stg.incident_id,
                    stg.name,
                    stg.sequence_index,
                    stg.start_time,
                    stg.end_time,
                    json.dumps(stg.reason_codes),
                ))

                for eid in stg.evidence_event_ids:
                    cursor.execute("""
                        INSERT OR REPLACE INTO stage_evidence (
                            stage_id, incident_id, event_id
                        ) VALUES (?, ?, ?)
                    """, (stg.stage_id, stg.incident_id, eid))

            conn.commit()

    def save_suppression_record(self, record: SuppressionRecord) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO suppression_records (
                    suppression_id, target_id, reason_code,
                    missing_requirements_json, details_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                record.suppression_id,
                record.target_id,
                record.reason_code,
                json.dumps(record.missing_requirements),
                json.dumps(record.details),
                now_iso,
            ))
            conn.commit()

    def list_incidents(self) -> List[Incident]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM incidents ORDER BY risk_index DESC, created_at DESC")
            rows = cursor.fetchall()

            incidents: List[Incident] = []
            for r in rows:
                risk_comp_dict = json.loads(r["risk_components_json"])
                incidents.append(
                    Incident(
                        incident_id=r["incident_id"],
                        status=r["status"],
                        severity=r["severity"],
                        risk_index=r["risk_index"],
                        risk_components=RiskComponents(**risk_comp_dict),
                        entity_ids=json.loads(r["entity_ids_json"]),
                        stage_ids=json.loads(r["stage_ids_json"]),
                        evidence_event_ids=json.loads(r["evidence_event_ids_json"]),
                        analysis_version=r["analysis_version"],
                        rule_version=r["rule_version"],
                    )
                )
            return incidents

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM incidents WHERE incident_id = ?", (incident_id,))
            r = cursor.fetchone()
            if not r:
                return None
            risk_comp_dict = json.loads(r["risk_components_json"])
            return Incident(
                incident_id=r["incident_id"],
                status=r["status"],
                severity=r["severity"],
                risk_index=r["risk_index"],
                risk_components=RiskComponents(**risk_comp_dict),
                entity_ids=json.loads(r["entity_ids_json"]),
                stage_ids=json.loads(r["stage_ids_json"]),
                evidence_event_ids=json.loads(r["evidence_event_ids_json"]),
                analysis_version=r["analysis_version"],
                rule_version=r["rule_version"],
            )

    def get_incident_stages(self, incident_id: str) -> List[Stage]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stages WHERE incident_id = ? ORDER BY sequence_index ASC", (incident_id,))
            rows = cursor.fetchall()

            stages: List[Stage] = []
            for r in rows:
                sid = r["stage_id"]
                # Fetch evidence event ids
                cursor.execute(
                    "SELECT event_id FROM stage_evidence WHERE stage_id = ? AND incident_id = ?",
                    (sid, incident_id),
                )
                ev_rows = cursor.fetchall()
                evidence_ids = [er["event_id"] for er in ev_rows]

                stages.append(
                    Stage(
                        stage_id=sid,
                        incident_id=r["incident_id"],
                        name=r["name"],
                        sequence_index=r["sequence_index"],
                        start_time=r["start_time"],
                        end_time=r["end_time"],
                        evidence_event_ids=evidence_ids,
                        reason_codes=json.loads(r["reason_codes_json"]),
                    )
                )
            return stages

    def get_events_by_ids(self, event_ids: List[str]) -> List[ThreatWeaveEvent]:
        if not event_ids:
            return []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join("?" for _ in event_ids)
            cursor.execute(f"SELECT * FROM events WHERE event_id IN ({placeholders})", event_ids)
            rows = cursor.fetchall()

            events: List[ThreatWeaveEvent] = []
            for r in rows:
                events.append(
                    ThreatWeaveEvent(
                        event_id=r["event_id"],
                        timestamp=r["timestamp"],
                        event_type=r["event_type"],
                        source=r["source"],
                        action=r["action"],
                        user_id=r["user_id"],
                        device_id=r["device_id"],
                        src_ip=r["src_ip"],
                        dst_ip=r["dst_ip"],
                        application=r["application"],
                        resource=r["resource"],
                        session_id=r["session_id"],
                        attributes=json.loads(r["attributes_json"] or "{}"),
                        raw=json.loads(r["raw_json"] or "{}"),
                    )
                )
            return events

    def get_signals_by_event_ids(self, event_ids: List[str]) -> List[Signal]:
        if not event_ids:
            return []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join("?" for _ in event_ids)
            cursor.execute(f"SELECT * FROM signals WHERE event_id IN ({placeholders})", event_ids)
            rows = cursor.fetchall()

            signals: List[Signal] = []
            for r in rows:
                signals.append(
                    Signal(
                        signal_id=r["signal_id"],
                        event_id=r["event_id"],
                        signal_type=r["signal_type"],
                        stage=r["stage"],
                        score=r["score"],
                        reason_code=r["reason_code"],
                        parameters=json.loads(r["parameters_json"] or "{}"),
                    )
                )
            return signals

    def list_suppression_records(self) -> List[SuppressionRecord]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppression_records ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [
                SuppressionRecord(
                    suppression_id=r["suppression_id"],
                    target_id=r["target_id"],
                    reason_code=r["reason_code"],
                    missing_requirements=json.loads(r["missing_requirements_json"]),
                    details=json.loads(r["details_json"]),
                )
                for r in rows
            ]
