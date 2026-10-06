"""
ThreatWeave Demo Seed & Validation Runner.
Verifies and pre-loads canonical scenarios for demonstration.
"""

import sys
from pathlib import Path

# Add backend to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.ingestion.validator import ingest_jsonl_file


def main():
    scenarios_dir = ROOT_DIR / "data" / "scenarios"
    scenarios = [
        ("Canonical Attack (Insider USB Exfil)", scenarios_dir / "attack_insider_usb.jsonl"),
        ("Benign Scenario (Routine Admin / Workstation)", scenarios_dir / "benign_admin.jsonl"),
        ("Partial Attack Scenario (No Exfil)", scenarios_dir / "attack_partial.jsonl"),
        ("Malformed Logs Scenario (Negative Control)", scenarios_dir / "malformed_logs.jsonl"),
    ]

    print("=" * 65)
    print("THREATWEAVE — SEED DATASET VERIFICATION & PRE-FLIGHT CHECK")
    print("=" * 65)

    all_passed = True
    for title, path in scenarios:
        if not path.is_file():
            print(f"[FAIL] Missing scenario file: {path}")
            all_passed = False
            continue

        report = ingest_jsonl_file(path)
        print(f"\n[*] {title}")
        print(f"    File: {path.name}")
        print(f"    Total records:       {report.total_records}")
        print(f"    Valid records:       {report.valid_records}")
        print(f"    Quarantined records: {report.quarantined_records}")
        print(f"    Duplicate records:   {report.duplicate_records}")

        if "Malformed" in title:
            if report.quarantined_records > 0:
                print("    Status: PASS (Quarantine behaved correctly)")
            else:
                print("    Status: FAIL (Expected quarantine records not found)")
                all_passed = False
        else:
            if report.quarantined_records == 0 and report.valid_records > 0:
                print("    Status: PASS (Clean ingestion)")
            else:
                print("    Status: FAIL (Unexpected quarantine in clean dataset)")
                all_passed = False

    print("\n" + "=" * 65)
    if all_passed:
        print("[SUCCESS] All seed datasets validated against Canonical Event Schema.")
    else:
        print("[ERROR] One or more datasets failed pre-flight verification.")
        sys.exit(1)


if __name__ == "__main__":
    main()
