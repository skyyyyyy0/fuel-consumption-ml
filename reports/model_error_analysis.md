# Model Overfitting & Error Analysis

## Objective

Evaluate the two leading XGBoost configurations for:

- Train vs Validation performance
- Overfitting
- Residual behavior
- Trip-distance error patterns
- Vehicle-level errors
- Period-level errors
- Extreme prediction failures

The chronological Test set remained untouched during this analysis.

---

# Candidate Models

Two Context-feature XGBoost models were evaluated.

## Original Context XGBoost

- n_estimators: 300
- learning_rate: 0.05
- max_depth: 4
- subsample: 0.8
- colsample_bytree: 0.8

## Tuned Context XGBoost

- n_estimators: 200
- learning_rate: 0.03
- max_depth: 5
- subsample: 1.0
- colsample_bytree: 1.0

---

# Train vs Validation Performance

| Model            | Train MAE | Validation MAE |    MAE Gap | Train RMSE | Validation RMSE | Train R² | Validation R² |
| ---------------- | --------: | -------------: | ---------: | ---------: | --------------: | -------: | ------------: |
| Original Context |    0.2145 |         0.3791 |     0.1646 |     0.5719 |          1.6833 |   0.9880 |        0.9102 |
| Tuned Context    |    0.2120 |     **0.3506** | **0.1385** |     0.6178 |          1.7868 |   0.9860 |        0.8989 |

---

# Overfitting Assessment

Both models perform substantially better on Train than on Validation.

This indicates some degree of overfitting.

However, Validation performance remains strong for both models.

The tuned model produced a smaller MAE gap:

`0.1646 → 0.1385`

This suggests slightly better generalization according to the primary MAE metric.

However, its RMSE gap and R² gap were slightly larger.

Therefore, tuning improved typical absolute prediction accuracy but did not reduce all forms of generalization error.

---

# Error by Trip Distance

## Original Context

| Distance Group | Trips |    MAE |
| -------------- | ----: | -----: |
| 0–0.5 km       |   378 | 0.2567 |
| 0.5–1 km       |   271 | 0.1067 |
| 1–5 km         |   722 | 0.1500 |
| 5–20 km        |   232 | 0.2764 |
| 20–50 km       |   265 | 0.8278 |
| 50+ km         |   117 | 2.0061 |

## Tuned Context

| Distance Group | Trips |    MAE |
| -------------- | ----: | -----: |
| 0–0.5 km       |   378 | 0.2167 |
| 0.5–1 km       |   271 | 0.1120 |
| 1–5 km         |   722 | 0.1352 |
| 5–20 km        |   232 | 0.2847 |
| 20–50 km       |   265 | 0.7904 |
| 50+ km         |   117 | 1.7984 |

---

# Distance-Based Finding

Prediction error increases substantially with trip length.

The largest errors occur in trips above 20 km, particularly trips above 50 km.

The tuned model improved MAE in the longest-distance groups:

- 20–50 km: 0.8278 → 0.7904
- 50+ km: 2.0061 → 1.7984

This suggests the tuned model improves typical long-trip prediction accuracy.

---

# Vehicle-Level Errors

The highest-error vehicles were consistently:

- VEH_05
- VEH_06
- VEH_11
- VEH_12

## Original Context

- VEH_05 MAE: 2.7630 L
- VEH_06 MAE: 1.3439 L
- VEH_11 MAE: 1.0355 L
- VEH_12 MAE: 0.9217 L

## Tuned Context

- VEH_05 MAE: 2.5801 L
- VEH_06 MAE: 1.2114 L
- VEH_11 MAE: 1.0506 L
- VEH_12 MAE: 0.8085 L

The tuned model improved average absolute error for VEH_05, VEH_06, and VEH_12.

VEH_11 performance was approximately unchanged.

These vehicles also operate in high-fuel and longer-distance regimes, confirming that fleet heterogeneity remains an important source of model error.

---

# Period-Level Errors

## Original Context

- After MAE: 0.3670 L
- Final MAE: 0.3885 L

## Tuned Context

- After MAE: 0.3380 L
- Final MAE: 0.3603 L

The tuned model improved MAE in both periods.

The Final period remains slightly harder to predict than the After period.

---

# Extreme Error Analysis

Several trips produced errors substantially larger than the typical prediction error.

The most extreme example was:

- Vehicle: VEH_05
- Actual Fuel: 66.41 L
- Original Prediction: 17.47 L
- Original Absolute Error: 48.94 L
- Tuned Prediction: 9.51 L
- Tuned Absolute Error: 56.90 L

The tuned model therefore improved average MAE but performed worse on this extreme observation.

Other extreme errors were also concentrated in high-fuel vehicles and unusual trip profiles.

---

# MAE vs RMSE Trade-Off

The two candidate models optimize different aspects of performance.

## Tuned Context

Strengths:

- Best Validation MAE
- Smaller MAE train-validation gap
- Better average performance for many vehicles
- Better MAE on long-distance trips

Weakness:

- Larger extreme errors
- Worse RMSE
- Slightly lower R²

## Original Context

Strengths:

- Best Validation RMSE
- Best Validation R²
- More robust to several extreme errors

Weakness:

- Higher average absolute error

---

# Key Finding

The tuned XGBoost model provides better typical trip-level accuracy.

However, the original Context model is more robust to large prediction errors.

The difference between MAE and RMSE is primarily driven by a small number of extreme high-fuel trips.

---

# Leakage Control

The final chronological Test dataset was not used during:

- Error analysis
- Model comparison
- Hyperparameter tuning
- Candidate selection

All conclusions in this report are based only on Train and Validation data.

---

# Decision

Both models remain viable final candidates.

Because MAE is the primary project metric, the Tuned Context XGBoost remains the leading candidate.

However, final model selection should explicitly acknowledge its weaker RMSE and sensitivity to extreme high-fuel observations.

## Status

**PASS — Overfitting and error analysis complete.**
