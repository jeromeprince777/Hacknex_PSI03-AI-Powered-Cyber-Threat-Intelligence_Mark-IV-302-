# THREATWEAVE — Attack Stage Evidence Traceability Report

Authoritative Standard: **HackNex 2026 Qualifier PS03 Key Rule #2 ("Every stage of the attack must have proof. An unsupported claim = doesn't count.")**  
Target Incident: **`inc-001` (Canonical Insider Threat & Removable Media Exfiltration)**  
Target Scenario: **`data/scenarios/attack_insider_usb.jsonl`**

---

## 1. Evidence Verification Summary Table

| Stage Index | Stage Name | Stage ID | Evidence Event IDs | Event Exists in Telemetry? | Semantically Supports Stage? | Event Timestamps Strictly Within Stage Window? | Visible in API & UI Drawer? | Stage Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | Initial access / Authentication novelty | `stage-01` | `evt-003` | **Yes** | **Yes** (VPN authentication from novel foreign IP) | `09:41:12Z` $\in [09:41:12\text{Z}, 09:41:12\text{Z}]$ | **Yes** | **VERIFIED** |
| **2** | Resource discovery / Collection | `stage-02` | `evt-008`, `evt-009` | **Yes** | **Yes** (Read access to payroll & M&A secrets) | `09:48:33Z`, `09:50:14Z` $\in [09:48:33\text{Z}, 09:50:14\text{Z}]$ | **Yes** | **VERIFIED** |
| **3** | Removable-media transfer / USB activity | `stage-03` | `evt-011`, `evt-012`, `evt-013` | **Yes** | **Yes** (Mount USB volume & copy secrets to USB) | `09:52:05Z`, `09:54:20Z`, `09:55:02Z` $\in [09:52:05\text{Z}, 09:55:02\text{Z}]$ | **Yes** | **VERIFIED** |
| **4** | Outbound data exfiltration | `stage-04` | `evt-015` | **Yes** | **Yes** (High-volume 14.5MB upload to external IP) | `09:58:45Z` $\in [09:58:45\text{Z}, 09:58:45\text{Z}]$ | **Yes** | **VERIFIED** |

---

## 2. Stage-by-Stage Forensic Proof Deep-Dive

### Stage 1: Initial access / Authentication novelty (`stage-01`)
* **Time Range:** `2026-10-06T09:41:12Z` to `2026-10-06T09:41:12Z`
* **Triggering Detector:** `AUTH_NEW_LOCATION` (Base score: 0.55)
* **Proof Telemetry:**
  ```json
  {
    "event_id": "evt-003",
    "timestamp": "2026-10-06T09:41:12Z",
    "source": "vpn",
    "event_type": "login_success",
    "action": "authenticate",
    "user_id": "user-42",
    "device_id": "device-17",
    "src_ip": "203.0.113.10",
    "dst_ip": "10.10.1.5",
    "attributes": {
      "login_location": "Bucharest, Romania",
      "vpn_profile": "Corp-Global-Access",
      "mfa_method": "push"
    }
  }
  ```
* **Semantic Proof:** User `user-42` normally authenticates from regional US office IPs (`10.10.x.x`). `203.0.113.10` is an external RFC 5737 test-net IP originating from Bucharest, Romania, triggering the authentication novelty baseline detector.

---

### Stage 2: Resource discovery / Collection (`stage-02`)
* **Time Range:** `2026-10-06T09:48:33Z` to `2026-10-06T09:50:14Z`
* **Triggering Detector:** `UNUSUAL_RESOURCE_ACCESS` (Base score: 0.70)
* **Proof Telemetry (Event 1):**
  ```json
  {
    "event_id": "evt-008",
    "timestamp": "2026-10-06T09:48:33Z",
    "source": "windows",
    "event_type": "file_access",
    "action": "read",
    "user_id": "user-42",
    "device_id": "device-17",
    "resource": "Finance/Q4/payroll.xlsx",
    "application": "explorer.exe",
    "attributes": {
      "share_path": "\\\\corp-fs01\\Finance\\Q4\\payroll.xlsx",
      "access_mask": "0x120089",
      "file_extension": "xlsx"
    }
  }
  ```
* **Proof Telemetry (Event 2):**
  ```json
  {
    "event_id": "evt-009",
    "timestamp": "2026-10-06T09:50:14Z",
    "source": "windows",
    "event_type": "file_access",
    "action": "read",
    "user_id": "user-42",
    "device_id": "device-17",
    "resource": "Legal/M&A/Project_Titan.pdf",
    "application": "explorer.exe",
    "attributes": {
      "share_path": "\\\\corp-fs01\\Legal\\M&A\\Project_Titan.pdf",
      "access_mask": "0x120089",
      "file_extension": "pdf"
    }
  }
  ```
* **Semantic Proof:** Routine files accessed earlier by other users (`timesheet.xlsx`, `all_hands.pdf`) passed without alarms. Events `evt-008` and `evt-009` targeted confidential enterprise shares containing sensitive keywords (`payroll`, `titan`, `m&a`), matching the collection rule.

---

### Stage 3: Removable-media transfer / USB activity (`stage-03`)
* **Time Range:** `2026-10-06T09:52:05Z` to `2026-10-06T09:55:02Z`
* **Triggering Detectors:** `USB_CONNECTED` (Base score: 0.65), `USB_COPY` (Base score: 0.85)
* **Proof Telemetry (Mount Event):**
  ```json
  {
    "event_id": "evt-011",
    "timestamp": "2026-10-06T09:52:05Z",
    "source": "edr",
    "event_type": "usb_connected",
    "action": "mount",
    "user_id": "user-42",
    "device_id": "device-17",
    "resource": "Volume:E:\\",
    "attributes": {
      "removable_media_id": "usb-kingston-992",
      "vendor": "Kingston",
      "serial": "KGT-88319-X",
      "drive_letter": "E:"
    }
  }
  ```
* **Proof Telemetry (Copy Event 1):**
  ```json
  {
    "event_id": "evt-012",
    "timestamp": "2026-10-06T09:54:20Z",
    "source": "edr",
    "event_type": "usb_copy",
    "action": "write",
    "user_id": "user-42",
    "device_id": "device-17",
    "resource": "Finance/Q4/payroll.xlsx",
    "attributes": {
      "destination_path": "E:\\backup\\payroll.xlsx",
      "bytes": 2450000,
      "removable_media_id": "usb-kingston-992"
    }
  }
  ```
* **Proof Telemetry (Copy Event 2):**
  ```json
  {
    "event_id": "evt-013",
    "timestamp": "2026-10-06T09:55:02Z",
    "source": "edr",
    "event_type": "usb_copy",
    "action": "write",
    "user_id": "user-42",
    "device_id": "device-17",
    "resource": "Legal/M&A/Project_Titan.pdf",
    "attributes": {
      "destination_path": "E:\\backup\\Project_Titan.pdf",
      "bytes": 8900000,
      "removable_media_id": "usb-kingston-992"
    }
  }
  ```
* **Semantic Proof:** Exactly demonstrates the HackNex PS03 canonical example: *"copies them to a USB drive they plugged in"*. Hardware mount on drive `E:` is directly followed by copy writes of the exact sensitive files gathered in Stage 2.

---

### Stage 4: Outbound data exfiltration (`stage-04`)
* **Time Range:** `2026-10-06T09:58:45Z` to `2026-10-06T09:58:45Z`
* **Triggering Detector:** `LARGE_OUTBOUND_TRANSFER` (Base score: 0.75)
* **Proof Telemetry:**
  ```json
  {
    "event_id": "evt-015",
    "timestamp": "2026-10-06T09:58:45Z",
    "source": "firewall",
    "event_type": "outbound_connection",
    "action": "connect",
    "user_id": "user-42",
    "device_id": "device-17",
    "dst_ip": "198.51.100.88",
    "resource": "https://198.51.100.88/upload",
    "attributes": {
      "bytes": 14500000,
      "bytes_sent": 14500000,
      "port": 443,
      "protocol": "tcp"
    }
  }
  ```
* **Semantic Proof:** Network egress from `device-17` immediately following collection and local staging transfers 14.5MB ($>10\text{MB}$ rule threshold) to external destination IP `198.51.100.88`.

---

## 3. Strict Rule Verification

- **Zero Unsupported Stages:** No stage exists without explicit, verified event IDs.
- **Strict Monotonicity:** Every stage timestamp window is strictly derived from `min(event.timestamp)` and `max(event.timestamp)` of its supporting telemetry.
- **Anti-Hallucination Barrier:** The AI Copilot verifier validates that any narrative generated references *only* these verified event IDs (`evt-003`, `evt-008`, `evt-009`, `evt-011`, `evt-012`, `evt-013`, `evt-015`). Any hallucinated ID is rejected.
