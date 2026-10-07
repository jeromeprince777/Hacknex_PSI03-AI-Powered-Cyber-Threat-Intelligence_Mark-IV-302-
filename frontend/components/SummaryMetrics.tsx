"use client";

import React from "react";
import { Incident, EvidencePack } from "../lib/types";
import { Activity, Database, Layers, ShieldCheck } from "lucide-react";

interface SummaryMetricsProps {
  incident: Incident;
  evidencePack: EvidencePack | null;
}

export const SummaryMetrics: React.FC<SummaryMetricsProps> = ({ incident, evidencePack }) => {
  const metrics = [
    {
      label: "RISK INDEX",
      value: incident.risk_index,
      suffix: "/ 100",
      detail: "Deterministic multi-factor index",
      icon: Activity,
      highlight: incident.risk_index >= 70 ? "text-rose-400" : "text-amber-400",
      accent: incident.risk_index >= 70 ? "border-rose-500/40 bg-rose-950/20" : "border-amber-500/40 bg-amber-950/20",
      barColor: incident.risk_index >= 70 ? "bg-rose-500" : "bg-amber-400",
      percentage: incident.risk_index,
    },
    {
      label: "EVIDENCE EVENTS",
      value: evidencePack?.events.length ?? incident.evidence_event_ids.length,
      suffix: "records",
      detail: "Forensic event IDs attached",
      icon: Database,
      highlight: "text-cyan-400",
      accent: "border-cyan-500/40 bg-cyan-950/20",
      barColor: "bg-cyan-400",
      percentage: Math.min(100, ((evidencePack?.events.length ?? incident.evidence_event_ids.length) / 20) * 100),
    },
    {
      label: "CORRELATED STAGES",
      value: evidencePack?.stages.length ?? incident.stage_ids.length,
      suffix: "stages",
      detail: "Kill chain stages confirmed",
      icon: Layers,
      highlight: "text-emerald-400",
      accent: "border-emerald-500/40 bg-emerald-950/20",
      barColor: "bg-emerald-400",
      percentage: Math.min(100, ((evidencePack?.stages.length ?? incident.stage_ids.length) / 4) * 100),
    },
    {
      label: "LINKED ENTITIES",
      value: incident.entity_ids.length,
      suffix: "entities",
      detail: "Hosts, users, and endpoints",
      icon: ShieldCheck,
      highlight: "text-sky-300",
      accent: "border-sky-500/40 bg-sky-950/20",
      barColor: "bg-sky-400",
      percentage: Math.min(100, (incident.entity_ids.length / 8) * 100),
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      {metrics.map((m) => {
        const Icon = m.icon;
        return (
          <div
            key={m.label}
            className={`border p-3 transition-colors ${m.accent} relative overflow-hidden`}
          >
            <div className="flex items-center justify-between">
              <span className="font-mono-technical text-[10px] uppercase tracking-wider text-slate-400">
                {m.label}
              </span>
              <Icon className={`h-3.5 w-3.5 ${m.highlight}`} />
            </div>

            <div className="mt-2 flex items-baseline gap-1.5 font-mono-technical">
              <span className={`text-2xl font-bold tracking-tight ${m.highlight}`}>
                {m.value}
              </span>
              <span className="text-[10px] font-normal text-slate-400">
                {m.suffix}
              </span>
            </div>

            <div className="mt-2 h-1 w-full bg-[#111822] overflow-hidden">
              <div
                className={`h-full ${m.barColor}`}
                style={{ width: `${Math.max(8, m.percentage)}%` }}
              />
            </div>

            <p className="mt-1.5 truncate text-[9px] font-mono-technical text-slate-400">
              {m.detail}
            </p>
          </div>
        );
      })}
    </div>
  );
};
