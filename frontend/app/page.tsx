"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { Sidebar } from "../components/Sidebar";
import { TopBar } from "../components/TopBar";
import { InvestigationConsole } from "../components/InvestigationConsole";
import { ReplayLab } from "../components/ReplayLab";
import { SuppressionLedger } from "../components/SuppressionLedger";
import { EvidenceDrawer } from "../components/EvidenceDrawer";
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

export default function ThreatWeaveWorkstation() {
  const [activeTab, setActiveTab] = useState<"console" | "replay" | "suppression">("console");
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // Core incident state
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [activeIncidentId, setActiveIncidentId] = useState<string | null>(null);
  const activeIncidentIdRef = useRef<string | null>(null);
  const [evidencePack, setEvidencePack] = useState<EvidencePack | null>(null);
  const [subgraph, setSubgraph] = useState<IncidentSubgraph | null>(null);
  const [suppressions, setSuppressions] = useState<SuppressionRecord[]>([]);

  // Interactive filtering & inspection state
  const [selectedStageId, setSelectedStageId] = useState<string | null>(null);
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
      // 1. Backend health
      try {
        await fetchHealth();
        setIsBackendHealthy(true);
      } catch {
        setIsBackendHealthy(false);
      }

      // 2. Fetch incidents & suppression audit log
      const [incList, supList] = await Promise.all([
        fetchIncidents(),
        fetchSuppressionRecords(),
      ]);

      setSuppressions(supList);

      if (incList.length > 0) {
        setIncidents(incList);
        const preferredIncidentId = activeIncidentIdRef.current;
        const targetId = preferredIncidentId && incList.some((i) => i.incident_id === preferredIncidentId)
          ? preferredIncidentId
          : incList[0].incident_id;
        activeIncidentIdRef.current = targetId;
        setActiveIncidentId(targetId);
        await loadIncidentDetails(targetId);
      } else {
        // Auto-seed canonical attack if database empty
        console.log("Seeding canonical attack reconstruction...");
        await runAnalysis("attack_insider_usb.jsonl");
        const refreshedList = await fetchIncidents();
        if (refreshedList.length > 0) {
          setIncidents(refreshedList);
          activeIncidentIdRef.current = refreshedList[0].incident_id;
          setActiveIncidentId(refreshedList[0].incident_id);
          await loadIncidentDetails(refreshedList[0].incident_id);
        }
      }
    } catch (err) {
      console.error("Telemetry sync error:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [loadIncidentDetails]);

  useEffect(() => {
    const initialLoad = window.setTimeout(() => {
      void loadAllData();
    }, 0);
    return () => window.clearTimeout(initialLoad);
  }, [loadAllData]);

  // Handle switching incidents
  const handleSelectIncident = (incId: string) => {
    activeIncidentIdRef.current = incId;
    setActiveIncidentId(incId);
    setSelectedStageId(null);
    setSelectedEventId(null);
    setSelectedEventItem(null);
    loadIncidentDetails(incId);
  };

  // Handle manual sync trigger
  const handleRefresh = async () => {
    setRefreshing(true);
    await loadAllData();
  };

  // Handle event inspection trigger
  const handleSelectEvent = (eventId: string) => {
    setSelectedEventId(eventId);
    if (evidencePack && evidencePack.events) {
      const match = evidencePack.events.find((e) => e.event_id === eventId);
      if (match) {
        setSelectedEventItem(match);
      }
    }
  };

  return (
    <div className="tw-app">
      <Sidebar
        activeTab={activeTab}
        onTabChange={(tab) => {
          setActiveTab(tab);
          setSelectedStageId(null);
        }}
        incidentCount={incidents.length}
        suppressionCount={suppressions.length}
      />

      <TopBar
        activeTab={activeTab}
        incidents={incidents}
        activeIncident={activeIncident}
        onSelectIncident={handleSelectIncident}
        isBackendHealthy={isBackendHealthy}
        refreshing={refreshing}
        onRefresh={handleRefresh}
      />

      <main id="main-content" tabIndex={-1} className="tw-main outline-none">
        {loading ? (
          <div role="status" className="tw-panel flex min-h-64 flex-col items-center justify-center gap-3 p-8 text-center font-mono-technical">
            <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs font-semibold text-cyan-300 tracking-wider">
              SYNCHRONIZING INCIDENT TELEMETRY // SECTOR-09…
            </p>
          </div>
        ) : activeTab === "console" ? (
          <InvestigationConsole
            activeIncident={activeIncident}
            evidencePack={evidencePack}
            subgraph={subgraph}
            selectedStageId={selectedStageId}
            selectedEventId={selectedEventId}
            onSelectStage={setSelectedStageId}
            onSelectEvent={handleSelectEvent}
          />
        ) : activeTab === "replay" ? (
          <ReplayLab onAnalysisCompleted={handleRefresh} />
        ) : (
          <SuppressionLedger suppressions={suppressions} />
        )}
      </main>

      {selectedEventItem && (
        <EvidenceDrawer
          event={selectedEventItem}
          onClose={() => {
            setSelectedEventItem(null);
            setSelectedEventId(null);
          }}
        />
      )}
    </div>
  );
}
