"""
ThreatWeave Deterministic Risk Index Engine.
Combines Signal Severity, Sequence Consistency, Entity Novelty, and Robust Statistical Anomaly Scoring.
Strictly adheres to docs/01_PRD.md Section 11 and docs/02_TECHNICAL_PRD.md Section 7 & 9.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Tuple

from app.schemas.events import RiskComponents, Signal, ThreatWeaveEvent


class RobustAnomalyScorer:
    """
    Evaluates statistical outlier magnitude using robust standardized deviation
    over a compact 6-dimensional telemetry feature vector.
    Conforms to docs/02_TECHNICAL_PRD.md Section 7 (Layer D - robust standardized deviation).
    """

    # Baseline enterprise reference parameters (mean, std, feature_weight)
    # Features: [external_auth, sensitive_files, usb_mount, usb_copy, log_bytes, event_velocity]
    BASELINE_PARAMS = {
        "external_auth": {"mean": 0.05, "std": 0.22, "weight": 0.20},
        "sensitive_files": {"mean": 0.10, "std": 0.35, "weight": 0.25},
        "usb_mount": {"mean": 0.08, "std": 0.27, "weight": 0.15},
        "usb_copy": {"mean": 0.01, "std": 0.10, "weight": 0.25},
        "log_bytes": {"mean": 3.80, "std": 1.20, "weight": 0.10},
        "event_velocity": {"mean": 4.50, "std": 2.50, "weight": 0.05},
    }

    def extract_features(self, events: List[ThreatWeaveEvent]) -> Dict[str, float]:
        """
        Extracts fixed 6-dimensional feature dictionary from an event cluster.
        """
        is_external = 0.0
        sensitive_files = 0.0
        has_usb_mount = 0.0
        usb_copies = 0.0
        total_bytes = 0.0

        for ev in events:
            # 1. External auth
            if ev.event_type == "login_success":
                src = ev.src_ip or ""
                if src.startswith("203.") or src.startswith("198.") or "Bucharest" in str(ev.attributes.get("login_location", "")):
                    is_external = 1.0

            # 2. Sensitive files
            if ev.event_type == "file_access":
                res = str(ev.resource or "").lower()
                if any(k in res for k in ["payroll", "titan", "confidential", "restricted"]):
                    sensitive_files += 1.0

            # 3. USB mount
            if ev.event_type == "usb_connected":
                has_usb_mount = 1.0

            # 4. USB copy
            if ev.event_type == "usb_copy":
                usb_copies += 1.0

            # 5. Bytes
            b = ev.attributes.get("bytes", 0) or ev.attributes.get("bytes_sent", 0) or 0
            total_bytes += float(b)

        log_bytes = math.log10(total_bytes + 1.0)
        event_velocity = float(len(events))

        return {
            "external_auth": is_external,
            "sensitive_files": sensitive_files,
            "usb_mount": has_usb_mount,
            "usb_copy": usb_copies,
            "log_bytes": log_bytes,
            "event_velocity": event_velocity,
        }

    def calculate_anomaly_score(self, events: List[ThreatWeaveEvent]) -> float:
        """
        Calculates normalized outlier score [0.0, 1.0] where higher = more anomalous.
        """
        if not events:
            return 0.0

        features = self.extract_features(events)
        weighted_z_sum = 0.0
        total_weight = 0.0

        for feat_name, params in self.BASELINE_PARAMS.items():
            val = features.get(feat_name, 0.0)
            mean = params["mean"]
            std = params["std"]
            weight = params["weight"]

            # Compute positive standard deviation excess
            z = max(0.0, (val - mean) / std)
            weighted_z_sum += weight * z
            total_weight += weight

        # Standardized deviation aggregation
        mean_z = weighted_z_sum / total_weight if total_weight > 0 else 0.0

        # Map to [0.0, 1.0] using a smooth logistic transfer function
        # A normal baseline session (mean_z ~ 0.2 - 0.5) maps to 0.10 - 0.25
        # An extreme multi-vector anomaly (mean_z >= 3.0) maps to 0.70 - 0.90
        scaled = 1.0 / (1.0 + math.exp(-0.9 * (mean_z - 1.8)))
        clamped = max(0.05, min(0.95, scaled))
        return round(clamped, 2)


class RiskEngine:
    """
    Computes explainable Risk Index and transparent factor breakdown.
    """

    WEIGHTS = {
        "signal": 0.35,
        "sequence": 0.30,
        "novelty": 0.20,
        "anomaly": 0.15,
    }

    def __init__(self) -> None:
        self.anomaly_scorer = RobustAnomalyScorer()

    def calculate_risk(
        self,
        signals: List[Signal],
        sequence_score: float,
        entity_novelty: float,
        events: List[ThreatWeaveEvent],
    ) -> Tuple[int, str, RiskComponents]:
        """
        Computes final deterministic Risk Index, severity label, and persisted factor components.
        Formula: clamp(100 * (0.35*Signal + 0.30*Sequence + 0.20*Novelty + 0.15*Anomaly))
        """
        # 1. Signal Score: weighted severity across observed attack stages
        if signals:
            stage_max_scores: Dict[str, float] = {}
            for s in signals:
                stage_max_scores[s.stage] = max(stage_max_scores.get(s.stage, 0.0), s.score)
            signal_score = round(sum(stage_max_scores.values()) / len(stage_max_scores), 2)
        else:
            signal_score = 0.0

        # 2. Sequence Score
        clamped_seq = round(max(0.0, min(1.0, sequence_score)), 2)

        # 3. Entity Novelty
        clamped_nov = round(max(0.0, min(1.0, entity_novelty)), 2)

        # 4. Statistical Anomaly Score
        anomaly_score = self.anomaly_scorer.calculate_anomaly_score(events)

        # Deterministic Weighted Formula
        raw_score = 100.0 * (
            self.WEIGHTS["signal"] * signal_score
            + self.WEIGHTS["sequence"] * clamped_seq
            + self.WEIGHTS["novelty"] * clamped_nov
            + self.WEIGHTS["anomaly"] * anomaly_score
        )

        risk_index = int(round(max(0.0, min(100.0, raw_score))))

        # Severity semantics per PRD Section 11
        if risk_index >= 75:
            severity = "high"
        elif risk_index >= 50:
            severity = "medium"
        elif risk_index >= 25:
            severity = "low"
        else:
            severity = "informational"

        components = RiskComponents(
            signal_score=signal_score,
            sequence_score=clamped_seq,
            entity_novelty=clamped_nov,
            anomaly_score=anomaly_score,
            weights=self.WEIGHTS,
        )

        return risk_index, severity, components
