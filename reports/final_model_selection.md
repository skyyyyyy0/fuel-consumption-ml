# Final Model Selection

## Objective

Select and freeze the final fuel-consumption prediction model using only Train and Validation results.

The chronological Test set remains untouched during this selection process.

---

## Candidate Models

The two strongest candidates were:

### Original Context XGBoost

- n_estimators: 300
- learning_rate: 0.05
- max_depth: 4
- subsample: 0.8
- colsample_bytree: 0.8

Validation performance:

- MAE: 0.3791 L
- RMSE: 1.6833 L
- R²: 0.9102

---

### Tuned Context XGBoost

- n_estimators: 200
- learning_rate: 0.03
- max_depth: 5
- subsample: 1.0
- colsample_bytree: 1.0

Validation performance:

- MAE: 0.3506 L
- RMSE: 1.7868 L
- R²: 0.8989

---

## Primary Selection Metric

The primary project metric is:

**Mean Absolute Error (MAE)**

MAE was selected because it provides a direct and interpretable measure of average trip-level prediction error in liters.

---

## Comparison

| Model                    |        MAE |       RMSE |         R² |
| ------------------------ | ---------: | ---------: | ---------: |
| Original Context XGBoost |     0.3791 | **1.6833** | **0.9102** |
| Tuned Context XGBoost    | **0.3506** |     1.7868 |     0.8989 |

The tuned model reduced MAE by approximately:

`0.0285 L`

relative to the original Context XGBoost.

---

## Overfitting Comparison

### Original Context

- Train MAE: 0.2145
- Validation MAE: 0.3791
- MAE gap: 0.1646

### Tuned Context

- Train MAE: 0.2120
- Validation MAE: 0.3506
- MAE gap: 0.1385

The tuned model produced a smaller MAE generalization gap.

---

## Error Analysis Consideration

The tuned model improved average absolute error for:

- Many short and medium trips
- Long-distance trips overall
- Several high-fuel vehicles

However, it produced larger errors on a small number of extreme observations.

This explains why RMSE and R² were slightly worse than the original Context XGBoost.

---

## Final Feature Set

The final model uses 13 predictors.

### Trip Features

- `trip_distance_km`
- `trip_duration_min`

### Speed Features

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`

### RPM Features

- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`

### Vehicle-State Feature

- `idle_ratio`

### Context Features

- `trip_hour`
- `day_of_week`
- `is_weekend`

---

## Excluded Variables

The following are not used as model predictors:

- `trip_id`
- `vehicle_id`
- `period`
- Target-derived fuel variables
- Fuel-match metadata

---

## Final Hyperparameters

```text
n_estimators = 200
learning_rate = 0.03
max_depth = 5
subsample = 1.0
colsample_bytree = 1.0
random_state = 42
```

## Vehicle Generalization

Leave-One-Vehicle-Out validation produced:

- MAE: **0.5369 L**
- RMSE: **2.0996 L**
- R²: **0.8442**

This indicates useful generalization to unseen vehicles, although performance varies across vehicle operating regimes.

---

## Final Decision

**Selected Model: Tuned Context XGBoost**

Selection rationale:

1. Best Validation MAE
2. MAE is the primary evaluation metric
3. Smaller Train–Validation MAE gap
4. Strong performance across most trip-distance groups
5. Strong performance across most vehicles
6. Useful unseen-vehicle generalization

The model's main limitation is sensitivity to a small number of extreme high-fuel observations.

---

## Model Freeze

The final model configuration is now frozen.

No additional:

- Feature selection
- Hyperparameter tuning
- Model switching
- Threshold adjustment

will be performed based on Test-set performance.

The next step is a single final evaluation on the untouched chronological Test dataset.
