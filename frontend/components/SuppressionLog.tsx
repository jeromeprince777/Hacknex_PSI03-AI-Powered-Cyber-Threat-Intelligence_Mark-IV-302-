"use client";

import React from "react";
import { Activity, ShieldCheck, Filter, AlertCircle } from "lucide-react";
import { SuppressionRecord } from "../lib/types";

interface SuppressionLogProps {
  suppressions: SuppressionRecord[];
}

export const SuppressionLog: React.FC<SuppressionLogProps> = ({ suppressions }) => {
  return (
    <div className="space-y-6">
      {/* Overview Banner */}
      <div className="rounded border border-[#1e2438] bg-[#0d101a] p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-mono text-base font-bold text-slate-100 flex items-center gap-2">
              <Activity className="h-5 w-5 text-cyan-400" />
              FALSE-POSITIVE SUPPRESSION AUDIT LOG
            </h2>
            <p className="mt-1 text-xs text-slate-400 leading-relaxed font-sans max-w-2xl">
              Signals and isolated clusters that failed the Incident Promotion Gate are preserved for forensic auditing rather than spamming the SOC queue with low-confidence false alarms.
            </p>
          </div>
          <div className="rounded border border-emerald-500/30 bg-emerald-950/30 px-3 py-1.5 font-mono text-xs text-emerald-300 text-right">
            <span>Suppressed Clusters: </span>
            <strong>{suppressions.length}</strong>
          </div>
        </div>
      </div>

      {/* Suppression Records Table */}
      <div className="rounded border border-[#1e2438] bg-[#0d101a] p-4">
        {suppressions.length === 0 ? (
          <div className="p-8 text-center text-xs font-mono text-slate-500">
            No suppression records logged yet. Replay the benign administrator scenario to observe false-positive suppression in action.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-[#1e2438] text-slate-400">
                  <th className="py-2.5 px-3">Suppression ID</th>
                  <th className="py-2.5 px-3">Target Entity</th>
                  <th className="py-2.5 px-3">Reason Code</th>
                  <th className="py-2.5 px-3">Missing Requirements Gate</th>
                  <th className="py-2.5 px-3">Cluster Stats</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#181d2f] text-slate-300">
                {suppressions.map((sup) => (
                  <tr key={sup.suppression_id} className="hover:bg-[#111422] transition">
                    <td className="py-3 px-3 font-bold text-cyan-400">
                      {sup.suppression_id}
                    </td>
                    <td className="py-3 px-3 text-slate-200">
                      {(sup.details?.primary_entity as string) || sup.target_id}
                    </td>
                    <td className="py-3 px-3">
                      <span className="rounded bg-blue-950/40 border border-blue-500/30 px-2 py-0.5 text-[11px] text-blue-300">
                        {sup.reason_code}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-rose-300/90 text-[11px]">
                      {sup.missing_requirements && sup.missing_requirements.length > 0 ? (
                        <ul className="list-disc list-inside space-y-0.5">
                          {sup.missing_requirements.map((req, i) => (
                            <li key={i}>{req}</li>
                          ))}
                        </ul>
                      ) : (
                        <span>Isolated single-stage signal</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-slate-400 text-[11px]">
                      Stages: {String(sup.details?.stages_count ?? 1)} | Events: {String(sup.details?.evidence_events_count ?? 1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
