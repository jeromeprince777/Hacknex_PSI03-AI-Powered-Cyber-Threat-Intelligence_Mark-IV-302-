"use client";

import React from "react";
import { Activity, ShieldCheck, Filter, AlertCircle, CheckCircle2 } from "lucide-react";
import { SuppressionRecord } from "../lib/types";

interface SuppressionLogProps {
  suppressions: SuppressionRecord[];
}

export const SuppressionLog: React.FC<SuppressionLogProps> = ({ suppressions }) => {
  return (
    <div className="space-y-4">
      {/* Overview Banner */}
      <section aria-label="Suppression Audit Log Header" className="rounded-sm border border-[#171d2b] bg-[#0c0f17] p-4 text-slate-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-[#151a26] pb-3 gap-2">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-cyan-400" />
            <h2 className="font-mono-technical text-sm font-bold tracking-wide text-slate-100">
              FALSE-POSITIVE SUPPRESSION AUDIT LEDGER
            </h2>
          </div>
          <div className="flex items-center gap-2 font-mono-technical text-[11px] text-emerald-300 bg-emerald-950/20 px-2 py-0.5 rounded-sm border border-emerald-500/25">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>SUPPRESSED CLUSTERS: {suppressions.length}</span>
          </div>
        </div>
        <p className="mt-2.5 text-xs font-mono-technical text-slate-400 leading-relaxed max-w-4xl">
          Suspicious signals and isolated activity clusters that failed the Incident Promotion Gate are preserved in this immutable audit ledger. This prevents false alarms from flooding the SOC triage queue while retaining full forensic auditability.
        </p>
      </section>

      {/* Suppression Records Table */}
      <section aria-label="Suppression Records Ledger" className="rounded-sm border border-[#171d2b] bg-[#0c0f17] p-4 text-slate-200">
        <div className="flex items-center justify-between border-b border-[#151a26] pb-2.5 mb-3 font-mono-technical text-xs">
          <span className="font-bold text-slate-200">GATE REJECTION AUDIT TRAIL</span>
          <span className="text-slate-400 text-[11px]">IMMUTABLE FORENSIC SUPPRESSION RECORDS</span>
        </div>

        {suppressions.length === 0 ? (
          <div className="py-12 text-center font-mono-technical text-xs text-slate-400 space-y-1">
            <div className="text-slate-300 font-bold">NO SUPPRESSION RECORDS LOGGED</div>
            <div>Replay the Benign Employee Baseline scenario in Dataset Replay to observe gate suppression in action.</div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono-technical text-xs">
              <thead>
                <tr className="border-b border-[#171d2b] text-[10px] uppercase text-slate-400">
                  <th className="py-2.5 px-3">Suppression ID</th>
                  <th className="py-2.5 px-3">Target Entity</th>
                  <th className="py-2.5 px-3">Suppression Reason Code</th>
                  <th className="py-2.5 px-3">Missing Requirements Gate</th>
                  <th className="py-2.5 px-3 text-right">Cluster Telemetry</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#151a26] text-slate-300">
                {suppressions.map((sup) => (
                  <tr key={sup.suppression_id} className="hover:bg-[#101420] transition">
                    <td className="py-3 px-3 font-bold text-cyan-400">
                      {sup.suppression_id}
                    </td>
                    <td className="py-3 px-3 text-slate-100 font-bold">
                      {(sup.details?.primary_entity as string) || sup.target_id}
                    </td>
                    <td className="py-3 px-3">
                      <span className="rounded-sm bg-[#141a28] border border-[#20293d] px-2 py-0.5 text-[11px] text-amber-300 font-medium">
                        {sup.reason_code}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-rose-300/90 text-[11px]">
                      {sup.missing_requirements && sup.missing_requirements.length > 0 ? (
                        <div className="space-y-0.5">
                          {sup.missing_requirements.map((req, i) => (
                            <div key={i} className="flex items-center gap-1.5">
                              <span className="h-1 w-1 rounded-full bg-rose-400" />
                              <span>{req}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-400">Single isolated atomic indicator</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right text-[11px] text-slate-400">
                      Stages: <span className="text-slate-200 font-bold">{String(sup.details?.stages_count ?? 1)}</span> • Events:{" "}
                      <span className="text-slate-200 font-bold">{String(sup.details?.evidence_events_count ?? 1)}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
