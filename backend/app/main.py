"""
ThreatWeave — Main FastAPI Application.
Problem Statement: HNX26PSI03 (AI-Powered Cyber Threat Intelligence).
Evidence-first cyber threat investigation and attack-chain reconstruction system.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router
from app.api.routes_ingest import router as ingest_router
from app.api.routes_analysis import router as analysis_router
from app.api.routes_incidents import router as incidents_router
from app.api.routes_copilot import router as copilot_router
from app.pipeline import PipelineOrchestrator
from app.storage.repository import StorageRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On cold startup, if no incidents exist, automatically seeds the canonical demo attack.
    Ensures that evaluator or fresh UI clone immediately displays working telemetry.
    """
    repo = StorageRepository()
    existing = repo.list_incidents()
    if not existing:
        scenarios_dir = Path(__file__).resolve().parent.parent.parent / "data" / "scenarios"
        attack_file = scenarios_dir / "attack_insider_usb.jsonl"
        if attack_file.is_file():
            orchestrator = PipelineOrchestrator(repo=repo)
            orchestrator.run_analysis(attack_file, dataset_id="attack_insider_usb.jsonl")
    yield


app = FastAPI(
    title="ThreatWeave Cyber Threat Intelligence API",
    description="Evidence-first attack chain reconstruction and audit platform.",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(ingest_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")
app.include_router(copilot_router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "ThreatWeave API",
        "docs": "/docs",
        "health": "/api/health",
        "incidents": "/api/incidents",
    }
