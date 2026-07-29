# XGBoost Modeling Results

## Objective

Evaluate whether a nonlinear tree-based model can capture additional predictive information from Speed, RPM, Idle, and Context features beyond basic trip characteristics.

Models were trained using the chronological Train split and evaluated on the Validation split.

The final Test set was not used.

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

# Initial XGBoost Configuration

The initial XGBoost experiments used:

- `n_estimators = 300`
- `learning_rate = 0.05`
- `max_depth = 4`
- `subsample = 0.8`
- `colsample_bytree = 0.8`

---

# Validation Results

| Feature Set | Features |        MAE |       RMSE |         R² |
| ----------- | -------: | ---------: | ---------: | ---------: |
| Baseline    |        2 |     0.5811 |     2.2616 |     0.8380 |
| Extended    |       10 |     0.4345 |     1.8658 |     0.8897 |
| Context     |       13 | **0.3791** | **1.6833** | **0.9102** |

Unlike Linear Regression, XGBoost benefited substantially from the additional driving-behavior and context features.

---

# Incremental Feature Value

## Baseline → Extended

Adding Speed, RPM, and Idle features improved:

- MAE: 0.5811 → 0.4345
- RMSE: 2.2616 → 1.8658
- R²: 0.8380 → 0.8897

This provides evidence that telemetry features contain predictive information beyond Trip Distance and Duration when nonlinear relationships and interactions are modeled.

---

# Context Feature Value

Adding contextual features further improved:

- MAE: 0.4345 → 0.3791
- RMSE: 1.8658 → 1.6833
- R²: 0.8897 → 0.9102

Time-of-day and operating-context features therefore provided measurable validation improvement in the nonlinear model.

---

# Feature Importance

For the Context XGBoost model, the strongest feature was:

`trip_distance_km`

Feature importance:

- Trip Distance: 0.6308
- Trip Duration: 0.1593
- Maximum RPM: 0.0482
- Trip Hour: 0.0378
- Maximum Speed: 0.0299
- Average Speed: 0.0230
- RPM Standard Deviation: 0.0207
- Average RPM: 0.0202
- Idle Ratio: 0.0110
- Speed Standard Deviation: 0.0103
- Day of Week: 0.0045
- Weekend Indicator: 0.0033
- High-RPM Ratio: 0.0010

Trip Distance remains the dominant predictor, consistent with the EDA.

---

# Linear Regression vs XGBoost

Best Linear Regression by MAE:

`0.7495 L`

Initial Context XGBoost:

`0.3791 L`

XGBoost therefore reduced validation MAE by approximately half relative to the strongest Linear Regression result.

This suggests that nonlinear relationships and feature interactions are important in the fuel-consumption prediction problem.

---

# Hyperparameter Tuning

A limited grid search evaluated 108 parameter combinations using the Validation dataset only.

The best MAE configuration was:

- `n_estimators = 200`
- `learning_rate = 0.03`
- `max_depth = 5`
- `subsample = 1.0`
- `colsample_bytree = 1.0`

Performance:

- Validation MAE: **0.3506 L**
- Validation RMSE: 1.7868 L
- Validation R²: 0.8989
- Train–Validation MAE Gap: 0.1385

---

# Tuning Trade-Off

Compared with the original Context XGBoost:

| Model            |        MAE |       RMSE |         R² |
| ---------------- | ---------: | ---------: | ---------: |
| Original Context |     0.3791 | **1.6833** | **0.9102** |
| Tuned XGBoost    | **0.3506** |     1.7868 |     0.8989 |

The tuned model improved MAE but produced slightly worse RMSE and R².

Therefore, tuning improved typical absolute prediction accuracy while increasing sensitivity to some larger prediction errors.

Because MAE is the primary evaluation metric, the tuned model remains the leading candidate but is not yet declared the final model.

---

# Vehicle Holdout Validation

Leave-One-Vehicle-Out validation was performed on the development population.

Overall unseen-vehicle performance:

- MAE: **0.5369 L**
- RMSE: **2.0996 L**
- R²: **0.8442**
- Median Vehicle MAE: 0.2150 L

The model generalized well to many unseen vehicles.

However, error was substantially higher for several high-fuel, long-distance vehicle profiles:

- VEH_05: MAE 3.0703 L
- VEH_06: MAE 1.8811 L
- VEH_11: MAE 2.0304 L
- VEH_12: MAE 1.8331 L

This indicates that vehicle operating regime remains an important source of heterogeneity.

---

# Current Model Decision

The current leading model according to the primary MAE metric is:

**Tuned XGBoost with Context Features**

However, the original Context XGBoost retains better RMSE and R².

Final selection will therefore also consider:

- Overfitting
- Residual behavior
- Large-error cases
- Vehicle-level errors
- Final model-comparison criteria

The untouched chronological Test set has not yet been used.

## Status

**XGBoost modeling and tuning complete.**
