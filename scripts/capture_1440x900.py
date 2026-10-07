import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path(r"C:\Users\ffgam\.gemini\antigravity-ide\brain\8f2af1e3-b507-478b-8844-eb9212e66a8b\visual_audit")
OUT_DIR.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    # 1. Investigation Console
    page.goto("http://localhost:3000", wait_until="networkidle")
    time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "01_investigation_console_1440x900.png"))
    print("[1] Captured Investigation Console")

    # 2. Dataset Replay
    replay_tab = page.locator("button:has-text('Dataset Replay')").first
    if replay_tab.is_visible():
        replay_tab.click()
        time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "02_dataset_replay_1440x900.png"))
    print("[2] Captured Dataset Replay")

    # 3. Suppression Audit
    suppression_tab = page.locator("button:has-text('Suppression Audit')").first
    if suppression_tab.is_visible():
        suppression_tab.click()
        time.sleep(1)
    page.screenshot(path=str(OUT_DIR / "03_suppression_audit_1440x900.png"))
    print("[3] Captured Suppression Audit")

    browser.close()

print("All 3 screenshots captured at 1440x900!")
