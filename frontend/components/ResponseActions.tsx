"use client";

import React from "react";
import { ShieldCheck, AlertCircle, Laptop, Lock, FileSearch, ShieldX, Archive } from "lucide-react";
import { ApprovedAction } from "../lib/types";

interface ResponseActionsProps {
  actions: ApprovedAction[];
}

export const ResponseActions: React.FC<ResponseActionsProps> = ({ actions }) => {
  const getActionIcon = (actionId: string) => {
    switch (actionId) {
      case "isolate-device":
        return <Laptop className="h-4 w-4 text-rose-400" />;
      case "disable-session":
        return <Lock className="h-4 w-4 text-amber-400" />;
      case "review-resource-access":
        return <FileSearch className="h-4 w-4 text-cyan-400" />;
      case "review-network-transfer":
        return <ShieldX className="h-4 w-4 text-purple-400" />;
      default:
        return <Archive className="h-4 w-4 text-slate-400" />;
    }
  };

  return (
    <div className="rounded border border-[#1e2438] bg-[#0d101a] p-4">
      <div className="flex items-center justify-between border-b border-[#161a29] pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold text-slate-100">
            APPROVED RESPONSE RECOMMENDATIONS
          </h3>
        </div>
        <span className="font-mono text-[11px] text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-500/30">
          Advisory Only — Controlled Playbook
        </span>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {actions.map((act) => (
          <div
            key={act.action_id}
            className="rounded border border-[#1e2438] bg-[#101320] p-3 flex flex-col justify-between space-y-3"
          >
            <div>
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] text-slate-400 uppercase">
                  ID: {act.action_id}
                </span>
                <div className="flex items-center gap-1 font-mono text-[10px] text-cyan-300">
                  {act.stage_keys.map((sk) => (
                    <span key={sk} className="rounded bg-[#161b2d] px-1.5 py-0.2 border border-[#21283d]">
                      {sk}
                    </span>
                  ))}
                </div>
              </div>

              <div className="mt-2 flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded border border-[#1e2438] bg-[#141827]">
                  {getActionIcon(act.action_id)}
                </div>
                <h4 className="text-xs font-bold text-slate-200">
                  {act.label}
                </h4>
              </div>

              <p className="mt-2 text-[11px] text-slate-400 leading-relaxed font-sans">
                {act.description}
              </p>
            </div>

            <div className="pt-2 border-t border-[#181d2f] flex items-center justify-between text-[10px] font-mono text-slate-500">
              <span>Status: RECOMMENDED</span>
              <span className="text-cyan-400/80">Pending IR Review</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
