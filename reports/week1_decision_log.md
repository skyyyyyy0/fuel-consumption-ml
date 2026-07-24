# Week 1 Decision Log

## 1. Purpose

This document summarizes the major decisions made during Week 1 and determines whether the Fuel Consumption ML project is ready to proceed to data processing and feature engineering.

---

# 2. Data Availability

## Fleet

- Vehicles: 12
- Primary modeling year: 2026
- Periods: Before, After, Final
- Vehicle-period combinations: 36

## Data Sources

Primary sources:

- GeoTab telemetry
- GeoTab Trip data
- GPS-based trip distance
- Trip Fuel Used telemetry

### Decision

**PASS**

Sufficient telemetry and trip-level data are available to construct the initial ML dataset.

---

# 3. Trip Definition

The final modeling unit is:

**1 Row = 1 GeoTab-defined Trip**

GeoTab Trip information is used instead of reconstructing trips from ignition events or timestamp gaps.

Primary trip fields:

- Trip start
- Trip stop
- Trip duration
- GPS distance

### Decision

**PASS**

Trip boundaries can be identified consistently across the fleet.

---

# 4. Target Definition

The prediction target is:

**Y = trip_fuel_used_liter**

Source:

`Trip fuel used`

Trip Fuel Used events are aligned with GeoTab trip-stop timestamps.

Matching rules:

- <= 30 seconds: High Confidence
- 30–60 seconds: Review
- > 60 seconds: Unmatched

Each fuel event may be assigned to only one trip.

### Fleet Validation Results

- GPS Trips: 15,827
- Trip Fuel records: 13,947
- High-confidence matches: 12,231
- High-confidence valid trips: 12,211
- Review matches: 631
- Rejected duplicate assignments: 253
- Unmatched trips: 2,712

Overall high-confidence usable rate:

**77.2%**

### Decision

**PASS**

The fuel-consumption target can be generated reliably for a sufficiently large subset of trips.

---

# 5. Distance

Primary distance source:

**GeoTab GPS Trip Distance**

GPS Trip data is available across all 12 vehicles and all three 2026 periods.

Odometer is not used as the primary distance feature because coverage is only 6/12 vehicles.

### Decision

**PASS**

`trip_distance_km` will be the primary distance feature.

---

# 6. Engine Speed / RPM

Coverage:

**12 / 12 vehicles**

Observed fleet range:

- Minimum: 0 RPM
- Maximum: 4508.5 RPM
- Negative values: 0

High RPM observations were identified but remain physically plausible and will not automatically be removed.

### Decision

**PASS**

RPM is suitable for feature engineering.

Planned features include:

- avg_rpm
- max_rpm
- rpm_std
- high_rpm_ratio

---

# 7. Vehicle Speed

Coverage:

**12 / 12 vehicles**

Valid speed unit:

`UnitOfMeasureKilometersPerHourId`

Observed valid road-speed range:

- Minimum: 0 km/h
- Maximum: 138 km/h
- Values above 160 km/h: 0

Records using:

`UnitOfMeasureMetersId`

were found under the Engine road speed signal but do not represent vehicle speed and must not be interpreted as km/h.

### Decision

**PASS WITH UNIT FILTER**

Only valid km/h observations will be used for speed feature engineering.

---

# 8. Data Quality Findings

Major issues identified during Week 1 include:

- Event-driven sampling
- Large timestamp gaps
- Duplicate records concentrated primarily in Odometer
- Mixed units under Engine road speed
- Limited Outside Temperature coverage
- Suspicious Outside Temperature values above 60°C
- Zero-distance GPS trips
- Large number of very short GPS trips
- Fuel events that do not match every GeoTab trip
- Duplicate candidate fuel-to-trip assignments

These issues have been investigated and documented.

Cleaning rules will be finalized during Week 2 rather than removing observations prematurely.

### Decision

**PASS WITH DOCUMENTED CLEANING REQUIREMENTS**

No identified issue prevents development of the initial ML dataset.

---

# 9. Core Feature Set

The initial baseline features are:

## Trip

- trip_distance_km
- trip_duration_min

## Speed

- avg_speed_kmh
- max_speed_kmh
- speed_std

## RPM

- avg_rpm
- max_rpm
- rpm_std
- high_rpm_ratio

## Vehicle State

- idle_ratio

### Decision

**APPROVED FOR INITIAL BASELINE**

---

# 10. Optional Features

The following features are not required for the initial baseline.

## Outside Temperature

Coverage:

**5 / 12 vehicles**

Status:

**Optional**

Additional validation is required before use.

## Gear Position

Coverage:

**11 / 12 vehicles**

Status:

**Optional**

Encoding and vehicle consistency require validation.

## Vehicle Type

Status:

**Optional**

May be useful for controlling vehicle-level differences.

---

# 11. Excluded / Unavailable Features

## Odometer

Excluded from baseline because of incomplete fleet coverage.

## Coolant Temperature

Unavailable.

## Engine Load

Unavailable.

---

# 12. Target Leakage Review

The following fuel-related variables will not be used as model inputs:

- Trip Fuel Used — Target only
- Total Fuel Used — Excluded
- Trip Idle Fuel Used — Excluded from baseline
- Total Fuel Used While Idling — Excluded

### Decision

**PASS**

Known direct fuel-consumption leakage variables have been identified and excluded from X.

---

# 13. Initial ML Dataset

The planned dataset structure is:

## Metadata

- vehicle_id
- trip_id
- period
- trip_start_time
- trip_end_time

## X — Core Features

- trip_distance_km
- trip_duration_min
- avg_speed_kmh
- max_speed_kmh
- speed_std
- avg_rpm
- max_rpm
- rpm_std
- high_rpm_ratio
- idle_ratio

## Y — Target

- trip_fuel_used_liter

Optional variables may be added in later experiments.

---

# 14. Week 1 Go / No-Go Checklist

- [x] Fuel target can be calculated reliably
- [x] Trips can be identified reliably
- [x] RPM is usable
- [x] Speed is usable
- [x] Distance is usable
- [x] Enough trips exist for modeling
- [x] Major data-quality problems are understood
- [x] Initial feature set has been defined
- [x] Potential target leakage has been identified
- [x] Initial ML dataset schema has been defined

---

# 15. Final Decision

## GO

The project is ready to proceed to Week 2.

Week 1 established:

- available data and signal coverage,
- known data-quality limitations,
- the trip-level modeling unit,
- GPS-based distance,
- the Trip Fuel Used target,
- fuel-to-trip matching rules,
- the baseline feature set,
- and leakage-sensitive variables.

A total of **12,211 high-confidence valid trip-target observations** were identified before final Week 2 cleaning and feature availability filtering.

Week 2 will focus on constructing the processed trip-level dataset, applying documented cleaning rules, and engineering the initial model features.
