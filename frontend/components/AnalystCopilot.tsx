"use client";

import React, { useState } from "react";
import { Bot, Send, ShieldCheck, ShieldAlert, Sparkles, CheckCircle2, AlertOctagon, Terminal } from "lucide-react";
import { askCopilot } from "../lib/api";
import { CopilotResponse } from "../lib/types";

interface AnalystCopilotProps {
  incidentId: string;
}

export const AnalystCopilot: React.FC<AnalystCopilotProps> = ({ incidentId }) => {
  const [question, setQuestion] = useState<string>("Why is this incident high risk?");
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<CopilotResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Evaluator demonstration injection switches
  const [injectFakeEvent, setInjectFakeEvent] = useState<boolean>(false);
  const [injectFakeAction, setInjectFakeAction] = useState<boolean>(false);

  const handleSubmit = async (q?: string) => {
    const query = q || question;
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await askCopilot(
        incidentId,
        query,
        injectFakeEvent ? "evt-fake-9999" : undefined,
        injectFakeAction ? "nuke-all-firewalls" : undefined
      );
      setResponse(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to obtain explanation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded border border-[#1e2438] bg-[#0d101a] p-4 space-y-4">
      {/* Title & Status */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-[#161a29] pb-3">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold text-slate-100">
            ANALYST COPILOT & ANTI-HALLUCINATION VERIFIER
          </h3>
        </div>
        <span className="font-mono text-[11px] text-slate-400">
          Bounded Evidence Pack Grounding — No Open DB Queries
        </span>
      </div>

      {/* Preset Query Chips */}
      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="text-slate-400 text-[11px] font-mono">Suggested:</span>
        <button
          onClick={() => {
            setQuestion("Why is this incident high risk?");
            handleSubmit("Why is this incident high risk?");
          }}
          className="rounded border border-[#1e2438] bg-[#121625] px-2.5 py-1 text-slate-300 hover:border-cyan-500/40 hover:text-cyan-300 transition"
        >
          Why is this incident high risk?
        </button>
        <button
          onClick={() => {
            setQuestion("What actions should the IR team take?");
            handleSubmit("What actions should the IR team take?");
          }}
          className="rounded border border-[#1e2438] bg-[#121625] px-2.5 py-1 text-slate-300 hover:border-cyan-500/40 hover:text-cyan-300 transition"
        >
          What actions should the IR team take?
        </button>
      </div>

      {/* Evaluator Demonstration Toggles (Negative Testing) */}
      <div className="rounded border border-[#1e2438] bg-[#0a0d16] p-3 text-xs space-y-2">
        <div className="flex items-center justify-between">
          <span className="font-mono text-[11px] font-bold text-slate-300">
            EVALUATOR NEGATIVE TESTING CONTROLS:
          </span>
          <span className="text-[10px] text-slate-400 font-mono">
            Simulate model hallucination to test verifier
          </span>
        </div>
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center gap-2 cursor-pointer text-slate-300">
            <input
              type="checkbox"
              checked={injectFakeEvent}
              onChange={(e) => setInjectFakeEvent(e.target.checked)}
              className="rounded bg-[#161b2c] border-[#222a42] text-rose-500 focus:ring-0"
            />
            <span className={injectFakeEvent ? "text-rose-400 font-semibold" : ""}>
              Inject Hallucinated Event ID (evt-fake-9999)
            </span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer text-slate-300">
            <input
              type="checkbox"
              checked={injectFakeAction}
              onChange={(e) => setInjectFakeAction(e.target.checked)}
              className="rounded bg-[#161b2c] border-[#222a42] text-rose-500 focus:ring-0"
            />
            <span className={injectFakeAction ? "text-rose-400 font-semibold" : ""}>
              Inject Unauthorized Action (nuke-all-firewalls)
            </span>
          </label>
        </div>
      </div>

      {/* Question Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        className="flex gap-2"
      >
        <div className="relative flex-1">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask Copilot regarding incident telemetry or root cause..."
            className="w-full rounded border border-[#1e2438] bg-[#121625] px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="flex items-center gap-1.5 rounded bg-cyan-600 hover:bg-cyan-500 px-4 py-2 font-mono text-xs font-semibold text-slate-900 transition disabled:opacity-50"
        >
          {loading ? (
            <Sparkles className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Send className="h-3.5 w-3.5" />
          )}
          <span>{loading ? "Analyzing..." : "Ask"}</span>
        </button>
      </form>

      {/* Error state */}
      {error && (
        <div className="rounded border border-rose-500/30 bg-rose-950/30 p-3 text-xs text-rose-300">
          {error}
        </div>
      )}

      {/* Response Box with Real-time Verification Badge */}
      {response && (
        <div className="space-y-3 pt-2">
          {/* Verification Banner */}
          {response.verified ? (
            <div className="flex items-center gap-2 rounded border border-emerald-500/40 bg-emerald-950/30 px-3 py-2 text-xs font-mono text-emerald-300">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
              <div>
                <strong>VERIFIED BY ANTI-HALLUCINATION GUARD:</strong> All cited event IDs, stage IDs, and response actions match the verified evidence pack 100%.
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 rounded border border-rose-500/50 bg-rose-950/40 px-3 py-2 text-xs font-mono text-rose-300">
              <AlertOctagon className="h-4 w-4 text-rose-400 shrink-0" />
              <div>
                <strong>AI EXPLANATION REJECTED:</strong> Evidence reference validation failed.
                <div className="mt-1 text-[11px] text-rose-400/90">
                  Reason: {response.rejection_reason}
                </div>
              </div>
            </div>
          )}

          {/* Explanation Content (Only shown if verified) */}
          {response.verified && response.explanation && (
            <div className="rounded border border-[#1e2438] bg-[#111422] p-4 space-y-3 font-sans text-xs">
              <div>
                <span className="font-mono text-[10px] text-cyan-400 font-bold uppercase tracking-wider block">
                  INCIDENT NARRATIVE
                </span>
                <p className="mt-1 text-slate-200 leading-relaxed font-sans">
                  {response.explanation.summary}
                </p>
              </div>

              {/* Stage Explanations */}
              <div className="space-y-2 border-t border-[#1a1f33] pt-3">
                <span className="font-mono text-[10px] text-slate-400 font-bold uppercase tracking-wider block">
                  STAGE-BY-STAGE EVIDENCE PROOF
                </span>
                {response.explanation.stage_explanations.map((stg) => (
                  <div key={stg.stage_id} className="rounded bg-[#0c0f1a] p-2.5 border border-[#1e2438]">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[11px] font-bold text-cyan-300 uppercase">
                        {stg.stage_id}
                      </span>
                      <div className="flex gap-1">
                        {stg.evidence_event_ids.map((eid) => (
                          <span
                            key={eid}
                            className="rounded bg-cyan-950 px-1.5 py-0.2 font-mono text-[10px] text-cyan-300 border border-cyan-500/30"
                          >
                            {eid}
                          </span>
                        ))}
                      </div>
                    </div>
                    <p className="mt-1 text-slate-300 text-[11px] font-sans">
                      {stg.explanation}
                    </p>
                  </div>
                ))}
              </div>

              {/* Limitations note */}
              {response.explanation.limitations && (
                <div className="border-t border-[#1a1f33] pt-2 text-[10px] font-mono text-slate-400">
                  <span className="font-bold text-slate-400">Model Bounds: </span>
                  {response.explanation.limitations.join(" • ")}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
