"use client";

import React, { useState, useMemo } from "react";
import { Network, ZoomIn, ZoomOut, Maximize2, ShieldAlert } from "lucide-react";
import { IncidentSubgraph, SubgraphNode } from "../lib/types";

interface EntityGraphProps {
  subgraph: IncidentSubgraph | null;
  selectedStageId?: string | null;
  onSelectEvent?: (eventId: string) => void;
}

export const EntityGraph: React.FC<EntityGraphProps> = ({
  subgraph,
  selectedStageId,
  onSelectEvent,
}) => {
  const [selectedNode, setSelectedNode] = useState<SubgraphNode | null>(null);
  const [filterType, setFilterType] = useState<"all" | "stages" | "entities">("all");
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);
  const [hoveredNode, setHoveredNode] = useState<SubgraphNode | null>(null);

  // Compute 2D node layout coordinates deterministically with 2-tier staggered entity distribution
  const layout = useMemo(() => {
    if (!subgraph || !subgraph.nodes.length) return { nodes: [], edges: [] };

    const width = 1100;
    const centerX = width / 2;

    const nodePositions: Record<string, { x: number; y: number }> = {};

    // Partition nodes by layer
    const incidentNodes = subgraph.nodes.filter((n) => n.type === "Incident");
    const stageNodes = subgraph.nodes.filter((n) => n.type === "Stage");
    const eventNodes = subgraph.nodes.filter((n) => n.type === "Event");
    const entityNodes = subgraph.nodes.filter(
      (n) => n.type !== "Incident" && n.type !== "Stage" && n.type !== "Event"
    );

    // 1. Incident node in Tier 1 (top center)
    incidentNodes.forEach((n) => {
      nodePositions[n.id] = { x: centerX, y: 55 };
    });

    // 2. Stages in Tier 2
    const stageCount = stageNodes.length;
    stageNodes.forEach((n, i) => {
      const step = stageCount > 1 ? (width - 320) / (stageCount - 1) : 0;
      nodePositions[n.id] = {
        x: stageCount > 1 ? 160 + i * step : centerX,
        y: 145,
      };
    });

    // 3. Evidence Events in Tier 3
    const evCount = eventNodes.length;
    eventNodes.forEach((n, i) => {
      const step = evCount > 1 ? (width - 240) / (evCount - 1) : 0;
      nodePositions[n.id] = {
        x: evCount > 1 ? 120 + i * step : centerX,
        y: 265,
      };
    });

    // 4. Entities in Tier 4: Staggered across two alternating rows to prevent label collision
    const entCount = entityNodes.length;
    entityNodes.forEach((n, i) => {
      const step = entCount > 1 ? (width - 180) / (entCount - 1) : 0;
      const isAlt = i % 2 === 1;
      nodePositions[n.id] = {
        x: entCount > 1 ? 90 + i * step : centerX,
        y: isAlt ? 440 : 375,
      };
    });

    // Filter nodes if needed
    const visibleNodes = subgraph.nodes.filter((n) => {
      if (filterType === "all") return true;
      if (filterType === "stages") return n.type === "Stage";
      if (filterType === "entities") return n.type !== "Stage" && n.type !== "Event" && n.type !== "Incident";
      return true;
    });

    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));

    const visibleEdges = subgraph.edges.filter(
      (e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)
    );

    return {
      nodes: visibleNodes.map((n) => ({
        ...n,
        pos: nodePositions[n.id] || { x: centerX, y: 270 },
      })),
      edges: visibleEdges.map((e) => ({
        ...e,
        sourcePos: nodePositions[e.source] || { x: centerX, y: 270 },
        targetPos: nodePositions[e.target] || { x: centerX, y: 270 },
      })),
    };
  }, [subgraph, filterType]);

  // Determine which nodes belong to the selected stage
  const stageRelevantNodeIds = useMemo(() => {
    if (!selectedStageId || !subgraph) return null;
    const relevant = new Set<string>();
    relevant.add(selectedStageId);

    // Add incident nodes
    subgraph.nodes.filter((n) => n.type === "Incident").forEach((n) => relevant.add(n.id));

    // Find edges connected to this stage
    subgraph.edges.forEach((edge) => {
      if (edge.source === selectedStageId) relevant.add(edge.target);
      if (edge.target === selectedStageId) relevant.add(edge.source);
    });

    // Find entities connected to those events
    subgraph.edges.forEach((edge) => {
      if (relevant.has(edge.source)) relevant.add(edge.target);
      if (relevant.has(edge.target)) relevant.add(edge.source);
    });

    return relevant;
  }, [selectedStageId, subgraph]);

  if (!subgraph || !subgraph.nodes.length) {
    return (
      <div className="flex h-64 items-center justify-center p-6 text-xs font-mono-technical text-slate-400">
        No graph topological relationships available for this incident.
      </div>
    );
  }

  const getNodeColor = (type: string) => {
    switch (type) {
      case "Incident":
        return { fill: "#f43f5e", stroke: "#fb7185", ring: "rgba(244, 63, 94, 0.4)" };
      case "Stage":
        return { fill: "#f59e0b", stroke: "#fcd34d", ring: "rgba(245, 158, 11, 0.3)" };
      case "Event":
        return { fill: "#06b6d4", stroke: "#38bdf8", ring: "rgba(6, 182, 212, 0.3)" };
      case "User":
        return { fill: "#818cf8", stroke: "#a5b4fc", ring: "rgba(129, 140, 248, 0.3)" };
      case "Device":
        return { fill: "#38bdf8", stroke: "#7dd3fc", ring: "rgba(56, 189, 248, 0.3)" };
      case "IP":
        return { fill: "#c084fc", stroke: "#e9d5ff", ring: "rgba(192, 132, 252, 0.3)" };
      case "Resource":
        return { fill: "#fb923c", stroke: "#fdba74", ring: "rgba(251, 146, 60, 0.3)" };
      case "RemovableDevice":
        return { fill: "#f43f5e", stroke: "#fda4af", ring: "rgba(244, 63, 94, 0.35)" };
      case "Application":
        return { fill: "#34d399", stroke: "#6ee7b7", ring: "rgba(52, 211, 153, 0.3)" };
      default:
        return { fill: "#94a3b8", stroke: "#cbd5e1", ring: "rgba(148, 163, 184, 0.3)" };
    }
  };

  return (
    <section aria-label="Incident Entity Graph" className="flex flex-col text-slate-200 select-none">
      {/* Header and Functional Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center gap-2">
          <Network className="h-4 w-4 text-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wide text-slate-100 font-mono-technical">
            CORRELATION RADAR
          </h3>
          <span className="font-mono-technical text-[10px] text-slate-400">
            {layout.nodes.length} NODES · {layout.edges.length} BUS EDGES
          </span>
        </div>

        {/* View filters and Zoom */}
        <div className="flex items-center gap-2">
          <div className="flex items-center border border-slate-800 bg-[#0a0e13] p-0.5 text-xs font-mono-technical">
            <button
              type="button"
              aria-pressed={filterType === "all"}
              onClick={() => setFilterType("all")}
              className={`px-2 py-0.5 text-[10px] font-bold ${
                filterType === "all" ? "bg-cyan-400 text-[#0b0f14]" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              ALL
            </button>
            <button
              type="button"
              aria-pressed={filterType === "stages"}
              onClick={() => setFilterType("stages")}
              className={`px-2 py-0.5 text-[10px] font-bold ${
                filterType === "stages" ? "bg-cyan-400 text-[#0b0f14]" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              STAGES
            </button>
            <button
              type="button"
              aria-pressed={filterType === "entities"}
              onClick={() => setFilterType("entities")}
              className={`px-2 py-0.5 text-[10px] font-bold ${
                filterType === "entities" ? "bg-cyan-400 text-[#0b0f14]" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              ENTITIES
            </button>
          </div>

          <div className="flex items-center gap-1 border-l border-slate-800 pl-2">
            <button
              type="button"
              onClick={() => setZoomLevel((z) => Math.min(1.5, z + 0.1))}
              className="p-1 text-slate-400 hover:bg-[#16202e] hover:text-cyan-300"
              title="Zoom in"
              aria-label="Zoom in"
            >
              <ZoomIn className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setZoomLevel((z) => Math.max(0.7, z - 0.1))}
              className="p-1 text-slate-400 hover:bg-[#16202e] hover:text-cyan-300"
              title="Zoom out"
              aria-label="Zoom out"
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setZoomLevel(1.0)}
              className="p-1 text-slate-400 hover:bg-[#16202e] hover:text-cyan-300"
              title="Reset zoom"
              aria-label="Reset zoom"
            >
              <Maximize2 className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* SVG Canvas Area with Radar Background */}
      <div className="relative mt-3 h-[380px] w-full overflow-auto border border-slate-800 bg-[#080c10]">
        {/* Background Radar Grid Pattern */}
        <div className="absolute inset-0 pointer-events-none opacity-20">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <radialGradient id="radarGrid" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.25" />
                <stop offset="100%" stopColor="#080c10" stopOpacity="0" />
              </radialGradient>
            </defs>
            <circle cx="50%" cy="50%" r="90" fill="url(#radarGrid)" stroke="#1e293b" strokeWidth="0.8" />
            <circle cx="50%" cy="50%" r="180" fill="none" stroke="#1e293b" strokeWidth="0.8" />
            <line x1="50%" y1="0" x2="50%" y2="100%" stroke="#1e293b" strokeWidth="0.5" />
            <line x1="0" y1="50%" x2="100%" y2="50%" stroke="#1e293b" strokeWidth="0.5" />
          </svg>
        </div>

        <svg
          viewBox="0 0 1100 520"
          className="h-full min-h-[380px] min-w-[760px] w-full max-w-none select-none relative z-10"
          style={{ transform: `scale(${zoomLevel})`, transformOrigin: "center center" }}
        >
          <defs>
            <marker
              id="arrow-cyan"
              viewBox="0 0 10 10"
              refX="18"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#06b6d4" />
            </marker>
            <marker
              id="arrow-rose"
              viewBox="0 0 10 10"
              refX="18"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#f43f5e" />
            </marker>
          </defs>

          {/* Graph Connecting Edges with Bus Flow */}
          {layout.edges.map((edge) => {
            const isRelevant = stageRelevantNodeIds
              ? stageRelevantNodeIds.has(edge.source) && stageRelevantNodeIds.has(edge.target)
              : true;
            const opacity = stageRelevantNodeIds ? (isRelevant ? 0.9 : 0.15) : 0.7;
            const isCriticalEdge = edge.label.toLowerCase().includes("exfil") || edge.label.toLowerCase().includes("compromise");

            return (
              <g key={`${edge.source}-${edge.target}-${edge.label}`} opacity={opacity}>
                <line
                  x1={edge.sourcePos.x}
                  y1={edge.sourcePos.y}
                  x2={edge.targetPos.x}
                  y2={edge.targetPos.y}
                  stroke={isCriticalEdge ? "#f43f5e" : "#06b6d4"}
                  strokeWidth={isCriticalEdge ? 2 : 1.2}
                  className="bus-flow"
                  markerEnd={isCriticalEdge ? "url(#arrow-rose)" : "url(#arrow-cyan)"}
                />
                <text
                  x={(edge.sourcePos.x + edge.targetPos.x) / 2}
                  y={(edge.sourcePos.y + edge.targetPos.y) / 2 - 4}
                  fill={isCriticalEdge ? "#f43f5e" : "#94a3b8"}
                  fontSize="8"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {edge.label}
                </text>
              </g>
            );
          })}

          {/* Graph Nodes */}
          {layout.nodes.map((node) => {
            const isSelected = selectedNode?.id === node.id;
            const isNodeInStage = stageRelevantNodeIds ? stageRelevantNodeIds.has(node.id) : true;
            const colors = getNodeColor(node.type);
            const opacity = stageRelevantNodeIds ? (isNodeInStage ? 1.0 : 0.2) : 1.0;
            const isCompromised = node.type === "RemovableDevice" || node.id.includes("workstation") || node.id.includes("198.51.100.88");

            return (
              <g
                key={node.id}
                transform={`translate(${node.pos.x}, ${node.pos.y})`}
                opacity={opacity}
                onClick={() => {
                  setSelectedNode(node);
                  if (node.type === "Event" && onSelectEvent) {
                    const eventId = node.data.event_id;
                    if (typeof eventId === "string") onSelectEvent(eventId);
                  }
                }}
                onMouseEnter={() => setHoveredNode(node)}
                onMouseLeave={() => setHoveredNode(null)}
                className="cursor-pointer"
                role="button"
                tabIndex={0}
                aria-pressed={isSelected}
              >
                {/* Glow ring for compromised/selected nodes */}
                {(isSelected || isCompromised) && (
                  <circle
                    r={isSelected ? 20 : 16}
                    fill="none"
                    stroke={colors.fill}
                    strokeWidth={1.5}
                    className="tactical-pulse"
                    opacity={0.6}
                  />
                )}

                {/* Outer ring */}
                <circle
                  r={isSelected ? 15 : 12}
                  fill="#0b0f14"
                  stroke={isSelected ? "#38bdf8" : colors.stroke}
                  strokeWidth={isSelected ? 2.5 : 1.5}
                />

                {/* Core dot */}
                <circle
                  r={isSelected ? 6 : 4}
                  fill={colors.fill}
                />

                {/* Node Label Text */}
                <text
                  y={22}
                  fill={isSelected ? "#38bdf8" : "#f1f5f9"}
                  fontSize="9.5"
                  fontFamily="monospace"
                  fontWeight={isSelected ? "bold" : "normal"}
                  textAnchor="middle"
                >
                  {node.label.length > 20 ? node.label.slice(0, 18) + "…" : node.label}
                </text>

                {/* Node Type Label */}
                <text
                  y={32}
                  fill="#94a3b8"
                  fontSize="7.5"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {node.type.toUpperCase()}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Node Hover Inspector Overlay */}
        {(hoveredNode || selectedNode) && (
          <div className="pointer-events-none absolute bottom-3 left-3 border border-slate-800 bg-[#0a0e13]/90 backdrop-blur-md p-2.5 font-mono-technical text-xs shadow-lg z-20">
            <div className="flex items-center gap-2">
              <span className="font-bold text-cyan-300">{(hoveredNode || selectedNode)?.label}</span>
              <span className="border border-slate-700 bg-[#16202e] px-1.5 py-0.5 text-[9px] text-slate-300">
                {(hoveredNode || selectedNode)?.type}
              </span>
            </div>
            <div className="mt-1 break-all text-[10px] text-slate-400">ID: {(hoveredNode || selectedNode)?.id}</div>
          </div>
        )}
      </div>

      {/* Semantic Legend Strip */}
      <div className="mt-3 flex flex-wrap items-center gap-3 border-t border-slate-800 pt-3 text-[10px] font-mono-technical text-slate-400">
        <span>ENTITY SEMAPHORES:</span>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 bg-rose-500 rounded-none inline-block" />
          <span>INCIDENT / EXFIL</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 bg-cyan-400 rounded-none inline-block" />
          <span>EVIDENCE EVENT</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 bg-indigo-400 rounded-none inline-block" />
          <span>USER IDENTITY</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 bg-sky-400 rounded-none inline-block" />
          <span>WORKSTATION</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 bg-purple-400 rounded-none inline-block" />
          <span>NETWORK IP</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 bg-emerald-400 rounded-none inline-block" />
          <span>PROCESS / APP</span>
        </div>
      </div>
    </section>
  );
};
