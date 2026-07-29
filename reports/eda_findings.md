# Exploratory Data Analysis Findings

## 1. Objective

This analysis evaluates the final trip-level machine-learning dataset before model development.

The objectives are to:

- Understand the distribution of trip fuel consumption
- Identify the major drivers of fuel consumption
- Evaluate driving-behavior features
- Quantify vehicle-level and period-level differences
- Identify redundant features
- Define candidate modeling feature sets
- Confirm that target leakage is controlled
- Verify that the dataset is ready for train / validation / test splitting

---

# 2. Final Analysis Dataset

Source dataset:

`data/processed/trip_ml_features.csv`

Final dataset:

- Trips: 9,923
- Vehicles: 12
- Vehicle-period combinations: 36
- Periods: Before, After, Final
- Duplicate Trip IDs: 0
- Missing candidate predictor values: 0
- Missing target values: 0

Target:

`trip_fuel_used_liter`

Each observation represents one cleaned and validated vehicle trip.

---

# 3. Target Distribution

Trip fuel consumption is strongly right-skewed.

Key statistics:

- Mean: 2.434 L
- Median: 0.340 L
- P95: 15.740 L
- P99: 22.367 L
- Maximum: 66.410 L
- Skewness: 3.282

The large difference between the mean and median reflects substantial variation in trip length across the fleet.

A `log1p` transformation reduced target skewness from:

`3.282 → 1.673`

However, the raw target remains the primary modeling target because fuel consumption in liters has direct physical and business interpretation.

A log-target model may be evaluated as a secondary experiment.

---

# 4. Trip Characteristics

Trip distance and duration are also right-skewed.

## Distance

- Mean: 10.890 km
- Median: 1.951 km
- P95: 62.605 km
- Maximum: 132.074 km

## Duration

- Mean: 16.687 minutes
- Median: 8.366 minutes
- P95: 58.497 minutes
- Maximum: 148.097 minutes

The dataset therefore contains a mixture of short local trips and substantially longer operating cycles.

Trips below 0.1 km were excluded during cleaning because fuel-per-distance measurements became unstable and operationally uninformative at extremely small distances.

---

# 5. Fuel vs Trip Size

Trip distance is the strongest individual predictor of total trip fuel consumption.

Observed correlations:

- Fuel vs Distance: 0.918
- Fuel vs Duration: 0.832
- Distance vs Duration: 0.942

This indicates that trip exposure explains a large portion of total fuel consumption.

Longer trips naturally consume more total fuel.

Because distance and duration are highly correlated, their incremental predictive value should be evaluated during modeling rather than removing one solely based on pairwise correlation.

---

# 6. Driving-Behavior Relationships

Raw fleet-level correlations with Fuel were:

- Average Speed: 0.708
- Speed Standard Deviation: 0.608
- Maximum Speed: 0.538
- Idle Ratio: -0.262
- RPM Standard Deviation: -0.225
- Maximum RPM: -0.222
- Average RPM: -0.154
- High-RPM Ratio: -0.042

At first glance, several Speed and RPM variables appear strongly related to Fuel.

However, these raw correlations are heavily influenced by trip distance and vehicle composition.

---

# 7. Distance-Controlled Driving Behavior

After controlling for trip distance, fleet-level relationships became substantially weaker.

After controlling for both distance and vehicle identity, correlations were approximately:

- Average RPM: 0.093
- Maximum RPM: 0.043
- Average Speed: 0.008
- Maximum Speed: 0.030
- Idle Ratio: -0.009
- High-RPM Ratio: 0.015

This is an important EDA finding.

Much of the apparent relationship between driving behavior and total Fuel at the fleet level is explained by:

1. Trip distance
2. Differences between vehicles

Driving-behavior variables may still provide incremental predictive value and therefore remain candidate features.

Their usefulness will be determined through validation experiments.

---

# 8. Speed Feature Redundancy

Strong correlations were observed among Speed features:

- Maximum Speed ↔ Speed Standard Deviation: 0.961
- Average Speed ↔ Speed Standard Deviation: 0.932
- Average Speed ↔ Maximum Speed: 0.887

These features contain substantial overlapping information.

They are retained initially because tree-based models can handle correlated predictors reasonably well, but reduced feature sets may be evaluated later.

---

# 9. RPM Feature Redundancy

RPM features also showed substantial internal correlation:

- Average RPM ↔ Maximum RPM: 0.855
- Maximum RPM ↔ RPM Standard Deviation: 0.877
- Average RPM ↔ RPM Standard Deviation: 0.796

High-RPM Ratio is less strongly correlated with the main RPM summary variables.

The RPM variables remain candidate predictors, but redundancy should be considered when interpreting feature importance and linear-model coefficients.

---

# 10. High-RPM Behavior

Fleet RPM analysis showed:

- Mean RPM: approximately 1,199
- P95: approximately 2,045 RPM
- P99: approximately 2,321 RPM
- Maximum observed RPM: approximately 4,439 RPM

The percentage of observations above 3,000 RPM was approximately 0.34%.

Therefore, `high_rpm_ratio` represents relatively rare high-RPM operating behavior.

The 3,000 RPM threshold is retained as an interpretable behavioral indicator, but its predictive contribution is expected to be limited.

---

# 11. Idle Behavior

The final time-weighted idle ratio had approximately:

- Mean: 0.148
- Median: 0.139
- P95: 0.318
- Maximum: 1.000

Because the telemetry is event-driven, idle behavior was calculated using time-weighted intervals rather than simple row-count proportions.

This reduces bias caused by irregular sampling intervals.

Vehicle Active was investigated but was not available as a usable signal in the source data.

Idle state was therefore derived primarily from available Speed and RPM information.

---

# 12. Vehicle-Level Differences

Substantial differences exist across vehicles.

Examples of mean trip Fuel:

- VEH_01: 0.326 L
- VEH_09: 0.301 L
- VEH_05: 11.663 L
- VEH_06: 9.572 L
- VEH_11: 13.725 L
- VEH_12: 8.078 L

These differences correspond with major differences in typical trip distance and operating patterns.

For example, several vehicles primarily operate short trips, while VEH_05, VEH_06, VEH_11, and VEH_12 have substantially longer average trips.

Vehicle identity is therefore an important source of heterogeneity.

The primary predictor set excludes `vehicle_id`, while a separate vehicle-aware modeling experiment will evaluate the benefit of explicitly including vehicle identity.

---

# 13. Period-Level Differences

Fleet-level average Fuel consumption was:

- Before: 2.402 L
- After: 2.403 L
- Final: 2.503 L

Average trip distance was also similar across periods:

- Before: 10.973 km
- After: 10.675 km
- Final: 11.050 km

Period-level differences are substantially smaller than vehicle-level differences.

Therefore, `period` is retained as metadata rather than included as a primary predictor.

---

# 14. Time and Context Features

Context-feature correlations with Fuel were:

- Trip Hour: -0.352
- Day of Week: 0.097
- Weekend Indicator: 0.167

Trip Hour shows a moderate raw relationship with Fuel.

However, this may reflect fleet schedules, vehicle assignments, and route patterns rather than a direct causal time-of-day effect.

Context variables are therefore treated as optional predictors.

Their inclusion will depend on validation performance.

---

# 15. Temperature

Outside-air temperature was investigated as a candidate predictor.

No sufficiently reliable Outside Air Temperature signal was available across the required dataset.

Temperature was therefore excluded rather than imputing or constructing an unreliable feature.

---

# 16. Multicollinearity Candidates

Feature pairs with absolute correlation of at least 0.80 included:

- Maximum Speed ↔ Speed Standard Deviation
- Trip Distance ↔ Trip Duration
- Average Speed ↔ Speed Standard Deviation
- Average Speed ↔ Maximum Speed
- Maximum RPM ↔ RPM Standard Deviation
- Average RPM ↔ Maximum RPM
- Trip Distance ↔ Average Speed

These relationships will be considered when interpreting models.

Features are not automatically removed solely because of high pairwise correlation.

---

# 17. Final Candidate Feature Sets

## Baseline Model

- `trip_distance_km`
- `trip_duration_min`

Purpose:

Establish how well total trip fuel consumption can be predicted from basic trip exposure alone.

## Extended Model

Baseline plus:

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`
- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`
- `idle_ratio`

Purpose:

Measure whether engine and driving-behavior telemetry improves prediction beyond Distance and Duration.

## Context Model

Extended model plus:

- `trip_hour`
- `day_of_week`
- `is_weekend`

Purpose:

Measure whether operating-time context provides additional predictive value.

## Vehicle-Aware Experiment

A separate experiment will evaluate selected predictors plus:

- `vehicle_id`

This experiment will be reported separately from vehicle-independent performance.

---

# 18. Metadata

The following variables are retained for splitting, diagnostics, and error analysis:

- `trip_id`
- `vehicle_id`
- `period`
- `trip_start_time`
- `trip_end_time`

They are not part of the primary numerical predictor matrix.

---

# 19. Target Leakage Validation

The final feature-selection validation passed.

Confirmed:

- Target is not included in X
- `trip_id` is not included in X
- Fuel-match confidence is not included in X
- Fuel-event timestamps are not included in X
- Total Fuel Used is not included in X
- Idle Fuel variables are not included in X
- No known target-derived feature is included in X
- Metadata is separated from the predictor matrix

Final validation result:

**PASS**

---

# 20. Final EDA Findings

The major findings are:

1. Trip distance is the dominant predictor of total trip fuel consumption.
2. Trip duration provides additional but highly overlapping trip-exposure information.
3. Raw Speed/RPM/Fuel relationships are strongly influenced by trip distance and vehicle composition.
4. Vehicle-level operating differences are substantial.
5. Speed and RPM feature groups contain significant redundancy.
6. Idle behavior is physically interpretable but has weak independent linear correlation with total Fuel after controlling for Distance and Vehicle.
7. Context variables may capture operating schedules but require validation before retention.
8. Temperature could not be included because of insufficient reliable signal coverage.
9. The final candidate predictor matrix contains no known target leakage.
10. Feature retention should ultimately be determined through out-of-sample validation performance.

---

# 21. Modeling Readiness

Final feature-selection validation:

- Rows: 9,923
- Vehicles: 12
- Baseline Features: 2
- Extended Features: 10
- Context Features: 13
- Missing Candidate Features: 0
- Duplicate Feature Definitions: 0
- Known Leakage in X: 0

## Final Decision

**GO — Dataset is ready for train / validation / test split design and baseline modeling.**
