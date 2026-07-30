# SHAP Analysis

## Purpose

The final XGBoost model achieved strong predictive performance on the unseen test dataset. However, high predictive accuracy alone is insufficient for operational decision-making. To improve model interpretability, SHAP (SHapley Additive exPlanations) was used to quantify the contribution of each feature to the model's predictions.

The objective of this analysis is to understand:

- Which features have the greatest impact on predicted fuel consumption.
- How each feature influences individual trip predictions.
- Whether the model behavior aligns with domain knowledge.

---

# Methodology

The analysis was performed on the untouched test dataset (1,985 trips).

The final frozen XGBoost model was retrained using the combined Train and Validation datasets before generating SHAP values.

Three SHAP visualizations were created:

- Global Feature Importance (Bar Plot)
- Global SHAP Summary (Beeswarm Plot)
- Local Explanation (Waterfall Plot)

The prediction reconstruction error between SHAP values and the model output was approximately zero, confirming that the SHAP explanations accurately represent the model behavior.

Maximum prediction reconstruction difference:

```
0.000032
```

---

# Global Feature Importance

The mean absolute SHAP values indicate how strongly each feature contributes to the model prediction across all trips.

| Rank | Feature           | Mean | SHAP |     |
| ---: | ----------------- | ---: | ---- | --- |
|    1 | trip_distance_km  | 2.62 |
|    2 | max_rpm           | 0.35 |
|    3 | trip_hour         | 0.32 |
|    4 | avg_rpm           | 0.16 |
|    5 | trip_duration_min | 0.12 |
|    6 | max_speed_kmh     | 0.11 |
|    7 | speed_std         | 0.07 |
|    8 | avg_speed_kmh     | 0.07 |
|    9 | rpm_std           | 0.06 |
|   10 | idle_ratio        | 0.04 |

## Interpretation

Trip distance is by far the most influential predictor of fuel consumption. Its contribution is substantially larger than all other variables, indicating that travel distance dominates fuel usage.

Engine RPM provides the second-largest contribution, suggesting that engine operating conditions also influence predicted fuel consumption after accounting for trip distance.

Trip hour also contributes meaningfully, indicating that the model captures differences associated with traffic conditions or driving patterns at different times of day.

---

# SHAP Summary Plot

The SHAP summary plot illustrates both feature importance and the direction of each feature's effect.

Major observations include:

- Larger trip distances consistently increase predicted fuel consumption.
- Short trips reduce predicted fuel consumption.
- Higher engine RPM generally increases fuel consumption.
- Higher idle ratio has a relatively small but positive contribution.
- Speed-related features provide moderate predictive value.
- Weekend and High RPM Ratio contribute very little to the final model.

Overall, the SHAP summary confirms that the learned relationships are consistent with expected vehicle operating behavior.

---

# Local Explanation

A representative trip was selected to demonstrate how the model generates an individual prediction.

The baseline prediction for an average trip is:

```
Expected Fuel = 2.417 L
```

For the selected trip, the final prediction was:

```
Predicted Fuel = 0.357 L
```

The largest contributing factor was:

- Short trip distance (-2.08 L)

Smaller contributions from engine RPM, speed, and idle behavior further adjusted the prediction.

This visualization demonstrates that SHAP can decompose a complex XGBoost prediction into understandable feature-level contributions.

---

# Business Insights

The SHAP analysis provides several operational insights.

- Trip distance is the dominant driver of fuel consumption.
- Engine RPM is the second most influential operational variable.
- Driving time contributes additional predictive information, likely reflecting traffic conditions.
- Idle behavior has a measurable but relatively small impact compared to trip distance.
- Weekend driving has almost no influence on predicted fuel consumption in this dataset.

These findings indicate that operational efficiency improvements should focus primarily on reducing unnecessary travel distance and optimizing engine operating conditions.

---

# Conclusion

SHAP analysis confirms that the final XGBoost model is both accurate and interpretable.

The model primarily relies on trip distance while incorporating engine RPM, driving conditions, and speed-related variables to refine its predictions.

By providing feature-level explanations for every prediction, SHAP increases transparency and supports the use of the model in fleet fuel-efficiency analysis.
