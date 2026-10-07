"use client";

import React, { useEffect, useState } from "react";
import { AlertCircle, Check, FileJson2, Play, RotateCw, Terminal, Layers } from "lucide-react";
import { fetchScenarios, runAnalysis } from "../lib/api";
import { AnalysisRunResult, ScenarioItem } from "../lib/types";

interface ReplayLabProps {
  onAnalysisCompleted: () => void;
}

const typeLabels: Record<ScenarioItem["type"], string> = {
  attack: "ATTACK SCENARIO",
  benign: "BENIGN BASELINE",
  partial: "PARTIAL SEQUENCE",
  malformed: "VALIDATION ANOMALY",
};

const runMetrics = (result: AnalysisRunResult) => [
  { label: "RECORDS PROCESSED", value: result.total_records_processed, highlight: "text-cyan-400" },
  { label: "VALID EVENTS", value: result.valid_events, highlight: "text-emerald-400" },
  { label: "SIGNALS DETECTED", value: result.signals_detected, highlight: "text-rose-400" },
  { label: "INCIDENTS CREATED", value: result.incidents_created, highlight: "text-amber-400" },
  { label: "CLUSTERS SUPPRESSED", value: result.suppressed_clusters, highlight: "text-slate-300" },
  { label: "EXECUTION RUNTIME", value: `${result.runtime_ms} ms`, highlight: "text-sky-400" },
];

export const ReplayLab: React.FC<ReplayLabProps> = ({ onAnalysisCompleted }) => {
  const [scenarios, setScenarios] = useState<ScenarioItem[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState("");
  const [loadingScenarios, setLoadingScenarios] = useState(true);
  const [running, setRunning] = useState(false);
  const [lastResult, setLastResult] = useState<AnalysisRunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const loadScenarios = async () => {
      try {
        setLoadingScenarios(true);
        const items = await fetchScenarios();
        if (!active) return;
        setScenarios(items);
        setSelectedScenarioId((current) => current || items[0]?.file || "");
        setError(null);
      } catch (loadError: unknown) {
        if (active) setError(loadError instanceof Error ? loadError.message : "Could not load scenario list.");
      } finally {
        if (active) setLoadingScenarios(false);
      }
    };

    void loadScenarios();
    return () => {
      active = false;
    };
  }, []);

  const activeScenario = scenarios.find((scenario) => scenario.file === selectedScenarioId) ?? null;

  const handleRun = async () => {
    if (!selectedScenarioId || running) return;
    try {
      setRunning(true);
      setError(null);
      const result = await runAnalysis(selectedScenarioId);
      setLastResult(result);
      onAnalysisCompleted();
    } catch (runError: unknown) {
      setError(runError instanceof Error ? runError.message : "Analysis run failed.");
    } finally {
      setRunning(false);
    }
  };

  const selectScenario = (file: string) => {
    setSelectedScenarioId(file);
    setLastResult(null);
    setError(null);
  };

  return (
    <div className="space-y-4 select-none">
      {/* Header */}
      <header className="tw-panel p-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 font-mono-technical text-[10px] text-cyan-400">
            <Terminal className="h-3.5 w-3.5" />
            <span>DATASET REPLAY ENVIRONMENT // PIPELINE BENCHMARK</span>
          </div>
          <h1 className="mt-1 text-lg sm:text-xl font-bold tracking-tight text-slate-100">
            Automated Attack Replay &amp; Telemetry Simulation
          </h1>
          <p className="mt-1 text-xs text-slate-400 max-w-2xl">
            Execute canonical forensic datasets through the validation, atomic detector, novelty scoring, and sequence correlator pipelines.
          </p>
        </div>
        {lastResult && (
          <div role="status" className="inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-950/40 border border-emerald-500/50 text-emerald-300 font-mono-technical text-xs">
            <Check className="h-4 w-4 text-emerald-400" aria-hidden="true" />
            <span>ANALYSIS COMPLETED // STATUS: {lastResult.status.toUpperCase()}</span>
          </div>
        )}
      </header>

      {/* Main Grid */}
      <section className="tw-panel grid min-h-[32rem] grid-cols-1 lg:grid-cols-[19rem_minmax(0,1fr)]" aria-label="Dataset replay controls">
        {/* Left Scenario Sidebar */}
        <aside className="border-b border-slate-800 bg-[#0a0e13] lg:border-b-0 lg:border-r" aria-labelledby="scenario-list-heading">
          <div className="flex items-center justify-between border-b border-slate-800 p-3 bg-[#111822]">
            <div>
              <h2 id="scenario-list-heading" className="text-xs font-bold text-slate-100 font-mono-technical">
                DATASET SCENARIOS
              </h2>
              <p className="mt-0.5 text-[10px] font-mono-technical text-slate-400">{loadingScenarios ? "Loading…" : `${scenarios.length} AVAILABLE`}</p>
            </div>
            <FileJson2 className="h-4 w-4 text-cyan-400" aria-hidden="true" />
          </div>

          {loadingScenarios ? (
            <p role="status" className="p-4 text-xs font-mono-technical text-slate-400">Loading dataset scenarios…</p>
          ) : (
            <ul className="divide-y divide-slate-800/80 font-mono-technical text-xs">
              {scenarios.map((scenario) => {
                const selected = scenario.file === selectedScenarioId;
                return (
                  <li key={scenario.file}>
                    <button
                      type="button"
                      onClick={() => selectScenario(scenario.file)}
                      aria-pressed={selected}
                      className={`block w-full border-l-2 p-3 text-left transition-colors ${
                        selected ? "border-l-cyan-400 bg-[#16202e]" : "border-l-transparent hover:bg-[#111822]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className={`text-xs font-bold ${selected ? "text-cyan-300" : "text-slate-200"}`}>
                          {scenario.name}
                        </span>
                        {selected && <span className="mt-1 h-1.5 w-1.5 rounded-full bg-cyan-400 tactical-pulse" />}
                      </div>
                      <span className="mt-1 block text-[10px] text-slate-400">{typeLabels[scenario.type]}</span>
                      <div className="mt-2 flex items-center justify-between text-[9px] text-slate-400">
                        <span>{scenario.records_count} records</span>
                        <span className={scenario.exists ? "text-emerald-400 font-semibold" : "text-rose-400"}>
                          {scenario.exists ? "READY" : "FILE MISSING"}
                        </span>
                      </div>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </aside>

        {/* Right Active Scenario Workspace */}
        <div className="p-4 sm:p-6 bg-[#0b0f14]">
          {activeScenario ? (
            <div className="max-w-4xl space-y-5">
              <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-800 pb-4">
                <div className="min-w-0">
                  <span className="inline-block border border-slate-700 bg-[#111822] px-2 py-0.5 text-[9px] font-mono-technical font-bold text-cyan-300">
                    {typeLabels[activeScenario.type]}
                  </span>
                  <h2 className="mt-2 text-lg font-bold tracking-tight text-slate-100">{activeScenario.name}</h2>
                  <p className="mt-1 max-w-2xl text-xs leading-relaxed text-slate-300">{activeScenario.description}</p>
                  <p className="mt-2 break-all font-mono-technical text-[10px] text-slate-400">
                    FILE: {activeScenario.file} · {activeScenario.records_count} RECORDS
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleRun}
                  disabled={running || !activeScenario.exists}
                  aria-busy={running}
                  className="tw-inline-action tw-primary-action px-4 py-2 text-xs font-bold shrink-0"
                >
                  {running ? <RotateCw className="h-3.5 w-3.5 animate-spin" aria-hidden="true" /> : <Play className="h-3.5 w-3.5" aria-hidden="true" />}
                  <span>{running ? "ANALYZING PIPELINE…" : "RUN ANALYSIS"}</span>
                </button>
              </div>

              {error && (
                <div role="alert" className="flex items-start gap-2 border border-rose-500/50 bg-rose-950/30 p-3 font-mono-technical text-xs text-rose-300">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-400" aria-hidden="true" />
                  <span>{error}</span>
                </div>
              )}

              {lastResult ? (
                <section aria-labelledby="replay-result-heading" className="space-y-4 font-mono-technical">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <h3 id="replay-result-heading" className="text-xs font-bold text-slate-100">
                      PIPELINE EXECUTION TELEMETRY
                    </h3>
                    <span className="text-[10px] text-cyan-400">DATASET: {lastResult.dataset_id}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                    {runMetrics(lastResult).map((m) => (
                      <div key={m.label} className="border border-slate-800 bg-[#111822] p-3">
                        <span className="text-[9px] font-bold text-slate-400 block">{m.label}</span>
                        <span className={`text-xl font-bold mt-1 block ${m.highlight}`}>{m.value}</span>
                      </div>
                    ))}
                  </div>

                  {lastResult.incidents.length > 0 && (
                    <div className="border border-slate-800 bg-[#111822] p-3 mt-4">
                      <h4 className="text-xs font-bold text-slate-100 mb-2">RECONSTRUCTED INCIDENTS</h4>
                      <ul className="divide-y divide-slate-800 text-xs">
                        {lastResult.incidents.map((incident) => (
                          <li key={incident.incident_id} className="flex items-center justify-between py-2">
                            <span className="font-bold text-cyan-400">{incident.incident_id}</span>
                            <span className="text-slate-300">
                              SEVERITY: <span className="text-rose-400 font-bold">{incident.severity.toUpperCase()}</span> · RISK: {incident.risk_index}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </section>
              ) : (
                <p className="text-xs font-mono-technical text-slate-400">
                  Execute analysis to view real-time stage detection, evidence validation, and threat correlation.
                </p>
              )}
            </div>
          ) : (
            <div className="flex min-h-64 flex-col items-center justify-center font-mono-technical text-slate-400">
              <FileJson2 className="h-6 w-6 text-slate-600 mb-2" />
              <p className="text-xs font-bold text-slate-300">SELECT A DATASET SCENARIO</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};
