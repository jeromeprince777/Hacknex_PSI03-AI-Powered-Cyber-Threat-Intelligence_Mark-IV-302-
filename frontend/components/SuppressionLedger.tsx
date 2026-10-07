"use client";

import React from "react";
import { ArchiveX, CircleHelp, ShieldAlert } from "lucide-react";
import { SuppressionRecord } from "../lib/types";

interface SuppressionLedgerProps {
  suppressions: SuppressionRecord[];
}

const displayCount = (value: unknown) => {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim()) return value;
  return "—";
};

export const SuppressionLedger: React.FC<SuppressionLedgerProps> = ({ suppressions }) => {
  return (
    <div className="space-y-4 select-none">
      {/* Header */}
      <header className="tw-panel p-4 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 font-mono-technical text-[10px] text-cyan-400">
            <ArchiveX className="h-3.5 w-3.5" />
            <span>PROMOTION GATE AUDIT // SUPPRESSION LEDGER</span>
          </div>
          <h1 className="mt-1 text-lg sm:text-xl font-bold tracking-tight text-slate-100">
            Noise Suppression &amp; Gate Evaluation Audit
          </h1>
          <p className="mt-1 text-xs text-slate-400 max-w-2xl">
            Review uncorrelated signal clusters and benign baseline activities that did not satisfy promotion criteria, preventing SOC alert fatigue.
          </p>
        </div>
        <div className="flex items-baseline gap-2 bg-[#0a0e13] px-3 py-1.5 border border-slate-800">
          <span className="font-mono-technical text-xl font-bold text-cyan-400 tabular-nums">
            {suppressions.length}
          </span>
          <span className="text-[10px] font-mono-technical text-slate-400">AUDITED RECORDS</span>
        </div>
      </header>

      {/* Main Table Panel */}
      <section className="tw-panel overflow-hidden" aria-labelledby="suppression-table-heading">
        <div className="flex items-center justify-between border-b border-slate-800 bg-[#111822] p-3">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-amber-400" aria-hidden="true" />
            <h2 id="suppression-table-heading" className="text-xs font-bold uppercase tracking-wider text-slate-100 font-mono-technical">
              SUPPRESSED CLUSTERS LEDGER
            </h2>
          </div>
          <span className="font-mono-technical text-[10px] text-slate-400">
            {suppressions.length} AUDIT ENTRIES
          </span>
        </div>

        {suppressions.length === 0 ? (
          <div className="p-8 text-center font-mono-technical text-slate-400 text-xs">
            No suppression records recorded in the current session.
          </div>
        ) : (
          <div className="tw-table-wrap overflow-x-auto">
            <table className="w-full min-w-[900px] border-collapse text-left font-mono-technical text-xs">
              <thead className="bg-[#16202e] text-[10px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                <tr className="h-7">
                  <th scope="col" className="px-3 py-1.5 font-semibold">RECORD ID</th>
                  <th scope="col" className="px-3 py-1.5 font-semibold">TARGET ENTITY</th>
                  <th scope="col" className="px-3 py-1.5 font-semibold">REASON CODE</th>
                  <th scope="col" className="px-3 py-1.5 font-semibold">MISSING REQUIREMENTS</th>
                  <th scope="col" className="px-3 py-1.5 font-semibold">CONTEXT RETURNED</th>
                  <th scope="col" className="px-3 py-1.5 text-right font-semibold">RECORDED</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80 bg-[#0b0f14]">
                {suppressions.map((suppression) => {
                  const primaryEntity = suppression.details?.primary_entity;
                  const target = typeof primaryEntity === "string" && primaryEntity ? primaryEntity : suppression.target_id;
                  const stages = displayCount(suppression.details?.stages_count);
                  const evidence = displayCount(suppression.details?.evidence_events_count);

                  return (
                    <tr key={suppression.suppression_id} className="hover:bg-[#111822] transition-colors">
                      <td className="px-3 py-2.5 font-mono text-[11px] font-bold text-cyan-400 whitespace-nowrap">
                        {suppression.suppression_id}
                      </td>
                      <td className="px-3 py-2.5 font-bold text-slate-200">{target}</td>
                      <td className="px-3 py-2.5">
                        <span className="border border-slate-700 bg-[#16202e] px-1.5 py-0.5 text-[10px] text-amber-300">
                          {suppression.reason_code}
                        </span>
                      </td>
                      <td className="px-3 py-2.5 text-slate-300">
                        {suppression.missing_requirements.length > 0 ? (
                          <ul className="space-y-0.5">
                            {suppression.missing_requirements.map((requirement, index) => (
                              <li key={`${suppression.suppression_id}-${index}`} className="flex items-center gap-1.5 text-[10px]">
                                <span className="h-1 w-1 rounded-none bg-amber-400 shrink-0" />
                                <span>{requirement}</span>
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <span className="text-slate-500 text-[10px]">No missing requirements</span>
                        )}
                      </td>
                      <td className="px-3 py-2.5 text-slate-400 text-[10px] whitespace-nowrap">
                        <span>STAGES: {stages}</span>
                        <span className="mx-1 text-slate-600">·</span>
                        <span>EVENTS: {evidence}</span>
                      </td>
                      <td className="px-3 py-2.5 text-right font-mono text-[10px] text-slate-400 whitespace-nowrap">
                        {suppression.created_at || (suppression.details?.timestamp as string) || "RECORDED"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
