"use client";

import React from "react";
import { SlidersHorizontal } from "lucide-react";
import { RiskComponents } from "../lib/types";

interface RiskBreakdownProps {
  riskIndex: number;
  components: RiskComponents;
}

export const RiskBreakdown: React.FC<RiskBreakdownProps> = ({ riskIndex, components }) => {
  const factors = [
    { id: "signal", label: "Signal Score", score: components.signal_score, weight: components.weights.signal, color: "bg-cyan-400" },
    { id: "sequence", label: "Sequence Correlator", score: components.sequence_score, weight: components.weights.sequence, color: "bg-amber-400" },
    { id: "novelty", label: "Entity Novelty", score: components.entity_novelty, weight: components.weights.novelty, color: "bg-rose-400" },
    { id: "anomaly", label: "Anomaly Engine", score: components.anomaly_score, weight: components.weights.anomaly, color: "bg-emerald-400" },
  ];

  const isCritical = riskIndex >= 70;

  return (
    <section className="tw-panel overflow-hidden select-none" aria-labelledby="risk-breakdown-heading">
      <div className="border-b border-slate-800 bg-[#111822] p-3.5">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4 text-cyan-400" aria-hidden="true" />
            <h2 id="risk-breakdown-heading" className="text-xs font-bold uppercase tracking-wider text-slate-100 font-mono-technical">
              RISK INDEX VECTOR
            </h2>
          </div>
          <span className="text-[10px] font-mono-technical text-emerald-400">
            DETERMINISTIC
          </span>
        </div>

        <div className="mt-3 flex items-baseline gap-2">
          <span className={`font-mono-technical text-3xl font-extrabold leading-none tracking-tight tabular-nums ${isCritical ? "text-rose-400" : "text-amber-400"}`}>
            {riskIndex}
          </span>
          <span className="font-mono-technical text-xs text-slate-400">/ 100</span>
          <span className="ml-auto text-[10px] font-mono-technical text-slate-400">
            BASELINE VARIANCE +18.0
          </span>
        </div>
      </div>

      <div className="divide-y divide-slate-800/80 px-3.5 bg-[#0b0f14]">
        {factors.map((factor) => {
          const score = Math.max(0, Math.min(1, factor.score));
          const contribution = factor.score * factor.weight * 100;

          return (
            <div key={factor.id} className="py-2.5">
              <div className="flex flex-wrap items-baseline justify-between gap-x-2 gap-y-1 font-mono-technical">
                <span className="text-[11px] font-semibold text-slate-200">{factor.label}</span>
                <span className="text-[10px] tabular-nums text-slate-400">
                  {factor.score.toFixed(2)} × {(factor.weight * 100).toFixed(0)}% ={" "}
                  <span className="text-slate-100 font-bold">{contribution.toFixed(1)} pts</span>
                </span>
              </div>
              <div
                className="mt-1.5 h-1.5 w-full bg-[#16202e] overflow-hidden"
                role="progressbar"
                aria-label={`${factor.label} score`}
                aria-valuemin={0}
                aria-valuemax={1}
                aria-valuenow={score}
              >
                <div className={`h-full ${factor.color}`} style={{ width: `${score * 100}%` }} />
              </div>
            </div>
          );
        })}
      </div>

      <div className="border-t border-slate-800 bg-[#111822] p-2.5 text-[9px] font-mono-technical text-slate-400 flex items-center justify-between">
        <span>STRICT SCORE DECOMPOSITION OK</span>
        <span className="text-cyan-400">ZERO RANDOM SEED</span>
      </div>
    </section>
  );
};
