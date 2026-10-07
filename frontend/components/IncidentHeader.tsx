"use client";

import React from "react";
import { ShieldAlert, AlertTriangle, ShieldCheck, User, Laptop, Globe, HardDrive, FileText, Database, Hash } from "lucide-react";
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
      <div className="rounded-sm border border-[#171d2b] bg-[#0c0f17] p-6 text-center font-mono-technical text-xs text-slate-400">
        NO ACTIVE INVESTIGATION FILE LOADED. REPLAY A DATASET SCENARIO TO INITIATE DETECTION.
      </div>
    );
  }

  const getSeverityBadge = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "high":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-rose-500/30 bg-rose-950/20 px-2 py-0.5 font-mono-technical text-xs font-bold text-rose-300">
            <ShieldAlert className="h-3.5 w-3.5 text-rose-400" />
            HIGH SEVERITY
          </span>
        );
      case "medium":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-amber-500/30 bg-amber-950/20 px-2 py-0.5 font-mono-technical text-xs font-bold text-amber-300">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
            MEDIUM SEVERITY
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 rounded-sm border border-slate-700 bg-slate-800/40 px-2 py-0.5 font-mono-technical text-xs font-bold text-slate-300">
            <ShieldCheck className="h-3.5 w-3.5 text-slate-400" />
            {sev.toUpperCase()} SEVERITY
          </span>
        );
    }
  };

  return (
    <section aria-label="Incident Case Dossier" className="rounded-sm border border-[#171d2b] bg-[#0c0f17] p-4 text-slate-200">
      {/* Top Banner: Incident ID, Badges & Case Selector */}
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between border-b border-[#151a26] pb-3.5">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="font-mono-technical text-xs text-slate-400 uppercase tracking-wider">
              CASE FILE:
            </span>
            {incidents.length > 1 ? (
              <select
                value={activeIncident.incident_id}
                onChange={(e) => onSelectIncident(e.target.value)}
                className="rounded-sm border border-[#21293c] bg-[#121622] px-2.5 py-1 font-mono-technical text-sm font-bold text-cyan-300 focus:border-cyan-500 focus:outline-none"
              >
                {incidents.map((inc) => (
                  <option key={inc.incident_id} value={inc.incident_id}>
                    {inc.incident_id} — RISK {inc.risk_index}/100 ({inc.severity.toUpperCase()})
                  </option>
                ))}
              </select>
            ) : (
              <span className="font-mono-technical text-base font-extrabold tracking-wide text-slate-100 bg-[#121622] px-2 py-0.5 rounded-sm border border-[#1e2638]">
                {activeIncident.incident_id}
              </span>
            )}
          </div>

          {getSeverityBadge(activeIncident.severity)}

          <span className="inline-flex items-center gap-1 rounded-sm border border-emerald-500/30 bg-emerald-950/20 px-2 py-0.5 font-mono-technical text-xs font-semibold text-emerald-300">
            STATUS: {activeIncident.status.toUpperCase()}
          </span>

          <span className="inline-flex items-center gap-1.5 rounded-sm border border-[#1e2638] bg-[#121622] px-2 py-0.5 font-mono-technical text-xs text-slate-300">
            <span className="text-slate-400">RISK INDEX:</span>
            <span className="font-bold text-rose-400">{activeIncident.risk_index}</span>
            <span className="text-slate-400">/100</span>
          </span>
        </div>

        {/* Engine Audit Telemetry */}
        <div className="flex items-center gap-3 font-mono-technical text-[11px] text-slate-400">
          <span>PIPELINE: {activeIncident.analysis_version}</span>
          <span className="text-slate-600">•</span>
          <span>RULES: {activeIncident.rule_version}</span>
        </div>
      </div>

      {/* Structured Forensic Entity Grid */}
      <div className="mt-3.5 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
        <div className="rounded-sm border border-[#171d2b] bg-[#10141f] p-2.5">
          <div className="flex items-center gap-1.5 text-[10px] font-mono-technical text-slate-400 uppercase tracking-wider">
            <User className="h-3 w-3 text-cyan-400" />
            <span>Target User</span>
          </div>
          <div className="mt-1 font-mono-technical text-xs font-bold text-cyan-300">
            {activeIncident.entity_ids.find((e) => e.startsWith("user-")) || "N/A"}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Primary Authenticated Identity</div>
        </div>

        <div className="rounded-sm border border-[#171d2b] bg-[#10141f] p-2.5">
          <div className="flex items-center gap-1.5 text-[10px] font-mono-technical text-slate-400 uppercase tracking-wider">
            <Laptop className="h-3 w-3 text-blue-400" />
            <span>Host Device</span>
          </div>
          <div className="mt-1 font-mono-technical text-xs font-bold text-blue-300">
            {activeIncident.entity_ids.find((e) => e.startsWith("device-") || e.startsWith("WKST-")) || "N/A"}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Compromised Endpoint Asset</div>
        </div>

        <div className="rounded-sm border border-[#171d2b] bg-[#10141f] p-2.5">
          <div className="flex items-center gap-1.5 text-[10px] font-mono-technical text-slate-400 uppercase tracking-wider">
            <Globe className="h-3 w-3 text-purple-400" />
            <span>External IP</span>
          </div>
          <div className="mt-1 font-mono-technical text-xs font-bold text-purple-300">
            {activeIncident.entity_ids.find((e) => e.includes(".") || e.startsWith("ip-")) || "N/A"}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Untrusted Remote Ingress/Egress</div>
        </div>

        <div className="rounded-sm border border-[#171d2b] bg-[#10141f] p-2.5">
          <div className="flex items-center gap-1.5 text-[10px] font-mono-technical text-slate-400 uppercase tracking-wider">
            <HardDrive className="h-3 w-3 text-amber-400" />
            <span>Removable Media</span>
          </div>
          <div className="mt-1 font-mono-technical text-xs font-bold text-amber-300">
            {activeIncident.entity_ids.find((e) => e.startsWith("usb-") || e.startsWith("RemovableDevice")) || "usb-storage-01"}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Physical Exfiltration Vector</div>
        </div>
      </div>

      {/* Correlated Entity Summary Row */}
      <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-[#151a26] pt-3 text-xs">
        <span className="font-mono-technical text-[11px] text-slate-400 uppercase">
          Total Correlated Entity Graph ({activeIncident.entity_ids.length}):
        </span>
        <div className="flex flex-wrap gap-1.5">
          {activeIncident.entity_ids.map((ent) => (
            <span
              key={ent}
              className="inline-flex items-center rounded-sm bg-[#121622] px-2 py-0.5 font-mono-technical text-[10px] text-slate-300 border border-[#1b2234]"
            >
              {ent}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
};
