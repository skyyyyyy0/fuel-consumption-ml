# Engine Feature Engineering Summary

## 1. Purpose

Trip-level speed and engine RPM features were generated from the event-driven telemetry data.

Only telemetry observations occurring within each GeoTab Trip's start and end timestamps were used.

The resulting feature table contains one row per Trip.

---

## 2. Dataset

- Total Trips: 15,827
- Unique Trip IDs: 15,827
- Vehicles: 12
- Periods: Before / After / Final

Output:

`data/processed/trip_features_engine.csv`

---

# 3. Speed Features

## Source Signal

`Engine road speed`

Only the following unit was accepted:

`UnitOfMeasureKilometersPerHourId`

Records using:

`UnitOfMeasureMetersId`

were excluded because the signal audit showed that these records did not represent valid vehicle-speed observations.

## Generated Features

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`
- `speed_obs_count`

## Validation Results

- Missing Speed Features: 506 Trips
- Missing Rate: 3.2%
- Minimum Trip Average Speed: 0.0 km/h
- Maximum Trip Average Speed: 64.99 km/h
- Maximum Observed Trip Speed: 138.0 km/h
- Negative Speed: Not observed in the validated km/h source data
- Extreme invalid speed values: Removed through unit filtering

Speed feature coverage was approximately 96–97% across the full dataset.

---

# 4. RPM Features

## Source Signal

`Engine speed`

Unit:

`UnitOfMeasureRevolutionsPerMinuteId`

## Generated Features

- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`
- `rpm_obs_count`

## Validation Results

- Missing RPM Features: 705 Trips
- Missing Rate: 4.5%
- Minimum Trip Average RPM: 0.0
- Maximum Trip Average RPM: 2587.21
- Maximum Observed Trip RPM: 4488.0
- Negative RPM: Not observed
- RPM above 5000: Not observed during the earlier signal audit

RPM feature coverage was approximately 95–96% across the full dataset.

---

# 5. High RPM Threshold

Several candidate thresholds were evaluated.

| Threshold  | Fleet Observations Above Threshold |
| ---------- | ---------------------------------: |
| RPM > 2500 |                              1.23% |
| RPM > 3000 |                              0.34% |
| RPM > 3500 |                              0.13% |
| RPM > 4000 |                              0.04% |

Fleet RPM distribution:

- Median vehicle-period mean RPM: 1198.7
- Median P90 RPM: 1916.9
- Median P95 RPM: 2044.6
- Median P99 RPM: 2320.7

## Final Decision

The initial high-RPM threshold is:

`RPM > 3000`

Therefore:

`high_rpm_ratio = observations with RPM > 3000 / total RPM observations within the Trip`

The 3,000 RPM threshold was selected as a practical high-RPM indicator after reviewing the fleet-wide RPM distribution.

Approximately 0.34% of RPM observations exceeded this threshold, making it a relatively rare but interpretable indicator of high-engine-speed operation.

---

# 6. Vehicle-Level Coverage

Most vehicles showed strong Speed and RPM coverage.

Lower RPM coverage was observed for:

- VEH_05: 85.8%
- VEH_12: 88.9%
- VEH_06: 91.1%

These observations will not be imputed during feature generation.

Missing-feature handling will be finalized during the cleaning stage.

---

# 7. Period-Level Coverage

## Speed

- Before: 95.9%
- After: 97.4%
- Final: 97.0%

## RPM

- Before: 94.8%
- After: 96.0%
- Final: 95.7%

No period showed evidence of a fleet-wide loss of Speed or RPM telemetry.

---

# 8. Data Quality Decisions

## Valid

- Speed values using the km/h unit
- RPM values within observed operating ranges
- Zero Speed observations
- Zero RPM observations when consistent with vehicle state
- High-RPM events above 3000 RPM

## Excluded

- `Engine road speed` records using `UnitOfMeasureMetersId`

## Deferred to Cleaning

- Trips with missing Speed features
- Trips with missing RPM features
- Trips with very few telemetry observations
- Zero-duration Trips
- Zero-distance Trips
- Final minimum-observation requirements

---

# 9. Final Feature Set

The following engine-related ML features are now available:

`avg_speed_kmh`

`max_speed_kmh`

`speed_std`

`avg_rpm`

`max_rpm`

`rpm_std`

`high_rpm_ratio`

Observation-count fields are retained for data-quality validation:

`speed_obs_count`

`rpm_obs_count`

---

# 10. Day 9 Decision

Speed and RPM telemetry provide sufficient coverage and physically plausible values for Trip-level feature engineering.

The engine feature dataset is ready to be combined with additional Trip-level features during the remaining Week 2 processing steps.

**Day 9 Status: PASS**
