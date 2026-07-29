# Vehicle Holdout Validation

## Objective

Evaluate whether the fuel-consumption model can generalize to vehicles that were completely unseen during training.

The primary chronological Test set was not used in this experiment.

---

# Validation Strategy

A Leave-One-Vehicle-Out evaluation was performed across all 12 vehicles.

For each iteration:

1. One vehicle was completely excluded from training.
2. The model was trained using the remaining 11 vehicles.
3. The excluded vehicle was used as the holdout set.
4. MAE, RMSE, and R² were calculated.

The tuned XGBoost Context model configuration was used.

---

# Overall Unseen-Vehicle Performance

- MAE: **0.5369 L**
- RMSE: **2.0996 L**
- R²: **0.8442**
- Median Vehicle MAE: **0.2150 L**
- Best Vehicle MAE: **0.1043 L**
- Worst Vehicle MAE: **3.0703 L**

---

# Vehicle-Level Results

| Vehicle | Trips | Mean Fuel (L) |    MAE |   RMSE |      R² |
| ------- | ----: | ------------: | -----: | -----: | ------: |
| VEH_01  | 1,402 |         0.313 | 0.1911 | 0.3862 |  0.5753 |
| VEH_02  |   494 |         0.755 | 0.1651 | 0.7008 | -0.2608 |
| VEH_03  |   463 |         1.097 | 0.1269 | 0.2203 |  0.9615 |
| VEH_04  |   544 |         1.019 | 0.2466 | 0.8291 |  0.5141 |
| VEH_05  |   291 |        11.844 | 3.0703 | 8.3095 |  0.4454 |
| VEH_06  |   469 |         9.595 | 1.8811 | 3.6939 |  0.6213 |
| VEH_07  |   408 |         0.886 | 0.2389 | 0.4622 |  0.5941 |
| VEH_08  |   628 |         0.639 | 0.1580 | 0.2466 |  0.9074 |
| VEH_09  | 1,427 |         0.298 | 0.1043 | 0.1829 |  0.4281 |
| VEH_10  | 1,038 |         0.404 | 0.1244 | 0.1976 |  0.7905 |
| VEH_11  |   255 |        13.654 | 2.0304 | 3.2548 |  0.8953 |
| VEH_12  |   519 |         8.277 | 1.8331 | 3.0212 |  0.7591 |

---

# Key Findings

The model generalized well to many unseen vehicles.

For VEH_01–04 and VEH_07–10, absolute prediction errors were relatively low, with MAE generally between approximately 0.10 and 0.25 L.

However, substantially larger errors were observed for:

- VEH_05
- VEH_06
- VEH_11
- VEH_12

These vehicles also had substantially higher average trip fuel consumption and generally longer-distance operating profiles.

This indicates that vehicle operating regime and fleet heterogeneity affect out-of-vehicle generalization.

---

# Interpretation of R²

R² should be interpreted together with absolute-error metrics.

For example, VEH_02 produced:

- MAE: 0.1651 L
- R²: -0.2608

Although R² was negative, the absolute prediction error remained relatively small.

A low or negative R² can occur when the target has limited within-vehicle variation, making R² particularly sensitive to prediction error.

For this reason, MAE remains the primary evaluation metric.

---

# Model Limitation

The model performs substantially better when an unseen vehicle has an operating profile similar to vehicles represented in the training data.

Performance deteriorates for some vehicles with substantially different fuel-consumption and trip-distance regimes.

Future improvements could include:

- Additional vehicles representing diverse operating profiles
- Vehicle-class information
- Vehicle specifications
- Engine characteristics
- Payload or load information
- Additional environmental features

---

# Leakage Control

The final chronological Test dataset was not used during the vehicle holdout experiment.

Vehicle ID was used only to define the holdout groups and was not included as a model predictor.

---

# Conclusion

The vehicle holdout experiment demonstrates that the model can generalize to many unseen vehicles, while also identifying an important limitation related to fleet heterogeneity.

Overall unseen-vehicle performance:

- MAE: **0.5369 L**
- RMSE: **2.0996 L**
- R²: **0.8442**

The results support continued evaluation of the XGBoost model while highlighting the need to account for differences between vehicle operating regimes.

## Status

**Vehicle generalization validation complete.**
