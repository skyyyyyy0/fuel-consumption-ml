# Final Feature Selection

## Objective

Define the candidate predictor sets used for fuel-consumption modeling.

Feature selection is based on:

- Physical interpretation
- Data quality
- Target leakage prevention
- Correlation analysis
- Feature redundancy
- Vehicle-level heterogeneity
- Incremental predictive value

Features are not removed solely because of high pairwise correlation.
Their contribution will be evaluated through validation experiments.

---

# Target

## Y

`trip_fuel_used_liter`

Actual fuel consumed during each matched trip.

The target is never included in the predictor matrix.

---

# Feature Set 1 — Baseline

The baseline model uses only trip exposure variables.

- `trip_distance_km`
- `trip_duration_min`

## Purpose

Establish how accurately fuel consumption can be predicted using only trip size.

This provides the reference performance against which additional telemetry features will be evaluated.

---

# Feature Set 2 — Driving Behavior

Baseline features plus:

## Speed

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`

## RPM

- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`

## Vehicle State

- `idle_ratio`

## Purpose

Determine whether engine and driving-behavior telemetry provides predictive information beyond trip distance and duration.

Because several Speed and RPM variables are highly correlated, feature importance and validation performance will be used to determine whether a reduced feature set is appropriate.

---

# Feature Set 3 — Context

Driving Behavior feature set plus:

- `trip_hour`
- `day_of_week`
- `is_weekend`

## Purpose

Test whether operating-time context improves prediction beyond physical trip and telemetry characteristics.

Context features will only be retained if they provide measurable validation improvement.

---

# Metadata

The following columns are retained for splitting, diagnostics, and error analysis but are not automatically included as numerical predictors:

- `trip_id`
- `vehicle_id`
- `period`
- `trip_start_time`
- `trip_end_time`

---

# Vehicle ID

`vehicle_id` is intentionally separated from the initial predictor sets.

Strong vehicle-level differences were observed in the EDA.

Therefore, vehicle identity will be evaluated separately to determine:

1. Performance when the model knows the vehicle identity
2. Performance when predicting without vehicle identity
3. Generalization to vehicles not represented during training

This distinction is important because strong performance caused primarily by memorizing vehicle identity would not necessarily indicate strong generalization.

---

# Period

`period` is retained as metadata.

Observed Before / After / Final differences were substantially smaller than vehicle-level differences.

It is therefore not included in the primary baseline predictor set.

---

# Excluded Features

The following must not be used as predictors:

- `trip_fuel_used_liter`
- Total Fuel Used
- Trip Idle Fuel Used
- Total Idle Fuel Used
- Fuel-match timestamps
- Fuel-match time differences
- Fuel-match confidence
- Any feature derived directly from the target

These variables could create target leakage.

---

# Temperature

Outside-air temperature was investigated but no sufficiently reliable signal was available.

Temperature is therefore excluded from the current modeling dataset.

---

# Feature Redundancy

Strong correlations were observed among:

- Distance and Duration
- Average Speed, Maximum Speed, and Speed Standard Deviation
- Average RPM, Maximum RPM, and RPM Standard Deviation

These variables are retained initially.

Reduced feature sets may be tested after baseline modeling.

---

# Modeling Experiment Structure

The initial modeling experiments will compare:

## Model A — Baseline

Distance + Duration

## Model B — Driving Behavior

Baseline + Speed + RPM + Idle

## Model C — Context

Driving Behavior + Time Context

## Model D — Vehicle-Aware Experiment

Selected predictors + Vehicle ID

Vehicle-aware performance will be reported separately from vehicle-independent performance.

---

# Final Candidate Feature List

## Baseline

- `trip_distance_km`
- `trip_duration_min`

## Driving Behavior

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`
- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`
- `idle_ratio`

## Context

- `trip_hour`
- `day_of_week`
- `is_weekend`

---

# Decision

The dataset contains a well-defined candidate feature space with no known target leakage.

Final feature retention will be determined using validation performance rather than pairwise correlation alone.

**Status: READY FOR MODELING EXPERIMENTS**
