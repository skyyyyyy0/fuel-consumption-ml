# Train / Validation / Test Split Strategy

## 1. Objective

Define a leakage-safe evaluation strategy for fuel-consumption modeling.

Because the project predicts future trip-level fuel consumption, the primary evaluation should preserve chronological ordering.

The final split strategy must ensure that future observations are not used to train models that are evaluated on earlier observations.

---

# 2. Modeling Dataset

Source:

`data/processed/trip_ml_features.csv`

Dataset characteristics:

- Total Trips: 9,923
- Vehicles: 12
- Earliest Trip: 2026-04-17
- Latest Trip: 2026-07-18
- Missing Trip Start Timestamps: 0

Each row represents one cleaned and validated vehicle trip.

---

# 3. Why Random Split Was Not Selected

A conventional random train/test split would mix earlier and later trips together.

This would create an overly optimistic evaluation because future operating patterns could appear in the training data while earlier observations appear in validation or test data.

The project therefore uses a chronological split as the primary evaluation strategy.

---

# 4. Period-Based Split Investigation

An initial candidate was:

- Before → Train
- After → Validation
- Final → Test

However, the operational periods overlap in time.

Observed boundaries:

## Before / After

Before latest timestamp:

`2026-05-19 07:56:33 UTC`

After earliest timestamp:

`2026-05-17 15:13:19 UTC`

The periods overlap.

## After / Final

After latest timestamp:

`2026-06-19 08:00:58 UTC`

Final earliest timestamp:

`2026-06-17 15:08:24 UTC`

These periods also overlap.

Therefore, the Before / After / Final labels are not used directly as ML split boundaries.

`period` remains metadata for diagnostics and error analysis.

---

# 5. Final Chronological Split

The complete dataset was sorted by:

`trip_start_time`

The final primary evaluation split is:

## Train

- Trips: 5,953
- Share: 60%
- Start: 2026-04-17 15:14:05 UTC
- End: 2026-06-11 06:32:02 UTC
- Vehicles represented: 12

## Validation

- Trips: 1,985
- Share: 20%
- Start: 2026-06-11 06:35:57 UTC
- End: 2026-06-29 07:36:27 UTC
- Vehicles represented: 12

## Test

- Trips: 1,985
- Share: 20%
- Start: 2026-06-29 07:37:02 UTC
- End: 2026-07-18 07:25:33 UTC
- Vehicles represented: 12

---

# 6. Chronological Validation

Confirmed:

`Train max timestamp < Validation min timestamp`

Result:

**True**

Confirmed:

`Validation max timestamp < Test min timestamp`

Result:

**True**

No chronological overlap exists between the final Train, Validation, and Test sets.

---

# 7. Vehicle Coverage

All 12 vehicles are represented in all three primary splits.

Even the vehicle with the smallest sample size remains represented across Train, Validation, and Test.

Example:

`VEH_11`

- Train: 190 Trips
- Validation: 65 Trips
- Test: 74 Trips

This provides vehicle coverage while preserving chronological ordering.

---

# 8. Target Distribution

The target distributions remain reasonably similar across splits.

## Train

- Mean Fuel: 2.393 L
- Median Fuel: 0.320 L

## Validation

- Mean Fuel: 2.499 L
- Median Fuel: 0.360 L

## Test

- Mean Fuel: 2.492 L
- Median Fuel: 0.370 L

The future splits contain slightly higher median fuel consumption, but no severe distribution collapse is observed.

---

# 9. Distance Distribution

Average Trip Distance:

- Train: 10.812 km
- Validation: 10.868 km
- Test: 11.146 km

Median Trip Distance:

- Train: 1.884 km
- Validation: 2.169 km
- Test: 1.963 km

Trip-distance distributions remain broadly comparable across splits.

---

# 10. Test Set Policy

The Test set is treated as an untouched final evaluation dataset.

The Test set must not be used for:

- Feature selection
- Hyperparameter tuning
- Model selection
- Threshold selection
- Comparing experimental feature sets
- Iterative debugging based on model performance

All development decisions are made using Train and Validation data only.

The Test set will be evaluated only after the final model configuration has been selected and frozen.

---

# 11. Secondary Generalization Test

The chronological split evaluates:

> How well does the model predict future trips for vehicles that were already observed during training?

A separate Vehicle Holdout experiment will later evaluate:

> How well does the model generalize to vehicles that were never observed during training?

These two evaluations answer different modeling questions and will be reported separately.

---

# 12. Final Decision

Primary evaluation strategy:

**Chronological 60 / 20 / 20 Train / Validation / Test Split**

- [x] Chronological ordering preserved
- [x] Train occurs before Validation
- [x] Validation occurs before Test
- [x] All 12 vehicles represented
- [x] Target distributions reviewed
- [x] Distance distributions reviewed
- [x] Period overlap investigated
- [x] Period labels excluded as split boundaries
- [x] Test set reserved for final evaluation

## Status

**PASS — Split strategy is ready for model development.**
