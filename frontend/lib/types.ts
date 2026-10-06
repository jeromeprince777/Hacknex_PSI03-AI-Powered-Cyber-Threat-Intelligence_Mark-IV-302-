export interface RiskComponents {
  signal_score: number;
  sequence_score: number;
  entity_novelty: number;
  anomaly_score: number;
  weights: {
    signal: number;
    sequence: number;
    novelty: number;
    anomaly: number;
  };
}

export interface Incident {
  incident_id: string;
  status: string;
  severity: "informational" | "low" | "medium" | "high";
  risk_index: number;
  risk_components: RiskComponents;
  entity_ids: string[];
  stage_ids: string[];
  evidence_event_ids: string[];
  analysis_version: string;
  rule_version: string;
}

export interface Stage {
  stage_id: string;
  incident_id: string;
  name: string;
  sequence_index: number;
  start_time: string;
  end_time: string;
  evidence_event_ids: string[];
  reason_codes: string[];
}

export interface TimelineItem {
  event_id: string;
  timestamp: string;
  stage_id: string;
  source: string;
  event_type: string;
  fact: string;
  linked_entities: string[];
}

export interface EvidenceItem {
  event_id: string;
  timestamp: string;
  source: string;
  raw: Record<string, unknown>;
  normalized: Record<string, unknown>;
  detectors: Array<{
    reason_code: string;
    signal_type: string;
    stage: string;
    score: string;
  }>;
  linked_entities: string[];
}

export interface ApprovedAction {
  action_id: string;
  label: string;
  stage_keys: string[];
  description: string;
}

export interface EvidencePack {
  incident: Incident;
  timeline: TimelineItem[];
  stages: Stage[];
  events: EvidenceItem[];
  entities: string[];
  approved_actions: ApprovedAction[];
}

export interface SubgraphNode {
  id: string;
  label: string;
  type: string;
  data: Record<string, unknown>;
}

export interface SubgraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  relation?: string;
}

export interface IncidentSubgraph {
  incident_id: string;
  nodes: SubgraphNode[];
  edges: SubgraphEdge[];
  total_nodes: number;
  total_edges: number;
}

export interface StageExplanation {
  stage_id: string;
  explanation: string;
  evidence_event_ids: string[];
}

export interface RecommendedAction {
  action_id: string;
  reason: string;
}

export interface CopilotExplanation {
  summary: string;
  confidence: "low" | "medium" | "high";
  stage_explanations: StageExplanation[];
  recommended_actions: RecommendedAction[];
  limitations: string[];
}

export interface CopilotResponse {
  incident_id: string;
  question: string;
  verified: boolean;
  verification_status: "VERIFIED" | "REJECTED";
  rejection_reason?: string | null;
  explanation?: CopilotExplanation | null;
  evidence_pack?: EvidencePack | null;
}

export interface SuppressionRecord {
  suppression_id: string;
  target_id: string;
  reason_code: string;
  missing_requirements: string[];
  details: Record<string, unknown>;
  created_at?: string;
}

export interface ScenarioItem {
  id: string;
  name: string;
  file: string;
  type: "attack" | "benign" | "partial" | "malformed";
  description: string;
  exists: boolean;
  records_count: number;
}

export interface AnalysisRunResult {
  dataset_id: string;
  status: string;
  runtime_ms: number;
  total_records_processed: number;
  valid_events: number;
  quarantined_records: number;
  signals_detected: number;
  clusters_formed: number;
  incidents_created: number;
  suppressed_clusters: number;
  incidents: Incident[];
  suppressions: SuppressionRecord[];
}
