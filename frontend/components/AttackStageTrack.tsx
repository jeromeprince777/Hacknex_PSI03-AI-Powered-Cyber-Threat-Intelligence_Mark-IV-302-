"use client";

import React from "react";
import { Stage } from "../lib/types";
import { CheckCircle2, AlertTriangle, Radio, ShieldAlert } from "lucide-react";

interface AttackStageTrackProps {
  stages: Stage[];
  selectedStageId: string | null;
  onSelectStage: (stageId: string | null) => void;
  onSelectEvent: (eventId: string) => void;
}

const formatUTC = (value: string) => {
  const timestamp = Date.parse(value);
  if (Number.isNaN(timestamp)) return value;
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZone: "UTC",
  }).format(timestamp) + " UTC";
};

export const AttackStageTrack: React.FC<AttackStageTrackProps> = ({
  stages,
  selectedStageId,
  onSelectStage,
  onSelectEvent,
}) => {
  if (stages.length === 0) {
    return <p className="py-3 text-xs font-mono-technical text-slate-400">No detected stages are attached to this case.</p>;
  }

  return (
    <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-4 relative select-none">
      {stages.map((stage, idx) => {
        const isSelected = selectedStageId === stage.stage_id;
        const isLastStage = idx === stages.length - 1;
        const isHotspot = idx === 2;

        let statusColor = "text-emerald-400 border-emerald-500/50 bg-[#111822]";
        let badgeText = "CONFIRMED";
        let barColor = "bg-emerald-400";
        let Icon = CheckCircle2;

        if (isLastStage) {
          statusColor = "text-rose-400 border-rose-500 bg-[#16131a] shadow-[0_0_12px_rgba(244,63,94,0.25)]";
          badgeText = "CRITICAL";
          barColor = "bg-rose-500 tactical-pulse";
          Icon = ShieldAlert;
        } else if (isHotspot) {
          statusColor = "text-cyan-400 border-cyan-500 bg-[#101b26] shadow-[0_0_10px_rgba(6,182,212,0.2)]";
          badgeText = "HOTSPOT";
          barColor = "bg-cyan-400 tactical-pulse";
          Icon = Radio;
        }

        return (
          <div
            key={stage.stage_id}
            className={`border p-3 relative flex flex-col justify-between transition-all ${
              isSelected
                ? "border-cyan-400 bg-[#182638] shadow-[0_0_15px_rgba(6,182,212,0.3)] ring-1 ring-cyan-400"
                : statusColor
            }`}
          >
            {/* Header: Stage index and Timestamp */}
            <div>
              <div className="flex items-center justify-between mb-1.5 font-mono-technical">
                <span className="text-[10px] font-bold flex items-center gap-1.5">
                  <Icon className="h-3.5 w-3.5" />
                  STAGE {String(stage.sequence_index || idx + 1).padStart(2, "0")}
                </span>
                <span className="text-[9px] text-slate-400 font-mono">
                  {formatUTC(stage.start_time)}
                </span>
              </div>

              {/* Stage Name Action */}
              <button
                type="button"
                onClick={() => onSelectStage(isSelected ? null : stage.stage_id)}
                className="block w-full text-left font-bold text-sm text-slate-100 hover:text-cyan-300 transition-colors"
              >
                {stage.name}
              </button>

              {/* Events & State */}
              <div className="flex items-center justify-between mt-2 text-[10px] font-mono-technical">
                <span className="text-slate-400">
                  {stage.evidence_event_ids.length} Telemetry Events
                </span>
                <span className="font-bold tracking-wider uppercase">
                  {badgeText}
                </span>
              </div>

              {/* Progress Indicator Line */}
              <div className="w-full bg-[#0a0e13] h-1 mt-2 overflow-hidden">
                <div className={`h-full w-full ${barColor}`} />
              </div>
            </div>

            {/* Evidence Event IDs Pills */}
            {stage.evidence_event_ids.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1 pt-2 border-t border-slate-800">
                {stage.evidence_event_ids.map((eventId) => (
                  <button
                    key={eventId}
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectEvent(eventId);
                    }}
                    className="px-1.5 py-0.5 bg-[#0a0e13] border border-slate-700 font-mono-technical text-[9px] text-slate-300 hover:border-cyan-400 hover:text-cyan-300 transition-colors"
                    title={`Inspect evidence event ${eventId}`}
                  >
                    {eventId}
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
