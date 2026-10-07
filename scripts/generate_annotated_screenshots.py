"""
Generate high-resolution annotated screenshots for ThreatWeave presentation.
Draws sleek bounding boxes, glowing badges, and numbered callouts.
"""

import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"c:\Users\ffgam\OneDrive\Desktop\Hacknex"
SCREENSHOTS_DIR = r"C:\Users\ffgam\.gemini\antigravity-ide\brain\8f2af1e3-b507-478b-8844-eb9212e66a8b\screenshots"
OUT_DIR = os.path.join(BASE_DIR, "assets", "annotated")
os.makedirs(OUT_DIR, exist_ok=True)

# Color palette
CYAN = (6, 182, 212, 255)
EMERALD = (16, 185, 129, 255)
ROSE = (244, 63, 94, 255)
AMBER = (245, 158, 11, 255)
PURPLE = (168, 85, 247, 255)
BLUE = (59, 130, 246, 255)
WHITE = (255, 255, 255, 255)
DARK_BG = (15, 23, 42, 230)

FONT_PATH = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SM_PATH = "C:/Windows/Fonts/segoeui.ttf"
try:
    font_lg = ImageFont.truetype(FONT_PATH, 20)
    font_md = ImageFont.truetype(FONT_PATH, 16)
    font_badge = ImageFont.truetype(FONT_PATH, 18)
    font_desc = ImageFont.truetype(FONT_SM_PATH, 14)
except Exception:
    font_lg = font_md = font_badge = font_desc = ImageFont.load_default()

def draw_callout_box(draw, box, color, num, label, desc=""):
    x1, y1, x2, y2 = box
    # Draw outer bounding box with thickness 3
    for i in range(3):
        draw.rectangle([x1 - i, y1 - i, x2 + i, y2 + i], outline=color)
    
    # Draw badge top-left
    badge_w = 32
    badge_h = 32
    badge_x = x1 - 10
    badge_y = max(10, y1 - 16)
    
    # Circular badge
    draw.ellipse([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], fill=color, outline=WHITE)
    num_str = str(num)
    draw.text((badge_x + 11, badge_y + 4), num_str, fill=(0, 0, 0, 255), font=font_badge)
    
    # Label pill
    label_text = f" {label} "
    pill_x = badge_x + badge_w + 6
    pill_y = badge_y + 2
    # Measure text
    text_bbox = font_md.getbbox(label_text)
    tw = text_bbox[2] - text_bbox[0]
    th = text_bbox[3] - text_bbox[1]
    
    draw.rounded_rectangle([pill_x, pill_y, pill_x + tw + 10, pill_y + th + 8], radius=4, fill=DARK_BG, outline=color)
    draw.text((pill_x + 5, pill_y + 3), label_text, fill=color, font=font_md)

# =========================================================================
# 1. EXECUTIVE CONSOLE & RISK GAUGE
# =========================================================================
def annotate_executive_console():
    src_path = os.path.join(SCREENSHOTS_DIR, "01_soc_dashboard_overview.png")
    im = Image.open(src_path).convert("RGBA")
    # Crop top 720 px (Header + Risk Meter + Incident Header + Actions)
    crop = im.crop((0, 0, 1600, 720))
    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # [1] Incident Title & Actor Header
    draw_callout_box(draw, (290, 80, 970, 270), CYAN, 1, "INCIDENT HEADER & ACTOR ATTRIBUTION")
    # [2] Radial Risk Gauge
    draw_callout_box(draw, (990, 80, 1530, 270), ROSE, 2, "RADIAL RISK GAUGE (89/100 HIGH)")
    # [3] 4-Factor Risk Breakdown
    draw_callout_box(draw, (290, 290, 1530, 480), AMBER, 3, "EXPLAINABLE 4-FACTOR RISK FORMULA")
    # [4] Approved Incident Response Actions
    draw_callout_box(draw, (290, 500, 1530, 700), EMERALD, 4, "APPROVED ACTION PLAYBOOK")
    
    res = Image.alpha_composite(crop, overlay)
    res.convert("RGB").save(os.path.join(OUT_DIR, "annotated_01_executive_console.png"), quality=95)
    print("Created annotated_01_executive_console.png")

# =========================================================================
# 2. ATTACK TIMELINE & STAGE DECOMPOSITION
# =========================================================================
def annotate_attack_timeline():
    src_path = os.path.join(SCREENSHOTS_DIR, "01_soc_dashboard_overview.png")
    im = Image.open(src_path).convert("RGBA")
    # Crop middle 720 to 1250 (Timeline section)
    crop = im.crop((0, 700, 1600, 1280))
    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # [1] Stage 1 Initial Access (VPN Bucharest)
    draw_callout_box(draw, (290, 80, 580, 520), CYAN, 1, "STAGE 1: INITIAL ACCESS (evt-003)")
    # [2] Stage 2 Sensitive Resource Collection
    draw_callout_box(draw, (600, 80, 890, 520), PURPLE, 2, "STAGE 2: COLLECTION (evt-008, 009)")
    # [3] Stage 3 Removable Media Transfer (USB)
    draw_callout_box(draw, (910, 80, 1200, 520), AMBER, 3, "STAGE 3: USB TRANSFER (evt-011-013)")
    # [4] Stage 4 Outbound Network Exfiltration
    draw_callout_box(draw, (1220, 80, 1530, 520), ROSE, 4, "STAGE 4: EXFILTRATION (evt-015)")
    
    res = Image.alpha_composite(crop, overlay)
    res.convert("RGB").save(os.path.join(OUT_DIR, "annotated_02_attack_timeline.png"), quality=95)
    print("Created annotated_02_attack_timeline.png")

# =========================================================================
# 3. INTERACTIVE SVG ENTITY GRAPH
# =========================================================================
def annotate_entity_graph():
    src_path = os.path.join(SCREENSHOTS_DIR, "02_entity_graph.png")
    im = Image.open(src_path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # [1] User & Device Central Hub
    draw_callout_box(draw, (550, 420, 950, 680), CYAN, 1, "PRIMARY ACTOR & DEVICE HUB (user-42, device-17)")
    # [2] Ingress Foreign IP
    draw_callout_box(draw, (320, 220, 580, 390), PURPLE, 2, "EXTERNAL INGRESS IP (203.0.113.10)")
    # [3] Confidential Corporate Files
    draw_callout_box(draw, (970, 220, 1380, 430), EMERALD, 3, "SENSITIVE RESOURCES (payroll.xlsx, Titan.pdf)")
    # [4] Removable Media Volume
    draw_callout_box(draw, (1000, 560, 1420, 770), AMBER, 4, "MOUNTED USB STORAGE (Volume: E:\\)")
    # [5] Exfiltration Destination IP
    draw_callout_box(draw, (320, 640, 580, 850), ROSE, 5, "EXTERNAL EGRESS IP (198.51.100.88)")
    
    res = Image.alpha_composite(im, overlay)
    res.convert("RGB").save(os.path.join(OUT_DIR, "annotated_03_entity_graph.png"), quality=95)
    print("Created annotated_03_entity_graph.png")

# =========================================================================
# 4. FORENSIC EVIDENCE DRAWER
# =========================================================================
def annotate_evidence_drawer():
    src_path = os.path.join(SCREENSHOTS_DIR, "03_forensic_evidence_drawer.png")
    im = Image.open(src_path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # [1] Active Selected Stage Header
    draw_callout_box(draw, (900, 30, 1570, 150), CYAN, 1, "SELECTED STAGE FORENSIC HEADER")
    # [2] Verified Telemetry Event Card (evt-003)
    draw_callout_box(draw, (900, 170, 1570, 550), EMERALD, 2, "GROUNDED TELEMETRY EVENT (evt-003)")
    # [3] Raw Event Schema & Payload Attributes
    draw_callout_box(draw, (900, 570, 1570, 950), AMBER, 3, "RAW LOG PAYLOAD & ZERO-HALLUCINATION PROOF")
    
    res = Image.alpha_composite(im, overlay)
    res.convert("RGB").save(os.path.join(OUT_DIR, "annotated_04_evidence_drawer.png"), quality=95)
    print("Created annotated_04_evidence_drawer.png")

# =========================================================================
# 5. BOUNDED AI COPILOT & VERIFICATION GUARD
# =========================================================================
def annotate_copilot():
    src_path = os.path.join(SCREENSHOTS_DIR, "04_copilot_verified.png")
    im = Image.open(src_path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # [1] Copilot Grounded Narrative Explanation
    draw_callout_box(draw, (290, 80, 1530, 370), CYAN, 1, "EVIDENCE-BOUNDED INCIDENT NARRATIVE")
    # [2] Cryptographic & Schema Verification Badge
    draw_callout_box(draw, (290, 390, 900, 510), EMERALD, 2, "EVIDENCE VERIFICATION PASSED SEAL")
    # [3] Cited Telemetry Grounding Links
    draw_callout_box(draw, (920, 390, 1530, 510), BLUE, 3, "100% TELEMETRY GROUNDED EVENT CITATIONS")
    # [4] Evaluator Anti-Hallucination Injection Sandbox
    draw_callout_box(draw, (290, 530, 1530, 850), ROSE, 4, "EVALUATOR STRESS-TEST INJECTION CONTROLS")
    
    res = Image.alpha_composite(im, overlay)
    res.convert("RGB").save(os.path.join(OUT_DIR, "annotated_05_copilot_verified.png"), quality=95)
    print("Created annotated_05_copilot_verified.png")

# =========================================================================
# 6. REPLAY LAB & MULTI-SCENARIO BENCHMARK
# =========================================================================
def annotate_replay_lab():
    src_path = os.path.join(SCREENSHOTS_DIR, "05_replay_benign_results.png")
    im = Image.open(src_path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # [1] Canonical Attack Scenario Card
    draw_callout_box(draw, (290, 150, 680, 480), CYAN, 1, "CANONICAL ATTACK (Promoted, Risk 89)")
    # [2] Benign Administrator Scenario Card
    draw_callout_box(draw, (700, 150, 1100, 480), EMERALD, 2, "BENIGN NOISE (0 Incidents, Suppressed)")
    # [3] Partial Attack Degradation Card
    draw_callout_box(draw, (1120, 150, 1530, 480), AMBER, 3, "PARTIAL ATTACK (Graceful Drop, Risk 76)")
    # [4] Evaluator Benchmark Summary Ledger
    draw_callout_box(draw, (290, 510, 1530, 850), PURPLE, 4, "OFFICIAL PS03 BENCHMARK PERFORMANCE LEDGER")
    
    res = Image.alpha_composite(im, overlay)
    res.convert("RGB").save(os.path.join(OUT_DIR, "annotated_06_replay_lab.png"), quality=95)
    print("Created annotated_06_replay_lab.png")

# =========================================================================
# 7. SUPPRESSION AUDIT LEDGER
# =========================================================================
def annotate_suppression_ledger():
    src_path = os.path.join(SCREENSHOTS_DIR, "06_suppression_audit_ledger.png")
    im = Image.open(src_path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # [1] Suppression Summary KPI Card
    draw_callout_box(draw, (290, 120, 1530, 280), EMERALD, 1, "FALSE-POSITIVE SUPPRESSION METRICS")
    # [2] Immutable Suppressed Cluster Records
    draw_callout_box(draw, (290, 300, 1530, 850), PURPLE, 2, "AUDITED SUPPRESSION LEDGER (INSUFFICIENT_CHAIN)")
    
    res = Image.alpha_composite(im, overlay)
    res.convert("RGB").save(os.path.join(OUT_DIR, "annotated_07_suppression_ledger.png"), quality=95)
    print("Created annotated_07_suppression_ledger.png")

if __name__ == "__main__":
    annotate_executive_console()
    annotate_attack_timeline()
    annotate_entity_graph()
    annotate_evidence_drawer()
    annotate_copilot()
    annotate_replay_lab()
    annotate_suppression_ledger()
    print("All annotated screenshots generated successfully.")
