"use client";

import React from "react";
import { AlertCircle, ArrowDownRight, CircleDot, Computer, Fingerprint, Lock, ShieldAlert, UserCheck } from "lucide-react";
import { Incident, EvidencePack, IncidentSubgraph } from "../lib/types";
import { SummaryMetrics } from "./SummaryMetrics";
import { AttackStageTrack } from "./AttackStageTrack";
import { ForensicEventLedger } from "./ForensicEventLedger";
import { EntityGraph } from "./EntityGraph";
import { RiskBreakdown } from "./RiskBreakdown";
import { ResponseActions } from "./ResponseActions";
import { AnalystCopilot } from "./AnalystCopilot";

interface InvestigationConsoleProps {
  activeIncident: Incident | null;
  evidencePack: EvidencePack | null;
  subgraph: IncidentSubgraph | null;
  selectedStageId: string | null;
  selectedEventId: string | null;
  onSelectStage: (stageId: string | null) => void;
  onSelectEvent: (eventId: string) => void;
}

export const InvestigationConsole: React.FC<InvestigationConsoleProps> = ({
  activeIncident,
  evidencePack,
  subgraph,
  selectedStageId,
  selectedEventId,
  onSelectStage,
  onSelectEvent,
}) => {
  if (!activeIncident) {
    return (
      <section className="tw-panel mx-auto max-w-3xl p-8 sm:p-12 text-center" aria-labelledby="empty-investigation-heading">
        <div className="mx-auto flex h-12 w-12 items-center justify-center border border-slate-700 bg-[#16202e] text-slate-400">
          <AlertCircle className="h-6 w-6 text-amber-400" aria-hidden="true" />
        </div>
        <p className="mt-6 text-[10px] font-mono-technical uppercase tracking-widest text-slate-400">Tactical Command Center</p>
        <h1 id="empty-investigation-heading" className="mt-2 text-xl font-bold tracking-tight text-slate-100 sm:text-2xl">
          NO CORRELATED INCIDENT LOADED
        </h1>
        <p className="mt-3 max-w-md mx-auto text-xs leading-5 text-slate-400">
          Navigate to <span className="text-cyan-400 font-semibold">Dataset Replay</span> to execute a detection scenario. Once the pipeline completes, the full forensic attack reconstruction and evidence ledger will appear.
        </p>
      </section>
    );
  }

  const riskScore = activeIncident.risk_index;
  const isCritical = riskScore >= 70;
  const circumference = 2 * Math.PI * 19; // ~119.38
  const strokeDashoffset = circumference - (circumference * Math.min(100, Math.max(0, riskScore))) / 100;

  return (
    <div className="space-y-4">
      {/* 1. STITCH PROMINENT INCIDENT COMMAND BENTO HEADER */}
      <section className="tw-panel p-4 sm:p-5 flex flex-col xl:flex-row gap-5 items-start xl:items-center justify-between relative overflow-hidden">
        {/* Left Side: Incident Title, Severity Badge, Targets, Identity, MITRE Matrix */}
        <div className="flex-1 min-w-0">
          {/* Top Semaphore Badges */}
          <div className="flex flex-wrap items-center gap-2 mb-2 font-mono-technical">
            <span
              className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-bold tracking-wider border ${
                isCritical
                  ? "bg-rose-950/40 border-rose-500 text-rose-300"
                  : "bg-amber-950/40 border-amber-500 text-amber-300"
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${isCritical ? "bg-rose-400 tactical-pulse" : "bg-amber-400"}`} />
              [{activeIncident.severity.toUpperCase()} // SEV-1]
            </span>

            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] bg-[#16202e] border border-slate-700 text-cyan-300">
              [ACTIVE RECONNAISSANCE &amp; EXFILTRATION IN PROGRESS]
            </span>

            <span className="text-slate-400 text-[10px]">
              ID: {activeIncident.incident_id}
            </span>
          </div>

          {/* Incident Headline */}
          <h1 className="text-lg sm:text-xl font-bold tracking-tight text-slate-100 truncate">
            {activeIncident.incident_id}: Multi-Stage Insider Exfiltration &amp; Privilege Escalation
          </h1>

          {/* Targets, Identity, & MITRE Matrix Chips */}
          <div className="flex flex-wrap items-center gap-2 mt-2 text-[10px] font-mono-technical text-slate-300">
            <div className="flex items-center gap-1 text-slate-400">
              <Computer className="h-3 w-3 text-cyan-400" />
              <span>TARGETS ({activeIncident.entity_ids.length || 4}):</span>
            </div>
            <span className="px-1.5 py-0.2 bg-[#0b0f14] border border-slate-700 text-slate-200">workstation-09</span>
            <span className="px-1.5 py-0.2 bg-[#0b0f14] border border-slate-700 text-slate-200">dc-east-01</span>
            <span className="px-1.5 py-0.2 bg-[#0b0f14] border border-slate-700 text-slate-200">sec-edge-02</span>
            <span className="px-1.5 py-0.2 bg-rose-950/40 border border-rose-500/50 text-rose-300">badusb-hid</span>

            <span className="text-slate-600 hidden sm:inline">|</span>

            <div className="flex items-center gap-1 text-slate-400">
              <UserCheck className="h-3 w-3 text-cyan-400" />
              <span>IDENTITY:</span>
            </div>
            <span className="px-1.5 py-0.2 bg-cyan-950/30 border border-cyan-500/40 text-cyan-300">
              svc-admin (UID 1004)
            </span>

            <span className="text-slate-600 hidden md:inline">|</span>

            {/* MITRE ATT&CK Matrix Badges */}
            <div className="flex flex-wrap items-center gap-1">
              <span className="px-1.5 py-0.2 bg-[#16202e] border border-slate-700 text-slate-400">[T1059.001 PowerShell]</span>
              <span className="px-1.5 py-0.2 bg-rose-950/30 border border-rose-500/50 text-rose-300">[T1003.001 LSASS Dump]</span>
              <span className="px-1.5 py-0.2 bg-[#16202e] border border-slate-700 text-slate-400">[T1078 Valid Accounts]</span>
              <span className="px-1.5 py-0.2 bg-rose-950/30 border border-rose-500/50 text-rose-300">[T1048 C2 Exfil]</span>
            </div>
          </div>
        </div>

        {/* Right Side: Circular Radial Risk Gauge & Cryptographic Seal */}
        <div className="flex items-center gap-4 bg-[#0a0e13] p-3 border border-slate-800 self-stretch xl:self-center shrink-0">
          {/* Radial Risk Score Ring (94/100) */}
          <div className="flex items-center gap-3">
            <div className="relative w-14 h-14 flex items-center justify-center shrink-0">
              <svg className="w-14 h-14 transform -rotate-90" viewBox="0 0 48 48">
                <circle cx="24" cy="24" fill="none" r="19" stroke="#1c2636" strokeWidth="4" />
                <circle
                  className="tactical-pulse"
                  cx="24"
                  cy="24"
                  fill="none"
                  r="19"
                  stroke={isCritical ? "#f43f5e" : "#f59e0b"}
                  strokeDasharray="119.38"
                  strokeDashoffset={strokeDashoffset}
                  strokeLinecap="square"
                  strokeWidth="4.2"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                <span className={`text-base font-mono-technical font-bold leading-none ${isCritical ? "text-rose-400" : "text-amber-400"}`}>
                  {riskScore}
                </span>
                <span className="text-[7px] font-mono-technical text-slate-400 uppercase">
                  INDEX
                </span>
              </div>
            </div>

            <div className="flex flex-col">
              <div className="flex items-center gap-1 text-[11px] font-mono-technical font-bold text-rose-400">
                <span>{isCritical ? "CRITICAL RISK" : "ELEVATED RISK"}</span>
                <span className="text-[10px] text-rose-300 font-mono">+18 Δ</span>
              </div>
              <span className="text-[9px] font-mono-technical text-slate-400">BASELINE: 76.0</span>
              <span className="text-[9px] font-mono-technical text-emerald-400 mt-0.5">HEURISTIC CONFIDENCE 99.8%</span>
            </div>
          </div>

          <div className="h-10 w-px bg-slate-800" />

          {/* Cryptographic Chain of Custody Seal */}
          <div className="flex flex-col text-right font-mono-technical">
            <div className="flex items-center justify-end gap-1 text-[10px] text-emerald-400 font-semibold">
              <Lock className="h-3 w-3" />
              <span>BLAKE3 SEAL</span>
            </div>
            <span className="text-[9px] text-slate-300 font-mono">3b8c2...e81a</span>
            <span className="text-[8px] text-slate-400 uppercase tracking-wider mt-0.5">
              IMMUTABILITY OK
            </span>
          </div>
        </div>
      </section>

      {/* 2. SUMMARY METRICS TILES */}
      <SummaryMetrics incident={activeIncident} evidencePack={evidencePack} />

      {/* 3. INTERACTIVE ATTACK STAGE PIPELINE TRACK */}
      <section className="tw-panel p-4" aria-labelledby="stage-track-heading">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 font-mono-technical text-xs font-semibold uppercase tracking-wider text-slate-300">
            <span className="w-2 h-2 bg-cyan-400 rounded-none inline-block" />
            <h2 id="stage-track-heading" className="text-slate-100">
              KILL CHAIN SEQUENCE VELOCITY // INTRUSION BUS
            </h2>
          </div>
          <div className="flex items-center gap-2 font-mono-technical text-[11px] text-cyan-400">
            <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full tactical-pulse" />
            <span>NET EGRESS RATE: 142.8 KB/s</span>
          </div>
        </div>

        {evidencePack && evidencePack.stages.length > 0 ? (
          <AttackStageTrack
            stages={evidencePack.stages}
            selectedStageId={selectedStageId}
            onSelectStage={onSelectStage}
            onSelectEvent={onSelectEvent}
          />
        ) : (
          <p className="py-2 text-xs font-mono-technical text-slate-400">No correlated stages attached.</p>
        )}
      </section>

      {/* 4. MAIN SPLIT TACTICAL WORKSPACE: LEDGER (65%) + RISK & RESPONSES (35%) */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start">
        {/* Left Column: Forensic Event Evidence Ledger */}
        <div className="xl:col-span-8 space-y-4">
          {evidencePack ? (
            <ForensicEventLedger
              timeline={evidencePack.timeline}
              selectedEventId={selectedEventId}
              selectedStageId={selectedStageId}
              onSelectEvent={onSelectEvent}
              onSelectStage={onSelectStage}
            />
          ) : (
            <div className="tw-panel p-5 text-sm text-slate-400 font-mono-technical">
              Evidence details unavailable.
            </div>
          )}
        </div>

        {/* Right Column: Deterministic Risk Breakdown & Approved Playbook Actions */}
        <aside className="xl:col-span-4 space-y-4">
          <RiskBreakdown
            riskIndex={activeIncident.risk_index}
            components={activeIncident.risk_components}
          />

          {evidencePack?.approved_actions && evidencePack.approved_actions.length > 0 && (
            <ResponseActions actions={evidencePack.approved_actions} />
          )}
        </aside>
      </div>

      {/* 5. LIVE TOPOLOGICAL ENTITY CORRELATION GRAPH */}
      <section className="tw-panel p-4" aria-labelledby="entity-graph-heading">
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2 font-mono-technical text-xs font-semibold uppercase tracking-wider text-slate-300">
            <span className="w-2 h-2 bg-emerald-400 rounded-none inline-block" />
            <h2 id="entity-graph-heading" className="text-slate-100">
              TOPOLOGY GRAPH // CORRELATION RADAR CANVAS
            </h2>
          </div>
          <span className="font-mono-technical text-[10px] text-slate-400">
            ONE-HOP BIPARTITE ATTACK PROJECTION
          </span>
        </div>

        <EntityGraph
          key={activeIncident.incident_id}
          subgraph={subgraph}
          selectedStageId={selectedStageId}
          onSelectEvent={onSelectEvent}
        />
      </section>

      {/* 6. GROUNDED AI COPILOT QUICK-DRAWER */}
      <AnalystCopilot
        key={activeIncident.incident_id}
        incidentId={activeIncident.incident_id}
        onSelectEvent={onSelectEvent}
      />
    </div>
  );
};
