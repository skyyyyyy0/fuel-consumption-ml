# Signal Inventory & Coverage Analysis

## Primary Modeling Scope

The primary ML dataset will use:

- 12 anonymized vehicles
- 2026 Before
- 2026 After
- 2026 Final

2025 data will be treated as supplementary because VEH_01 is missing several core signals during the 2025 periods.

## Core Signals

- GPS Trip Distance — 12/12 vehicles
- Engine Speed (RPM) — 12/12 vehicles
- Engine Road Speed — 12/12 vehicles
- Trip Fuel Used — 12/12 vehicles
- Ignition — 12/12 vehicles
- Vehicle Active — 12/12 vehicles

## Target Candidate

Primary target candidate:

`Trip fuel used`

Observed 2026 range:

- Minimum: 0.01 L
- Maximum: 66.41 L
- Negative values: 0

Trip-level timestamp alignment with GeoTab trips must still be validated before the target is finalized.

## Distance Strategy

Primary distance feature:

`GPS Trip Distance`

Supporting validation:

- GeoTab Odometer
- Manual Odometer measurements

## Data Quality Findings

### Engine Speed

- Range: 0–4508.5 RPM
- No negative values
- Zero values exist

### Engine Road Speed

- Range: 0–3400
- No negative values
- Implausibly high values detected
- Unit inconsistency detected

This signal requires investigation during Day 4.

## Optional Signals

- Gear Position — 11/12 vehicles
- Outside Air Temperature — 5/12 vehicles

## Validation Signals

- Total Fuel Used
- Odometer

## Excluded Signals

- Engine Load
- Coolant Temperature

## Decision

The 2026 dataset provides sufficient core telemetry coverage to proceed with ML dataset development.

The next step is to investigate data-quality issues and define cleaning rules.
