# Data Quality Audit

## Scope

The audit focused on the 2026 primary modeling periods:

- Before
- After
- Final

across 12 anonymized vehicles.

The objective was to identify data-quality issues before cleaning and feature engineering.

---

## 1. Timestamp Quality

### Result

- Missing UTC timestamps: 0
- Missing KST timestamps: 0
- Timestamp ordering violations: 0
- UTC/KST mismatches: 0

### Classification

**Valid**

Timestamp quality is sufficient for trip-level alignment and time-based feature engineering.

---

## 2. Engine Road Speed

### Valid Records

Records with:

`UnitOfMeasureKilometersPerHourId`

showed:

- Minimum: 0 km/h
- Maximum: 138 km/h
- No values above 160 km/h

### Invalid Records

Some records labeled as `Engine road speed` used:

`UnitOfMeasureMetersId`

These records produced incompatible values up to 3,400.

### Classification

**Kilometers-per-hour records: Valid**

**Meters-unit records: Invalid as speed**

### Potential Cleaning Rule

Retain only:

`unit == UnitOfMeasureKilometersPerHourId`

for the ML speed feature.

---

## 3. Engine Speed (RPM)

Observed range:

- Minimum: 0 RPM
- Maximum: 4,508.5 RPM
- Negative values: 0
- RPM > 5,000: 0

High RPM observations above 4,000 were rare but appeared across multiple vehicles and periods.

### Classification

**Valid / Context-dependent**

Zero RPM may represent engine-off states.

High RPM values will not be removed solely based on a fixed threshold.

---

## 4. Trip Fuel Used

Observed range:

- Minimum: 0.01 L
- Maximum: 66.41 L
- Zero values: 0
- Negative values: 0

Higher fuel values were concentrated in specific vehicles and were observed consistently across multiple periods rather than appearing as isolated spikes.

### Classification

**Valid target candidate**

Large values require validation against trip distance rather than arbitrary removal.

---

## 5. GPS Trip Distance

Total GPS trips:

15,827

Observed results:

- Missing distance: 0
- Negative distance: 0
- Maximum distance: 132.07 km
- Zero-distance trips: 142
- Trips below 0.1 km: 3,470
- Trips below 1 km: 7,739
- Trips above 100 km: 32
- Trips above 300 km: 0

### Classification

Normal and long-distance trips:

**Valid**

Zero and extremely short trips:

**Suspicious**

### Potential Cleaning Rule

A minimum trip-distance threshold may be introduced during Week 2 after evaluating its effect on fuel-consumption calculations.

---

## 6. Trip Fuel ↔ GPS Alignment

Fleet-wide alignment was evaluated across:

- 12 vehicles
- Before / After / Final
- 36 vehicle-period combinations

Results:

- Fuel records: 13,947
- GPS trips: 15,827
- Median trip-stop timestamp difference: 10.68 seconds
- Within 30 seconds: 85.8%
- Within 60 seconds: 91.1%

### Classification

**Valid but imperfect alignment**

Trip Fuel Used is strongly associated with GPS trip-stop timestamps.

### Proposed Matching Strategy

High-confidence:

`timestamp difference <= 30 seconds`

Review range:

`30 < difference <= 60 seconds`

Unmatched:

`difference > 60 seconds`

One-to-one matching must still be validated before final target construction.

---

## 7. Duplicate Records

Duplicate records were concentrated in:

- Odometer
- Outside Air Temperature

No meaningful duplicate issue was identified in the primary RPM, Speed, Fuel, Ignition, or Vehicle Active signals.

### Odometer

Duplicates were concentrated primarily in VEH_11 and VEH_04.

### Outside Air Temperature

A smaller number of repeated records were observed.

### Classification

**Suspicious but non-critical**

Odometer is a validation-only signal.

Outside Air Temperature is optional.

---

## 8. Sampling Gaps

Long sampling gaps were observed across the telemetry dataset.

Examples include:

- Gaps > 5 minutes
- Gaps > 30 minutes
- Gaps > 2 hours

Because GeoTab telemetry is event-driven, large gaps between events do not automatically indicate data-quality failures.

### Classification

**Valid / Context-dependent**

Trip-level signal coverage will be evaluated after trip construction.

---

## 9. Outside Air Temperature

Coverage:

5 / 12 vehicles

Observed ranges included values above 60°C for several vehicles.

Maximum observed value:

approximately 72°C

These values may reflect sensor placement, heat-soak effects, or diagnostic mapping issues rather than ambient air temperature.

### Classification

**Suspicious / Optional**

Outside temperature will not be required in the baseline ML model.

---

## 10. Odometer

Coverage:

6 / 12 vehicles

Odometer data is incomplete and contains substantial repeated records.

### Classification

**Validation only**

GPS Trip Distance will be used as the primary distance source.

Manual odometer measurements may be used for spot validation.

---

## 11. Known Coverage Limitations

### 2025 VEH_01

VEH_01 is missing several core telemetry signals during the 2025 Before and After periods.

Therefore:

2026 Before / After / Final will be the primary modeling dataset.

2025 data will be treated as supplementary historical data.

---

# Final Data Quality Classification

## Valid / Core

- GPS Trip Distance
- Engine Speed
- Engine Road Speed with km/h unit
- Trip Fuel Used
- Ignition
- Vehicle Active
- UTC/KST timestamps

## Suspicious / Requires Review

- Very short GPS trips
- Fuel-GPS matches between 30–60 seconds
- High RPM observations
- Outside Air Temperature
- Duplicate Odometer values
- Long event-driven sampling gaps

## Invalid / Exclude

- Engine Road Speed records with `UnitOfMeasureMetersId`
- Engine Load — unavailable
- Coolant Temperature — unavailable

---

# Day 4 Decision

The 2026 dataset is sufficiently reliable to proceed to trip-level dataset construction and feature engineering.

Cleaning rules will be finalized in Week 2 rather than applied prematurely during the audit phase.
