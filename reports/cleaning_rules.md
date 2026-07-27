# Cleaning Rules

## 1. Purpose

This document defines the final cleaning rules applied to the trip-level ML dataset before modeling.

The objective is to remove only observations that are clearly invalid, unreliable, or unsuitable for the baseline model.

Outliers were not removed solely because they were extreme. Each suspicious pattern was investigated before a final decision was made.

---

# 2. Input Dataset

Source:

`data/processed/trip_ml_master.csv`

Initial rows:

**15,827 Trips**

Modeling unit:

**1 Row = 1 GeoTab-defined Trip**

Target:

**Y = trip_fuel_used_liter**

---

# 3. Target Quality Rule

Only trips with:

`fuel_match_confidence == "High"`

are retained for the baseline modeling dataset.

High-confidence means:

`Fuel timestamp difference <= 30 seconds from GeoTab trip stop`

## Result

Initial:

15,827 Trips

After High-confidence filtering:

**12,231 Trips**

Removed:

**3,596 Trips**

### Decision

**Required**

Review and unmatched target observations remain available in the master dataset but are excluded from the baseline ML dataset.

---

# 4. Fuel Rule

Required:

`trip_fuel_used_liter > 0`

Observed in High-confidence population:

- Missing fuel: 0
- Zero fuel: 0
- Negative fuel: 0

### Decision

**Required**

No additional observations were removed by this rule after the High-confidence target filter.

---

# 5. Core Feature Completeness

The baseline model requires complete values for:

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
- `trip_fuel_used_liter`

Trips missing one or more core features are excluded from the baseline dataset.

## Result

High-confidence Trips:

12,231

Complete Core Trips:

**11,999**

Removed:

**232 Trips**

### Decision

**Required**

Missing core features are not imputed in the baseline model.

---

# 6. Distance Rule

## Invalid

Trips with:

`trip_distance_km <= 0`

are not suitable for fuel-consumption modeling.

## Micro-Trip Investigation

A substantial number of very short trips were identified.

For trips below 0.1 km:

- Median distance: approximately 0.046 km
- Median duration: approximately 0.76 min
- Median fuel: approximately 0.02 L
- Median diagnostic fuel intensity: approximately 71.6 L/100 km
- P95 diagnostic fuel intensity: approximately 758 L/100 km

The extremely unstable fuel-per-distance relationship is caused by very small distance denominators and GeoTab micro-trip segmentation.

These trips may represent real short movements, but they are unsuitable for the initial baseline fuel-consumption model.

## Final Rule

Retain:

`trip_distance_km >= 0.1`

## Result

Before distance rule:

11,999 Trips

After distance rule:

**9,924 Trips**

Removed:

**2,075 Trips**

### Decision

**Baseline exclusion**

Trips below 0.1 km are not labeled as universally invalid raw data. They are excluded because they produce unstable trip-level fuel relationships for this modeling objective.

---

# 7. Duration Rule

Required:

`trip_duration_min > 0`

Zero-duration trips had already been excluded indirectly through other baseline requirements.

Long-duration trips were manually reviewed.

Trips above 120 minutes generally showed:

- long GPS distances,
- plausible average speeds,
- plausible fuel consumption,
- normal RPM behavior.

### Decision

**Retain valid long-duration trips**

No upper duration threshold is applied.

Trips are not removed simply because they exceed a percentile or fixed long-duration threshold.

---

# 8. Speed Rules

Speed features use only:

`Engine road speed`

with:

`UnitOfMeasureKilometersPerHourId`

Records using:

`UnitOfMeasureMetersId`

were excluded during feature generation.

## Required

`avg_speed_kmh >= 0`

## Observed Clean Candidate Range

- Average Speed: 0 to approximately 62.9 km/h
- Maximum Speed: up to 138 km/h
- Speed above 160 km/h: not observed
- Negative Speed: not observed

### Decision

**Valid**

No additional speed-based outlier removal is required.

---

# 9. RPM Rules

Required:

`avg_rpm >= 0`

Observed values were physically plausible.

After the baseline cleaning filters:

- Average RPM: approximately 511 to 2022 RPM
- Maximum RPM: up to approximately 4147 RPM

Trips with maximum RPM above 4000 were manually inspected.

These trips generally showed:

- plausible trip distances,
- plausible fuel consumption,
- plausible average RPM,
- isolated high-RPM events.

### Decision

**Retain**

High RPM alone is not considered an invalid observation.

No fixed upper RPM threshold is applied below the previously observed physical maximum.

---

# 10. Idle Ratio Rule

Required range:

`0 <= idle_ratio <= 1`

Observed:

- Minimum: 0
- Maximum: 1
- No values outside the valid range

Trips with:

`idle_ratio == 1`

were manually reviewed.

These trips generally represented very short, low-speed operating conditions with valid RPM observations.

### Decision

**Retain**

An idle ratio of 1 is not automatically treated as invalid.

---

# 11. Long-Distance Trips

Trips above 100 km were manually investigated.

Observed long-distance trips showed:

- consistent vehicle concentration,
- plausible duration,
- plausible average speed,
- plausible RPM,
- internally consistent fuel consumption.

### Decision

**Retain**

Long distance alone is not an outlier-removal criterion.

---

# 12. High Fuel Trips

Trips with:

`trip_fuel_used_liter > 50`

were manually inspected.

Most high-fuel observations corresponded to substantial trip distances and were internally consistent.

One observation was identified as clearly inconsistent:

`VEH_05_FINAL_0036`

Observed characteristics included approximately:

- Distance: 0.114 km
- Duration: 1.22 min
- Fuel: 51.24 L

The fuel value was physically inconsistent with the trip distance and duration.

### Decision

Remove:

`VEH_05_FINAL_0036`

All other high-fuel trips were retained.

---

# 13. Confirmed Invalid Anomaly

The following Trip is explicitly excluded:

`VEH_05_FINAL_0036`

Reason:

Fuel consumption was physically inconsistent with trip distance, duration, speed, and RPM characteristics.

---

# 14. Final Sequential Cleaning Rules

The baseline modeling dataset applies the following rules in order:

1. `fuel_match_confidence == "High"`
2. `trip_fuel_used_liter > 0`
3. Complete core ML features
4. `trip_distance_km >= 0.1`
5. `trip_duration_min > 0`
6. `avg_speed_kmh >= 0`
7. `avg_rpm >= 0`
8. `0 <= idle_ratio <= 1`
9. Remove confirmed anomaly `VEH_05_FINAL_0036`

---

# 15. Final Dataset

Output:

`data/processed/trip_ml_clean.csv`

## Final Results

Initial Master Dataset:

**15,827 Trips**

High-confidence target:

**12,231 Trips**

Complete core features:

**11,999 Trips**

After minimum-distance rule:

**9,924 Trips**

After confirmed anomaly removal:

**9,923 Trips**

---

# 16. Final Validation

The clean dataset contains:

- Rows: 9,923
- Vehicles: 12
- Vehicle-period combinations: 36
- Duplicate Trip IDs: 0
- Missing Core Features: 0
- Distance below 0.1 km: 0
- Duration <= 0: 0
- Fuel <= 0: 0
- Negative Speed: 0
- Negative RPM: 0
- Idle Ratio outside 0–1: 0

---

# 17. Cleaning Philosophy

The project intentionally avoids aggressive percentile-based outlier removal.

Extreme observations are retained when they are:

- physically plausible,
- internally consistent,
- repeated across similar operating conditions,
- or representative of genuine vehicle behavior.

Observations are removed only when there is a clear data-quality or modeling justification.

This preserves real fleet variability while preventing clearly unreliable observations from affecting the baseline model.

---

# 18. Decision

The final cleaned dataset contains:

**9,923 model-ready Trip observations**

The dataset retains all 12 vehicles and all 36 vehicle-period combinations.

The cleaned data is ready for final Week 2 validation.
