"use client";

import React from "react";
import { Sliders, HelpCircle } from "lucide-react";
import { RiskComponents } from "../lib/types";

interface RiskBreakdownProps {
  riskIndex: number;
  components: RiskComponents;
}

export const RiskBreakdown: React.FC<RiskBreakdownProps> = ({ riskIndex, components }) => {
  const factors = [
    {
      name: "Signal Severity",
      weightLabel: "35% weight",
      score: components.signal_score,
      color: "bg-rose-500",
      textColor: "text-rose-400",
      description: "Severity of highest-scoring atomic indicators across attack stages",
    },
    {
      name: "Sequence Consistency",
      weightLabel: "30% weight",
      score: components.sequence_score,
      color: "bg-amber-500",
      textColor: "text-amber-400",
      description: "Temporal ordering match with canonical multi-stage attack transitions",
    },
    {
      name: "Entity Novelty",
      weightLabel: "20% weight",
      score: components.entity_novelty,
      color: "bg-purple-500",
      textColor: "text-purple-400",
      description: "First-seen external IP, first-time resource read, or unrecognized USB",
    },
    {
      name: "Statistical Anomaly",
      weightLabel: "15% weight",
      score: components.anomaly_score,
      color: "bg-cyan-500",
      textColor: "text-cyan-400",
      description: "Normalized multivariate standard deviation excess against baseline",
    },
  ];

  return (
    <div className="rounded border border-[#1e2438] bg-[#0d101a] p-4">
      <div className="flex items-center justify-between border-b border-[#161a29] pb-3">
        <div className="flex items-center gap-2">
          <Sliders className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold text-slate-100">
            DETERMINISTIC RISK INDEX
          </h3>
        </div>
        <span className="font-mono text-xs text-slate-400">
          Not a Probability — Transparent Product Index
        </span>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
        {/* Left: Big Score Meter */}
        <div className="md:col-span-1 flex flex-col items-center justify-center rounded border border-[#1e2438] bg-[#121624] p-4 text-center">
          <div className="text-4xl font-extrabold font-mono text-rose-400 tracking-tight">
            {riskIndex}
            <span className="text-lg text-slate-500 font-normal">/100</span>
          </div>
          <div className="mt-1 font-mono text-xs uppercase font-semibold text-rose-300">
            HIGH RISK TIER
          </div>
          <div className="mt-3 w-full bg-[#1e2438] rounded-full h-2 overflow-hidden">
            <div
              className="bg-rose-500 h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, riskIndex))}%` }}
            />
          </div>
        </div>

        {/* Right: Component Factor Bars */}
        <div className="md:col-span-3 space-y-3">
          {factors.map((f) => (
            <div key={f.name} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-slate-200">{f.name}</span>
                  <span className="text-[10px] font-mono text-slate-400 bg-[#161b2c] px-1.5 py-0.2 rounded border border-[#1e2438]">
                    {f.weightLabel}
                  </span>
                </div>
                <span className={`font-mono font-bold ${f.textColor}`}>
                  {f.score.toFixed(2)}
                </span>
              </div>
              <div className="h-1.5 w-full bg-[#151926] rounded-full overflow-hidden">
                <div
                  className={`h-full ${f.color} rounded-full`}
                  style={{ width: `${Math.round(f.score * 100)}%` }}
                />
              </div>
              <p className="text-[10px] text-slate-400">{f.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Formula Explanation Footer */}
      <div className="mt-4 rounded border border-[#181d2f] bg-[#0a0d16] p-2 text-[11px] font-mono text-slate-400 flex items-center justify-between">
        <span>
          Formula: clamp(100 × [0.35×Signal + 0.30×Seq + 0.20×Novelty + 0.15×Anomaly])
        </span>
        <span className="text-slate-300">
          Result: {riskIndex}
        </span>
      </div>
    </div>
  );
};
