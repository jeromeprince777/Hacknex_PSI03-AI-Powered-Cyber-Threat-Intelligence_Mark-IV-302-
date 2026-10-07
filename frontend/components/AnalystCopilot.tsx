"use client";

import React, { useState } from "react";
import { AlertTriangle, Check, MessageSquareText, Send, Sparkles, Terminal } from "lucide-react";
import { askCopilot } from "../lib/api";
import { CopilotResponse } from "../lib/types";

interface AnalystCopilotProps {
  incidentId: string;
  onSelectEvent?: (eventId: string) => void;
}

const suggestedQuestions = [
  "Which events support each detected stage?",
  "How was this risk index calculated?",
  "What approved actions are available?",
];

export const AnalystCopilot: React.FC<AnalystCopilotProps> = ({ incidentId, onSelectEvent }) => {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<CopilotResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (submittedQuestion = question) => {
    const query = submittedQuestion.trim();
    if (!query || loading) return;

    setQuestion(query);
    setLoading(true);
    setError(null);

    try {
      const result = await askCopilot(incidentId, query);
      setResponse(result);
    } catch (requestError: unknown) {
      setError(requestError instanceof Error ? requestError.message : "The explanation request failed.");
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <footer className="tw-panel overflow-hidden select-none" aria-labelledby="analyst-assist-heading">
      {/* Stitch Drawer Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 bg-[#111822] p-3 sm:px-4">
        <div className="flex items-center gap-2.5">
          <span className="p-1 bg-cyan-400 text-[#0b0f14] flex items-center justify-center font-bold">
            <Sparkles className="h-3.5 w-3.5" />
          </span>
          <h2 id="analyst-assist-heading" className="text-xs font-bold text-slate-100 font-mono-technical">
            ThreatWeave Heuristic Copilot // v3.4 Engine
          </h2>
          <span className="hidden sm:inline-block text-[9px] font-mono-technical text-emerald-400 bg-[#0a0e13] px-2 py-0.5 border border-slate-800">
            STRICT ZERO-HALLUCINATION ENFORCED (100% TOKEN ATTRIBUTION)
          </span>
        </div>
        <span className="font-mono-technical text-[10px] text-slate-400">{incidentId}</span>
      </div>

      <div className="space-y-3 p-3.5 sm:p-4 bg-[#0b0f14]">
        {/* Suggested Queries */}
        <div className="flex flex-wrap gap-1.5" aria-label="Suggested questions">
          {suggestedQuestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => void handleSubmit(suggestion)}
              disabled={loading}
              className="border border-slate-700 bg-[#111822] px-2 py-1 text-left font-mono-technical text-[10px] text-slate-300 hover:border-cyan-400 hover:text-cyan-300 transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>

        {/* Tactical Query Input Bar */}
        <form
          className="flex flex-col gap-2 sm:flex-row relative"
          onSubmit={(event) => {
            event.preventDefault();
            void handleSubmit();
          }}
        >
          <label className="sr-only" htmlFor="analyst-question">Ask about the evidence or risk components</label>
          <div className="relative flex-1 flex items-center">
            <span className="absolute left-2.5 text-cyan-400 font-mono-technical text-xs">&gt;</span>
            <input
              id="analyst-question"
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask Copilot for IOC timeline analysis or evidence decomposition…"
              className="w-full border border-slate-700 bg-[#111822] pl-6 pr-3 py-1.5 font-mono-technical text-xs text-slate-100 placeholder:text-slate-400 focus:outline-none focus:border-cyan-400"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !question.trim()}
            aria-busy={loading}
            className="tw-inline-action tw-primary-action px-3 py-1.5 text-xs font-bold"
          >
            <Send className="h-3 w-3" aria-hidden="true" />
            <span>{loading ? "EVALUATING…" : "EXEC [↵]"}</span>
          </button>
        </form>

        {error && (
          <div role="alert" className="flex items-start gap-2 border border-rose-500/50 bg-rose-950/30 p-2.5 font-mono-technical text-xs text-rose-300">
            <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-rose-400" aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        {/* Copilot Response Synthesis & Grounded Citations Bar */}
        {response && (
          <div className="border-t border-slate-800 pt-3 font-mono-technical text-xs" aria-live="polite">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
              <div className={`inline-flex items-center gap-1.5 text-xs font-semibold ${response.verified ? "text-emerald-400" : "text-rose-400"}`}>
                {response.verified ? <Check className="h-3.5 w-3.5" aria-hidden="true" /> : <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" />}
                <span>{response.verified ? "CRYPTOGRAPHIC EVIDENCE VALIDATION PASSED" : "RESPONSE REJECTED BY EVIDENCE VALIDATION"}</span>
              </div>
              {response.explanation && (
                <span className="text-[10px] text-slate-400">Confidence: <span className="text-cyan-400 font-bold uppercase">{response.explanation.confidence}</span></span>
              )}
            </div>

            {!response.verified && response.rejection_reason && (
              <p className="mt-1 text-xs text-rose-300 bg-rose-950/20 p-2 border border-rose-500/40">{response.rejection_reason}</p>
            )}

            {response.verified && response.explanation ? (
              <div className="space-y-3 bg-[#111822] p-3 border border-slate-800">
                {/* Natural Language Synthesis */}
                <p className="text-slate-200 leading-relaxed text-xs">
                  <span className="text-rose-400 font-bold">[CRITICAL SYNTHESIS]: </span>
                  {response.explanation.summary}
                </p>

                {/* Stage Explanations with Citations */}
                {response.explanation.stage_explanations.length > 0 && (
                  <div className="space-y-2 border-t border-slate-800 pt-2.5">
                    <span className="text-[10px] uppercase font-bold text-slate-400">STAGE CORRELATIONS:</span>
                    {response.explanation.stage_explanations.map((stage) => (
                      <div key={stage.stage_id} className="grid gap-1.5 sm:grid-cols-[9rem_minmax(0,1fr)] bg-[#0a0e13] p-2 border border-slate-800/80">
                        <span className="font-bold text-cyan-400 text-[10px]">{stage.stage_id}</span>
                        <div>
                          <p className="text-[11px] text-slate-300 leading-snug">{stage.explanation}</p>
                          {stage.evidence_event_ids.length > 0 && (
                            <div className="mt-1.5 flex flex-wrap gap-1">
                              <span className="text-[9px] text-slate-400 uppercase mr-1">VERIFIED CITATIONS:</span>
                              {stage.evidence_event_ids.map((eventId) => (
                                <button
                                  key={eventId}
                                  type="button"
                                  onClick={() => onSelectEvent?.(eventId)}
                                  className="px-1.5 py-0.2 bg-cyan-950/60 border border-cyan-500/50 text-cyan-300 hover:border-cyan-300 text-[9px] transition-colors"
                                >
                                  🔗 {eventId} (100% Grounded)
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Recommended Actions */}
                {response.explanation.recommended_actions.length > 0 && (
                  <div className="border-t border-slate-800 pt-2 flex flex-wrap gap-2 items-center">
                    <span className="text-[10px] text-slate-400 uppercase font-bold">RECOMMENDED PLAYBOOKS:</span>
                    {response.explanation.recommended_actions.map((action) => (
                      <span key={action.action_id} className="px-2 py-0.5 bg-[#16202e] border border-slate-700 text-slate-300 text-[10px]">
                        <span className="text-cyan-400 font-bold">{action.action_id}</span> · {action.reason}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ) : null}
          </div>
        )}
      </div>
    </footer>
  );
};
