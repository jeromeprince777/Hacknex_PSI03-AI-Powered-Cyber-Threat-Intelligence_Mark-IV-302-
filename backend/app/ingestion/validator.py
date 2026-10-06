"""
ThreatWeave Ingestion Validator & Quarantining Pipeline.
Strictly adheres to docs/PRD.md FR-02 and docs/04_DATA_API_CONTRACTS.md.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from pydantic import ValidationError

from app.schemas.events import ThreatWeaveEvent


class QuarantineRecord:
    def __init__(
        self,
        record_index: int,
        raw_payload: str,
        reason_code: str,
        error_details: str,
    ) -> None:
        self.record_index = record_index
        self.raw_payload = raw_payload
        self.reason_code = reason_code
        self.error_details = error_details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_index": self.record_index,
            "raw_payload": self.raw_payload,
            "reason_code": self.reason_code,
            "error_details": self.error_details,
        }


class IngestionReport:
    def __init__(self) -> None:
        self.total_records: int = 0
        self.valid_records: int = 0
        self.quarantined_records: int = 0
        self.duplicate_records: int = 0
        self.events: List[ThreatWeaveEvent] = []
        self.quarantine: List[QuarantineRecord] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "quarantined_records": self.quarantined_records,
            "duplicate_records": self.duplicate_records,
            "quarantine_reasons": [q.to_dict() for q in self.quarantine],
        }


def validate_dict_event(
    raw_dict: Dict[str, Any],
    seen_event_ids: Set[str],
    index: int = 0,
) -> Tuple[Optional[ThreatWeaveEvent], Optional[QuarantineRecord]]:
    """
    Validates a single pre-parsed dictionary against the Canonical Event Schema.
    Ensures unique event_id within the ingest session.
    """
    event_id = raw_dict.get("event_id")
    if not event_id or not str(event_id).strip():
        return None, QuarantineRecord(
            record_index=index,
            raw_payload=json.dumps(raw_dict),
            reason_code="MISSING_EVENT_ID",
            error_details="Required field 'event_id' is missing or empty.",
        )

    str_event_id = str(event_id).strip()
    if str_event_id in seen_event_ids:
        return None, QuarantineRecord(
            record_index=index,
            raw_payload=json.dumps(raw_dict),
            reason_code="DUPLICATE_EVENT_ID",
            error_details=f"Event ID '{str_event_id}' already seen in this stream.",
        )

    try:
        event = ThreatWeaveEvent(**raw_dict)
        seen_event_ids.add(str_event_id)
        return event, None
    except ValidationError as ve:
        return None, QuarantineRecord(
            record_index=index,
            raw_payload=json.dumps(raw_dict),
            reason_code="SCHEMA_VALIDATION_ERROR",
            error_details=str(ve),
        )
    except Exception as e:
        return None, QuarantineRecord(
            record_index=index,
            raw_payload=json.dumps(raw_dict),
            reason_code="UNEXPECTED_ERROR",
            error_details=str(e),
        )


def ingest_jsonl_content(content: str) -> IngestionReport:
    """
    Parses and validates a raw string of newline-delimited JSON.
    Quarantines malformed syntax or invalid schema records without crashing.
    """
    report = IngestionReport()
    seen_event_ids: Set[str] = set()

    lines = content.strip().splitlines()
    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        if not clean_line:
            continue

        report.total_records += 1

        # Step 1: JSON syntax parse
        try:
            payload = json.loads(clean_line)
        except json.JSONDecodeError as jde:
            report.quarantined_records += 1
            report.quarantine.append(
                QuarantineRecord(
                    record_index=idx,
                    raw_payload=clean_line,
                    reason_code="INVALID_JSON",
                    error_details=f"JSON parsing failed: {jde}",
                )
            )
            continue

        if not isinstance(payload, dict):
            report.quarantined_records += 1
            report.quarantine.append(
                QuarantineRecord(
                    record_index=idx,
                    raw_payload=clean_line,
                    reason_code="NOT_A_JSON_OBJECT",
                    error_details="Top-level item must be a JSON object.",
                )
            )
            continue

        # Step 2: Canonical Schema & Uniqueness Validation
        event, quarantine = validate_dict_event(payload, seen_event_ids, index=idx)
        if event is not None:
            report.valid_records += 1
            report.events.append(event)
        elif quarantine is not None:
            report.quarantined_records += 1
            if quarantine.reason_code == "DUPLICATE_EVENT_ID":
                report.duplicate_records += 1
            report.quarantine.append(quarantine)

    return report


def ingest_jsonl_file(file_path: Union[str, Path]) -> IngestionReport:
    """
    Ingests and validates a JSONL file from disk.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    content = path.read_text(encoding="utf-8")
    return ingest_jsonl_content(content)
