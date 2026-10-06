"use client";

import React, { useState, useMemo } from "react";
import { Network, ZoomIn, ZoomOut, Maximize2, Shield, User, Laptop, Globe, FileText, HardDrive, Cpu, Layers } from "lucide-react";
import { IncidentSubgraph, SubgraphNode } from "../lib/types";

interface EntityGraphProps {
  subgraph: IncidentSubgraph | null;
  onSelectEvent?: (eventId: string) => void;
}

export const EntityGraph: React.FC<EntityGraphProps> = ({ subgraph, onSelectEvent }) => {
  const [selectedNode, setSelectedNode] = useState<SubgraphNode | null>(null);
  const [filterType, setFilterType] = useState<string>("all");
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);

  // Compute 2D node layout coordinates deterministically
  const layout = useMemo(() => {
    if (!subgraph || !subgraph.nodes.length) return { nodes: [], edges: [] };

    const width = 800;
    const height = 480;
    const centerX = width / 2;
    const centerY = height / 2;

    const nodePositions: Record<string, { x: number; y: number }> = {};

    // Partition nodes by layer
    const incidentNodes = subgraph.nodes.filter((n) => n.type === "Incident");
    const stageNodes = subgraph.nodes.filter((n) => n.type === "Stage");
    const eventNodes = subgraph.nodes.filter((n) => n.type === "Event");
    const entityNodes = subgraph.nodes.filter(
      (n) => n.type !== "Incident" && n.type !== "Stage" && n.type !== "Event"
    );

    // 1. Incident in top center
    incidentNodes.forEach((n) => {
      nodePositions[n.id] = { x: centerX, y: 55 };
    });

    // 2. Stages in tier 2
    const stageCount = stageNodes.length;
    stageNodes.forEach((n, i) => {
      const step = stageCount > 1 ? (width - 240) / (stageCount - 1) : 0;
      nodePositions[n.id] = {
        x: stageCount > 1 ? 120 + i * step : centerX,
        y: 150,
      };
    });

    // 3. Evidence Events in tier 3
    const evCount = eventNodes.length;
    eventNodes.forEach((n, i) => {
      const step = evCount > 1 ? (width - 180) / (evCount - 1) : 0;
      nodePositions[n.id] = {
        x: evCount > 1 ? 90 + i * step : centerX,
        y: 270,
      };
    });

    // 4. Peripheral Entities in bottom tier / arc
    const entCount = entityNodes.length;
    entityNodes.forEach((n, i) => {
      const step = entCount > 1 ? (width - 160) / (entCount - 1) : 0;
      nodePositions[n.id] = {
        x: entCount > 1 ? 80 + i * step : centerX,
        y: 400,
      };
    });

    // Filter nodes if needed
    const visibleNodes = subgraph.nodes.filter((n) => {
      if (filterType === "all") return true;
      if (filterType === "stages") return n.type === "Stage" || n.type === "Incident";
      if (filterType === "entities") return n.type !== "Stage" && n.type !== "Event";
      return true;
    });

    const visibleNodeIds = new Set(visibleNodes.map((n) => n.id));

    const visibleEdges = subgraph.edges.filter(
      (e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)
    );

    return {
      nodes: visibleNodes.map((n) => ({
        ...n,
        pos: nodePositions[n.id] || { x: centerX, y: centerY },
      })),
      edges: visibleEdges.map((e) => ({
        ...e,
        sourcePos: nodePositions[e.source] || { x: centerX, y: centerY },
        targetPos: nodePositions[e.target] || { x: centerX, y: centerY },
      })),
    };
  }, [subgraph, filterType]);

  if (!subgraph) {
    return (
      <div className="rounded border border-[#1e2438] bg-[#0d101a] p-8 text-center text-sm text-slate-400">
        Loading entity graph telemetry...
      </div>
    );
  }

  const getNodeColor = (type: string) => {
    switch (type) {
      case "Incident":
        return { fill: "#ef4444", stroke: "#f87171", text: "text-rose-300" };
      case "Stage":
        return { fill: "#f43f5e", stroke: "#fb7185", text: "text-rose-400" };
      case "User":
        return { fill: "#06b6d4", stroke: "#22d3ee", text: "text-cyan-300" };
      case "Device":
        return { fill: "#3b82f6", stroke: "#60a5fa", text: "text-blue-300" };
      case "IP":
        return { fill: "#a855f7", stroke: "#c084fc", text: "text-purple-300" };
      case "Resource":
        return { fill: "#f59e0b", stroke: "#fbbf24", text: "text-amber-300" };
      case "RemovableDevice":
        return { fill: "#f97316", stroke: "#fb923c", text: "text-orange-300" };
      case "Application":
        return { fill: "#10b981", stroke: "#34d399", text: "text-emerald-300" };
      default:
        return { fill: "#64748b", stroke: "#94a3b8", text: "text-slate-300" };
    }
  };

  return (
    <div className="rounded border border-[#1e2438] bg-[#0d101a] p-4 flex flex-col">
      {/* Header & Controls */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b border-[#161a29] pb-3">
        <div className="flex items-center gap-2">
          <Network className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-sm font-bold text-slate-100">
            INCIDENT ENTITY GRAPH (1-HOP SUBGRAPH)
          </h3>
          <span className="font-mono text-xs text-slate-400">
            ({layout.nodes.length} nodes, {layout.edges.length} edges)
          </span>
        </div>

        {/* View filter & zoom */}
        <div className="flex items-center gap-2">
          <div className="flex items-center rounded border border-[#1e2438] bg-[#121624] p-0.5 text-xs font-mono">
            <button
              onClick={() => setFilterType("all")}
              className={`px-2 py-0.5 rounded ${
                filterType === "all" ? "bg-cyan-950 text-cyan-300" : "text-slate-400"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType("stages")}
              className={`px-2 py-0.5 rounded ${
                filterType === "stages" ? "bg-cyan-950 text-cyan-300" : "text-slate-400"
              }`}
            >
              Stages
            </button>
            <button
              onClick={() => setFilterType("entities")}
              className={`px-2 py-0.5 rounded ${
                filterType === "entities" ? "bg-cyan-950 text-cyan-300" : "text-slate-400"
              }`}
            >
              Entities
            </button>
          </div>

          <div className="flex items-center gap-1 border-l border-[#1e2438] pl-2">
            <button
              onClick={() => setZoomLevel((z) => Math.min(1.5, z + 0.1))}
              className="rounded p-1 text-slate-400 hover:text-slate-100 hover:bg-[#1e2438]"
              title="Zoom in"
            >
              <ZoomIn className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.7, z - 0.1))}
              className="rounded p-1 text-slate-400 hover:text-slate-100 hover:bg-[#1e2438]"
              title="Zoom out"
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setZoomLevel(1.0)}
              className="rounded p-1 text-slate-400 hover:text-slate-100 hover:bg-[#1e2438]"
              title="Reset zoom"
            >
              <Maximize2 className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Interactive SVG Canvas */}
      <div className="relative mt-3 h-[420px] w-full overflow-hidden rounded border border-[#161a29] bg-[#090b12]">
        <svg
          viewBox="0 0 800 480"
          className="h-full w-full select-none"
          style={{ transform: `scale(${zoomLevel})`, transformOrigin: "center center" }}
        >
          <defs>
            <marker
              id="arrow"
              viewBox="0 0 10 10"
              refX="18"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#334155" />
            </marker>
          </defs>

          {/* Edges */}
          {layout.edges.map((edge) => {
            const isHighlighted =
              selectedNode &&
              (selectedNode.id === edge.source || selectedNode.id === edge.target);

            return (
              <g key={edge.id}>
                <line
                  x1={edge.sourcePos.x}
                  y1={edge.sourcePos.y}
                  x2={edge.targetPos.x}
                  y2={edge.targetPos.y}
                  stroke={isHighlighted ? "#06b6d4" : "#1e293b"}
                  strokeWidth={isHighlighted ? 2.0 : 1.2}
                  strokeDasharray={edge.label === "BELONGS_TO" ? "3 3" : undefined}
                  markerEnd="url(#arrow)"
                />
                {/* Edge Label */}
                <text
                  x={(edge.sourcePos.x + edge.targetPos.x) / 2}
                  y={(edge.sourcePos.y + edge.targetPos.y) / 2 - 4}
                  fill="#64748b"
                  fontSize="8"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {edge.label}
                </text>
              </g>
            );
          })}

          {/* Nodes */}
          {layout.nodes.map((node) => {
            const isSelected = selectedNode?.id === node.id;
            const colors = getNodeColor(node.type);

            return (
              <g
                key={node.id}
                transform={`translate(${node.pos.x}, ${node.pos.y})`}
                onClick={() => {
                  setSelectedNode(node);
                  if (node.type === "Event" && onSelectEvent) {
                    onSelectEvent((node.data.event_id as string) || node.label.split(" ")[0]);
                  }
                }}
                className="cursor-pointer transition-transform duration-150 hover:scale-110"
              >
                <circle
                  r={isSelected ? 18 : 14}
                  fill="#0f172a"
                  stroke={isSelected ? "#22d3ee" : colors.fill}
                  strokeWidth={isSelected ? 3 : 2}
                />
                <circle
                  r={isSelected ? 7 : 5}
                  fill={colors.fill}
                />
                {/* Node Label */}
                <text
                  y={24}
                  fill={isSelected ? "#f8fafc" : "#cbd5e1"}
                  fontSize="10"
                  fontFamily="monospace"
                  fontWeight={isSelected ? "bold" : "normal"}
                  textAnchor="middle"
                >
                  {node.label.length > 20 ? node.label.slice(0, 18) + "…" : node.label}
                </text>
                <text
                  y={34}
                  fill="#64748b"
                  fontSize="8"
                  fontFamily="monospace"
                  textAnchor="middle"
                >
                  {node.type}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Selected Node Inspector Drawer Overlay */}
        {selectedNode && (
          <div className="absolute bottom-3 left-3 right-3 rounded border border-cyan-500/40 bg-[#0c101d]/95 p-3 backdrop-blur shadow-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-cyan-300">
                  {selectedNode.label}
                </span>
                <span className="rounded bg-[#182136] px-1.5 py-0.5 font-mono text-[10px] text-slate-300">
                  Type: {selectedNode.type}
                </span>
              </div>
              <p className="mt-1 font-mono text-[11px] text-slate-400">
                Node ID: {selectedNode.id}
              </p>
            </div>

            <div className="flex items-center gap-2">
              {selectedNode.type === "Event" && onSelectEvent && (
                <button
                  onClick={() =>
                    onSelectEvent(
                      (selectedNode.data.event_id as string) || selectedNode.label.split(" ")[0]
                    )
                  }
                  className="rounded bg-cyan-900/60 border border-cyan-500/40 px-2 py-1 font-mono text-[11px] text-cyan-200 hover:bg-cyan-800"
                >
                  Inspect in Evidence Drawer
                </button>
              )}
              <button
                onClick={() => setSelectedNode(null)}
                className="rounded border border-[#1e2438] bg-[#141827] px-2 py-1 font-mono text-[11px] text-slate-400 hover:text-slate-200"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap items-center gap-3 border-t border-[#161a29] pt-2 text-[11px] font-mono text-slate-400">
        <span className="font-bold text-slate-300">Legend:</span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-rose-500" /> Incident
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-rose-400" /> Stage
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-cyan-400" /> User
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-blue-500" /> Device
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-purple-500" /> IP
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-amber-500" /> Resource
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-orange-500" /> Removable USB
        </span>
      </div>
    </div>
  );
};
