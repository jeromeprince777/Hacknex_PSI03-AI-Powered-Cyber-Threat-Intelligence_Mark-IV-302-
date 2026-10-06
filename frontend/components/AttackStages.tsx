"use client";

import React from "react";
import { Layers, ShieldCheck, CheckCircle2 } from "lucide-react";
import { Stage } from "../lib/types";

interface AttackStagesProps {
  stages: Stage[];
  onSelectEvent: (eventId: string) => void;
}

export const AttackStages: React.FC<AttackStagesProps> = ({ stages, onSelectEvent }) => {
  return (
    <div className="rounded border border-[#1e2438] bg-[#0d101a] p-4">
      <div className="flex items-center justify-between border-b border-[#161a29] pb-3">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold text-slate-100">
            DETECTED ATTACK STAGES
          </h3>
        </div>
        <span className="font-mono text-xs text-slate-400">
          Every Stage Backed by Concrete Evidence Event IDs
        </span>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
        {stages.map((stg) => {
          const startTime = stg.start_time.split("T")[1]?.replace("Z", "") || stg.start_time;
          const endTime = stg.end_time.split("T")[1]?.replace("Z", "") || stg.end_time;

          return (
            <div
              key={stg.stage_id}
              className="rounded border border-[#1e2438] bg-[#101320] p-3 space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[11px] font-bold text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/30">
                  STAGE {String(stg.sequence_index).padStart(2, "0")}
                </span>
                <span className="font-mono text-[11px] text-slate-400">
                  {startTime} → {endTime} UTC
                </span>
              </div>

              <h4 className="font-semibold text-sm text-slate-100">
                {stg.name}
              </h4>

              {/* Supporting Evidence Pills */}
              <div className="space-y-1">
                <span className="text-[11px] text-slate-400 font-medium">Supporting Evidence:</span>
                <div className="flex flex-wrap gap-1.5">
                  {stg.evidence_event_ids.map((eid) => (
                    <button
                      key={eid}
                      onClick={() => onSelectEvent(eid)}
                      className="rounded border border-cyan-500/30 bg-cyan-950/30 px-2 py-0.5 font-mono text-xs text-cyan-300 hover:bg-cyan-900/40 transition"
                      title="Inspect event in evidence drawer"
                    >
                      {eid}
                    </button>
                  ))}
                </div>
              </div>

              {/* Fired Detector Reason Codes */}
              {stg.reason_codes && stg.reason_codes.length > 0 && (
                <div className="space-y-1 pt-1 border-t border-[#181d2f]">
                  <span className="text-[10px] text-slate-400">Detector Reason Codes:</span>
                  <div className="flex flex-wrap gap-1">
                    {stg.reason_codes.map((rc) => (
                      <span
                        key={rc}
                        className="rounded bg-[#161a29] px-1.5 py-0.5 text-[10px] font-mono text-slate-300 border border-[#20263b]"
                      >
                        {rc}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
