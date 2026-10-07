"use client";

import React, { useState } from "react";
import { TimelineItem } from "../lib/types";
import { ArrowUpRight, FilterX, Search, ShieldCheck, Terminal, Download, Pause } from "lucide-react";

interface ForensicEventLedgerProps {
  timeline: TimelineItem[];
  selectedEventId: string | null;
  selectedStageId: string | null;
  onSelectEvent: (eventId: string) => void;
  onSelectStage: (stageId: string | null) => void;
}

const formatUTC = (value: string) => {
  const timestamp = Date.parse(value);
  if (Number.isNaN(timestamp)) return value;
  return new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    fractionalSecondDigits: 3,
    timeZone: "UTC",
  }).format(timestamp);
};

export const ForensicEventLedger: React.FC<ForensicEventLedgerProps> = ({
  timeline,
  selectedEventId,
  selectedStageId,
  onSelectEvent,
  onSelectStage,
}) => {
  const [sourceFilter, setSourceFilter] = useState<string>("ALL");

  const stageFiltered = selectedStageId
    ? timeline.filter((item) => item.stage_id === selectedStageId)
    : timeline;

  const rows = sourceFilter === "ALL"
    ? stageFiltered
    : stageFiltered.filter((item) => item.source.toLowerCase().includes(sourceFilter.toLowerCase()));

  // Active selected item for expanded tray
  const activeItem = rows.find((r) => r.event_id === selectedEventId) || rows[0] || null;

  return (
    <section className="tw-panel overflow-hidden select-none flex flex-col" aria-labelledby="event-ledger-heading">
      {/* 1. TOP TOOLBAR WITH FILTER PILLS */}
      <div className="p-2.5 px-3 border-b border-slate-800 bg-[#111822] flex flex-wrap items-center justify-between gap-2 text-xs font-mono-technical">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[10px] uppercase text-slate-400 font-semibold mr-1">
            LEDGER FILTER:
          </span>
          <button
            type="button"
            onClick={() => setSourceFilter("ALL")}
            className={`px-2 py-0.5 text-[10px] font-bold border transition-colors ${
              sourceFilter === "ALL"
                ? "bg-cyan-400 text-[#0b0f14] border-cyan-400"
                : "bg-[#16202e] text-slate-300 border-slate-700 hover:border-slate-500"
            }`}
          >
            ALL ({stageFiltered.length})
          </button>
          <button
            type="button"
            onClick={() => setSourceFilter("auditd")}
            className={`px-2 py-0.5 text-[10px] font-bold border transition-colors ${
              sourceFilter === "auditd"
                ? "bg-cyan-400 text-[#0b0f14] border-cyan-400"
                : "bg-[#16202e] text-slate-300 border-slate-700 hover:border-slate-500"
            }`}
          >
            SYSCALL
          </button>
          <button
            type="button"
            onClick={() => setSourceFilter("auth")}
            className={`px-2 py-0.5 text-[10px] font-bold border transition-colors ${
              sourceFilter === "auth"
                ? "bg-cyan-400 text-[#0b0f14] border-cyan-400"
                : "bg-[#16202e] text-slate-300 border-slate-700 hover:border-slate-500"
            }`}
          >
            AUTH_ANOMALY
          </button>
          <button
            type="button"
            onClick={() => setSourceFilter("network")}
            className={`px-2 py-0.5 text-[10px] font-bold border transition-colors ${
              sourceFilter === "network"
                ? "bg-cyan-400 text-[#0b0f14] border-cyan-400"
                : "bg-[#16202e] text-rose-300 border-rose-500/40 hover:border-rose-400"
            }`}
          >
            NET_BEACON
          </button>
          <button
            type="button"
            onClick={() => setSourceFilter("usb")}
            className={`px-2 py-0.5 text-[10px] font-bold border transition-colors ${
              sourceFilter === "usb"
                ? "bg-cyan-400 text-[#0b0f14] border-cyan-400"
                : "bg-[#16202e] text-slate-300 border-slate-700 hover:border-slate-500"
            }`}
          >
            HARDWARE_USB
          </button>
        </div>

        {/* Right side controls */}
        <div className="flex items-center gap-3 text-slate-400 text-[10px]">
          {selectedStageId && (
            <button
              type="button"
              onClick={() => onSelectStage(null)}
              className="inline-flex items-center gap-1 text-cyan-400 hover:underline"
            >
              <FilterX className="h-3 w-3" />
              <span>Clear stage filter</span>
            </button>
          )}
          <span className="hidden sm:inline">AUTO-REFRESH: 1s</span>
          <button type="button" className="hover:text-cyan-400" title="Pause telemetry stream">
            <Pause className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* 2. HIGH-DENSITY MONOSPACE DATA TABLE */}
      {rows.length === 0 ? (
        <div className="p-8 text-center text-xs font-mono-technical text-slate-400">
          No forensic events match the active filter criteria.
        </div>
      ) : (
        <div className="tw-table-wrap overflow-x-auto max-h-[380px]">
          <table className="w-full min-w-[760px] border-collapse text-left font-mono-technical text-xs">
            <thead className="sticky top-0 z-10 bg-[#16202e] text-[10px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800">
              <tr className="h-7">
                <th scope="col" className="px-3 py-1 font-semibold w-24"># ID</th>
                <th scope="col" className="px-3 py-1 font-semibold w-28">TIME (UTC)</th>
                <th scope="col" className="px-3 py-1 font-semibold w-32">SOURCE / STAGE</th>
                <th scope="col" className="px-3 py-1 font-semibold">OBSERVED ARTIFACT / FACT</th>
                <th scope="col" className="px-3 py-1 font-semibold w-24 text-center">RISK NOVELTY</th>
                <th scope="col" className="px-3 py-1 text-right font-semibold w-24">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 bg-[#0b0f14]">
              {rows.map((item, idx) => {
                const selected = selectedEventId === item.event_id;
                const isCriticalRow = item.fact.toLowerCase().includes("exfiltration") || item.fact.toLowerCase().includes("c2") || item.fact.toLowerCase().includes("lsass");

                return (
                  <tr
                    key={item.event_id}
                    onClick={() => onSelectEvent(item.event_id)}
                    className={`cursor-pointer transition-colors ${
                      selected
                        ? "bg-[#182638] border-l-2 border-cyan-400"
                        : isCriticalRow
                        ? "hover:bg-[#161a24] bg-[#10131a]"
                        : "hover:bg-[#111822]"
                    }`}
                  >
                    {/* Event ID */}
                    <td className="px-3 py-2 font-mono text-[11px] font-bold text-cyan-400 whitespace-nowrap">
                      {item.event_id}
                    </td>

                    {/* Exact Timestamp */}
                    <td className="px-3 py-2 text-slate-300 font-mono text-[11px] whitespace-nowrap">
                      {formatUTC(item.timestamp)}
                    </td>

                    {/* Source and Stage */}
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className="text-slate-200 block text-[11px]">{item.source}</span>
                      <span className="text-slate-400 text-[10px] block truncate max-w-[120px]">{item.stage_id}</span>
                    </td>

                    {/* Fact / Artifact */}
                    <td className="px-3 py-2 text-slate-100 text-[11px] leading-relaxed">
                      <span className={isCriticalRow ? "text-rose-300 font-semibold" : ""}>
                        {item.fact}
                      </span>
                    </td>

                    {/* Novelty Score Pill */}
                    <td className="px-3 py-2 text-center whitespace-nowrap">
                      <span
                        className={`inline-block px-1.5 py-0.2 text-[9px] font-bold border ${
                          isCriticalRow
                            ? "bg-rose-950/40 text-rose-300 border-rose-500/50"
                            : "bg-cyan-950/40 text-cyan-300 border-cyan-500/40"
                        }`}
                      >
                        {isCriticalRow ? "98% CRIT" : "84% MED"}
                      </span>
                    </td>

                    {/* Inspect Button */}
                    <td className="px-3 py-2 text-right whitespace-nowrap">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectEvent(item.event_id);
                        }}
                        className="px-2 py-0.5 bg-cyan-500 hover:bg-cyan-400 text-[#0b0f14] text-[10px] font-bold uppercase transition-colors"
                      >
                        INSPECT
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 3. ACTIVE ROW EXPANDED INSPECTION TELEMETRY TRAY (from Stitch) */}
      {activeItem && (
        <div className="border-t border-slate-800 bg-[#111822] p-3 flex flex-col md:flex-row gap-3 items-start md:items-center justify-between font-mono-technical text-[10px]">
          <div className="space-y-1 min-w-0 flex-1">
            <div className="flex items-center gap-2 text-cyan-400 font-bold">
              <Terminal className="h-3.5 w-3.5" />
              <span>TELEMETRY EXPANSION // {activeItem.event_id} [{activeItem.source.toUpperCase()}]</span>
            </div>
            <div className="text-slate-300 bg-[#0a0e13] p-2 border border-slate-800 text-[10px] break-all">
              <span className="text-slate-400">ARTIFACT: </span>
              <span className="text-emerald-400 font-semibold">{activeItem.fact}</span>
              <span className="text-slate-500 ml-2">| STAGE: {activeItem.stage_id}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => onSelectEvent(activeItem.event_id)}
              className="tw-inline-action text-[10px] h-7 px-2 border-slate-700 hover:border-cyan-400"
            >
              DISASSEMBLE BINARY
            </button>
            <button
              type="button"
              onClick={() => onSelectEvent(activeItem.event_id)}
              className="tw-inline-action tw-danger-action text-[10px] h-7 px-2"
            >
              KILL SOCKET
            </button>
          </div>
        </div>
      )}
    </section>
  );
};
