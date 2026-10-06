"use client";

import React, { useState } from "react";
import { X, FileCode, CheckCircle, Database, ShieldAlert, Copy, Check } from "lucide-react";
import { EvidenceItem } from "../lib/types";

interface EvidenceDrawerProps {
  event: EvidenceItem | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ event, onClose }) => {
  const [activeTab, setActiveTab] = useState<"normalized" | "raw">("normalized");
  const [copied, setCopied] = useState<boolean>(false);

  if (!event) return null;

  const copyJson = () => {
    const payload = activeTab === "normalized" ? event.normalized : event.raw;
    navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[540px] border-l border-[#1e2438] bg-[#0c0f1a] shadow-2xl flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#1e2438] bg-[#090c14] p-4">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold text-slate-100">
            TELEMETRY EVIDENCE INSPECTOR
          </h3>
          <span className="rounded border border-cyan-500/30 bg-cyan-950/40 px-2 py-0.5 font-mono text-xs font-bold text-cyan-300">
            {event.event_id}
          </span>
        </div>
        <button
          onClick={onClose}
          className="rounded p-1 text-slate-400 hover:text-slate-100 hover:bg-[#1a2034]"
          title="Close inspector"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Body: Metadata & Reason Codes */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Basic Stats Grid */}
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="rounded border border-[#1e2438] bg-[#121625] p-2">
            <span className="text-slate-400 text-[10px] block">Timestamp (UTC)</span>
            <span className="text-slate-200">{event.timestamp}</span>
          </div>
          <div className="rounded border border-[#1e2438] bg-[#121625] p-2">
            <span className="text-slate-400 text-[10px] block">Source Origin</span>
            <span className="text-cyan-300 uppercase">{event.source}</span>
          </div>
        </div>

        {/* Detectors that fired */}
        {event.detectors && event.detectors.length > 0 && (
          <div className="rounded border border-rose-500/30 bg-rose-950/20 p-3 space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-rose-300">
              <ShieldAlert className="h-3.5 w-3.5" />
              <span>DETECTORS TRIGGERED ON THIS EVENT</span>
            </div>
            {event.detectors.map((d, i) => (
              <div
                key={i}
                className="rounded border border-rose-500/20 bg-[#161220] p-2 text-xs font-mono flex items-center justify-between"
              >
                <div>
                  <span className="font-bold text-rose-300 block">{d.reason_code}</span>
                  <span className="text-[10px] text-slate-400">Signal: {d.signal_type}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-amber-300 block uppercase">
                    Stage: {d.stage}
                  </span>
                  <span className="text-[10px] text-rose-400 font-bold">
                    Score: {d.score}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Linked Entities */}
        {event.linked_entities && event.linked_entities.length > 0 && (
          <div className="space-y-1">
            <span className="text-xs text-slate-400 font-medium">Associated Entities:</span>
            <div className="flex flex-wrap gap-1.5">
              {event.linked_entities.map((ent) => (
                <span
                  key={ent}
                  className="rounded border border-[#1e2438] bg-[#141828] px-2 py-0.5 font-mono text-[11px] text-slate-300"
                >
                  {ent}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Payload Inspector (Normalized vs Raw) */}
        <div className="rounded border border-[#1e2438] bg-[#090b12] overflow-hidden">
          <div className="flex items-center justify-between border-b border-[#1e2438] bg-[#101320] px-3 py-2">
            <div className="flex items-center gap-1 font-mono text-xs">
              <button
                onClick={() => setActiveTab("normalized")}
                className={`rounded px-2.5 py-1 transition ${
                  activeTab === "normalized"
                    ? "bg-[#1d2338] text-cyan-300 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Canonical Normalized Event
              </button>
              <button
                onClick={() => setActiveTab("raw")}
                className={`rounded px-2.5 py-1 transition ${
                  activeTab === "raw"
                    ? "bg-[#1d2338] text-cyan-300 font-bold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Raw Vendor Record
              </button>
            </div>

            <button
              onClick={copyJson}
              className="flex items-center gap-1 rounded bg-[#181e30] border border-[#232a42] px-2 py-0.5 font-mono text-[11px] text-slate-300 hover:bg-[#202840]"
              title="Copy JSON to clipboard"
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3 text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>

          <pre className="p-3 font-mono text-[11px] text-cyan-100 overflow-x-auto max-h-[360px] leading-relaxed">
            {JSON.stringify(
              activeTab === "normalized" ? event.normalized : event.raw,
              null,
              2
            )}
          </pre>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-[#1e2438] bg-[#090c14] p-3 text-right">
        <button
          onClick={onClose}
          className="rounded border border-[#1e2438] bg-[#141827] px-4 py-1.5 font-mono text-xs text-slate-300 hover:bg-[#1a2034]"
        >
          Close Drawer
        </button>
      </div>
    </div>
  );
};
