import {
  AnalysisRunResult,
  CopilotResponse,
  EvidencePack,
  Incident,
  IncidentSubgraph,
  ScenarioItem,
  SuppressionRecord,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function fetchHealth(): Promise<Record<string, unknown>> {
  const res = await fetch(`${BASE_URL}/api/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchIncidents(): Promise<Incident[]> {
  const res = await fetch(`${BASE_URL}/api/incidents`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load incidents");
  const data = await res.json();
  return data.incidents || [];
}

export async function fetchIncidentEvidence(incidentId: string): Promise<EvidencePack> {
  const res = await fetch(`${BASE_URL}/api/incidents/${incidentId}/evidence`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load evidence for ${incidentId}`);
  return res.json();
}

export async function fetchIncidentGraph(incidentId: string): Promise<IncidentSubgraph> {
  const res = await fetch(`${BASE_URL}/api/incidents/${incidentId}/graph`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load graph for ${incidentId}`);
  return res.json();
}

export async function fetchSuppressionRecords(): Promise<SuppressionRecord[]> {
  const res = await fetch(`${BASE_URL}/api/incidents/suppression`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load suppression records");
  const data = await res.json();
  return data.suppression_records || [];
}

export async function fetchScenarios(): Promise<ScenarioItem[]> {
  const res = await fetch(`${BASE_URL}/api/datasets/scenarios`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load scenarios catalog");
  const data = await res.json();
  return data.scenarios || [];
}

export async function runAnalysis(scenarioName: string): Promise<AnalysisRunResult> {
  const res = await fetch(`${BASE_URL}/api/analysis/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario_name: scenarioName }),
  });
  if (!res.ok) throw new Error(`Failed to run analysis for ${scenarioName}`);
  return res.json();
}

export async function askCopilot(
  incidentId: string,
  question: string,
  injectFakeEventId?: string,
  injectFakeActionId?: string
): Promise<CopilotResponse> {
  const res = await fetch(`${BASE_URL}/api/copilot/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      incident_id: incidentId,
      question,
      inject_fake_event_id: injectFakeEventId || null,
      inject_fake_action_id: injectFakeActionId || null,
    }),
  });
  if (!res.ok) throw new Error("Copilot explanation request failed");
  return res.json();
}
