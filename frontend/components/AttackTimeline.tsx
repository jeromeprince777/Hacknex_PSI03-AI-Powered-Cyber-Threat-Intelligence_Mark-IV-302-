"use client";

import React from "react";
import { Clock, ShieldAlert, FileText, HardDrive, Wifi, ArrowRight } from "lucide-react";
import { TimelineItem } from "../lib/types";

interface AttackTimelineProps {
  timeline: TimelineItem[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
}

export const AttackTimeline: React.FC<AttackTimelineProps> = ({
  timeline,
  selectedEventId,
  onSelectEvent,
}) => {
  const getSourceIcon = (source: string) => {
    switch (source.toLowerCase()) {
      case "vpn":
        return <Wifi className="h-3.5 w-3.5 text-purple-400" />;
      case "windows":
        return <FileText className="h-3.5 w-3.5 text-blue-400" />;
      case "edr":
        return <HardDrive className="h-3.5 w-3.5 text-rose-400" />;
      case "firewall":
        return <Wifi className="h-3.5 w-3.5 text-cyan-400" />;
      default:
        return <Clock className="h-3.5 w-3.5 text-slate-400" />;
    }
  };

  const getStageBadgeStyle = (stageId: string) => {
    switch (stageId) {
      case "stage-01":
        return "border-purple-500/30 bg-purple-950/30 text-purple-300";
      case "stage-02":
        return "border-blue-500/30 bg-blue-950/30 text-blue-300";
      case "stage-03":
        return "border-amber-500/30 bg-amber-950/30 text-amber-300";
      case "stage-04":
        return "border-rose-500/30 bg-rose-950/30 text-rose-300";
      default:
        return "border-slate-700 bg-slate-800 text-slate-300";
    }
  };

  return (
    <div className="rounded border border-[#1e2438] bg-[#0d101a] p-4">
      <div className="flex items-center justify-between border-b border-[#161a29] pb-3">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold text-slate-100">
            ATTACK RECONSTRUCTION TIMELINE
          </h3>
        </div>
        <span className="font-mono text-xs text-slate-400">
          Chronologically Ordered Telemetry ({timeline.length} events)
        </span>
      </div>

      <div className="mt-4 relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#1e2438]">
        {timeline.map((item, idx) => {
          const isSelected = selectedEventId === item.event_id;
          const timeFormatted = item.timestamp.replace("T", " ").replace("Z", " UTC");

          return (
            <div
              key={item.event_id}
              onClick={() => onSelectEvent(item.event_id)}
              className={`relative cursor-pointer rounded border p-3 transition ${
                isSelected
                  ? "border-cyan-500 bg-[#14192b] shadow-md shadow-cyan-950/20"
                  : "border-[#1e2438] bg-[#101320] hover:border-[#2b334d] hover:bg-[#131726]"
              }`}
            >
              {/* Timeline marker node */}
              <div
                className={`absolute -left-[27px] top-3.5 h-3 w-3 rounded-full border-2 ${
                  isSelected
                    ? "border-cyan-400 bg-cyan-950"
                    : "border-[#1e2438] bg-[#0d101a]"
                }`}
              />

              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                {/* Event Metadata Strip */}
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xs font-bold text-cyan-300 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/30">
                    {item.event_id}
                  </span>

                  <span
                    className={`inline-flex items-center rounded border px-2 py-0.5 font-mono text-[10px] uppercase font-semibold ${getStageBadgeStyle(
                      item.stage_id
                    )}`}
                  >
                    {item.stage_id}
                  </span>

                  <span className="inline-flex items-center gap-1 rounded bg-[#161b2c] px-2 py-0.5 font-mono text-[11px] text-slate-300 border border-[#1e2438]">
                    {getSourceIcon(item.source)}
                    {item.source}
                  </span>

                  <span className="font-mono text-[11px] text-slate-400">
                    {timeFormatted}
                  </span>
                </div>

                {/* Inspect Action Hint */}
                <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400 group-hover:text-cyan-300">
                  <span>Inspect</span>
                  <ArrowRight className="h-3 w-3" />
                </div>
              </div>

              {/* Factual Non-Hallucinated Statement */}
              <p className="mt-2 text-xs text-slate-200 leading-relaxed font-sans">
                {item.fact}
              </p>

              {/* Entity tags */}
              {item.linked_entities && item.linked_entities.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {item.linked_entities.map((ent) => (
                    <span
                      key={ent}
                      className="rounded bg-[#181d2f] px-1.5 py-0.2 text-[10px] font-mono text-slate-400 border border-[#21273d]"
                    >
                      {ent}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
