"use client";

import React, { useState } from "react";
import { ChevronDown, RefreshCw, ServerOff, ShieldAlert, Zap } from "lucide-react";
import { Incident } from "../lib/types";

interface TopBarProps {
  activeTab: "console" | "replay" | "suppression";
  incidents: Incident[];
  activeIncident: Incident | null;
  onSelectIncident: (id: string) => void;
  isBackendHealthy: boolean;
  refreshing: boolean;
  onRefresh: () => void;
}

const labels = {
  console: "Investigation Console",
  replay: "Dataset Replay Lab",
  suppression: "Suppression Audit Ledger",
} as const;

export const TopBar: React.FC<TopBarProps> = ({
  activeTab,
  incidents,
  activeIncident,
  onSelectIncident,
  isBackendHealthy,
  refreshing,
  onRefresh,
}) => {
  const [quarantineActive, setQuarantineActive] = useState(false);
  const [playbookExecuted, setPlaybookExecuted] = useState(false);

  const handleQuarantine = () => {
    setQuarantineActive(!quarantineActive);
  };

  const handleExecutePlaybook = () => {
    setPlaybookExecuted(true);
    setTimeout(() => setPlaybookExecuted(false), 2500);
  };

  return (
    <div className="tw-contextbar select-none">
      <div className="tw-contextbar-inner">
        {/* Left Section: Breadcrumb & Live Socket Stream Ticker */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs">
          <div className="flex items-center gap-1.5 font-mono-technical text-[11px] text-slate-400">
            <span className="text-slate-500">WORKSPACE</span>
            <span className="text-slate-600">/</span>
            <span className="font-semibold text-slate-200">{labels[activeTab]}</span>
            {activeTab === "console" && activeIncident && (
              <>
                <span className="text-slate-600">/</span>
                <span className="truncate font-semibold text-cyan-400">
                  {activeIncident.incident_id}
                </span>
              </>
            )}
          </div>

          {/* Telemetry WebSocket Status Badge (from Stitch) */}
          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-[#0a0e13] border border-slate-800 text-[10px] font-mono-technical">
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isBackendHealthy ? "bg-emerald-400 tactical-pulse" : "bg-rose-500"
              }`}
            />
            <span className={isBackendHealthy ? "text-emerald-400" : "text-rose-400"}>
              {isBackendHealthy ? "[SOCKET: CONNECTED // 128.4k evt/s]" : "[SOCKET: DISCONNECTED]"}
            </span>
          </div>

          {/* Live Velocity Sparkline (from Stitch) */}
          <div className="hidden xl:flex items-center gap-2 pl-2 border-l border-slate-800 font-mono-technical text-[10px] text-slate-400">
            <span>LAT: 12ms</span>
            <span>JIT: 0.4ms</span>
            <svg className="w-16 h-3 text-cyan-400 stroke-current fill-none stroke-[1.2]" viewBox="0 0 64 12">
              <polyline points="0,7 8,6 16,9 24,3 32,7 40,2 48,6 56,1 64,5" />
            </svg>
          </div>
        </div>

        {/* Right Section: Incident Selector & Tactical Action Triggers */}
        <div className="flex min-w-0 flex-wrap items-center justify-end gap-2 sm:gap-2.5">
          {/* Incident Switcher */}
          {activeTab === "console" && incidents.length > 1 && activeIncident && (
            <label className="relative flex min-w-0 items-center">
              <span className="sr-only">Select Incident</span>
              <select
                value={activeIncident.incident_id}
                onChange={(event) => onSelectIncident(event.target.value)}
                className="h-8 max-w-44 appearance-none border border-slate-700 bg-[#111822] py-1 pl-2.5 pr-7 font-mono-technical text-[11px] text-slate-200 focus:border-cyan-400 sm:max-w-64"
              >
                {incidents.map((incident) => (
                  <option key={incident.incident_id} value={incident.incident_id}>
                    {incident.incident_id} · {incident.severity.toUpperCase()} · RISK {incident.risk_index}
                  </option>
                ))}
              </select>
              <ChevronDown className="pointer-events-none absolute right-2 h-3 w-3 text-slate-400" aria-hidden="true" />
            </label>
          )}

          {/* Tactical Playbook Trigger */}
          <button
            type="button"
            onClick={handleExecutePlaybook}
            className={`tw-inline-action text-[11px] h-8 px-2.5 ${
              playbookExecuted
                ? "border-emerald-500 bg-emerald-950/40 text-emerald-300"
                : "border-slate-700 hover:border-cyan-400 hover:text-cyan-300"
            }`}
            title="Execute approved containment playbook"
          >
            <Zap className={`h-3 w-3 ${playbookExecuted ? "text-emerald-400" : "text-cyan-400"}`} />
            <span>{playbookExecuted ? "PLAYBOOK ENGAGED" : "EXECUTE PLAYBOOK"}</span>
          </button>

          {/* Tactical Quarantine Button */}
          <button
            type="button"
            onClick={handleQuarantine}
            className={`tw-inline-action text-[11px] h-8 px-2.5 ${
              quarantineActive
                ? "border-rose-500 bg-rose-600 text-white font-bold"
                : "tw-danger-action font-bold"
            }`}
            title="Isolate compromised endpoints immediately"
          >
            <ShieldAlert className="h-3 w-3" />
            <span>{quarantineActive ? "ISOLATION ACTIVE" : "QUARANTINE"}</span>
          </button>

          {/* Sync Refresh Button */}
          <button
            type="button"
            onClick={onRefresh}
            disabled={refreshing}
            className="tw-inline-action h-8 px-2"
            title="Refresh incident telemetry and audit logs"
          >
            <RefreshCw className={`h-3 w-3 ${refreshing ? "animate-spin text-cyan-400" : ""}`} aria-hidden="true" />
            <span className="hidden sm:inline">{refreshing ? "SYNCING" : "SYNC"}</span>
          </button>

          {/* Analyst Callsign Badge (from Stitch) */}
          <div
            className="flex h-7 w-7 items-center justify-center border border-cyan-500/60 bg-[#111822] font-mono-technical text-[10px] font-bold text-cyan-400"
            title="Analyst Tactical Callsign"
          >
            OP-9
          </div>
        </div>
      </div>
    </div>
  );
};
