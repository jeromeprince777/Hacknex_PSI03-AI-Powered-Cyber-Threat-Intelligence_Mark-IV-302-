"use client";

import React from "react";
import { AlertTriangle, User, Laptop, Globe, ShieldAlert, Clock } from "lucide-react";
import { Incident } from "../lib/types";

interface IncidentHeaderProps {
  incidents: Incident[];
  activeIncident: Incident | null;
  onSelectIncident: (id: string) => void;
}

export const IncidentHeader: React.FC<IncidentHeaderProps> = ({
  incidents,
  activeIncident,
  onSelectIncident,
}) => {
  if (!activeIncident) {
    return (
      <div className="rounded border border-[#1e2438] bg-[#0f121d] p-4 text-center text-sm text-slate-400">
        No active incident selected. Replay a dataset to run detection.
      </div>
    );
  }

  const getSeverityStyle = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "high":
        return "border-rose-500/40 bg-rose-950/40 text-rose-300";
      case "medium":
        return "border-amber-500/40 bg-amber-950/40 text-amber-300";
      case "low":
        return "border-blue-500/40 bg-blue-950/40 text-blue-300";
      default:
        return "border-slate-500/40 bg-slate-800/40 text-slate-300";
    }
  };

  return (
    <div className="rounded border border-[#1e2438] bg-[#0d101a] p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        {/* Left: Incident Title & Badges */}
        <div className="flex flex-wrap items-center gap-3">
          {incidents.length > 1 ? (
            <select
              value={activeIncident.incident_id}
              onChange={(e) => onSelectIncident(e.target.value)}
              className="rounded border border-[#1e2438] bg-[#141827] px-3 py-1.5 font-mono text-sm text-cyan-300 focus:outline-none focus:border-cyan-500"
            >
              {incidents.map((inc) => (
                <option key={inc.incident_id} value={inc.incident_id}>
                  {inc.incident_id} — Risk {inc.risk_index} ({inc.severity.toUpperCase()})
                </option>
              ))}
            </select>
          ) : (
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg font-bold text-slate-100">
                {activeIncident.incident_id}
              </span>
            </div>
          )}

          <span
            className={`inline-flex items-center gap-1 rounded border px-2.5 py-0.5 font-mono text-xs font-semibold uppercase tracking-wider ${getSeverityStyle(
              activeIncident.severity
            )}`}
          >
            <ShieldAlert className="h-3.5 w-3.5" />
            {activeIncident.severity} SEVERITY
          </span>

          <span className="inline-flex items-center gap-1 rounded border border-emerald-500/30 bg-emerald-950/30 px-2 py-0.5 font-mono text-xs text-emerald-300">
            STATUS: {activeIncident.status.toUpperCase()}
          </span>

          <span className="font-mono text-xs text-slate-400">
            Stages: <strong className="text-slate-200">{activeIncident.stage_ids.length}</strong> | Evidence Events:{" "}
            <strong className="text-slate-200">{activeIncident.evidence_event_ids.length}</strong>
          </span>
        </div>

        {/* Right: Versioning and Audit stamp */}
        <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
          <Clock className="h-3.5 w-3.5 text-slate-500" />
          <span>Engine: {activeIncident.analysis_version}</span>
          <span className="text-slate-600">|</span>
          <span>Rules: {activeIncident.rule_version}</span>
        </div>
      </div>

      {/* Entity Pill Strip */}
      <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-[#161a29] pt-3 text-xs">
        <span className="text-slate-400 font-medium">Correlated Entities:</span>
        {activeIncident.entity_ids.map((ent) => {
          const isUser = ent.startsWith("user-");
          const isDevice = ent.startsWith("device-") || ent.startsWith("WKST-");
          const isIp = ent.includes(".");

          return (
            <span
              key={ent}
              className={`inline-flex items-center gap-1 rounded px-2 py-0.5 font-mono text-[11px] border ${
                isUser
                  ? "border-cyan-500/30 bg-cyan-950/30 text-cyan-300"
                  : isDevice
                  ? "border-blue-500/30 bg-blue-950/30 text-blue-300"
                  : isIp
                  ? "border-purple-500/30 bg-purple-950/30 text-purple-300"
                  : "border-slate-700 bg-slate-800/40 text-slate-300"
              }`}
            >
              {isUser && <User className="h-3 w-3" />}
              {isDevice && <Laptop className="h-3 w-3" />}
              {isIp && <Globe className="h-3 w-3" />}
              {ent}
            </span>
          );
        })}
      </div>
    </div>
  );
};
