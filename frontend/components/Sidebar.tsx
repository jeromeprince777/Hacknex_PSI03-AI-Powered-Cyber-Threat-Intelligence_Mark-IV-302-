"use client";

import React from "react";
import { Activity, ArchiveX, Crosshair, Shield, Terminal } from "lucide-react";

interface SidebarProps {
  activeTab: "console" | "replay" | "suppression";
  onTabChange: (tab: "console" | "replay" | "suppression") => void;
  incidentCount: number;
  suppressionCount: number;
}

const destinations = [
  { id: "console", label: "Incident Command", icon: Crosshair },
  { id: "replay", label: "Dataset Replay", icon: Activity },
  { id: "suppression", label: "Suppression Audit", icon: ArchiveX },
] as const;

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  incidentCount,
  suppressionCount,
}) => {
  return (
    <header className="tw-masthead select-none">
      <div className="tw-masthead-inner">
        {/* Brand & Sector Callout */}
        <div className="flex items-center gap-3">
          <a
            href="#main-content"
            className="flex items-center gap-2.5 text-inherit no-underline"
          >
            <span className="tw-brand-mark" aria-hidden="true">
              <Shield className="h-4 w-4" strokeWidth={2} />
            </span>
            <div className="leading-tight">
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-slate-100 text-sm">
                  ThreatWeave
                </span>
                <span className="text-[10px] font-mono-technical font-semibold text-cyan-400 border border-cyan-500/30 bg-cyan-950/40 px-1 py-0.2">
                  HNX26PSI03
                </span>
              </div>
              <span className="block text-[10px] font-mono-technical text-slate-400">
                TACTICAL SOC COMMAND // SECTOR-09
              </span>
            </div>
          </a>
        </div>

        {/* Primary Navigation Tabs */}
        <nav aria-label="Work areas" className="flex h-full items-center gap-1 sm:gap-2">
          {destinations.map(({ id, label, icon: Icon }) => {
            const count = id === "console" ? incidentCount : id === "suppression" ? suppressionCount : null;
            const selected = activeTab === id;

            return (
              <button
                key={id}
                type="button"
                aria-current={selected ? "page" : undefined}
                onClick={() => onTabChange(id)}
                className="tw-nav-link"
              >
                <Icon className={`h-3.5 w-3.5 ${selected ? "text-cyan-400" : "text-slate-400"}`} strokeWidth={2} aria-hidden="true" />
                <span className="text-xs tracking-wide">{label}</span>
                {count !== null && count > 0 && (
                  <span
                    className={`px-1.5 py-0.5 font-mono-technical text-[10px] font-semibold tabular-nums border ${
                      selected
                        ? "bg-cyan-950/80 text-cyan-300 border-cyan-500/40"
                        : "bg-[#16202e] text-slate-400 border-slate-700/60"
                    }`}
                  >
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Operational Status Ticker */}
        <div className="hidden lg:flex items-center gap-3 text-[11px] font-mono-technical text-slate-400">
          <div className="flex items-center gap-1.5 px-2 py-1 bg-[#111822] border border-slate-800">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 tactical-pulse" />
            <span className="text-emerald-400 font-semibold text-[10px]">REDCON-1</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-500 text-[10px]">
            <Terminal className="h-3 w-3 text-cyan-500" />
            <span>HEURISTIC ENGINE v3.4</span>
          </div>
        </div>
      </div>
    </header>
  );
};
