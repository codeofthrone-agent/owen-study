# Automation Test System Installation Guide

> Document Type: Standard Operating Procedure (SOP)  
> Version: v1.1 (Draft)  
> Last Updated: 2026-05-08  
> Scope: WFCO PwrPro automated test environment (Robotic Arm + Control Boards + Hub + IPCAM + Speaker + Wi‑Fi)

### SOP Document Control
| Field | Content |
|---|---|
| Owner | `<Owner Name>` |
| Reviewer | `<Reviewer Name>` |
| Effective Date | `YYYY-MM-DD` |
| Change Type | Chapter-opening diagram restructuring + SOP formatting |

### How to Use This SOP
1. Execute steps in chapter order; do not skip safety checks.  
2. Complete the corresponding checklist at the end of each chapter.  
3. If site conditions differ from this document, stop and log a controlled change.

---

## 1. System Overview and Network Architecture

### Chapter Overview Diagrams (Figure 1 + Figure 2)
![System Layout](https://drive.google.com/uc?export=view&id=1ZMmWd5I4OJ7QmjIPW4ioC2KNTBS-2iXt)

*Figure 1: System Layout (zone-based physical placement overview)*

![Network and Device Topology](https://drive.google.com/uc?export=view&id=1roD82kDBS9iYUXlkyvy0cbKczhOMT1Ts)

*Figure 2: Network and Device Topology (board/hub/camera/arm/network relationships)*

> This chapter defines the baseline from two dimensions—physical layout and network topology—before wiring and assembly execution.

### SOP Block (Chapter 1)
- **Objective**: Define system boundary, topology, and deployment prerequisites.
- **Preconditions**: Hardware, cables, and tools are ready; power remains OFF.
- **Procedure**: Confirm scope -> validate topology -> confirm material and network prerequisites.
- **Verification**: Check naming, wiring order, and pre-power safety conditions against chapter rules.
- **Pass Criteria**: Architecture baseline and prerequisites are confirmed with no unresolved high-risk items.
- **Exceptions**: If site topology or device inventory differs from this SOP, stop work and log a controlled change.

### 1.1 Project Scope and Objectives
This document provides a repeatable and maintainable installation procedure for an automated test system. Objectives:

- Establish a stable hardware installation and wiring process
- Ensure coordinated operation across control boards, hubs, robotic arm, cameras, and audio devices
- Define standardized validation and troubleshooting workflows
- Reduce deployment time and rework risk

---

### 1.2 System Topology and Architecture Overview
The system consists of the following subsystems:

- **Control/Compute Subsystem**: main controller, control boards (WF-3534 / 3611A / 3611C)
- **I/O and Data Subsystem**: USB hubs, extension cables, imaging and other expansion peripherals
- **Sensing and Actuation Subsystem**: IPCAM, speakers, RobotArm board, robotic arm
- **Network Subsystem**: Wi‑Fi router, test SSID, and device network grouping
- **Spatial Deployment Subsystem**: zone-based physical layout and cable routing paths

---

### 1.3 Hardware, Tools, and Cable Requirements

#### A. Main Hardware
- Control boards: 3611A, 3611C, WF-3534
- USB hubs (multi-port)
- IPCAM (x5, adjustable by project needs)
- Speakers (x4)
- RobotArm board (based on deployment points)
- Robotic arm unit and base plate
- Router (Wi‑Fi AP)

#### B. Cables and Accessories
- USB Type‑A cables
- L-shaped Type‑C to Type‑A cables
- UART wires (G / RX / TX)
- USB extension cable (e.g., 10m, assess power and signal attenuation)
- Double-sided tape, cable mounts, screws, cable ties, labeling stickers

#### C. Tools
- Screwdrivers (matching required screw types)
- Cable label printer (recommended)
- Multimeter (continuity/short checks before power-on)
- Laptop (installation, configuration, validation)

---

### 1.4 Network Architecture and Prerequisites

#### A. Basic Network Settings
- Test Wi‑Fi SSID: `qa_rpt`
- Test Wi‑Fi Password: `12345678`

> Best practice: maintain separate credentials for production and lab usage to reduce leakage risk.


---

### 1.5 Safety, Power Isolation, and Power-On Rules

1. **Do not apply power during wiring and mechanical fastening**
2. Verify connector orientation and terminal mapping before power-on
3. UART wiring must follow:
   - `G -> G`
   - `RX -> TX`
   - `TX -> RX`
4. Prevent cables from being pinched by moving parts, steps, doors, or flip panels
5. After arm installation, ensure interface faces outward and movement is unobstructed
6. Connect main power only as the final step

---

## 2. Control Boards and Hubs Wiring Guide

### Chapter Overview Diagram
![Wiring Detail](https://drive.google.com/uc?export=view&id=1XE3O7h17guDEkzzsTE8ZMLZFj0ecc8tY)

> This chapter focuses on board-to-hub wiring direction, port planning, and labeling rules to prevent RX/TX or port mapping errors.

### SOP Block (Chapter 2)
- **Objective**: Complete board and hub wiring design with stable communication and power distribution.
- **Preconditions**: Board models, port naming convention, and cable specs are confirmed.
- **Procedure**: Define hub hierarchy and port map first, then execute orientation rules and labeling.
- **Verification**: Run checklist 2.6 to verify power, detection, UART mapping, and labels.
- **Pass Criteria**: All nodes are detectable, no reverse/wrong insertion, and cable fixation is complete.
- **Exceptions**: If ports are insufficient or conflicting, update the routing table before continuing work.

### 2.1 Control Board Roles and Interface Map
- **3611A / 3611C**: zone control/interface boards
- **WF-3534**: inter-board connection and control aggregation node
- **RobotArm board**: robotic arm control logic board

---

### 2.2 Hub Topology and Port Allocation
Recommended hierarchy: **Main Hub -> Sub Hub -> End Devices**

- Main hub: connects main controller and primary I/O
- Sub Hub A: control-board and serial-adapter peripherals (as needed)
- Sub Hub B: IPCAM / speaker / RobotArm-related peripherals (as needed)
- Sub Hub C: imaging and other expansion peripherals (as needed)

> Assign a unique label to every port: `H1-P01`, `H1-P02`, `H2-P01`, etc.

---

### 2.3 Cable and Connector Standards
- USB Type‑A: general data/peripheral links
- L-Type C to A: board-to-board or board-to-interface box links
- UART: inter-board communication, requires RX/TX crossover
- Extension cable: beyond 5m requires signal and power quality evaluation

---

### 2.4 Wiring Rules and Direction Requirements
Connector direction rules (per diagram):

- `First Right`
- `First Top`
- `First Bottom`

These direction rules must match board model specifics. Different boards may have different first-pin orientations.  
Do not force insertion when uncertain.

---

### 2.5 Wiring Labels, Node IDs, and Routing Table

#### A. Node Naming (Example)
- `WF-3611-A` (left/entry area)
- `WF-3611-C` (mid-right/walkway area)
- `WF-3611-B`, `WF-3610-B`, `WF-3511-B` (Pass-thru storage)

#### B. Wiring Table Template (Recommended)
| Cable ID | Source | Destination | Connector Type | Route | Label | Status |
|---|---|---|---|---|---|---|
| C-001 | WF-3534 | 3611A | USB-C (angled) | behind left-middle cabinet | WF-3611A-L1 | Installed |
| C-002 | WF-3534 | 3611C | USB-C (angled) | under central walkway | WF-3611C-L1 | Installed |
| C-003 | UART-01 | Control Header | G/RX/TX | short inter-board path | UART-X | Verify |

---

### 2.6 Verification Checklist for Board-to-Hub Connections
- [ ] All hubs are powered
- [ ] Main controller detects hubs and card readers
- [ ] UART pin order is correct (G/G, RX/TX crossover)
- [ ] Cable labels are applied
- [ ] No loose connectors, sharp bends, or cable pinching

---

### 2.7 Common Wiring Errors and Quick Recovery
| Symptom | Possible Cause | Quick Action |
|---|---|---|
| Device not detected | Wrong hub port / insufficient hub power | Move to main hub, verify power |
| No serial response | RX/TX not crossed or reversed | Re-check UART mapping |
| Intermittent disconnects | Overlong extension / signal attenuation | Shorten cable or use active extender |
| Device offline after boot | Not on same SSID | Reconnect to `qa_rpt`, verify DHCP |

---

## 3. Robotic Arm and Base Hardware Assembly

### Chapter Overview Diagram
![Robot Arm Assembly](https://drive.google.com/uc?export=view&id=1z1aUfe4O4kPEcjyr5Lg8QLkneW-JKC36)

> This chapter centers on robotic arm assembly, emphasizing fastening order, flip-over handling, cable slack, and pre-power validation.

### SOP Block (Chapter 3)
- **Objective**: Complete robotic arm and base assembly with mechanical and cable safety.
- **Preconditions**: Base plate, mounts, screws, boards, and cables are prepared.
- **Procedure**: Follow section 3.2 for fastening, wiring, flip-over handling, and final checks.
- **Verification**: Verify fastening quality, movement range, cable slack, and interference status.
- **Pass Criteria**: Arm can operate safely without looseness, cable tension, or abnormal noise risk.
- **Exceptions**: If interference appears during flip-over or trial motion, power off and roll back one step for correction.

### 3.1 Assembly Preparation
- Confirm base plate, mounts, tape, and screws are complete
- Prepare 3611A / 3611C / WF-3534 and all cables
- Confirm screw type/spec from robotic arm package

---

### 3.2 Step-by-Step Assembly

#### Step 1 — Mount and Tape Positioning
- Remove tape backing
- Place mounts at designated positions (avoid reserved openings)

#### Step 2 — Install 3611A / 3611C
- Insert both panels into their slots
- Fasten with screws (avoid over-torque)

#### Step 3 — Board Wiring
- Connect WF-3534, L-shaped Type‑C/Type‑A cables, and UART
- Follow UART rule: `G/G, RX/TX crossover`

#### Step 4 — Flip and Mount Robotic Arm
- After rear-side cabling is complete, flip assembly
- Place arm on base with **interface facing outward**
- Tighten mounting screws

#### Step 5 — Final Pre-Power Check
- Verify movement range, cable slack, and fasteners
- Apply power only after checks are complete

---

### 3.3 Mechanical and Cable Safety Notes
- Keep service loop for cables to prevent tension during arm movement
- Do not route cables across high-heat (HVAC) or sharp edges
- Keep at least 20~30mm clearance from moving parts (adjust per site)

---

## 4. Device Spatial Deployment and Positioning

### Chapter Overview Diagram
![System Layout](https://drive.google.com/uc?export=view&id=1ZMmWd5I4OJ7QmjIPW4ioC2KNTBS-2iXt)

> This chapter defines zone-based placement and spatial constraints to ensure coverage quality, maintainability, and safe cable routing.

### SOP Block (Chapter 4)
- **Objective**: Build a maintainable and safe spatial deployment and device placement plan.
- **Preconditions**: Site zoning, device counts, and cable routing constraints are confirmed.
- **Procedure**: Define zones first, then place devices by function and routing constraints.
- **Verification**: Validate coverage quality, maintainability, routing safety, and service accessibility.
- **Pass Criteria**: Each zone has valid placement, safe routing, and accessible maintenance windows.
- **Exceptions**: If structural constraints require deviations, document alternate routes and risk notes.

### 4.1 Zoning Strategy
Deploy by area zones (Zone 1~4):
- Zone 1: living/main traffic path
- Zone 2: kitchen/mid section
- Zone 3: bathroom/corridor
- Zone 4: bedroom/front compartment

---

### 4.2 Device Placement Guidelines
#### IPCAM
- Prioritize entry points, primary pathway, and robotic arm work area
- Avoid backlight, reflective surfaces, and blind spots

#### Speaker
- Distribute by zone; avoid one-sided concentration
- Keep distance from high-interference bundles and control boards

#### RobotArm board
- Prefer serviceable locations (e.g., near pass-thru storage)
- Ensure easy maintenance and replug access

---

### 4.3 Routing Constraints
- Avoid exposed routes in wet areas
- Avoid frequently opened/closed door and panel edges
- Prefer routing behind cabinets, under flooring, or in fixed cable channels

---

### 4.4 Maintenance Accessibility
- Keep labels facing outward
- Preserve access to test points
- Ensure at least one service access point per zone

---

## 5. Commissioning, Validation, and Troubleshooting

### SOP Block (Chapter 5)
- **Objective**: Complete power-on, functional validation, and troubleshooting to reach handover-ready status.
- **Preconditions**: Installation and checks from Chapters 1-4 are complete.
- **Procedure**: Execute pre-power checks -> power-on sequence -> functional validation -> failure handling.
- **Verification**: Verify results against section 5.3 and acceptance checklist 5.5.
- **Pass Criteria**: Critical devices are online, continuous run test passes, and handover records are complete.
- **Exceptions**: If high-risk anomalies occur (overheat/abnormal noise/repeated disconnects), stop operation immediately and escalate.

### 5.1 Pre-Power Checklist
- [ ] All screws are tightened
- [ ] Cable order and orientation verified
- [ ] Hub and control board connections complete
- [ ] Network settings verified (SSID/password)
- [ ] No movement interference in arm workspace
- [ ] Safety review complete for power-on

---

### 5.2 Power-On Sequence
1. Power on router and network devices  
2. Power on main controller and hubs  
3. Power on control boards and arm system  
4. Verify audio interface indicator (green light)  
5. Validate IPCAM and speaker online status

---

### 5.3 Functional Validation
- **Network**: all devices connected to `qa_rpt`
- **Boards**: 3611A/3611C/WF-3534 communication OK
- **UART**: normal response, no packet errors
- **Video**: camera stream accessible
- **Audio**: speaker playback/alert works
- **Arm**: basic motion complete without abnormal noise/vibration

---

### 5.4 Common Failures and Recovery
| Failure | Checkpoint | Action |
|---|---|---|
| Router up but devices offline | SSID/password/DHCP | Reconfigure network, reboot device |
| Board communication failure | UART mapping | Rewire RX/TX |
| Intermittent disconnect | Hub power/extension cable | Improve power, shorten cable |
| Arm motion abnormal | Mounting/cable interference | Re-route cables and re-align arm |

---

### 5.5 Acceptance Criteria and Handover
Acceptance requires:

- [ ] All critical devices online and controllable
- [ ] Continuous operation test passed (recommended >= 30 minutes)
- [ ] Wiring/port/node tables updated
- [ ] Site photos and revision logs archived
- [ ] Troubleshooting SOP handed over

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
