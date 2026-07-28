# Target & Trip EDA Findings

## 1. Dataset

EDA was performed on the cleaned feature dataset:

`data/processed/trip_ml_features.csv`

Dataset characteristics:

- Trips: 9,923
- Vehicles: 12
- Minimum trip distance: 0.1 km
- Missing core features: 0

---

# 2. Fuel Target Distribution

The fuel-consumption target is strongly right-skewed.

- Mean: 2.434 L
- Median: 0.340 L
- P95: 15.740 L
- P99: 22.367 L
- Maximum: 66.410 L
- Skewness: 3.282

Most trips consume relatively small amounts of fuel, while a smaller number of long or high-consumption trips create a long right tail.

This distribution is consistent with the heterogeneous trip-length and vehicle-operation patterns observed in the fleet.

---

# 3. Trip Distance Distribution

Trip distance is also strongly right-skewed.

- Mean: 10.890 km
- Median: 1.951 km
- P95: 62.605 km
- Maximum: 132.074 km
- Skewness: 2.526

The fleet contains many short trips and a smaller number of substantially longer trips.

Therefore, median and percentile statistics are more representative than the mean alone.

---

# 4. Trip Duration Distribution

Trip duration shows a similar right-skewed pattern.

- Mean: 16.687 min
- Median: 8.366 min
- P95: 58.497 min
- Maximum: 148.097 min
- Skewness: 2.194

Long-duration trips represent a relatively small portion of the dataset.

---

# 5. Fuel vs. Distance

Fuel consumption has a strong positive relationship with trip distance.

Pearson correlation:

`Fuel vs. Distance = 0.9185`

Longer trips generally consume more fuel, making trip distance a strong candidate predictor for the baseline model.

Trip distance is not derived from the fuel target and therefore does not represent target leakage.

The scatter plot also shows multiple consumption bands, suggesting that distance alone does not explain all variation.

Vehicle characteristics and operating behavior may explain additional differences.

---

# 6. Fuel vs. Duration

Fuel consumption is also strongly associated with trip duration.

Pearson correlation:

`Fuel vs. Duration = 0.8317`

Trip distance and duration are themselves strongly correlated:

`Distance vs. Duration = 0.9420`

Both variables will remain candidate features, but their relationship should be considered during correlation and model diagnostics.

---

# 7. Short vs. Long Trips

Median fuel consumption increases substantially with trip distance.

| Distance Group | Trips | Median Fuel |
| -------------- | ----: | ----------: |
| 0.1–0.5 km     | 2,084 |      0.06 L |
| 0.5–1 km       | 1,366 |      0.14 L |
| 1–5 km         | 3,418 |      0.34 L |
| 5–20 km        | 1,151 |      1.14 L |
| 20–50 km       | 1,284 |      6.28 L |
| 50+ km         |   620 |     18.20 L |

This provides a physically interpretable relationship between trip length and total fuel consumption.

---

# 8. Target Transformation Investigation

The raw fuel target has substantial positive skew.

`Raw target skewness = 3.2822`

Applying a `log1p` transformation reduced the skewness:

`log1p target skewness = 1.6726`

The transformation improves the distribution but does not completely normalize it.

## Decision

The baseline target will remain:

`trip_fuel_used_liter`

A log-transformed target will be tested as an alternative during modeling.

The final choice will be based on validation performance and residual behavior rather than target skewness alone.

---

# 9. Key EDA Finding

Trip distance explains a large portion of fuel-consumption variation.

However, the Fuel vs. Distance scatter plot contains multiple visible consumption bands.

This suggests that additional variables may explain residual fuel variation, including:

- Vehicle characteristics
- RPM behavior
- Speed behavior
- Idle behavior
- Operating context

These relationships will be investigated in the next EDA stage.
