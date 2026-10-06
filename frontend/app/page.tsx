"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Navbar } from "../components/Navbar";
import { IncidentHeader } from "../components/IncidentHeader";
import { RiskBreakdown } from "../components/RiskBreakdown";
import { AttackTimeline } from "../components/AttackTimeline";
import { AttackStages } from "../components/AttackStages";
import { EntityGraph } from "../components/EntityGraph";
import { EvidenceDrawer } from "../components/EvidenceDrawer";
import { ResponseActions } from "../components/ResponseActions";
import { AnalystCopilot } from "../components/AnalystCopilot";
import { DatasetReplay } from "../components/DatasetReplay";
import { SuppressionLog } from "../components/SuppressionLog";
import {
  fetchHealth,
  fetchIncidents,
  fetchIncidentEvidence,
  fetchIncidentGraph,
  fetchSuppressionRecords,
  runAnalysis,
} from "../lib/api";
import {
  Incident,
  EvidencePack,
  IncidentSubgraph,
  EvidenceItem,
  SuppressionRecord,
} from "../lib/types";

export default function ThreatWeaveDashboard() {
  const [activeTab, setActiveTab] = useState<"console" | "replay" | "suppression">("console");
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // Core incident data
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [activeIncidentId, setActiveIncidentId] = useState<string | null>(null);
  const [evidencePack, setEvidencePack] = useState<EvidencePack | null>(null);
  const [subgraph, setSubgraph] = useState<IncidentSubgraph | null>(null);
  const [suppressions, setSuppressions] = useState<SuppressionRecord[]>([]);

  // Drawer inspection state
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedEventItem, setSelectedEventItem] = useState<EvidenceItem | null>(null);

  const activeIncident = incidents.find((i) => i.incident_id === activeIncidentId) || incidents[0] || null;

  // Load telemetry for active incident
  const loadIncidentDetails = useCallback(async (incId: string) => {
    try {
      const [evPack, graphData] = await Promise.all([
        fetchIncidentEvidence(incId),
        fetchIncidentGraph(incId),
      ]);
      setEvidencePack(evPack);
      setSubgraph(graphData);
    } catch (err) {
      console.error("Failed to load incident detail:", err);
    }
  }, []);

  // Main data synchronizer
  const loadAllData = useCallback(async () => {
    try {
      // 1. Health check
      try {
        await fetchHealth();
        setIsBackendHealthy(true);
      } catch {
        setIsBackendHealthy(false);
      }

      // 2. Fetch incidents & suppressions
      const [incList, supList] = await Promise.all([
        fetchIncidents(),
        fetchSuppressionRecords(),
      ]);

      setSuppressions(supList);

      if (incList.length > 0) {
        setIncidents(incList);
        const targetId = activeIncidentId && incList.some((i) => i.incident_id === activeIncidentId)
          ? activeIncidentId
          : incList[0].incident_id;
        setActiveIncidentId(targetId);
        await loadIncidentDetails(targetId);
      } else {
        // Auto-seed canonical attack if database empty
        console.log("No incidents found on startup, auto-seeding canonical attack...");
        await runAnalysis("attack_insider_usb.jsonl");
        const refreshedList = await fetchIncidents();
        if (refreshedList.length > 0) {
          setIncidents(refreshedList);
          setActiveIncidentId(refreshedList[0].incident_id);
          await loadIncidentDetails(refreshedList[0].incident_id);
        }
      }
    } catch (err) {
      console.error("Initialization error:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [activeIncidentId, loadIncidentDetails]);

  useEffect(() => {
    loadAllData();
  }, [loadAllData]);

  // Handle incident switch
  const handleSelectIncident = async (id: string) => {
    setActiveIncidentId(id);
    setSelectedEventId(null);
    setSelectedEventItem(null);
    await loadIncidentDetails(id);
  };

  // Handle event inspection click
  const handleSelectEvent = (eventId: string) => {
    setSelectedEventId(eventId);
    if (evidencePack) {
      const found = evidencePack.events.find((e) => e.event_id === eventId);
      if (found) {
        setSelectedEventItem(found);
      } else {
        // Fallback placeholder item
        setSelectedEventItem({
          event_id: eventId,
          timestamp: new Date().toISOString(),
          source: "telemetry",
          raw: {},
          normalized: { event_id: eventId },
          detectors: [],
          linked_entities: [],
        });
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#08090e] text-[#f1f5f9] flex flex-col">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isBackendHealthy={isBackendHealthy}
        onRefresh={() => {
          setRefreshing(true);
          loadAllData();
        }}
        refreshing={refreshing}
      />

      {/* Main Content Area */}
      <main className="flex-1 p-4 md:p-6 max-w-[1600px] w-full mx-auto">
        {loading ? (
          <div className="flex h-96 items-center justify-center font-mono text-sm text-cyan-400">
            Initializing ThreatWeave Investigation Engine...
          </div>
        ) : (
          <>
            {/* VIEW 1: SOC INVESTIGATION CONSOLE */}
            {activeTab === "console" && (
              <div className="space-y-5">
                {/* 1. Header with Case Identity & Entity Binding */}
                <IncidentHeader
                  incidents={incidents}
                  activeIncident={activeIncident}
                  onSelectIncident={handleSelectIncident}
                />

                {/* 2. Risk Index & 4-Factor Breakdown */}
                {activeIncident && (
                  <RiskBreakdown
                    riskIndex={activeIncident.risk_index}
                    components={activeIncident.risk_components}
                  />
                )}

                {/* 3. Attack Stages & Reconstructed Timeline */}
                {evidencePack && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                    {/* Attack Stages */}
                    <AttackStages
                      stages={evidencePack.stages}
                      onSelectEvent={handleSelectEvent}
                    />

                    {/* Timeline */}
                    <AttackTimeline
                      timeline={evidencePack.timeline}
                      selectedEventId={selectedEventId}
                      onSelectEvent={handleSelectEvent}
                    />
                  </div>
                )}

                {/* 4. Entity Graph (1-Hop Subgraph) */}
                <EntityGraph
                  subgraph={subgraph}
                  onSelectEvent={handleSelectEvent}
                />

                {/* 5. Approved Response Actions */}
                {evidencePack && (
                  <ResponseActions actions={evidencePack.approved_actions} />
                )}

                {/* 6. AI Analyst Copilot with Verification Seal */}
                {activeIncident && (
                  <AnalystCopilot incidentId={activeIncident.incident_id} />
                )}
              </div>
            )}

            {/* VIEW 2: DATASET REPLAY & BENCHMARK */}
            {activeTab === "replay" && (
              <DatasetReplay
                onAnalysisCompleted={() => {
                  loadAllData();
                }}
              />
            )}

            {/* VIEW 3: SUPPRESSION AUDIT LOG */}
            {activeTab === "suppression" && (
              <SuppressionLog suppressions={suppressions} />
            )}
          </>
        )}
      </main>

      {/* Slide-over Evidence Telemetry Drawer */}
      {selectedEventItem && (
        <EvidenceDrawer
          event={selectedEventItem}
          onClose={() => {
            setSelectedEventId(null);
            setSelectedEventItem(null);
          }}
        />
      )}
    </div>
  );
}
