# Automation Test System Installation Guide  
**Automation Test System Installation Guide**

> Document Type: Standard Operating Procedure (SOP)  
> Version: v1.2 (Draft)  
> Last Updated: 2026-05-15  
> Scope: WFCO PwrPro automated test environment (Robotic Arm + Control Boards + Hub + IPCAM + Speaker + Wi‑Fi)

### SOP Document Control
| Field | Content |
|---|---|
| Owner | `Owen ke` |
| Version | `v1.2` |
| Last Updated | `2026-05-15` |
| Change Summary | `v1.2: synced with latest Chinese structure; improved readability for non-technical installers` |

### How to Use This SOP
1. Follow chapters in order. Do not skip safety checks.  
2. After each chapter, tick the corresponding checklist.  
3. If site conditions differ from this document, pause and mark the change.  
4. If anything is unclear, contact the owner and update the document.

### Safety First (Read Before Work)
- **Do not power on during wiring and mechanical fastening.**
- Before power-on, always check cable direction, terminal mapping, and moving-part clearance.
- If unsure at any step, stop and mark `Blocked`.

---

## 0. Pre-Work Preparation (Recommended for New Installers)

### 0.1 What You Will Complete
Complete device/tool inventory, role confirmation, and risk checks before installation to avoid mid-process blockers.

### 0.2 Device and Tool Checklist (Tick before starting)
- [ ] Host PC
- [ ] Wi‑Fi devices (Router/AP/Extender; choose as needed)
- [ ] IPCAM: 5 units shipped this time (CAM1~CAM5)
  - CAM1~CAM3: fixed for environment monitoring
  - CAM4~CAM5: install if needed; if not used, mark and store properly
- [ ] Speaker + Scarlett 4i4
- [ ] FP2 Sensor
- [ ] Robotic Arm and control boards (WF-3534 / 3611A / 3611C)
- [ ] USB Hub, USB extension cable, Burner
- [ ] USB cables (USB-A / USB-C as required)
- [ ] UART cables (spares recommended)
- [ ] Keyboard, mouse, external monitor (for PC/RobotArm network checks)
- [ ] Cable labels, ties, mounts, insulation tape
- [ ] Basic tools (screwdriver, cutter, multimeter)

### 0.3 Roles and Contacts
- On-site installation owner: `<fill>`
- Acceptance sign-off owner: `<fill>`
- Taipei support contact: `<owen.ke>`

### 0.4 Estimated Time (Reference)
- Chapter 1 (Overview): 15~25 min
- Chapter 2 (Installation): 90~150 min
- Chapter 3 (Host placement): 20~40 min
- Chapter 4 (Burner/USB/Hub): 30~50 min
- Chapter 5 (Robotic arm/panels): 45~75 min
- Chapter 6 (Final acceptance): 15~30 min
- **Total (single operator):** ~3.5~6 hours (depends on routing complexity/rework)

### 0.5 Start Conditions (all must be met)
- [ ] Figure 1 and Figure 2 are accessible
- [ ] `qa_rpt` existing setup is confirmed (reuse existing setup, no reset)
- [ ] Work area is clear and safe
- [ ] Confirmed power is OFF before work

### 0.6 Accounts and Passwords (Installation Use)
> Keep this section in internal version only; remove/mask for external sharing.

- Common password: `thortron`
- Wi‑Fi test credentials: `SSID: qa_rpt / Password: 12345678`
- PC login ID: `thortron`
- PC login password: `thortron`
- RobotArm login ID: `er`
- RobotArm login password: `thortron`
- Scope: on-site install/maintenance, login to PC and RobotArm controller, and network checks
- Rule: **Do not change account/password values**, otherwise Taipei may lose remote maintenance access. If change is unavoidable, owner approval and document update are required.

---

## 1. System Overview

> **Done state for this chapter:** installer understands system boundaries and chapter flow. No physical installation is performed here.

### Overview Diagrams (Figure 1 + Figure 2)
![System Layout](https://drive.google.com/uc?export=view&id=1NMFMvyxQza_j-wfTMYb3aPwnLLS1jNVp)

*Figure 1: System Layout (overall zone and device placement)*

![Network and Device Topology](https://drive.google.com/uc?export=view&id=1roD82kDBS9iYUXlkyvy0cbKczhOMT1Ts)

*Figure 2: Network and Device Topology (board/hub/camera/arm/network relationships)*

### SOP Block (Chapter 1)
- **Objective:** align understanding of system, components, and chapter flow.
- **Preconditions:** Figure 1/2 available and Chapter 0 completed.
- **Procedure:** review diagrams, component boundaries, and chapter map.
- **Verification:** installer can explain the difference between Chapter 1 and Chapter 2.
- **Pass Criteria:** installer clearly understands Chapter 1 is overview only.
- **Exceptions:** if chapter boundaries are still mixed up, align verbally before entering Chapter 2.

### 1.1 Purpose of this Chapter
This chapter provides system context and reading map only:
- document usage logic
- component boundaries
- chapter guidance
- no physical install action

### 1.2 System Components and Boundaries (Reading only)
**Quick terms**
- **AP**: wireless access point
- **Extender**: Wi‑Fi range extender
- **Backhaul**: link from extender back to core network (wired/wireless)
- **IPCAM**: network camera
- **Scarlett 4i4**: audio interface

Included in install scope:
- network setup to “connectable”
- camera positioning/power/basic stream access
- audio wiring complete
- FP2 positioning/power/triggerable
- safe cable routing

Not included here:
- physical install steps
- full functional verification/stability tests
- full troubleshooting workflows

### 1.3 Chapter Guide
- **Chapter 2:** Installation (Wi‑Fi / IPCAM / Speaker / FP2)
- **Chapter 3:** Host placement
- **Chapter 4:** Burner / USB extension / USB hub
- **Chapter 5:** Robotic arm and panel setup
- **Chapter 6:** Final acceptance and delivery status

---

## 2. Installation (Wi‑Fi / IPCAM / Speaker / FP2)

> **Done state for this chapter:** phone can use `qa_rpt` internet, PC can use `qa_rpt`, RobotArm controller can use `qa_rpt`, and at least one IPCAM stream is viewable.

### SOP Block (Chapter 2)
- **Objective:** complete baseline on-site installation for Wi‑Fi, IPCAM, Speaker/Scarlett 4i4, and FP2.
- **Preconditions:** Chapter 1 reviewed, Figure 1/2 available, equipment/cables ready.
- **Procedure:** Wi‑Fi → IPCAM → Speaker/Scarlett 4i4 → FP2.
- **Verification:** complete per-item install checks (not final full validation).
- **Pass Criteria:** four device categories installed with basic usability.
- **Exceptions:** if constrained or failed, mark `Blocked/Rework` with reason.
- **Handoff:** after Chapter 2, update installation records and proceed to next chapter.

### 2.0.1 Chapter 2 completion records (simple)
1. **[Required]** Tick all Chapter 2 verification items.
2. **[Required]** Add required photos (overall/cabling/host screen).
3. **[Required]** Mark incomplete items as `Blocked/Rework` with reason.

### 2.1 Wi‑Fi location, power, and cabling planning
1. Use Figure 1 to choose Router/AP/Extender candidate positions.
2. Evaluate power and cable feasibility for each position.
3. Choose LAN backhaul or Extender based on site constraints.
4. Fix placement/power/cables safely.
5. Connect with `SSID: qa_rpt / Password: 12345678`, confirm internet and internal reachability, record final setup.
6. **[Required]** Installer must verify internet on phone connected to `qa_rpt`.

**Verification Criteria**
- [ ] Wi‑Fi placement matches Figure 1 coverage need
- [ ] LAN/Extender option selected with reason
- [ ] Power/cabling complete and fixed
- [ ] `qa_rpt` stable for 5 minutes
- [ ] Installer phone on `qa_rpt` can access internet
- [ ] IPCAM and host both can connect to `qa_rpt` (sample at least 1 IPCAM)

### 2.2 IPCAM positioning and power (Wi‑Fi preconfigured before shipment)
1. Power on IPCAM and confirm existing `qa_rpt` settings load.
2. Follow network method from 2.1 (LAN preferred if possible).
3. Place each IPCAM by Figure 1 view targets.
4. Complete safe power/cable fixation.
5. Create label mapping (`CAM-xx` + actual zone).
6. Update installation/position records (CAM IDs and zones).

### 2.2.1 IPCAM app install and member join (SwitchBot)
1. Install **SwitchBot App** on site phone (iOS/Android).
2. Log in and confirm home page access.
3. Open family member invitation from owner device.
4. Use invitation code method (current code: `UDQ9TN`).
5. Confirm view access to CAM1~CAM3 (and CAM4~CAM5 if needed).
6. If devices not visible, confirm correct family/group and retry with latest code.

> ⚠️ Invitation code expiry reminder  
> Current code: `UDQ9TN`  
> If expired, contact: `owen.ke@thortron.com`

**Verification Criteria**
- [ ] All IPCAMs are at required positions
- [ ] IPCAM power/online stable (5 min)
- [ ] Host can read all required streams
- [ ] CAM1~CAM5 install/position records complete (or reason if not installed)
- [ ] Installer joined app and can view required camera feeds

### 2.3 Speaker placement, power, wiring (to Scarlett 4i4)
1. Place speakers per Figure 1 with maintainability priority.
2. Complete power and fixation for each speaker.
3. Complete wiring back to audio interface.
4. Place Scarlett 4i4 at maintainable and cool location.
5. Connect/label speaker outputs to Scarlett 4i4 ports.

> Note: this is an installation chapter. No full audio correctness testing here.

**Verification Criteria**
- [ ] Speaker placement matches Figure 1
- [ ] Speaker power/wiring complete
- [ ] Scarlett 4i4 fixed and clearly wired

### 2.4 FP2 sensor positioning and power (Awning + Light4)
![FP2 orientation and coverage](https://drive.google.com/uc?export=view&id=1WVI5SHkc_YI7gLS-H1U6NgtyR1xQtuyX)

1. Locate target detection area per Figure 1.
2. Adjust orientation/coverage based on figure and site.
3. Trial place with magnetic mount; fix after detection confirms.
4. Complete power/cable fixation.
5. Run Awning + Light4 trigger check and record successful zone.

**Verification Criteria**
- [ ] FP2 stably detects Awning + Light4
- [ ] Installation remains quickly removable
- [ ] Power/cabling complete and safe

---

## 3. Host Placement (site-based)
<div style="page-break-after: always;"></div>

> **Done state for this chapter:** host is in maintainable position, cables fixed, PC logged in and connected to `qa_rpt` with internet access.

### SOP Block (Chapter 3)
- Objective/preconditions/procedure follow Chinese version structure.

### 3.1 Purpose
Determine final host position based on space, cooling, maintenance path, and cable lengths.

### 3.2 Principles
- dry/ventilated/maintainable
- avoid heat/humidity/collision zones
- consider cable lengths to hub/burner/audio/arm
- quick access to power/network

### 3.2.1 PC boot and network check (`qa_rpt`)
1. **[Required]** Connect monitor/keyboard/mouse.
2. **[Required]** Log in with installer account (see 0.6).
3. **[Required]** Confirm Wi‑Fi SSID is `qa_rpt`.
4. **[Required]** Confirm internet access via browser.

### 3.3 Verification Criteria
- [ ] Host position does not block operation/maintenance
- [ ] Host power/network stable
- [ ] Related cabling fixed safely
- [ ] PC logged in on `qa_rpt` with internet access

---

## 4. Burner / USB Extension / USB Hub Configuration (to PC)
<div style="page-break-after: always;"></div>

### 4.1 Purpose
Complete stable topology for burner, hub, extension, and PC.

### 4.2 Steps
1. Confirm burner and hub positions.
2. Route extension cable safely.
3. Connect `Burner -> USB Hub -> USB Extension -> PC`.
4. (Optional) Add labels.
5. Verify device detection at PC.

### 4.3 Verification Criteria
- [ ] All burners recognized by PC
- [ ] Hub/extension cabling fixed safely
- [ ] No intermittent disconnects in 10-minute observation

---

## 5. Robotic Arm and Panel Configuration
<div style="page-break-after: always;"></div>

> **Done state for this chapter:** arm fixed, panel placement correct, cabling safe, RobotArm controller logged in and connected to `qa_rpt`.

### 5.1 Purpose
Complete robotic arm and panel installation with safe fixation and wiring.

### 5.2 Steps
1. Connect rear USB‑A to end USB‑C (first install).
2. Fix arm base and confirm no motion interference.
3. Install panels (3611A/3611C/WF-3534).
4. Confirm all cables connected and no pinch/crossing moving parts.
5. Final pre-power check.

### 5.2.1 RobotArm controller boot and network check (`qa_rpt`)
1. **[Required]** Connect monitor/keyboard/mouse to RobotArm controller PC.
2. **[Required]** Boot and log in (see 0.6).
3. **[Required]** Confirm Wi‑Fi SSID is `qa_rpt`.
4. **[Required]** Confirm internet access via browser.
5. **[Only if needed]** If not on `qa_rpt`, fix network before continuing.

### 5.3 Verification Criteria
- [ ] Arm fixed and movement range normal
- [ ] Panel positions correct and maintainable
- [ ] Cabling complete and safe
- [ ] RobotArm controller logged in and connected to `qa_rpt`

### 5.4 Safety / Power-on Rules
1. No power during wiring/fastening.
2. Check orientation/terminal mapping before power-on.
3. UART mapping: `G->G`, `RX->TX`, `TX->RX`.
4. No cables under moving/stepping/door/flip areas.
5. Confirm outward-facing interfaces and clear movement.
6. Main power connection is last step.

### 5.5 3611A/3511A position switching (by test purpose)
1. Voice test: move back to wall position.
2. Arm click test: mount 3611A to arm base after arm setup.
3. Update label/photo each switch.

---

## 6. Final Acceptance and Delivery Status
<div style="page-break-after: always;"></div>

### 6.1 Chapter checklist
- [ ] Chapter 1 overview complete
- [ ] Chapter 2 Wi‑Fi/IPCAM/Speaker/Scarlett4i4/FP2 installation complete
- [ ] Chapter 3 host placement complete
- [ ] Chapter 4 burner/USB/hub/PC connection complete
- [ ] Chapter 5 robotic arm/panel setup complete
- [ ] Chapter 2 records and photos updated

### 6.2 Final status
- Status: `Ready / Blocked / Rework`
- Blocked reason: `<fill if blocked>`
- Owner sign-off: `<Owner Name>`
- Date: `YYYY-MM-DD`

---

## 7. New Installer Quick Troubleshooting
<div style="page-break-after: always;"></div>

| Symptom | Possible cause | First action | If still failing | Notify |
|---|---|---|---|---|
| Cannot find `qa_rpt` | Wi‑Fi not powered/too far | Check Router/AP power/LED | Use Extender or adjust location | On-site installation owner |
| IPCAM no stream | Network/power unstable | Replug power and confirm `qa_rpt` | Record CAM ID, mark `Blocked`, move to later testing chapter | On-site installation owner |
| PC cannot detect burner | USB path/connector loose | Replug `Burner -> Hub -> Extension -> PC` | Replace extension or hub port | On-site installation owner |
| Robotic arm abnormal | Cable interference/wrong mapping | Power off and check UART and movement range | Mark `Blocked`, fix then power on | On-site installation owner |

---

## Appendix C — On-site Acceptance Forms
<div style="page-break-after: always;"></div>

### C.2 One-page printable checklist
- File: `docs/ch2_onsite_acceptance_onepage_zh.md`

### C.3 Full acceptance table (unified)
> New installers can fill only minimum fields first: `Item ID/Name`, `Power Done`, `Wiring/Connection`, `Notes (including Blocked reason)`.

(Use the same table structure as Chinese version.)

---

## Appendix A — Naming Convention
- Device: `CAM-01`, `SPK-01`, `ARM-CTRL-01`
- Hub Port: `H1-P01`, `H2-P03`
- Cable: `C-001`, `UART-01`, `USB-EXT-01`
- Node: `WF-3611-A`, `WF-3611-C`, `WF-3611-B`

## Appendix B — Document Control
- Author: `<Owner Name>`
- Reviewer: `<Reviewer Name>`
- Effective Date: `YYYY-MM-DD`
- Revision History:
  - v1.0 initial draft
  - v1.2 synced with latest Chinese version

## Appendix D — Plain-language Terms
- **Backhaul**: connection path from extender back to core network
- **Extender**: Wi‑Fi signal extender
- **IPCAM**: network camera for live view
- **Scarlett 4i4**: audio interface for speaker output
- **FP2**: sensor for Awning + Light4 trigger behavior
- **Burner**: USB device for flashing/board connection
- **Blocked / Rework**:
  - `Blocked`: cannot proceed without external support
  - `Rework`: can proceed after redo/fix
