"use client";

import React from "react";
import { Layers, ArrowRight, ShieldCheck, Clock, CheckCircle2 } from "lucide-react";
import { Stage } from "../lib/types";

interface AttackStagesProps {
  stages: Stage[];
  selectedStageId: string | null;
  onSelectStage: (stageId: string | null) => void;
  onSelectEvent: (eventId: string) => void;
}

export const AttackStages: React.FC<AttackStagesProps> = ({
  stages,
  selectedStageId,
  onSelectStage,
  onSelectEvent,
}) => {
  return (
    <section aria-label="Detected Attack Stages Chain" className="rounded-sm border border-[#171d2b] bg-[#0c0f17] p-4 text-slate-200">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-[#151a26] pb-3">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono-technical text-sm font-bold tracking-wide text-slate-100">
            RECONSTRUCTED ATTACK CHAIN SEQUENCE
          </h3>
        </div>
        <div className="flex items-center gap-2 font-mono-technical text-[11px] text-slate-400">
          <span>{stages.length} CONFIRMED STAGES</span>
          <span className="text-slate-600">•</span>
          <span>CLICK STAGE TO FOCUS TIMELINE & GRAPH</span>
        </div>
      </div>

      {/* Interactive Progression Cards */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
        {stages.map((stg) => {
          const isSelected = selectedStageId === stg.stage_id;
          const startTime = stg.start_time.split("T")[1]?.replace("Z", "") || stg.start_time;
          const endTime = stg.end_time.split("T")[1]?.replace("Z", "") || stg.end_time;

          return (
            <div
              key={stg.stage_id}
              onClick={() => onSelectStage(isSelected ? null : stg.stage_id)}
              className={`group relative cursor-pointer rounded-sm border p-3 flex flex-col justify-between transition-all select-none ${
                isSelected
                  ? "border-cyan-400 bg-[#121929] shadow-md shadow-cyan-950/40 ring-1 ring-cyan-400/30"
                  : "border-[#171d2b] bg-[#10141f] hover:border-[#2b354d] hover:bg-[#131826]"
              }`}
            >
              <div>
                {/* Stage sequence banner */}
                <div className="flex items-center justify-between">
                  <span
                    className={`rounded-sm px-1.5 py-0.5 font-mono-technical text-[10px] font-bold tracking-wider ${
                      isSelected
                        ? "bg-cyan-500 text-slate-950"
                        : "bg-[#182030] text-cyan-400 border border-[#212b40]"
                    }`}
                  >
                    STAGE {String(stg.sequence_index).padStart(2, "0")}
                  </span>
                  <span className="font-mono-technical text-[10px] text-slate-400">
                    {startTime} → {endTime}
                  </span>
                </div>

                {/* Stage Name */}
                <h4 className="mt-2.5 font-mono-technical text-xs font-bold uppercase tracking-wide text-slate-100 group-hover:text-cyan-300 transition-colors">
                  {stg.name}
                </h4>

                {/* Detector Reason Codes */}
                {stg.reason_codes && stg.reason_codes.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {stg.reason_codes.map((rc) => (
                      <span
                        key={rc}
                        className="rounded-sm bg-[#161c29] px-1.5 py-0.2 font-mono-technical text-[9px] text-slate-300 border border-[#20273a]"
                      >
                        {rc}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Bottom: Evidence Event Citations */}
              <div className="mt-3.5 pt-2.5 border-t border-[#181f2f]">
                <div className="flex items-center justify-between text-[10px] font-mono-technical text-slate-400 mb-1.5">
                  <span>Supporting Evidence ({stg.evidence_event_ids.length}):</span>
                  {isSelected && <span className="text-cyan-400 font-bold">FOCUSED</span>}
                </div>

                <div className="flex flex-wrap gap-1">
                  {stg.evidence_event_ids.map((eid) => (
                    <button
                      key={eid}
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectEvent(eid);
                      }}
                      className="rounded-sm border border-cyan-500/25 bg-cyan-950/30 px-1.5 py-0.2 font-mono-technical text-[10px] font-semibold text-cyan-300 hover:bg-cyan-500 hover:text-slate-950 transition"
                      title={`Inspect ${eid} telemetry`}
                    >
                      {eid}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
