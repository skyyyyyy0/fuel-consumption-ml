# Week 2 — Final Dataset Validation

## 1. Purpose

This report documents the final validation of the trip-level modeling dataset produced during Week 2.

The objective is to confirm that the dataset is structurally valid, physically reasonable, free of known target leakage, and ready for train / validation / test splitting.

---

# 2. Final Dataset

File:

`data/processed/trip_ml_clean.csv`

Final modeling population:

- Total trips: 9,923
- Vehicles: 12
- Vehicle-period combinations: 36
- Duplicate Trip IDs: 0
- Missing targets: 0
- Missing core features: 0

Each observation represents:

**1 Row = 1 GeoTab Trip**

Target:

`trip_fuel_used_liter`

---

# 3. Dataset Construction Summary

The final dataset was constructed through the following pipeline:

1. Standardize GeoTab GPS Trip records
2. Generate unique Trip IDs
3. Match Trip Fuel Used events to Trip stop timestamps
4. Retain high-confidence fuel matches
5. Aggregate Speed telemetry within each Trip
6. Aggregate RPM telemetry within each Trip
7. Estimate time-weighted idle behavior
8. Merge all Trip-level features
9. Apply final cleaning rules
10. Validate the modeling dataset

---

# 4. Target Validation

Target:

`trip_fuel_used_liter`

Validation results:

- Missing target: 0
- Fuel <= 0: 0
- Negative fuel: 0
- Duplicate Trip IDs: 0
- High-confidence matching required

Final target distribution:

- Minimum: 0.01 L
- Median: 0.34 L
- Mean: 2.43 L
- P95: 15.74 L
- P99: 22.37 L
- Maximum: 66.41 L

The large upper-tail values were retained because they correspond to valid long-distance trips rather than confirmed measurement errors.

---

# 5. Trip Validation

## Distance

Final rules:

- Trips below 0.1 km were excluded
- Zero-distance trips were excluded
- Valid long-distance trips were retained

Final distribution:

- Minimum: 0.10 km
- Median: 1.95 km
- Mean: 10.89 km
- P95: 62.60 km
- P99: 86.75 km
- Maximum: 132.07 km

## Duration

Validation results:

- Duration <= 0: 0

Final distribution:

- Minimum: 0.23 min
- Median: 8.37 min
- Mean: 16.69 min
- P95: 58.50 min
- P99: 93.87 min
- Maximum: 148.10 min

---

# 6. Speed Validation

Features:

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`

Validation results:

- Missing speed features: 0
- Negative average speed: 0
- Maximum speed > 160 km/h: 0

Observed maximum speed:

138 km/h

No physically impossible speed observations remain in the clean modeling dataset.

---

# 7. RPM Validation

Features:

- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`

High RPM definition:

`RPM > 3000`

Validation results:

- Missing RPM features: 0
- Negative average RPM: 0
- Maximum RPM > 5000: 0

Observed maximum RPM:

4,147 RPM

The 3,000 RPM threshold was retained as a high-load / high-engine-speed indicator after reviewing the fleet RPM distribution.

---

# 8. Vehicle-State Validation

Primary feature:

`idle_ratio`

Idle behavior was estimated using time-weighted telemetry rather than simple row counts because the source telemetry is event-driven.

Validation results:

- Missing idle ratio: 0
- Idle ratio < 0: 0
- Idle ratio > 1: 0

Distribution:

- Median: 0.139
- Mean: 0.148
- P95: 0.318
- P99: 0.427
- Maximum: 1.0

---

# 9. Vehicle Coverage

Final clean Trip counts:

| Vehicle | Trips |
| ------- | ----: |
| VEH_01  | 1,684 |
| VEH_02  |   637 |
| VEH_03  |   570 |
| VEH_04  |   687 |
| VEH_05  |   378 |
| VEH_06  |   583 |
| VEH_07  |   513 |
| VEH_08  |   757 |
| VEH_09  | 1,829 |
| VEH_10  | 1,308 |
| VEH_11  |   329 |
| VEH_12  |   648 |

All 12 vehicles remain represented in the final dataset.

Vehicle-level differences in fuel consumption and trip distance will be investigated during Week 3 EDA rather than removed automatically.

---

# 10. Period Coverage

| Period | Trips |
| ------ | ----: |
| Before | 3,246 |
| After  | 3,572 |
| Final  | 3,105 |

All three experimental periods remain well represented.

Average fuel consumption:

- Before: 2.40 L/trip
- After: 2.40 L/trip
- Final: 2.50 L/trip

These values are descriptive only. They should not be interpreted as treatment effects because vehicle mix, trip distance, route conditions, and operating behavior may differ across periods.

---

# 11. Final Modeling Features

Approved baseline X variables:

- `trip_distance_km`
- `trip_duration_min`
- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`
- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`
- `idle_ratio`

Target Y:

- `trip_fuel_used_liter`

Metadata such as `vehicle_id`, `trip_id`, `period`, and timestamps are retained for identification, splitting, diagnostics, and evaluation but are not automatically treated as baseline numeric predictors.

---

# 12. Leakage Validation

The following variables are excluded from the modeling feature matrix:

- Total Fuel Used
- Trip Idle Fuel Used
- Total Idle Fuel Used
- Target-derived fuel variables
- `trip_fuel_used_liter`
- `trip_id`

Validation:

- Known fuel leakage columns present in X: No
- Target included in X: No
- Trip ID included in X: No

Target leakage is controlled for the baseline modeling dataset.

---

# 13. Final Data Quality Status

- [x] Final row count confirmed
- [x] 12 vehicles confirmed
- [x] 36 vehicle-period combinations confirmed
- [x] Duplicate Trip IDs removed
- [x] Missing targets removed
- [x] Missing core features removed
- [x] Invalid short-distance Trips removed
- [x] Negative fuel absent
- [x] Impossible speed absent
- [x] Impossible RPM absent
- [x] Idle ratio validated
- [x] Target leakage controlled
- [x] All three periods represented

---

# 14. Week 2 Final Decision

## GO — Dataset Ready for Modeling

The final clean dataset contains:

**9,923 trip-level observations across 12 vehicles and 36 vehicle-period combinations.**

All required core features are complete, the fuel target is valid, known leakage variables are excluded, and major data-quality issues identified during Weeks 1–2 have been addressed.
