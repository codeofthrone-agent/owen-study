# Proposal: Robot Arm Calibration Script

This proposal outlines the creation of a standalone calibration script to find the optimal `down_angles` and `up_angles` for robot arm buttons, specifically targeting the `lcd_a` button in the Taipei Lab environment.

## Goal

Automate the search for robot arm joint angles that yield the highest success rate, verified by receiving an `A_KEY` trigger from the serial port `/dev/cu.wchusbserial3140` at 115200 baud.

## What Changes

1. **New Script**: `scripts/robot_arm_calibration.py`
   - A Python script that performs a grid search or randomized jitter search around a base coordinate.
   - Integrated serial monitoring using `pyserial`.
   - Direct integration with `MyCobotSocketController` for rapid command execution.
2. **Logging**:
   - Save calibration results to `output/calibration_results_<timestamp>.csv` including:
     - Joint angles (J1-J6)
     - Timestamp
     - Serial feedback status (Success/Failure)
     - Delay between press and feedback.

## Capabilities

### New Capabilities
- `robot-arm-calibration`: A script to automatically iterate through robot arm angles and verify success via serial feedback.

## Impact

- **Affected Systems**: `MyCobotSocketController`, `taipei_lab_buttons.yaml` (via reference).
- **Dependencies**: `pyserial`, `loguru`.
- **Hardware**: Requires the MyCobot 280 and the serial-enabled LCD panel to be connected.

## Proposed Search Strategy

1. **Base Angles**: Start from the current values in `taipei_lab_buttons.yaml`.
2. **Search Grid**:
   - Focus on **J2** (depth) and **J3** (height) as they are the primary joints affecting click precision.
   - Range: +/- 2.0 degrees with 0.5-degree steps.
   - Repeat each coordinate 3-5 times to calculate a reliability percentage.
3. **Verification**:
   - Listen for `A_KEY` on `/dev/cu.wchusbserial3140`.
   - Timeout: 2.0 seconds from the start of the "Down" command.
