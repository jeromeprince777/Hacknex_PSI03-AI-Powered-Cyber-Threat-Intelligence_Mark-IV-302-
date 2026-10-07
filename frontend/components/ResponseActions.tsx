"use client";

import React, { useState } from "react";
import { ChevronDown, ChevronRight, ShieldCheck, Zap } from "lucide-react";
import { ApprovedAction } from "../lib/types";

interface ResponseActionsProps {
  actions: ApprovedAction[];
}

export const ResponseActions: React.FC<ResponseActionsProps> = ({ actions }) => {
  const [expandedAction, setExpandedAction] = useState<string | null>(null);

  return (
    <section className="tw-panel overflow-hidden select-none" aria-labelledby="response-actions-heading">
      <div className="flex items-center justify-between gap-3 border-b border-slate-800 bg-[#111822] p-3.5">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" aria-hidden="true" />
          <h2 id="response-actions-heading" className="text-xs font-bold uppercase tracking-wider text-slate-100 font-mono-technical">
            APPROVED RESPONSE PLAYBOOKS
          </h2>
        </div>
        <span className="text-[10px] font-mono-technical text-cyan-400">SOC ADVISORY</span>
      </div>

      <ul className="divide-y divide-slate-800/80 bg-[#0b0f14]">
        {actions.map((action) => {
          const expanded = expandedAction === action.action_id;
          const detailsId = `response-${action.action_id.replace(/[^a-zA-Z0-9_-]/g, "-")}`;

          return (
            <li key={action.action_id}>
              <button
                type="button"
                aria-expanded={expanded}
                aria-controls={detailsId}
                onClick={() => setExpandedAction(expanded ? null : action.action_id)}
                className="flex w-full items-center justify-between gap-3 p-3 text-left hover:bg-[#16202e] transition-colors"
              >
                <span className="flex min-w-0 items-start gap-2.5">
                  <Zap className="mt-0.5 h-3.5 w-3.5 shrink-0 text-cyan-400" aria-hidden="true" />
                  <span className="min-w-0">
                    <span className="block text-xs font-bold text-slate-200">{action.label}</span>
                    <span className="mt-0.5 block break-all font-mono-technical text-[10px] text-slate-400">
                      ID: {action.action_id}
                    </span>
                    {action.stage_keys.length > 0 && (
                      <span className="mt-1.5 flex flex-wrap gap-1">
                        {action.stage_keys.map((stageKey) => (
                          <span
                            key={stageKey}
                            className="border border-slate-700 bg-[#111822] px-1.5 py-0.2 font-mono-technical text-[9px] text-cyan-300"
                          >
                            {stageKey}
                          </span>
                        ))}
                      </span>
                    )}
                  </span>
                </span>
                <span className="flex shrink-0 items-center gap-1 font-mono-technical text-[10px] text-slate-400">
                  <span>{expanded ? "HIDE" : "VIEW"}</span>
                  {expanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
                </span>
              </button>
              {expanded && (
                <div id={detailsId} className="border-t border-slate-800 bg-[#0f1722] p-3 pl-8 text-xs leading-relaxed text-slate-300 font-mono-technical">
                  {action.description}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
};
