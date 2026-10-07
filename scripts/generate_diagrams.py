"""
Generate clean, professional SVG diagrams for ThreatWeave repository.
Dark modern SOC aesthetic with cyan, emerald, amber, and rose accents.
"""

import os

BASE_DIR = r"c:\Users\ffgam\OneDrive\Desktop\Hacknex"
DIAGRAMS_DIR = os.path.join(BASE_DIR, "assets", "diagrams")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

# 1. ARCHITECTURE OVERVIEW SVG
SVG_ARCHITECTURE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080c14" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    <linearGradient id="cyanCard" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#06b6d4" flood-opacity="0.25"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#06b6d4" />
    </marker>
    <marker id="arrow-emerald" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#10b981" />
    </marker>
    <marker id="arrow-rose" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#f43f5e" />
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1200" height="680" fill="url(#bg)" rx="16" />

  <!-- Header -->
  <text x="60" y="55" font-family="Segoe UI, Inter, sans-serif" font-size="14" font-weight="bold" fill="#06b6d4" letter-spacing="2">THREATWEAVE ARCHITECTURE // HNX26PSI03</text>
  <text x="60" y="90" font-family="Segoe UI, Inter, sans-serif" font-size="26" font-weight="bold" fill="#f8fafc">End-to-End Threat Intelligence &amp; Correlation Pipeline</text>

  <!-- STAGE 1: INGESTION -->
  <g transform="translate(60, 130)">
    <rect width="320" height="150" rx="12" fill="url(#cyanCard)" stroke="#1e293b" stroke-width="2" filter="url(#glow)"/>
    <rect x="0" y="0" width="320" height="6" fill="#3b82f6" rx="3"/>
    <text x="24" y="38" font-family="Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#38bdf8">1. Multi-Source Ingestion</text>
    <text x="24" y="68" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Windows EventLog, VPN, EDR, NetFlow</text>
    <text x="24" y="92" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Pydantic CanonicalEvent-v1 Schema</text>
    <text x="24" y="116" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Automated Malformed Quarantine</text>
  </g>

  <!-- ARROW 1 -> 2 -->
  <path d="M 380 205 L 435 205" fill="none" stroke="#06b6d4" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- STAGE 2: ATOMIC DETECTORS -->
  <g transform="translate(440, 130)">
    <rect width="320" height="150" rx="12" fill="url(#cyanCard)" stroke="#1e293b" stroke-width="2" filter="url(#glow)"/>
    <rect x="0" y="0" width="320" height="6" fill="#06b6d4" rx="3"/>
    <text x="24" y="38" font-family="Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#06b6d4">2. Signal Detection</text>
    <text x="24" y="68" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Declarative YAML Detection Rules</text>
    <text x="24" y="92" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Entity Novelty Baseline Modeling</text>
    <text x="24" y="116" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Base Severity Weight Assignment</text>
  </g>

  <!-- ARROW 2 -> 3 -->
  <path d="M 760 205 L 815 205" fill="none" stroke="#06b6d4" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- STAGE 3: TEMPORAL CORRELATOR -->
  <g transform="translate(820, 130)">
    <rect width="320" height="150" rx="12" fill="url(#cyanCard)" stroke="#1e293b" stroke-width="2" filter="url(#glow)"/>
    <rect x="0" y="0" width="320" height="6" fill="#a855f7" rx="3"/>
    <text x="24" y="38" font-family="Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#c084fc">3. Temporal Correlator</text>
    <text x="24" y="68" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Sliding 3600s Actor Windows</text>
    <text x="24" y="92" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Actor Clustering (user_id / device_id)</text>
    <text x="24" y="116" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Strict Monotonic Timestamp Validation</text>
  </g>

  <!-- ARROW 3 DOWN TO GATE -->
  <path d="M 980 280 L 980 340 L 780 340" fill="none" stroke="#06b6d4" stroke-width="2.5" marker-end="url(#arrow)" />

  <!-- PROMOTION GATE (DECISION DIAMOND / CARD) -->
  <g transform="translate(440, 320)">
    <rect width="320" height="140" rx="12" fill="#1e1b4b" stroke="#6366f1" stroke-width="2.5" />
    <text x="30" y="36" font-family="Segoe UI, sans-serif" font-size="15" font-weight="bold" fill="#a5b4fc">RULE 1: PROMOTION GATE</text>
    <text x="30" y="66" font-family="Segoe UI, sans-serif" font-size="13" fill="#e0e7ff">• Requires ≥ 3 Telemetry Events</text>
    <text x="30" y="90" font-family="Segoe UI, sans-serif" font-size="13" fill="#e0e7ff">• Requires ≥ 2 Discrete Attack Stages</text>
    <text x="30" y="114" font-family="Segoe UI, sans-serif" font-size="13" fill="#e0e7ff">• Monotonic Chronological Order</text>
  </g>

  <!-- GATE BRANCH LEFT -> SUPPRESSION (FAIL) -->
  <path d="M 440 390 L 380 390 L 380 490 L 380 515" fill="none" stroke="#f43f5e" stroke-width="2.5" marker-end="url(#arrow-rose)" />
  <text x="390" y="440" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#f43f5e">FAIL (&lt;2 stages)</text>

  <!-- SUPPRESSION LEDGER CARD -->
  <g transform="translate(60, 480)">
    <rect width="320" height="150" rx="12" fill="url(#cyanCard)" stroke="#881337" stroke-width="2" />
    <rect x="0" y="0" width="320" height="6" fill="#f43f5e" rx="3"/>
    <text x="24" y="38" font-family="Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#fb7185">Suppression Audit Ledger</text>
    <text x="24" y="68" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Routine Admin Activity Suppressed</text>
    <text x="24" y="92" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Reason: INSUFFICIENT_CHAIN</text>
    <text x="24" y="116" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Zero False Alarms in SOC Queue</text>
  </g>

  <!-- GATE BRANCH RIGHT -> PROMOTION (PASS) -->
  <path d="M 760 390 L 820 390 L 820 490 L 820 515" fill="none" stroke="#10b981" stroke-width="2.5" marker-end="url(#arrow-emerald)" />
  <text x="830" y="440" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#10b981">PASS (≥2 stages)</text>

  <!-- PROMOTED INCIDENT & COPILOT -->
  <g transform="translate(440, 480)">
    <rect width="320" height="150" rx="12" fill="url(#cyanCard)" stroke="#1e293b" stroke-width="2" />
    <rect x="0" y="0" width="320" height="6" fill="#f59e0b" rx="3"/>
    <text x="24" y="38" font-family="Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#fbbf24">4. 4-Factor Risk Engine</text>
    <text x="24" y="68" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• 35% Signal Severity (0.71)</text>
    <text x="24" y="92" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• 30% Sequence Consistency (1.00)</text>
    <text x="24" y="116" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• 20% Novelty + 15% Anomaly = 89/100</text>
  </g>

  <g transform="translate(820, 480)">
    <rect width="320" height="150" rx="12" fill="url(#cyanCard)" stroke="#1e293b" stroke-width="2" />
    <rect x="0" y="0" width="320" height="6" fill="#10b981" rx="3"/>
    <text x="24" y="38" font-family="Segoe UI, sans-serif" font-size="16" font-weight="bold" fill="#34d399">5. Verified AI Copilot &amp; UI</text>
    <text x="24" y="68" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Bounded Evidence Pack Context</text>
    <text x="24" y="92" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Schema Verifier Blocks Fake Tokens</text>
    <text x="24" y="116" font-family="Segoe UI, sans-serif" font-size="13" fill="#94a3b8">• Interactive Next.js 16 SOC Console</text>
  </g>
  
  <path d="M 760 555 L 815 555" fill="none" stroke="#10b981" stroke-width="2.5" marker-end="url(#arrow-emerald)" />
</svg>
"""

# 2. PROMOTION GATE FLOWCHART SVG
SVG_PROMOTION_GATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" width="100%" height="100%">
  <defs>
    <linearGradient id="gateBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080c14" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    <marker id="g-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#06b6d4" />
    </marker>
    <marker id="g-arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#10b981" />
    </marker>
    <marker id="g-arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#f43f5e" />
    </marker>
  </defs>

  <rect width="900" height="520" fill="url(#gateBg)" rx="16" />

  <text x="50" y="45" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#06b6d4" letter-spacing="2">RULE 1 ENFORCEMENT ENGINE</text>
  <text x="50" y="80" font-family="Segoe UI, sans-serif" font-size="22" font-weight="bold" fill="#f8fafc">Multi-Stage Incident Promotion Gate</text>

  <!-- Input Cluster -->
  <g transform="translate(50, 120)">
    <rect width="220" height="90" rx="10" fill="#1e293b" stroke="#334155" stroke-width="2"/>
    <text x="20" y="35" font-family="Segoe UI, sans-serif" font-size="14" font-weight="bold" fill="#38bdf8">Incoming Signal Cluster</text>
    <text x="20" y="60" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">Clustered by Primary Actor</text>
    <text x="20" y="78" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">(user_id or device_id)</text>
  </g>

  <path d="M 270 165 L 340 165" fill="none" stroke="#06b6d4" stroke-width="2.5" marker-end="url(#g-arrow)" />

  <!-- Decision 1: Event Count -->
  <g transform="translate(350, 115)">
    <polygon points="100,0 200,50 100,100 0,50" fill="#1e1b4b" stroke="#6366f1" stroke-width="2"/>
    <text x="45" y="48" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#e0e7ff">Events ≥ 3 ?</text>
    <text x="55" y="66" font-family="Segoe UI, sans-serif" font-size="11" fill="#c7d2fe">(Evidence check)</text>
  </g>

  <!-- Decision 1 -> FAIL -->
  <path d="M 450 215 L 450 340" fill="none" stroke="#f43f5e" stroke-width="2.5" marker-end="url(#g-arrow-red)" />
  <text x="460" y="270" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#f43f5e">NO (&lt;3 events)</text>

  <!-- Decision 1 -> YES -> Decision 2 -->
  <path d="M 550 165 L 620 165" fill="none" stroke="#10b981" stroke-width="2.5" marker-end="url(#g-arrow-green)" />
  <text x="565" y="150" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#10b981">YES</text>

  <!-- Decision 2: Stages Count -->
  <g transform="translate(630, 115)">
    <polygon points="100,0 200,50 100,100 0,50" fill="#1e1b4b" stroke="#6366f1" stroke-width="2"/>
    <text x="45" y="48" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#e0e7ff">Stages ≥ 2 ?</text>
    <text x="45" y="66" font-family="Segoe UI, sans-serif" font-size="11" fill="#c7d2fe">(Multi-stage check)</text>
  </g>

  <!-- Decision 2 -> FAIL -->
  <path d="M 730 215 L 730 310 L 580 370" fill="none" stroke="#f43f5e" stroke-width="2.5" marker-end="url(#g-arrow-red)" />
  <text x="740" y="270" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#f43f5e">NO (1 stage)</text>

  <!-- Decision 2 -> PASS -->
  <path d="M 830 165 L 870 165 L 870 410 L 680 410" fill="none" stroke="#10b981" stroke-width="2.5" marker-end="url(#g-arrow-green)" />
  <text x="835" y="150" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#10b981">YES</text>

  <!-- SUPPRESSION LEDGER RESULT -->
  <g transform="translate(250, 340)">
    <rect width="320" height="120" rx="10" fill="#1c1917" stroke="#dc2626" stroke-width="2"/>
    <text x="24" y="32" font-family="Segoe UI, sans-serif" font-size="15" font-weight="bold" fill="#f87171">FALSE-POSITIVE SUPPRESSION</text>
    <text x="24" y="58" font-family="Segoe UI, sans-serif" font-size="12" fill="#d6d3d1">• Reason: INSUFFICIENT_CHAIN_EVIDENCE</text>
    <text x="24" y="78" font-family="Segoe UI, sans-serif" font-size="12" fill="#d6d3d1">• Routed to Immutable SQLite Audit Log</text>
    <text x="24" y="98" font-family="Segoe UI, sans-serif" font-size="12" fill="#d6d3d1">• Quiet SOC Queue: Zero Incidents Created</text>
  </g>

  <!-- PROMOTED INCIDENT RESULT -->
  <g transform="translate(600, 340)">
    <rect width="260" height="120" rx="10" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
    <text x="20" y="32" font-family="Segoe UI, sans-serif" font-size="15" font-weight="bold" fill="#34d399">INCIDENT PROMOTED</text>
    <text x="20" y="58" font-family="Segoe UI, sans-serif" font-size="12" fill="#d1fae5">• Compute 4-Factor Risk Score</text>
    <text x="20" y="78" font-family="Segoe UI, sans-serif" font-size="12" fill="#d1fae5">• Extract 1-Hop Entity Subgraph</text>
    <text x="20" y="98" font-family="Segoe UI, sans-serif" font-size="12" fill="#d1fae5">• Build Bounded Evidence Pack</text>
  </g>
</svg>
"""

# 3. BOUNDED COPILOT VERIFICATION FLOW SVG
SVG_COPILOT_VERIFIER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 520" width="100%" height="100%">
  <defs>
    <linearGradient id="copilotBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080c14" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    <marker id="c-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#06b6d4" />
    </marker>
    <marker id="c-arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#10b981" />
    </marker>
    <marker id="c-arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1 L 8 5 L 0 9 z" fill="#f43f5e" />
    </marker>
  </defs>

  <rect width="960" height="520" fill="url(#copilotBg)" rx="16" />

  <text x="50" y="45" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#06b6d4" letter-spacing="2">RULE 2 ZERO-HALLUCINATION ENFORCEMENT</text>
  <text x="50" y="80" font-family="Segoe UI, sans-serif" font-size="22" font-weight="bold" fill="#f8fafc">Bounded AI Copilot &amp; Output Verification Guard</text>

  <!-- Step 1: Bounded Evidence Pack -->
  <g transform="translate(50, 130)">
    <rect width="240" height="140" rx="10" fill="#1e293b" stroke="#334155" stroke-width="2"/>
    <text x="20" y="32" font-family="Segoe UI, sans-serif" font-size="14" font-weight="bold" fill="#38bdf8">1. Bounded Evidence Pack</text>
    <text x="20" y="60" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">• Valid Event IDs: {evt-003, ...}</text>
    <text x="20" y="80" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">• Promoted Stages: {stage-01..04}</text>
    <text x="20" y="100" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">• Approved Action Catalog</text>
    <text x="20" y="120" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">• Deterministic Context Clamp</text>
  </g>

  <path d="M 290 200 L 350 200" fill="none" stroke="#06b6d4" stroke-width="2.5" marker-end="url(#c-arrow)" />

  <!-- Step 2: Synthesis Engine -->
  <g transform="translate(360, 130)">
    <rect width="240" height="140" rx="10" fill="#1e1b4b" stroke="#818cf8" stroke-width="2"/>
    <text x="20" y="32" font-family="Segoe UI, sans-serif" font-size="14" font-weight="bold" fill="#c7d2fe">2. Synthesis Engine</text>
    <text x="20" y="60" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">• Deterministic Copilot Provider</text>
    <text x="20" y="80" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">• Generates Structured JSON</text>
    <text x="20" y="100" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">• Cites Supporting Event IDs</text>
    <text x="20" y="120" font-family="Segoe UI, sans-serif" font-size="12" fill="#94a3b8">• Proposes Response Actions</text>
  </g>

  <path d="M 600 200 L 660 200" fill="none" stroke="#06b6d4" stroke-width="2.5" marker-end="url(#c-arrow)" />

  <!-- Step 3: Copilot Output Verifier Guard -->
  <g transform="translate(670, 115)">
    <polygon points="120,0 240,65 120,130 0,65" fill="#0f172a" stroke="#06b6d4" stroke-width="2.5"/>
    <text x="50" y="58" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#38bdf8">Output Verifier</text>
    <text x="55" y="78" font-family="Segoe UI, sans-serif" font-size="11" fill="#94a3b8">Schema &amp; Sets</text>
  </g>

  <!-- FAIL: Unapproved Token -->
  <path d="M 790 245 L 790 350 L 520 350 L 520 380" fill="none" stroke="#f43f5e" stroke-width="2.5" marker-end="url(#c-arrow-red)" />
  <text x="700" y="335" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#f43f5e">REJECT (Ungrounded token or fake ID)</text>

  <g transform="translate(360, 380)">
    <rect width="320" height="100" rx="10" fill="#450a0a" stroke="#dc2626" stroke-width="2"/>
    <text x="20" y="30" font-family="Segoe UI, sans-serif" font-size="14" font-weight="bold" fill="#fca5a5">OUTPUT REJECTED</text>
    <text x="20" y="54" font-family="Segoe UI, sans-serif" font-size="12" fill="#fecaca">• Intercepts fake events (e.g. evt-fake-9999)</text>
    <text x="20" y="74" font-family="Segoe UI, sans-serif" font-size="12" fill="#fecaca">• Intercepts unapproved actions</text>
  </g>

  <!-- PASS: Verified Tokens -->
  <path d="M 910 180 L 930 180 L 930 400 L 880 400" fill="none" stroke="#10b981" stroke-width="2.5" marker-end="url(#c-arrow-green)" />
  <text x="820" y="270" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#10b981">PASS (100% Grounded)</text>

  <g transform="translate(680, 380)">
    <rect width="250" height="100" rx="10" fill="#064e3b" stroke="#10b981" stroke-width="2"/>
    <text x="20" y="30" font-family="Segoe UI, sans-serif" font-size="14" font-weight="bold" fill="#6ee7b7">VERIFICATION PASSED</text>
    <text x="20" y="54" font-family="Segoe UI, sans-serif" font-size="12" fill="#d1fae5">• Display Green Verified Seal</text>
    <text x="20" y="74" font-family="Segoe UI, sans-serif" font-size="12" fill="#d1fae5">• Render Grounded Citations in UI</text>
  </g>
</svg>
"""

# 4. ENTITY GRAPH TOPOLOGY SVG
SVG_ENTITY_GRAPH = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" width="100%" height="100%">
  <defs>
    <linearGradient id="topoBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080c14" />
      <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
  </defs>

  <rect width="960" height="540" fill="url(#topoBg)" rx="16" />

  <text x="50" y="45" font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#06b6d4" letter-spacing="2">NETWORKX MULTI-RELATIONAL TOPOLOGY</text>
  <text x="50" y="80" font-family="Segoe UI, sans-serif" font-size="22" font-weight="bold" fill="#f8fafc">Incident inc-001 Correlated Entity Subgraph</text>

  <!-- EDGES -->
  <line x1="200" y1="200" x2="350" y2="280" stroke="#334155" stroke-width="2.5" />
  <line x1="350" y1="280" x2="520" y2="280" stroke="#06b6d4" stroke-width="3" />
  <line x1="520" y1="280" x2="680" y2="180" stroke="#334155" stroke-width="2.5" />
  <line x1="520" y1="280" x2="680" y2="380" stroke="#334155" stroke-width="2.5" />
  <line x1="520" y1="280" x2="780" y2="280" stroke="#f43f5e" stroke-width="2.5" stroke-dasharray="6,4" />

  <!-- EDGE LABELS -->
  <rect x="235" y="225" width="80" height="22" rx="4" fill="#0f172a" stroke="#1e293b"/>
  <text x="245" y="240" font-family="Segoe UI, sans-serif" font-size="10" font-weight="bold" fill="#a855f7">FROM_IP</text>

  <rect x="400" y="268" width="90" height="22" rx="4" fill="#0f172a" stroke="#1e293b"/>
  <text x="408" y="283" font-family="Segoe UI, sans-serif" font-size="10" font-weight="bold" fill="#38bdf8">OCCURRED_ON</text>

  <rect x="560" y="210" width="120" height="22" rx="4" fill="#0f172a" stroke="#1e293b"/>
  <text x="566" y="225" font-family="Segoe UI, sans-serif" font-size="10" font-weight="bold" fill="#10b981">ACCESSED_RESOURCE</text>

  <rect x="580" y="340" width="90" height="22" rx="4" fill="#0f172a" stroke="#1e293b"/>
  <text x="588" y="355" font-family="Segoe UI, sans-serif" font-size="10" font-weight="bold" fill="#f59e0b">MOUNTED_USB</text>

  <rect x="610" y="268" width="120" height="22" rx="4" fill="#0f172a" stroke="#1e293b"/>
  <text x="618" y="283" font-family="Segoe UI, sans-serif" font-size="10" font-weight="bold" fill="#f43f5e">CONNECTED_TO_IP</text>

  <!-- NODES -->
  <!-- 1. Ingress IP -->
  <g transform="translate(200, 200)">
    <circle r="40" fill="#2e1065" stroke="#a855f7" stroke-width="2.5" />
    <text x="-28" y="-5" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold" fill="#e9d5ff">Ingress IP</text>
    <text x="-32" y="15" font-family="Segoe UI, sans-serif" font-size="9" fill="#c084fc">203.0.113.10</text>
  </g>

  <!-- 2. User Actor -->
  <g transform="translate(350, 280)">
    <circle r="46" fill="#1e1b4b" stroke="#6366f1" stroke-width="3" />
    <text x="-25" y="-5" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#c7d2fe">Actor</text>
    <text x="-28" y="16" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold" fill="#ffffff">user-42</text>
  </g>

  <!-- 3. Workstation Device -->
  <g transform="translate(520, 280)">
    <circle r="46" fill="#083344" stroke="#06b6d4" stroke-width="3" />
    <text x="-28" y="-5" font-family="Segoe UI, sans-serif" font-size="12" font-weight="bold" fill="#a5f3fc">Device</text>
    <text x="-32" y="16" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold" fill="#ffffff">device-17</text>
  </g>

  <!-- 4. Sensitive Resource -->
  <g transform="translate(680, 180)">
    <circle r="40" fill="#064e3b" stroke="#10b981" stroke-width="2.5" />
    <text x="-28" y="-5" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold" fill="#a7f3d0">Resource</text>
    <text x="-30" y="15" font-family="Segoe UI, sans-serif" font-size="9" fill="#6ee7b7">payroll.xlsx</text>
  </g>

  <!-- 5. Removable Storage -->
  <g transform="translate(680, 380)">
    <circle r="40" fill="#451a03" stroke="#f59e0b" stroke-width="2.5" />
    <text x="-32" y="-5" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold" fill="#fde68a">USB Storage</text>
    <text x="-28" y="15" font-family="Segoe UI, sans-serif" font-size="9" fill="#fcd34d">Volume:E:\\</text>
  </g>

  <!-- 6. Egress IP -->
  <g transform="translate(780, 280)">
    <circle r="40" fill="#450a0a" stroke="#f43f5e" stroke-width="2.5" />
    <text x="-26" y="-5" font-family="Segoe UI, sans-serif" font-size="11" font-weight="bold" fill="#fecaca">Egress IP</text>
    <text x="-34" y="15" font-family="Segoe UI, sans-serif" font-size="9" fill="#f87171">198.51.100.88</text>
  </g>
</svg>
"""

with open(os.path.join(DIAGRAMS_DIR, "architecture_overview.svg"), "w", encoding="utf-8") as f:
    f.write(SVG_ARCHITECTURE)
print("Created architecture_overview.svg")

with open(os.path.join(DIAGRAMS_DIR, "promotion_gate.svg"), "w", encoding="utf-8") as f:
    f.write(SVG_PROMOTION_GATE)
print("Created promotion_gate.svg")

with open(os.path.join(DIAGRAMS_DIR, "copilot_verification.svg"), "w", encoding="utf-8") as f:
    f.write(SVG_COPILOT_VERIFIER)
print("Created copilot_verification.svg")

with open(os.path.join(DIAGRAMS_DIR, "entity_graph_topology.svg"), "w", encoding="utf-8") as f:
    f.write(SVG_ENTITY_GRAPH)
print("Created entity_graph_topology.svg")
