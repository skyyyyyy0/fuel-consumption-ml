# Feature Dictionary

## Overview

This document defines the variables available for fuel-consumption modeling and their intended roles.

The modeling target is trip-level fuel consumption.

---

# Target

| Feature                | Description                          | Unit  | Role   |
| ---------------------- | ------------------------------------ | ----- | ------ |
| `trip_fuel_used_liter` | Actual fuel consumed during the trip | Liter | Target |

---

# Core Trip Features

| Feature             | Description                   | Unit    | Role               |
| ------------------- | ----------------------------- | ------- | ------------------ |
| `trip_distance_km`  | Total GPS-based trip distance | km      | Baseline predictor |
| `trip_duration_min` | Total trip duration           | minutes | Baseline predictor |

These variables represent the fundamental size and duration of each trip.

---

# Speed Features

| Feature         | Description                               | Unit | Role               |
| --------------- | ----------------------------------------- | ---- | ------------------ |
| `avg_speed_kmh` | Mean engine road speed during the trip    | km/h | Extended predictor |
| `max_speed_kmh` | Maximum engine road speed during the trip | km/h | Extended predictor |
| `speed_std`     | Standard deviation of engine road speed   | km/h | Extended predictor |

Speed features describe driving intensity and speed variability.

Strong correlations exist among these variables, so their incremental predictive value will be evaluated during modeling.

---

# RPM Features

| Feature          | Description                                  | Unit  | Role               |
| ---------------- | -------------------------------------------- | ----- | ------------------ |
| `avg_rpm`        | Mean engine speed during the trip            | RPM   | Extended predictor |
| `max_rpm`        | Maximum engine speed during the trip         | RPM   | Extended predictor |
| `rpm_std`        | Standard deviation of engine speed           | RPM   | Extended predictor |
| `high_rpm_ratio` | Fraction of RPM observations above 3,000 RPM | Ratio | Extended predictor |

The 3,000 RPM threshold was retained as a high-RPM behavior indicator after reviewing the fleet RPM distribution.

---

# Vehicle-State Feature

| Feature      | Description                                          | Unit  | Role               |
| ------------ | ---------------------------------------------------- | ----- | ------------------ |
| `idle_ratio` | Estimated proportion of valid trip time spent idling | Ratio | Extended predictor |

`idle_ratio` is time-weighted rather than calculated from raw event counts.

This reduces bias caused by event-driven telemetry sampling.

---

# Context Features

| Feature       | Description                            | Unit          | Role               |
| ------------- | -------------------------------------- | ------------- | ------------------ |
| `trip_hour`   | Trip start hour in Korea Standard Time | Hour (0–23)   | Optional predictor |
| `day_of_week` | Day of week of trip start              | Integer (0–6) | Optional predictor |
| `is_weekend`  | Weekend indicator                      | Binary        | Optional predictor |

Context features will only be retained if they provide measurable validation improvement.

---

# Metadata

| Feature           | Description                               | Role                              |
| ----------------- | ----------------------------------------- | --------------------------------- |
| `trip_id`         | Unique anonymized trip identifier         | Metadata                          |
| `vehicle_id`      | Anonymized vehicle identifier             | Metadata / experimental predictor |
| `period`          | Before, After, or Final evaluation period | Metadata                          |
| `trip_start_time` | Trip start timestamp                      | Metadata                          |
| `trip_end_time`   | Trip end timestamp                        | Metadata                          |

Metadata variables are retained for splitting, diagnostics, and error analysis.

They are not included in the primary numerical predictor matrix.

---

# Vehicle ID Policy

Large vehicle-level differences were observed in trip distance and fuel consumption.

Because of this, directly including `vehicle_id` could substantially improve prediction while also allowing the model to learn vehicle-specific behavior.

The primary model therefore excludes vehicle identity.

A separate vehicle-aware experiment will evaluate whether explicitly including vehicle identity improves prediction.

This distinction allows vehicle-independent and vehicle-aware performance to be reported separately.

---

# Period Policy

`period` is retained as metadata rather than a primary predictor.

Before, After, and Final periods showed relatively small fleet-level differences compared with vehicle-level variation.

The objective is to predict expected fuel consumption from trip and operating characteristics rather than from experimental period labels.

---

# Temperature

Outside-air temperature was investigated as a candidate predictor.

No sufficiently reliable temperature signal was available across the dataset.

Temperature is therefore excluded from the current feature set.

---

# Leakage Controls

The following variables must not be included in X:

- `trip_fuel_used_liter`
- Total Fuel Used
- Trip Idle Fuel Used
- Total Idle Fuel Used
- Fuel-event timestamps
- Fuel-match time differences
- Fuel-match confidence
- Any variable calculated from the target

`trip_id` is also excluded from the predictor matrix.

---

# Modeling Feature Sets

## Baseline

- `trip_distance_km`
- `trip_duration_min`

## Extended

Baseline plus:

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`
- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`
- `idle_ratio`

## Context

Extended plus:

- `trip_hour`
- `day_of_week`
- `is_weekend`

## Vehicle-Aware Experiment

Selected predictors plus:

- `vehicle_id`

---

# Final Status

All candidate features have:

- A defined physical or operational interpretation
- A documented unit
- A defined modeling role
- No known direct target leakage

Final feature retention will be determined using validation performance.
