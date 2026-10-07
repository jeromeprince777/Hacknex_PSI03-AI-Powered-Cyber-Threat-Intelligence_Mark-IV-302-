"use client";

import React, { useEffect, useState } from "react";
import { Check, Copy, FileJson2, X, Terminal, ShieldAlert } from "lucide-react";
import { EvidenceItem } from "../lib/types";

interface EvidenceDrawerProps {
  event: EvidenceItem | null;
  onClose: () => void;
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({ event, onClose }) => {
  const [activeTab, setActiveTab] = useState<"normalized" | "raw">("normalized");
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);

  useEffect(() => {
    if (!event) return;
    const onKeyDown = (keyboardEvent: KeyboardEvent) => {
      if (keyboardEvent.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [event, onClose]);

  if (!event) return null;

  const payload = activeTab === "normalized" ? event.normalized : event.raw;

  const copyJson = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
      setCopied(true);
      setCopyError(false);
      window.setTimeout(() => setCopied(false), 1400);
    } catch {
      setCopied(false);
      setCopyError(true);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end select-none">
      <button
        type="button"
        className="absolute inset-0 cursor-default bg-black/60 backdrop-blur-sm"
        onClick={onClose}
        aria-label="Close evidence detail"
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="evidence-drawer-heading"
        className="relative flex h-full w-full max-w-[min(44rem,100vw)] flex-col border-l border-slate-800 bg-[#0b0f14] shadow-2xl text-slate-200"
      >
        <header className="flex items-center justify-between gap-4 border-b border-slate-800 bg-[#111822] px-4 py-3 sm:px-5">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <Terminal className="h-4 w-4 text-cyan-400" />
              <p className="text-[10px] font-mono-technical font-bold uppercase tracking-wider text-slate-400">
                FORENSIC EVENT INSPECTOR
              </p>
            </div>
            <h2 id="evidence-drawer-heading" className="mt-0.5 break-all font-mono-technical text-sm font-bold text-cyan-400">
              {event.event_id}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="tw-inline-action h-7 px-2 text-slate-400 hover:text-slate-100"
            aria-label="Close evidence detail"
          >
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </header>

        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4 sm:p-5 font-mono-technical text-xs">
          {/* Metadata Grid */}
          <dl className="grid grid-cols-1 border border-slate-800 bg-[#111822] sm:grid-cols-2 divide-y sm:divide-y-0 sm:divide-x divide-slate-800">
            <div className="p-3">
              <dt className="text-[9px] font-bold uppercase text-slate-400">EXACT UTC TIMESTAMP</dt>
              <dd className="mt-1 break-all text-[11px] text-slate-200">{event.timestamp}</dd>
            </div>
            <div className="p-3">
              <dt className="text-[9px] font-bold uppercase text-slate-400">INGESTION SOURCE</dt>
              <dd className="mt-1 break-all text-[11px] text-cyan-300 font-bold">{event.source}</dd>
            </div>
          </dl>

          {/* Detector Signals */}
          {event.detectors.length > 0 && (
            <section aria-labelledby="detector-signals-heading" className="border border-slate-800 bg-[#111822] p-3">
              <div className="flex items-baseline justify-between gap-2 border-b border-slate-800 pb-2">
                <h3 id="detector-signals-heading" className="text-xs font-bold text-slate-100">
                  TRIGGERED DETECTOR SIGNALS
                </h3>
                <span className="text-[10px] text-slate-400">{event.detectors.length} detectors</span>
              </div>
              <ul className="mt-2 divide-y divide-slate-800/80">
                {event.detectors.map((detector, index) => (
                  <li key={`${detector.reason_code}-${index}`} className="grid gap-1 py-2 sm:grid-cols-[minmax(0,1fr)_auto]">
                    <div className="min-w-0">
                      <p className="break-all text-[11px] font-bold text-rose-400">{detector.reason_code}</p>
                      <p className="mt-0.5 text-[10px] text-slate-400">{detector.signal_type}</p>
                    </div>
                    <div className="flex gap-3 text-[10px] text-slate-400 sm:flex-col sm:items-end sm:gap-0.5">
                      <span>Stage: <span className="text-cyan-400">{detector.stage}</span></span>
                      <span>Score: <span className="text-amber-400 font-bold">{detector.score}</span></span>
                    </div>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Linked Entities */}
          {event.linked_entities.length > 0 && (
            <section aria-labelledby="linked-entities-heading" className="border border-slate-800 bg-[#111822] p-3">
              <div className="flex items-baseline justify-between gap-2 mb-2">
                <h3 id="linked-entities-heading" className="text-xs font-bold text-slate-100">
                  LINKED ATTRIBUTION ENTITIES
                </h3>
                <span className="text-[10px] text-cyan-400">{event.linked_entities.length} items</span>
              </div>
              <ul className="flex flex-wrap gap-1.5">
                {event.linked_entities.map((entity) => (
                  <li key={entity} className="border border-slate-700 bg-[#0b0f14] px-2 py-0.5 text-[10px] text-slate-300">
                    {entity}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Raw / Normalized Payload JSON */}
          <section className="border border-slate-800 bg-[#111822] overflow-hidden" aria-labelledby="event-payload-heading">
            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 p-2.5">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setActiveTab("normalized")}
                  className={`px-2 py-1 text-[10px] font-bold border transition-colors ${
                    activeTab === "normalized"
                      ? "bg-cyan-400 text-[#0b0f14] border-cyan-400"
                      : "bg-[#0b0f14] text-slate-400 border-slate-700"
                  }`}
                >
                  NORMALIZED SCHEMA
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab("raw")}
                  className={`px-2 py-1 text-[10px] font-bold border transition-colors ${
                    activeTab === "raw"
                      ? "bg-cyan-400 text-[#0b0f14] border-cyan-400"
                      : "bg-[#0b0f14] text-slate-400 border-slate-700"
                  }`}
                >
                  RAW RECORD
                </button>
              </div>
              <button
                type="button"
                onClick={() => void copyJson()}
                className="tw-inline-action h-7 px-2 text-[10px]"
              >
                {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                <span>{copied ? "COPIED" : "COPY JSON"}</span>
              </button>
            </div>
            {copyError && <p role="status" className="px-3 pt-2 text-[10px] text-rose-400">Clipboard access blocked.</p>}
            <div className="max-h-[45vh] overflow-auto bg-[#080c10] p-3">
              <pre className="whitespace-pre-wrap break-all text-[10.5px] leading-relaxed text-emerald-300 font-mono">
                {JSON.stringify(payload, null, 2)}
              </pre>
            </div>
          </section>
        </div>
      </aside>
    </div>
  );
};
