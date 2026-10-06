"""
Dataset Ingestion & Scenario Catalog API Routes.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.ingestion.validator import ingest_jsonl_content, ingest_jsonl_file
from app.storage.repository import StorageRepository

router = APIRouter(prefix="/datasets", tags=["Datasets"])
SCENARIOS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "scenarios"


class IngestRequest(BaseModel):
    dataset_id: str = "custom-dataset"
    content: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None


@router.get("/scenarios")
def list_available_scenarios():
    """Lists pre-packaged seed demonstration scenarios."""
    scenarios = [
        {
            "id": "attack_insider_usb",
            "name": "Canonical Attack: Insider Threat & USB Exfiltration",
            "file": "attack_insider_usb.jsonl",
            "type": "attack",
            "description": "Multi-stage attack: external VPN login -> sensitive payroll & merger collection -> USB mount -> USB data copy -> outbound network exfil.",
        },
        {
            "id": "benign_admin",
            "name": "Benign Baseline: Routine Admin & IT Maintenance",
            "file": "benign_admin.jsonl",
            "type": "benign",
            "description": "Normal administrator backup tasks, standard employee document access, and authorized IT USB diagnostic scans.",
        },
        {
            "id": "attack_partial",
            "name": "Partial Attack: Missing Data Copy / Exfiltration",
            "file": "attack_partial.jsonl",
            "type": "partial",
            "description": "Unusual login and sensitive access without completing file copy to removable media.",
        },
        {
            "id": "malformed_logs",
            "name": "Negative Control: Corrupted / Malformed Telemetry",
            "file": "malformed_logs.jsonl",
            "type": "malformed",
            "description": "Invalid JSON syntax, missing IDs, bad timestamp formats, and duplicate records to test quarantining.",
        },
    ]

    # Annotate with real record counts
    for sc in scenarios:
        p = SCENARIOS_DIR / sc["file"]
        if p.is_file():
            sc["exists"] = True
            sc["records_count"] = len(p.read_text(encoding="utf-8").strip().splitlines())
        else:
            sc["exists"] = False
            sc["records_count"] = 0

    return {"scenarios": scenarios}


@router.post("/ingest")
def ingest_dataset(req: IngestRequest):
    """Parses and validates raw JSONL content or records into storage."""
    repo = StorageRepository()

    if req.records:
        import json
        content = "\n".join(json.dumps(r) for r in req.records)
        report = ingest_jsonl_content(content)
    elif req.content:
        report = ingest_jsonl_content(req.content)
    else:
        raise HTTPException(status_code=400, detail="Either 'content' or 'records' must be provided.")

    repo.save_events(report.events)

    return {
        "dataset_id": req.dataset_id,
        "accepted_events": report.valid_records,
        "rejected_events": report.quarantined_records,
        "warnings": report.duplicate_records,
        "quarantine_summary": [q.to_dict() for q in report.quarantine[:5]],
    }
