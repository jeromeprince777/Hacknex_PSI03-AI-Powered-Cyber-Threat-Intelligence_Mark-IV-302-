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
    <header className="border-b border-[#1e2438] bg-[#0c0e17] px-6 py-3">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        {/* Brand & North Star Statement */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded border border-cyan-500/30 bg-cyan-950/40 text-cyan-400">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-base font-bold tracking-wider text-slate-100">
                THREATWEAVE
              </span>
              <span className="rounded border border-[#1e2438] bg-[#141827] px-1.5 py-0.5 font-mono text-[10px] text-cyan-400">
                HNX26PSI03
              </span>
              <span className="hidden sm:inline-block rounded bg-slate-800/60 px-1.5 py-0.5 font-mono text-[10px] text-slate-400">
                v0.1.0-qualifier
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Evidence-First Attack Chain Reconstruction & Audit Console
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-1 rounded border border-[#1e2438] bg-[#08090e] p-1">
          <button
            onClick={() => setActiveTab("console")}
            className={`flex items-center gap-1.5 rounded px-3 py-1.5 text-xs font-medium transition ${
              activeTab === "console"
                ? "bg-[#1c2237] text-cyan-300 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Terminal className="h-3.5 w-3.5" />
            Investigation Console
          </button>
          <button
            onClick={() => setActiveTab("replay")}
            className={`flex items-center gap-1.5 rounded px-3 py-1.5 text-xs font-medium transition ${
              activeTab === "replay"
                ? "bg-[#1c2237] text-cyan-300 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            Dataset Replay & Audit
          </button>
          <button
            onClick={() => setActiveTab("suppression")}
            className={`flex items-center gap-1.5 rounded px-3 py-1.5 text-xs font-medium transition ${
              activeTab === "suppression"
                ? "bg-[#1c2237] text-cyan-300 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Activity className="h-3.5 w-3.5" />
            Suppression Log
          </button>
        </div>

        {/* Backend Status & Global Controls */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-[11px]">
            <span
              className={`h-2 w-2 rounded-full ${
                isBackendHealthy ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
              }`}
            />
            <span className="font-mono text-slate-300">
              {isBackendHealthy ? "CORE ONLINE" : "DISCONNECTED"}
            </span>
          </div>

          <button
            onClick={onRefresh}
            disabled={refreshing}
            className="flex items-center gap-1 rounded border border-[#1e2438] bg-[#141827] px-2.5 py-1 text-xs text-slate-300 hover:bg-[#1a2034] transition disabled:opacity-50"
            title="Refresh active incident telemetry"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? "animate-spin text-cyan-400" : ""}`} />
            <span>Sync</span>
          </button>
        </div>
      </div>
    </header>
  );
};
