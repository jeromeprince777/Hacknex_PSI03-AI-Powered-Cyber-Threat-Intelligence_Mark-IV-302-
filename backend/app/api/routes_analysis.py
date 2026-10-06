"""
Detection & Correlation Analysis Runner API Routes.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.pipeline import PipelineOrchestrator
from app.storage.repository import StorageRepository

router = APIRouter(prefix="/analysis", tags=["Analysis"])
SCENARIOS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "scenarios"


class RunAnalysisRequest(BaseModel):
    dataset_id: str = "demo-run"
    scenario_name: Optional[str] = "attack_insider_usb.jsonl"
    records: Optional[List[Dict[str, Any]]] = None
    mode: str = "full"


@router.post("/run")
def run_analysis_pipeline(req: RunAnalysisRequest):
    """
    Runs end-to-end detection, correlation, and incident generation.
    Can replay pre-packaged scenario files or user-supplied records.
    """
    repo = StorageRepository()
    orchestrator = PipelineOrchestrator(repo=repo)

    if req.records:
        result = orchestrator.run_analysis(req.records, dataset_id=req.dataset_id)
    elif req.scenario_name:
        fname = req.scenario_name if req.scenario_name.endswith(".jsonl") else f"{req.scenario_name}.jsonl"
        scenario_file = SCENARIOS_DIR / fname
        if not scenario_file.is_file():
            raise HTTPException(status_code=404, detail=f"Scenario file '{req.scenario_name}' not found.")
        result = orchestrator.run_analysis(scenario_file, dataset_id=req.dataset_id or req.scenario_name)
    else:
        raise HTTPException(status_code=400, detail="Either 'scenario_name' or 'records' must be specified.")

    return result
