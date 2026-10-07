"use client";

import React, { useState, useEffect } from "react";
import { Play, CheckCircle2, AlertTriangle, Layers, Clock, ShieldCheck, Database, RefreshCw, Terminal, Check } from "lucide-react";
import { fetchScenarios, runAnalysis } from "../lib/api";
import { AnalysisRunResult, ScenarioItem } from "../lib/types";

interface DatasetReplayProps {
  onAnalysisCompleted: () => void;
}

export const DatasetReplay: React.FC<DatasetReplayProps> = ({ onAnalysisCompleted }) => {
  const [scenarios, setScenarios] = useState<ScenarioItem[]>([]);
  const [loadingScenarios, setLoadingScenarios] = useState<boolean>(true);
  const [runningScenario, setRunningScenario] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<AnalysisRunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    void fetchScenarios()
      .then((items) => {
        if (active) setScenarios(items);
      })
      .catch((err: unknown) => {
        if (active) setError(err instanceof Error ? err.message : "Failed to load test scenarios");
      })
      .finally(() => {
        if (active) setLoadingScenarios(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const handleRun = async (file: string) => {
    try {
      setRunningScenario(file);
      setError(null);
      const result = await runAnalysis(file);
      setLastResult(result);
      onAnalysisCompleted();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Analysis run failed");
    } finally {
      setRunningScenario(null);
    }
  };

  const getScenarioPurpose = (type: string) => {
    switch (type) {
      case "attack":
        return {
          purpose: "Full 4-Stage Attack Chain Reconstruction",
          badge: "border-rose-500/30 bg-rose-950/20 text-rose-300",
        };
      case "benign":
        return {
          purpose: "False-Positive Suppression Control",
          badge: "border-emerald-500/30 bg-emerald-950/20 text-emerald-300",
        };
      case "partial":
        return {
          purpose: "Sequence Degradation & Missing Stage Resilience",
          badge: "border-amber-500/30 bg-amber-950/20 text-amber-300",
        };
      default:
        return {
          purpose: "Schema Validation & Ingestion Quarantine Check",
          badge: "border-slate-700 bg-slate-800 text-slate-300",
        };
    }
  };

  return (
    <div className="space-y-4">
      {/* Banner */}
      <section aria-label="Engineering Replay Workspace" className="rounded-sm border border-[#171d2b] bg-[#0c0f17] p-4 text-slate-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[#151a26] pb-3">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-cyan-400" />
            <h2 className="font-mono-technical text-sm font-bold tracking-wide text-slate-100">
              DATASET REPLAY & CORRELATION HARNESS
            </h2>
          </div>
          <div className="flex items-center gap-2 font-mono-technical text-[11px] text-slate-400">
            <span>DETERMINISTIC EVALUATION ENGINE</span>
            <span className="text-slate-600">•</span>
            <span>REPRODUCIBLE TELEMETRY PIPELINE</span>
          </div>
        </div>
        <p className="mt-2.5 text-xs font-mono-technical text-slate-400 leading-relaxed max-w-4xl">
          Execute canonical telemetry datasets through ThreatWeave ingestion normalization, atomic signal detection, temporal sequence correlation, and false-positive suppression gates.
        </p>
      </section>

      {error && (
        <div className="rounded-sm border border-rose-500/40 bg-rose-950/20 p-3 font-mono-technical text-xs text-rose-300">
          EXECUTION ERROR: {error}
        </div>
      )}

      {/* Scenarios Table / Matrix */}
      <section aria-label="Evaluation Scenarios" className="rounded-sm border border-[#171d2b] bg-[#0c0f17] p-4 text-slate-200">
        <div className="flex items-center justify-between border-b border-[#151a26] pb-2.5 mb-3 font-mono-technical text-xs">
          <span className="font-bold text-slate-200">AVAILABLE TELEMETRY SCENARIOS ({scenarios.length})</span>
          <span className="text-slate-400 text-[11px]">{loadingScenarios ? "LOADING SCENARIOS" : "SELECT A SCENARIO"}</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {scenarios.map((sc) => {
            const isRunning = runningScenario === sc.file;
            const meta = getScenarioPurpose(sc.type);

            return (
              <div
                key={sc.id}
                className="rounded-sm border border-[#171d2b] bg-[#10141f] p-3.5 flex flex-col justify-between space-y-3 hover:border-[#2b354d] transition"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span
                      className={`rounded-sm px-2 py-0.5 font-mono-technical text-[10px] uppercase font-bold border ${meta.badge}`}
                    >
                      {sc.type.toUpperCase()} SCENARIO
                    </span>
                    <span className="font-mono-technical text-[11px] text-slate-400">
                      {sc.records_count} RECORDS
                    </span>
                  </div>

                  <h3 className="mt-2 font-mono-technical text-xs font-bold text-slate-100">
                    {sc.name}
                  </h3>

                  <div className="mt-2 space-y-1 font-mono-technical text-[11px]">
                    <div className="text-slate-300">
                      <span className="text-slate-400">Purpose: </span>
                      {meta.purpose}
                    </div>
                  </div>
                </div>

                <div className="pt-2.5 border-t border-[#171d2b] flex items-center justify-between">
                  <span className="font-mono-technical text-[10px] text-slate-400">
                    File: {sc.file}
                  </span>

                  <button
                    onClick={() => handleRun(sc.file)}
                    disabled={isRunning}
                    className="flex items-center gap-1.5 rounded-sm bg-cyan-600 hover:bg-cyan-500 px-3 py-1 font-mono-technical text-xs font-bold text-slate-950 transition disabled:opacity-50"
                  >
                    {isRunning ? (
                      <>
                        <RefreshCw className="h-3 w-3 animate-spin" />
                        <span>RUNNING...</span>
                      </>
                    ) : (
                      <>
                        <Play className="h-3 w-3 fill-current" />
                        <span>REPLAY DATASET</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Execution Results Ledger (Real API Output) */}
      {lastResult && (
        <section aria-label="Pipeline Run Execution Ledger" className="rounded-sm border border-[#171d2b] bg-[#0c0f17] p-4 text-slate-200 space-y-3">
          <div className="flex items-center justify-between border-b border-[#151a26] pb-2.5">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <h3 className="font-mono-technical text-xs font-bold text-slate-100 uppercase tracking-wide">
                PIPELINE EXECUTION OUTPUT ({lastResult.dataset_id})
              </h3>
            </div>
            <span className="font-mono-technical text-[10px] text-emerald-300 bg-emerald-950/30 px-2 py-0.5 rounded-sm border border-emerald-500/30">
              STATUS: {lastResult.status.toUpperCase()} ({lastResult.runtime_ms}ms)
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 font-mono-technical text-xs">
            <div className="rounded-sm border border-[#171d2b] bg-[#10141f] p-2.5">
              <span className="text-[10px] text-slate-400 block uppercase">Ingested Records</span>
              <span className="text-slate-100 font-bold mt-0.5 block">{lastResult.total_records_processed}</span>
            </div>
            <div className="rounded-sm border border-[#171d2b] bg-[#10141f] p-2.5">
              <span className="text-[10px] text-slate-400 block uppercase">Promoted Incidents</span>
              <span className="text-cyan-300 font-bold mt-0.5 block">{lastResult.incidents_created}</span>
            </div>
            <div className="rounded-sm border border-[#171d2b] bg-[#10141f] p-2.5">
              <span className="text-[10px] text-slate-400 block uppercase">Suppressed Clusters</span>
              <span className="text-amber-300 font-bold mt-0.5 block">{lastResult.suppressed_clusters}</span>
            </div>
            <div className="rounded-sm border border-[#171d2b] bg-[#10141f] p-2.5">
              <span className="text-[10px] text-slate-400 block uppercase">Quarantined Records</span>
              <span className="text-rose-300 font-bold mt-0.5 block">{lastResult.quarantined_records}</span>
            </div>
          </div>
        </section>
      )}

      {/* Static Benchmark Reference Section Clearly Tagged */}
      <section aria-label="Benchmark Reference Standard" className="rounded-sm border border-[#171d2b] bg-[#090c13] p-3.5 text-slate-400 font-mono-technical text-[11px] space-y-1.5">
        <div className="flex items-center justify-between text-slate-300 font-bold text-xs border-b border-[#151a26] pb-1.5">
          <span>BENCHMARK STANDARD REFERENCE (OFFLINE EVALUATION SUITE)</span>
          <span className="text-[10px] text-slate-400 uppercase">REFERENCE ONLY • NOT LIVE TELEMETRY</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          HNX26PSI03 Baseline Specification: Canonical insider exfiltration must produce $\ge 3$ correlated stages with $Risk \ge 75$. Benign baseline runs must produce 0 promoted incidents with $100\%$ suppression gate compliance.
        </p>
      </section>
    </div>
  );
};
