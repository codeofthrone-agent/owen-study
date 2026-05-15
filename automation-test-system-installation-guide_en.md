# Automation Test System Installation Guide  

> Document Type: Standard Operating Procedure (SOP)  
> Version: v1.2 (Draft)  
> Last Updated: 2026-05-15  
> Scope: WFCO PwrPro automated test environment (Robotic Arm + Control Boards + Hub + IPCAM + Speaker + Wi‑Fi)

### SOP Document Control
| Field | Content |
|---|---|
| Owner | `<Owner Name>` |
| Reviewer | `<Reviewer Name>` |
| Effective Date | `YYYY-MM-DD` |
| Change Type | Added SOP blocks for Chapters 2–5 + revised Wi‑Fi/IPCAM/FP2/robotic-arm steps + synced EN with latest ZH |

### How to Use This SOP
1. Execute steps in chapter order; do not skip safety checks.  
2. Complete the corresponding checklist at the end of each chapter.  
3. If site conditions differ from this document, stop and log a controlled change.

---

## 1. System Overview

### Chapter Overview Diagrams (Figure 1 + Figure 2)
![System Layout](https://drive.google.com/uc?export=view&id=1_xDdE393fwM6hEDepC55_PjGOVfhiuoX)

*Figure 1: System Layout (overall zoning and device placement)*

![Network and Device Topology](https://drive.google.com/uc?export=view&id=1roD82kDBS9iYUXlkyvy0cbKczhOMT1Ts)

*Figure 2: Network and Device Topology (relationships among boards, hub, camera, arm, and network)*

> This chapter establishes the system baseline, then completes installation and acceptance of Wi‑Fi, IPCAM, Speaker/Scarlett 4i4, and FP2.

### SOP Block (Chapter 1)
- **Objective**: Complete Chapter 1 on-site baseline deployment (Wi‑Fi, IPCAM, Speaker/Scarlett 4i4, FP2) and make it acceptance-ready.
- **Preconditions**: Figure 1/2 available for reference, devices and cables ready, IPCAM can use `qa_rpt`, on-site power points confirmed.
- **Procedure**: Execute in order: **Wi‑Fi location + cabling/power -> IPCAM placement + power -> Speaker placement + Scarlett 4i4 cabling -> FP2 (Awning + Light4) placement + power**.
- **Verification**: Use Appendix C unified checklist to verify location, power, cabling, and functional tests.
- **Pass Criteria**: All four device categories installed; `qa_rpt`, video streaming, audio output, and FP2 trigger test are all verified.
- **Exceptions**: If site differs from diagrams, or power/cabling constraints or failed tests occur, mark `Blocked/Rework` and record reason before moving on.

### 1.1 Project Scope and Objectives
This document defines a repeatable and maintainable installation process for an automated test system. Objectives:

- Build a stable hardware installation and wiring workflow
- Ensure coordinated operation across control boards, hub, robotic arm, cameras, and audio devices
- Establish standardized acceptance and troubleshooting procedures
- Reduce deployment time and rework risk

---

### 1.2 System Topology and Architecture Overview
The system includes the following subsystems:

- **Control/Compute Subsystem**: main controller, control boards (WF-3534 / 3611A / 3611C)
- **I/O and Data Subsystem**: USB hub, extension cables, burner, and related peripherals
- **Sensing and Actuation Subsystem**: IPCAM, speaker, crossover, FP2, RobotArm board, robotic arm
- **Network Subsystem**: Wi‑Fi router, test SSID, and network grouping
- **Spatial Deployment Subsystem**: zone-based placement and cable paths

---

### 1.3 Wi‑Fi Location Evaluation and Power/Cabling Planning
1. Based on Figure 1, identify candidate locations for Wi‑Fi equipment (Router / AP / Extender), prioritizing coverage of **main operator pathways** and **actual IPCAM installation areas**.
2. For each candidate location, evaluate:
   - Power feasibility (distance to outlets, extension route, fixation)
   - Cabling feasibility (whether LAN cable can be routed safely)
3. Choose one network backhaul option based on site conditions:
   - **LAN wired backhaul**: preferred when cabling path is safe and feasible.
   - **Wi‑Fi Extender wireless extension**: used when routing LAN is difficult or cross-zone extension is needed.
4. Finalize device placement, power, and cable fixation; avoid moving mechanisms and high-risk areas.
5. After enablement, confirm SSID is `qa_rpt`, and record final placement, power points, and chosen link method (LAN / Extender).

**Acceptance Criteria**
- [ ] Wi‑Fi device placement satisfies Figure 1 coverage requirements
- [ ] LAN or Extender option selected and rationale recorded
- [ ] Power and cabling completed and fixed
- [ ] `qa_rpt` connection is stable
- [ ] IPCAM and host can both connect to `qa_rpt` (sample at least 1 IPCAM)

---

### 1.4 IPCAM Positioning and Power (Wi‑Fi Preconfigured Before Shipment)
> IPCAM units are preconfigured with Wi‑Fi before shipment; on site, only positioning, power, and connectivity checks are required.

1. After power-on, confirm IPCAM can load existing Wi‑Fi setting (`qa_rpt`).
2. Follow the network approach selected in 1.3: prefer LAN if feasible; otherwise use planned Wi‑Fi Extender coverage.
3. Place each IPCAM at the Figure 1 observation position and confirm view coverage.
4. Complete power and cable fixation; avoid pinching, tension, and high-heat zones.
5. Apply labels/mapping (`CAM-xx` + actual zone).
6. **After both 1.3 and 1.4 are completed, notify the Taipei team to remotely connect for monitoring and fine-tune camera positions.**

**Acceptance Criteria**
- [ ] All IPCAM units are at Figure 1 designated positions
- [ ] All IPCAM units have stable power and are online
- [ ] Host can access all streams
- [ ] Taipei team has been notified and remote monitoring session completed

---

### 1.5 Speaker Placement, Power, and Cabling (to Scarlett 4i4)
1. Place speakers according to Figure 1 so prompt tones cover the test area.
2. Complete power and fixation for each speaker.
3. Complete cabling and route back to the audio interface.
4. Position Scarlett 4i4 in a maintainable, cool, and cable-safe location.
5. Connect speaker output lines to Scarlett 4i4 ports and apply labels.

**Acceptance Criteria**
- [ ] Speaker placement matches Figure 1
- [ ] Speaker power and cabling complete
- [ ] Scarlett 4i4 fixed in place with clear wiring

---

### 1.6 FP2 Sensor Positioning, Installation, and Power (Awning + Light4)

#### Figure: Installation Orientation and Coverage
![FP2 installation orientation and coverage](https://drive.google.com/uc?export=view&id=1WVI5SHkc_YI7gLS-H1U6NgtyR1xQtuyX)

1. FP2 is mainly used to detect **Awning + Light4**; first locate the target detection zone based on Figure 1.
2. Confirm installation orientation and coverage based on the figure, then adjust to a suitable position according to real site conditions.
3. Use FP2 magnetic mounting for trial placement; secure it after trigger behavior is verified.
4. Complete power and cable fixation while keeping maintainability space.
5. Run Awning + Light4 trigger tests and record successful trigger zones.

**Acceptance Criteria**
- [ ] FP2 can stably detect Awning + Light4
- [ ] Installation is quickly removable (magnetic mount)
- [ ] Power is complete and cabling is safe

---

## 2. Host Placement (Site-Based)

### Chapter Figure
![System Layout](https://drive.google.com/uc?export=view&id=1_xDdE393fwM6hEDepC55_PjGOVfhiuoX)

*Figure: System Layout (host location should follow maintainability and routing constraints)*

### SOP Block (Chapter 2)
- **Objective**: Determine final host location based on site conditions, balancing cooling, maintainability, and cable reachability.
- **Preconditions**: Chapter 1 complete, Figure 1 available, host/power/network interfaces available.
- **Procedure**: Execute in order: **candidate evaluation -> power/network reachability check -> related cable path check -> host fixation and marking**.
- **Verification**: Use 2.3 to verify maintainability, stable power/network, and cable fixation.
- **Pass Criteria**: Host position does not obstruct operations; power/network/related routing are all stable.
- **Exceptions**: If blocked by space/cooling/routing constraints, mark `Blocked/Rework` and record alternative location and reason.

### 2.1 Purpose
Based on actual site space, cooling, maintenance path, and cable length, determine the final host location.

### 2.2 Placement Principles
- Prioritize dry, ventilated, and maintainable locations
- Avoid high-heat, humid, or collision-prone zones
- Consider routing lengths for USB hub, burner, audio interface, and robotic-arm control cables
- Ensure quick access to power and network interfaces

### 2.3 Acceptance Criteria
- [ ] Host placement does not obstruct operation/maintenance
- [ ] Host power and network are stable
- [ ] Related cable lengths are reasonable and fixed

---

## 3. Burner / USB Extension / USB Hub Configuration (Back to PC)

### Chapter Figure
![Wiring Detail](https://drive.google.com/uc?export=view&id=1XE3O7h17guDEkzzsTE8ZMLZFj0ecc8tY)

*Figure: Wiring Detail (reference for burner, hub, extension routing to PC)*

### SOP Block (Chapter 3)
- **Objective**: Complete stable topology for burner, USB extension, and USB hub, ensuring sustainable connection to PC.
- **Preconditions**: Host location fixed; hub and burner can be powered; PC device detection available.
- **Procedure**: Execute in order: **device positioning -> USB path routing -> topology connection (burner->hub->extension->PC) -> (Optional) labeling -> PC detection verification**.
- **Verification**: Use 3.3 to verify detection rate, link stability, and cabling safety.
- **Pass Criteria**: All target devices can be stably detected by PC with no intermittent disconnects over time.
- **Exceptions**: If extension length/quality is insufficient or signal unstable, mark `Rework` and change route/cable.

### 3.1 Purpose
Complete topology for burner, USB extension cable, and USB hub to ensure stable back-connection to PC.

### 3.2 Configuration Steps
1. Confirm installation locations for burner and USB hub (near maintenance area, avoid cable tension).
2. Route USB extension cable along site path, avoiding doors, moving mechanisms, and high-heat areas.
3. Connect: `Burner -> USB Hub -> USB Extension -> PC`.
4. (Optional) Create labels for cables and interfaces as needed (e.g., `H1-P01`, `USB-EXT-01`, `BURNER-01`).
5. On PC, confirm devices are recognized and remain stable.

### 3.3 Acceptance Criteria
- [ ] All burners can be recognized by PC
- [ ] USB extension and hub cabling is fixed and safe
- [ ] No intermittent disconnects during long-run connection

---

## 4. Robotic Arm and Panel Configuration

### Chapter Figure
![Robot Arm Assembly](https://drive.google.com/uc?export=view&id=1z1aUfe4O4kPEcjyr5Lg8QLkneW-JKC36)

*Figure: Robot Arm Assembly (reference for robotic arm and panel installation)*

### SOP Block (Chapter 4)
- **Objective**: Complete robotic arm and panel installation with reliable fixation, correct cable connections, and safe power-on readiness.
- **Preconditions**: Base mounting surface is available; required cables are ready; pre-power safety rules confirmed.
- **Procedure**: Execute in order: **initial USB-A ↔ USB-C connection -> arm base fixation -> panel installation -> full cable connection check -> final pre-power inspection**.
- **Verification**: Use 4.3 and 4.4 to verify fixation status, cable safety, and power-on rules.
- **Pass Criteria**: Arm movement range is normal, panel location is correct, and cabling meets safety requirements.
- **Exceptions**: If interference, loose connectors, or cable compression occurs, mark `Blocked/Rework` and fix before power-on.

### 4.1 Purpose
Complete installation of robotic arm and panels (control boards), ensuring safe fixation, cabling, and operation.

### 4.2 Configuration Steps
1. During first installation, connect rear-arm **USB‑A** to end-effector **USB‑C** first.
2. Fix robotic arm base according to the diagram and confirm movement range has no interference.
3. Install panels (e.g., 3611A / 3611C / WF-3534) at designated positions.
4. Verify all cables are connected, and ensure no cable pinching or crossing over moving parts.
5. Perform final pre-power inspection.

### 4.3 Acceptance Criteria
- [ ] Robotic arm is firmly fixed and movement range is normal
- [ ] Panel positions are correct and maintainable
- [ ] Cabling is complete and compliant with safety rules

### 4.4 Safety, Power Isolation, and Power-On Rules

1. **Do not power on during wiring and mechanical fastening**
2. After all cable insertion is complete, verify orientation and terminal mapping before power-on
3. UART mapping must follow:
   - `G -> G`
   - `RX -> TX`
   - `TX -> RX`
4. Cables must not be routed under moving mechanisms, steps, doors, or flip panels
5. After arm fixation, ensure interface faces outward and movement range is unobstructed
6. Connect main power and boot only as the final step

---

## 5. Overview Review Status

### SOP Block (Chapter 5)
- **Objective**: Complete final whole-document acceptance and status decision for handover.
- **Preconditions**: Chapters 1–4 are complete with corresponding check records.
- **Procedure**: Execute in order: **chapter result review -> gap fix/marking -> final status reporting -> owner sign-off**.
- **Verification**: Check completeness of 5.1 and 5.2 fields (Status, Blocked Reason, Sign-off, Date).
- **Pass Criteria**: All required fields complete and status traceable (Ready/Blocked/Rework).
- **Exceptions**: If records are incomplete, temporarily mark `Rework` and close only after backfill.

### 5.1 Chapter Summary Checklist
- [ ] Chapter 1: Overview + Wi‑Fi/IPCAM/Speaker/Scarlett4i4/FP2 completed
- [ ] Chapter 2: Host placement confirmed
- [ ] Chapter 3: Burner/USB extension/Hub/PC connection completed
- [ ] Chapter 4: Robotic arm and panel configuration completed

### 5.2 Final Status
- **Status**: `Ready / Blocked / Rework`
- **Blocked Reason**: `<fill if blocked>`
- **Owner Sign-off**: `<Owner Name>`
- **Date**: `YYYY-MM-DD`

---

## Appendix C — On-Site Acceptance Diagram and Forms

### C.1 Diagram (follow Figure 1 logic, Wi‑Fi excluded)
(Diagram removed. On site, use Chapter 1 Figure 1: System Layout.)

### C.2 One-Page Printable Checklist (large checkbox fields)
- File: `docs/ch1_onsite_acceptance_onepage_zh.md`

### C.3 Full On-Site Acceptance Table (Unified)

| Category | Item ID/Name | Figure-1 Zone | Actual Position | Power Done (Y/N) | Wiring/Connection | Functional Test Result | Acceptance (Pass/Fail) | Notes |
|---|---|---|---|---|---|---|---|---|
| Wi‑Fi | WIFI-01 Router/AP |  |  |  | Wired/Extender | SSID `qa_rpt` link: Normal/Abnormal |  |  |
| Wi‑Fi | WIFI-EXT-01 Extender (if used) |  |  |  | Wired/Extender | Signal extension: Normal/Abnormal |  |  |
| IPCAM | CAM-01 |  |  |  | Wired/Extender | Stream: Normal/Abnormal |  |  |
| IPCAM | CAM-02 |  |  |  | Wired/Extender | Stream: Normal/Abnormal |  |  |
| IPCAM | CAM-03 |  |  |  | Wired/Extender | Stream: Normal/Abnormal |  |  |
| IPCAM | CAM-04 |  |  |  | Wired/Extender | Stream: Normal/Abnormal |  |  |
| Speaker | SPK-01 |  |  |  | Scarlett 4i4 port: | Playback: Normal/Abnormal |  |  |
| Speaker | SPK-02 |  |  |  | Scarlett 4i4 port: | Playback: Normal/Abnormal |  |  |
| Speaker | SPK-03 |  |  |  | Scarlett 4i4 port: | Playback: Normal/Abnormal |  |  |
| Audio Interface | Scarlett 4i4 |  |  |  | I/O cabling done (Y/N) | Audio routing: Normal/Abnormal |  |  |
| Sensor | SEN-FP2-01 (Awning + Light4) |  |  |  | Magnetic mount (Y/N) | Trigger: Normal/Abnormal |  |  |
| Host | Host PC |  |  |  | Hub/burner back-link done (Y/N) | Device detection: Normal/Abnormal |  |  |
| Arm/Panels | Robot Arm + Panels |  |  |  | Cable safety check (Y/N) | Motion/communication: Normal/Abnormal |  |  |

| Owner | Date | Final Status |
|---|---|---|
|  |  | Ready / Blocked / Rework |

---

## Appendix A — Recommended Naming Convention
- Device: `CAM-01`, `SPK-01`, `ARM-CTRL-01`
- Hub Port: `H1-P01`, `H2-P03`
- Cable: `C-001`, `UART-01`, `USB-EXT-01`
- Node: `WF-3611-A`, `WF-3611-C`, `WF-3611-B`

## Appendix B — Document Control
- Author: `<Owner Name>`
- Reviewer: `<Reviewer Name>`
- Effective Date: `YYYY-MM-DD`
- Revision History:  
  - v1.0 Initial draft
  - v1.2 Synced with latest Chinese version
