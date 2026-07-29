# Final Model Results

## Objective

Evaluate the frozen final fuel-consumption prediction model on the untouched chronological Test set.

The final model configuration was selected using only Train and Validation data.

No additional feature selection, hyperparameter tuning, or model switching was performed after reviewing Test performance.

---

## Final Model

**Algorithm:** XGBoost Regressor

**Feature Set:** Context

**Number of Predictors:** 13

### Hyperparameters

```text
n_estimators = 200
learning_rate = 0.03
max_depth = 5
subsample = 1.0
colsample_bytree = 1.0
random_state = 42
```

# Final Feature Set

The final model uses 13 predictors.

## Trip Features

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

---

# Final Training Strategy

The final model was retrained using the combined Train and Validation datasets.

## Development Dataset

- Train: 5,953 trips
- Validation: 1,985 trips
- Combined Development: 7,938 trips

## Final Test Dataset

- Test: 1,985 trips
- Vehicles: 12

The Test set represented the latest chronological portion of the dataset and remained untouched until final evaluation.

---

# Final Test Performance

| Metric |       Result |
| ------ | -----------: |
| MAE    | **0.3573 L** |
| RMSE   | **1.6166 L** |
| R²     |   **0.9032** |

The model achieved an average absolute prediction error of approximately:

**0.36 liters per trip**

on the untouched future Test dataset.

---

# Validation vs Test Performance

| Dataset    |    MAE |       RMSE |         R² |
| ---------- | -----: | ---------: | ---------: |
| Validation | 0.3506 |     1.7868 |     0.8989 |
| Final Test | 0.3573 | **1.6166** | **0.9032** |

Test performance remained very close to Validation performance.

MAE increased only slightly:

`0.3506 → 0.3573 L`

while RMSE and R² improved.

This indicates that the selected model generalized well to the later chronological Test period.

# Comparison with Simple Baseline

## Mean Baseline

- MAE: 3.2754 L
- RMSE: 5.6199 L
- R²: approximately 0

## Final XGBoost Model

- MAE: 0.3573 L
- RMSE: 1.6166 L
- R²: 0.9032

The final model substantially outperformed the naive baseline.

---

# Comparison with Linear Regression

## Best Linear Regression

- MAE: 0.7495 L
- RMSE: 2.4686 L
- R²: 0.8070

## Final XGBoost Model

- MAE: 0.3573 L
- RMSE: 1.6166 L
- R²: 0.9032

The nonlinear XGBoost model produced substantially stronger predictive performance than Linear Regression.

---

# Vehicle-Level Test Performance

The highest-error vehicles were:

- VEH_11: MAE = 1.5940 L
- VEH_05: MAE = 1.5156 L
- VEH_06: MAE = 1.4146 L
- VEH_12: MAE = 0.8599 L

The lowest-error vehicles included:

- VEH_09: MAE = 0.0871 L
- VEH_10: MAE = 0.0885 L
- VEH_01: MAE = 0.1165 L
- VEH_03: MAE = 0.1185 L

This confirms that vehicle operating regime remains an important source of model-performance variation.

---

# Distance-Level Test Performance

| Distance Group | Trips |      MAE |
| -------------- | ----: | -------: |
| 0–0.5 km       |   420 | 0.2329 L |
| 0.5–1 km       |   254 | 0.0988 L |
| 1–5 km         |   666 | 0.2020 L |
| 5–20 km        |   247 | 0.2005 L |
| 20–50 km       |   265 | 0.7306 L |
| 50+ km         |   133 | 1.5688 L |

Prediction error increased with longer trip distances.

The highest absolute errors remained concentrated in long-distance and high-fuel operating regimes.

---

# Extreme Error Analysis

The largest Test error occurred for:

- Vehicle: VEH_06
- Distance: 30.66 km
- Actual Fuel: 55.95 L
- Predicted Fuel: 8.50 L
- Absolute Error: 47.45 L

Other large errors were concentrated among:

- VEH_05
- VEH_06
- VEH_11
- VEH_12

These vehicles also showed higher fuel consumption and different operating patterns during earlier EDA and vehicle-holdout validation.

# Final Feature Importance

The strongest predictor in the final model was:

`trip_distance_km`

Feature importance:

- Trip Distance: 0.7957
- Maximum Speed: 0.0441
- Maximum RPM: 0.0299
- Average RPM: 0.0276
- Trip Hour: 0.0256
- Idle Ratio: 0.0221
- Speed Standard Deviation: 0.0146
- Trip Duration: 0.0117
- Average Speed: 0.0112
- RPM Standard Deviation: 0.0097
- Day of Week: 0.0059
- High-RPM Ratio: 0.0016
- Weekend Indicator: 0.0000

Trip distance remained the dominant predictor of total trip fuel consumption.

However, the modeling experiments showed that engine, driving-behavior, and context features provided additional predictive value when modeled nonlinearly.

---

# Generalization Findings

Two different forms of generalization were evaluated.

## Future-Trip Generalization

Chronological Test performance:

- MAE: 0.3573 L
- RMSE: 1.6166 L
- R²: 0.9032

This indicates strong generalization to later trips from vehicles represented during model development.

## Unseen-Vehicle Generalization

Leave-One-Vehicle-Out performance:

- MAE: 0.5369 L
- RMSE: 2.0996 L
- R²: 0.8442

The model generalized to many unseen vehicles but experienced larger errors for high-fuel and long-distance vehicle profiles.

---

# Model Limitations

The main limitations identified were:

1. Higher prediction error for some high-fuel vehicles
2. Increased error for long-distance trips
3. Sensitivity to a small number of extreme fuel observations
4. Limited fleet size of 12 vehicles
5. No reliable Engine Load signal
6. No reliable Outside Air Temperature feature
7. Limited vehicle-specification information

Potential future improvements include:

- More vehicles
- More diverse operating regimes
- Vehicle-class information
- Engine specifications
- Payload or weight
- Engine-load data
- Additional environmental variables

---

# Leakage Control

The project maintained strict separation between model development and final evaluation.

The Test dataset was not used for:

- Feature selection
- Hyperparameter tuning
- Model comparison
- Error-driven model modification
- Final model selection

The final configuration was frozen before Test evaluation.

No additional tuning was performed after reviewing the Test results.

---

# Final Conclusion

The final Tuned Context XGBoost model successfully predicts trip-level fuel consumption using trip characteristics, engine telemetry, driving behavior, and operating context.

Final untouched Test performance:

- **MAE: 0.3573 L**
- **RMSE: 1.6166 L**
- **R²: 0.9032**

The model substantially outperformed both the naive baseline and Linear Regression while maintaining strong performance on future chronological data.

Vehicle-holdout testing also demonstrated useful generalization to unseen vehicles, although performance varied across different operating regimes.

---

# Final Decision

**GO — Final model selected and validated.**

The Machine Learning Modeling stage is complete.
