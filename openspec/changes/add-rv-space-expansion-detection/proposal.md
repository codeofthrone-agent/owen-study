# Proposal: Add RV Space Expansion Detection

## Problem Statement
The RV environment requires detection of actual physical space expansion (e.g. slide-out mechanisms). Existing ROI methods based on light detection are insufficient due to limited depth sensitivity and high susceptibility to environmental brightness fluctuations. We need a reliable, depth-aware visual tracking method to continuously determine whether the RV space is collapsed or fully expanded.

## What Changes
This change introduces a vision-based depth and expansion detection capability using physical ArUco markers placed on expanding walls or slide-out structures. By parsing the real-time pixel area and geometric perspective of the marker via the existing IP Camera feed, the system can reliably deduce the current physical state of expansion.

## Capabilities

### New Capabilities
- `rv-space-expansion`: Detects physical space expansion in RVs by computing the physical distance differences represented by ArUco marker pixel areas.

### Modified Capabilities
- None

## Impact
- `config/ipcam_config.yaml`: Adds `space_expansion` configuration section to define marker types, target cameras, and reference areas (collapsed/expanded).
- `config/ipcam_config.py`: Adds new methods to parse expansion logic config.
- `libraries/rv_space_detection/`: A brand new, isolated library module containing the marker detection logic and corresponding Robot Framework keywords.
- `scripts/rv_expansion_calibrator.py`: New interactive calibration script for initializing expected marker areas during actual deployment.
