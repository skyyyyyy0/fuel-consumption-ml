# Correlation & Feature Analysis

## 1. Objective

This analysis evaluated:

- Feature-to-target relationships
- Feature-to-feature relationships
- Multicollinearity candidates
- Redundancy among Speed and RPM features
- Vehicle-level differences
- Period-level differences
- Context-feature relationships

The objective was to identify which features should remain candidates for the final modeling dataset.

---

# 2. Dataset

Source:

`data/processed/trip_ml_features.csv`

Dataset size:

- Trips: 9,923
- Vehicles: 12
- Periods: 3
- Missing core features: 0

Target:

`trip_fuel_used_liter`

---

# 3. Feature-to-Target Correlation

The strongest correlations with the target were:

| Feature           | Correlation |
| ----------------- | ----------: |
| trip_distance_km  |       0.918 |
| trip_duration_min |       0.832 |
| avg_speed_kmh     |       0.708 |
| speed_std         |       0.608 |
| max_speed_kmh     |       0.538 |
| trip_hour         |      -0.352 |
| idle_ratio        |      -0.262 |
| rpm_std           |      -0.225 |
| max_rpm           |      -0.222 |
| is_weekend        |       0.167 |
| avg_rpm           |      -0.154 |
| day_of_week       |       0.097 |
| high_rpm_ratio    |      -0.042 |

Trip distance is the strongest individual predictor of total trip fuel consumption.

However, pairwise correlations do not establish independent predictive importance.

---

# 4. Trip Distance and Duration

Trip distance and trip duration are highly correlated:

`trip_distance_km ↔ trip_duration_min = 0.942`

Both are also strongly associated with fuel consumption.

This indicates substantial overlap in the information captured by these two features.

## Decision

Retain both as modeling candidates.

Their incremental value will be tested through model comparison rather than removing one solely based on correlation.

---

# 5. Speed Feature Redundancy

Speed-related features showed strong internal correlation:

- `max_speed_kmh ↔ speed_std = 0.961`
- `avg_speed_kmh ↔ speed_std = 0.932`
- `avg_speed_kmh ↔ max_speed_kmh = 0.887`

This indicates substantial redundancy among the three Speed features.

## Decision

All Speed features remain candidate variables for now.

A reduced Speed feature set may be selected after baseline model comparison and feature-importance analysis.

---

# 6. RPM Feature Redundancy

RPM-related features also showed strong relationships:

- `avg_rpm ↔ max_rpm = 0.855`
- `max_rpm ↔ rpm_std = 0.877`
- `avg_rpm ↔ rpm_std = 0.796`

High-RPM ratio showed lower-to-moderate correlation with the other RPM variables.

## Decision

RPM features remain candidates, but redundancy should be considered during final feature selection.

---

# 7. Driving Behavior vs Fuel

Raw fleet-level correlations suggested relationships between Fuel and Speed/RPM/Idle behavior.

However, earlier distance-controlled analysis showed that most of these relationships weakened substantially after controlling for:

- Trip distance
- Vehicle identity

This indicates that much of the apparent fleet-level relationship is driven by trip composition and vehicle differences.

## Decision

Driving-behavior features remain secondary candidate predictors rather than primary baseline predictors.

---

# 8. Vehicle Effect

Large differences exist across vehicles.

Examples of mean trip fuel consumption:

- VEH_01: 0.326 L
- VEH_09: 0.301 L
- VEH_05: 11.663 L
- VEH_11: 13.725 L
- VEH_12: 8.078 L

Vehicle-level differences are also visible in:

- Trip distance
- Duration
- Average RPM
- Speed
- Idle behavior

## Decision

Vehicle identity is important for evaluation and split strategy.

Whether `vehicle_id` should be used directly as a model feature will be determined during final feature selection.

---

# 9. Period Effect

Observed mean fuel consumption:

- Before: 2.402 L
- After: 2.403 L
- Final: 2.503 L

The differences are relatively small compared with vehicle-level differences.

## Decision

`period` will remain metadata / optional context rather than a required baseline predictor.

---

# 10. Context Features

Observed target correlations:

- `trip_hour`: -0.352
- `day_of_week`: 0.097
- `is_weekend`: 0.167

The `trip_hour` relationship may reflect differences in vehicle and route operating schedules rather than a direct time-of-day effect.

## Decision

Context variables remain candidate features.

Their inclusion should be evaluated through validation performance rather than raw correlation alone.

---

# 11. Multicollinearity Candidates

Feature pairs with absolute correlation >= 0.80:

- `max_speed_kmh` ↔ `speed_std`
- `trip_distance_km` ↔ `trip_duration_min`
- `avg_speed_kmh` ↔ `speed_std`
- `avg_speed_kmh` ↔ `max_speed_kmh`
- `max_rpm` ↔ `rpm_std`
- `avg_rpm` ↔ `max_rpm`
- `trip_distance_km` ↔ `avg_speed_kmh`

These pairs should be considered when interpreting linear-model coefficients and feature importance.

They are not automatically removed for tree-based models.

---

# 12. Candidate Feature Groups

## Core Trip Features

- `trip_distance_km`
- `trip_duration_min`

## Speed Features

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`

## RPM Features

- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`

## Vehicle-State Feature

- `idle_ratio`

## Context Features

- `trip_hour`
- `day_of_week`
- `is_weekend`

## Metadata / Evaluation Variables

- `vehicle_id`
- `period`
- `trip_id`
- Trip timestamps

---

# 13. Key Finding

The analysis confirms that:

> Trip distance and vehicle-specific operating patterns explain a large portion of fuel-consumption variation.

Speed, RPM, idle, and context variables may still provide incremental predictive value, but many are correlated with other trip characteristics.

Therefore, final feature selection should be based on model validation rather than correlation thresholds alone.

---

## Final Decision

**Correlation & Feature Analysis Complete**

Proceed to Final Feature Selection.
