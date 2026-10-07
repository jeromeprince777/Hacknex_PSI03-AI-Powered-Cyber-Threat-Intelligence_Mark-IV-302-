"use client";

import React from "react";
import { Shield, Activity, RefreshCw, Terminal, Layers } from "lucide-react";

interface NavbarProps {
  activeTab: "console" | "replay" | "suppression";
  setActiveTab: (tab: "console" | "replay" | "suppression") => void;
  isBackendHealthy: boolean;
  onRefresh: () => void;
  refreshing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  isBackendHealthy,
  onRefresh,
  refreshing,
}) => {
  return (
    <header className="border-b border-[#171d2b] bg-[#090b12] px-4 md:px-6 py-2.5 select-none">
      <div className="flex flex-col gap-2.5 md:flex-row md:items-center md:justify-between max-w-[1720px] mx-auto">
        {/* Brand & Forensic System Identity */}
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-sm border border-cyan-500/30 bg-cyan-950/30 text-cyan-400">
            <Shield className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono-technical text-sm font-bold tracking-wider text-slate-100">
                THREATWEAVE
              </span>
              <span className="rounded-sm border border-[#1e2638] bg-[#111624] px-1.5 py-0.2 font-mono-technical text-[10px] text-cyan-400 font-medium">
                HNX26PSI03
              </span>
              <span className="hidden sm:inline-block rounded-sm bg-[#131826] px-1.5 py-0.2 font-mono-technical text-[10px] text-slate-400 border border-[#1b2234]">
                v0.1.0-STABLE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 tracking-tight">
              Evidence-Grounded Attack Chain Reconstruction & SOC Investigation Workstation
            </p>
          </div>
        </div>

        {/* Operational View Switcher */}
        <nav aria-label="Workstation Navigation" className="flex items-center gap-1 rounded-sm border border-[#171d2b] bg-[#0c0f18] p-1">
          <button
            onClick={() => setActiveTab("console")}
            className={`flex items-center gap-1.5 rounded-sm px-3 py-1 text-xs font-mono-technical transition ${
              activeTab === "console"
                ? "bg-[#182032] text-cyan-300 font-semibold border border-cyan-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-[#121624]"
            }`}
          >
            <Terminal className="h-3.5 w-3.5" />
            <span>Investigation Console</span>
          </button>
          <button
            onClick={() => setActiveTab("replay")}
            className={`flex items-center gap-1.5 rounded-sm px-3 py-1 text-xs font-mono-technical transition ${
              activeTab === "replay"
                ? "bg-[#182032] text-cyan-300 font-semibold border border-cyan-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-[#121624]"
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Dataset Replay</span>
          </button>
          <button
            onClick={() => setActiveTab("suppression")}
            className={`flex items-center gap-1.5 rounded-sm px-3 py-1 text-xs font-mono-technical transition ${
              activeTab === "suppression"
                ? "bg-[#182032] text-cyan-300 font-semibold border border-cyan-500/20"
                : "text-slate-400 hover:text-slate-200 hover:bg-[#121624]"
            }`}
          >
            <Activity className="h-3.5 w-3.5" />
            <span>Suppression Audit</span>
          </button>
        </nav>

        {/* System Online Telemetry & Sync */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 rounded-sm border border-[#171d2b] bg-[#0c0f18] px-2.5 py-1 text-[11px] font-mono-technical">
            <span
              className={`h-2 w-2 rounded-full ${
                isBackendHealthy ? "bg-emerald-500 shadow-sm shadow-emerald-500/50" : "bg-rose-500"
              }`}
            />
            <span className="text-slate-300 font-medium">
              {isBackendHealthy ? "ENGINE ONLINE" : "ENGINE OFFLINE"}
            </span>
          </div>

          <button
            onClick={onRefresh}
            disabled={refreshing}
            className="flex items-center gap-1.5 rounded-sm border border-[#1e2638] bg-[#121622] px-2.5 py-1 text-xs font-mono-technical text-slate-300 hover:bg-[#182032] hover:text-cyan-300 transition disabled:opacity-50"
            title="Synchronize active incident telemetry from backend"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin text-cyan-400" : ""}`} />
            <span>Sync</span>
          </button>
        </div>
      </div>
    </header>
  );
};
