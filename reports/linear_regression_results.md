# Linear Regression Results

## Objective

Evaluate an interpretable regression baseline and determine whether driving-behavior and context features provide additional predictive value beyond basic trip characteristics.

Models were trained using the chronological Train split and evaluated only on the Validation split.

The final Test set was not used.

---

# Dataset Split

- Train: 5,953 trips
- Validation: 1,985 trips
- Test: 1,985 trips — reserved for final evaluation

Target:

`trip_fuel_used_liter`

Primary evaluation metric:

**MAE**

Secondary metrics:

- RMSE
- R²

---

# Feature Sets

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

---

# Validation Results

| Feature Set | Features |        MAE |       RMSE |         R² |
| ----------- | -------: | ---------: | ---------: | ---------: |
| Baseline    |        2 | **0.7495** |     2.4686 |     0.8070 |
| Extended    |       10 |     0.7999 |     2.4383 |     0.8117 |
| Context     |       13 |     0.8014 | **2.4138** | **0.8154** |

---

# Train vs Validation

## Baseline

Train:

- MAE: 0.6868
- RMSE: 1.9383
- R²: 0.8619

Validation:

- MAE: 0.7495
- RMSE: 2.4686
- R²: 0.8070

## Extended

Train:

- MAE: 0.7417
- RMSE: 1.8938
- R²: 0.8681

Validation:

- MAE: 0.7999
- RMSE: 2.4383
- R²: 0.8117

## Context

Train:

- MAE: 0.7407
- RMSE: 1.8814
- R²: 0.8698

Validation:

- MAE: 0.8014
- RMSE: 2.4138
- R²: 0.8154

---

# Incremental Feature Value

## Baseline → Extended

Adding Speed, RPM, and Idle features:

- MAE: 0.7495 → 0.7999
- RMSE: 2.4686 → 2.4383
- R²: 0.8070 → 0.8117

MAE became slightly worse while RMSE and R² improved slightly.

This suggests that the additional telemetry features may reduce some larger prediction errors but do not improve average absolute prediction accuracy under a linear relationship.

---

# Context Feature Value

Adding time/context variables:

- MAE: 0.7999 → 0.8014
- RMSE: 2.4383 → 2.4138
- R²: 0.8117 → 0.8154

Context features produced only small improvements in RMSE and R² and did not improve MAE.

---

# Key Finding

The strongest Linear Regression configuration according to the primary MAE metric was the simple Baseline model using only:

- Trip Distance
- Trip Duration

This supports the earlier EDA finding that trip exposure explains a large portion of total fuel consumption.

Driving-behavior variables showed limited incremental value when modeled only through linear relationships.

---

# Comparison with Simple Baseline

Simple Mean Baseline:

- MAE: 3.2754 L
- RMSE: 5.6199 L
- R²: approximately 0

Baseline Linear Regression:

- MAE: 0.7495 L
- RMSE: 2.4686 L
- R²: 0.8070

Linear Regression therefore provides a substantial improvement over the naive baseline.

---

# Decision

## Best Linear Regression by MAE

**Baseline Linear Regression**

Features:

- `trip_distance_km`
- `trip_duration_min`

Validation performance:

- MAE: **0.7495 L**
- RMSE: 2.4686 L
- R²: 0.8070

The Extended and Context feature sets remain candidates for nonlinear modeling because their relationships with Fuel may not be adequately represented by Linear Regression.

## Status

**Linear Regression evaluation complete.**
