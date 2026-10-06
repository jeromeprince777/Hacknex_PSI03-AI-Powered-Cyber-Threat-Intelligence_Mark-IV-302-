"""
ThreatWeave End-to-End Detection & Correlation Pipeline Orchestrator.
Connects ingestion, rules, novelty, sequence correlation, entity graph, risk scoring, and storage.
"""

from __future__ import annotations
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from app.schemas.events import (
    Incident,
    Signal,
    Stage,
    SuppressionRecord,
    ThreatWeaveEvent,
)
from app.ingestion.validator import ingest_jsonl_content, ingest_jsonl_file
from app.detectors.rules import AtomicRuleDetector
from app.detectors.novelty import BaselineProfile, EntityNoveltyScorer
from app.detectors.sequence import TemporalSequenceCorrelator
from app.graph.builder import EntityGraphBuilder
from app.scoring.risk import RiskEngine
from app.storage.repository import StorageRepository


class PipelineOrchestrator:
    """
    Coordinates the entire ThreatWeave detection workflow deterministically.
    """

    def __init__(self, repo: Optional[StorageRepository] = None) -> None:
        self.repo = repo or StorageRepository()
        self.risk_engine = RiskEngine()
        self.novelty_scorer = EntityNoveltyScorer()

    def run_analysis(
        self,
        dataset_source: Union[str, Path, List[Dict[str, Any]]],
        dataset_id: str = "demo-dataset",
    ) -> Dict[str, Any]:
        """
        Executes end-to-end detection pipeline on the provided dataset.
        """
        start_time = time.perf_counter()

        # Step 1: Ingestion & Validation
        if isinstance(dataset_source, list):
            # Already a list of dicts
            import json
            content = "\n".join(json.dumps(r) for r in dataset_source)
            report = ingest_jsonl_content(content)
        elif isinstance(dataset_source, (str, Path)) and Path(dataset_source).is_file():
            report = ingest_jsonl_file(dataset_source)
        else:
            report = ingest_jsonl_content(str(dataset_source))

        events = report.events
        self.repo.save_events(events)

        # Step 2: Atomic Signal Detection
        all_signals: List[Signal] = []
        for ev in events:
            sigs = AtomicRuleDetector.evaluate_event(ev)
            all_signals.extend(sigs)
        self.repo.save_signals(all_signals)

        # Step 3: Entity Graph Construction
        graph_builder = EntityGraphBuilder()
        graph_builder.add_events_batch(events)

        # Step 4: Clustering by Primary Entity
        clusters = TemporalSequenceCorrelator.cluster_events_and_signals(events, all_signals)

        created_incidents: List[Incident] = []
        suppression_records: List[SuppressionRecord] = []

        # Step 5: Correlation, Promotion Gate, and Risk Scoring
        inc_counter = 1
        for cluster in clusters:
            temp_inc_id = f"inc-{inc_counter:03d}"
            stages = TemporalSequenceCorrelator.build_attack_stages(temp_inc_id, cluster)

            # Evaluate False-Positive Promotion Gate
            promoted, suppression = TemporalSequenceCorrelator.evaluate_promotion_gate(cluster, stages)

            if promoted:
                seq_score = TemporalSequenceCorrelator.calculate_sequence_score(stages, cluster.events)
                nov_score, _ = self.novelty_scorer.score_event_cluster(cluster.events)

                risk_index, severity, risk_components = self.risk_engine.calculate_risk(
                    signals=cluster.signals,
                    sequence_score=seq_score,
                    entity_novelty=nov_score,
                    events=cluster.events,
                )

                incident = Incident(
                    incident_id=temp_inc_id,
                    status="open",
                    severity=severity,
                    risk_index=risk_index,
                    risk_components=risk_components,
                    entity_ids=sorted(list(set(
                        [e.user_id for e in cluster.events if e.user_id]
                        + [e.device_id for e in cluster.events if e.device_id]
                        + [e.src_ip for e in cluster.events if e.src_ip]
                    ))),
                    stage_ids=[s.stage_id for s in stages],
                    evidence_event_ids=list(dict.fromkeys(
                        eid for s in stages for eid in s.evidence_event_ids
                    )),
                    analysis_version="0.1.0",
                    rule_version="demo-2026-01",
                )

                self.repo.save_incident(incident, stages)
                created_incidents.append(incident)
                inc_counter += 1
            else:
                if suppression:
                    self.repo.save_suppression_record(suppression)
                    suppression_records.append(suppression)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "dataset_id": dataset_id,
            "status": "success",
            "runtime_ms": elapsed_ms,
            "total_records_processed": report.total_records,
            "valid_events": report.valid_records,
            "quarantined_records": report.quarantined_records,
            "signals_detected": len(all_signals),
            "clusters_formed": len(clusters),
            "incidents_created": len(created_incidents),
            "suppressed_clusters": len(suppression_records),
            "incidents": [inc.model_dump() for inc in created_incidents],
            "suppressions": [sup.model_dump() for sup in suppression_records],
        }
