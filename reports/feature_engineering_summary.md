# Feature Engineering Summary

## 1. Purpose

Day 14 extended the clean trip-level modeling dataset created during Week 2.

The objectives were to:

- Review the availability of temperature data
- Evaluate additional contextual features
- Generate time-based features from Trip timestamps
- Preserve the integrity of the clean modeling dataset
- Define which new features should be retained as modeling candidates

---

# 2. Input Dataset

Input:

`data/processed/trip_ml_clean.csv`

Dataset size:

- Trips: 9,923
- Vehicles: 12
- Vehicle-period combinations: 36
- Duplicate Trip IDs: 0
- Missing core modeling features: 0

Each row represents one GeoTab Trip.

---

# 3. Temperature Feature Investigation

The `Outside air temperature` signal was investigated as a potential environmental feature.

The Day 14 audit did not identify a usable temperature signal under the expected signal definition and source structure.

Because temperature availability and consistency could not be established reliably across the fleet, temperature was not added to the baseline modeling dataset.

## Decision

**Baseline status: Excluded**

Temperature may be revisited as an optional feature if the source signal definition and coverage can be validated later.

This decision prevents an incompletely validated environmental signal from reducing dataset quality or fleet coverage.

---

# 4. Timestamp Parsing

The initial timestamp conversion produced 1,019 invalid timestamps because the source timestamps contained mixed ISO datetime formats.

Timestamp parsing was therefore updated to use mixed-format parsing.

After correction:

- Invalid Trip start timestamps: 0
- Missing time-derived features: 0

All 9,923 clean Trips were retained.

---

# 5. Timezone Standardization

Trip timestamps are stored in UTC.

Because the vehicles operate in Korea, Trip start timestamps were converted from UTC to:

**Korea Standard Time (KST / Asia/Seoul)**

Time-based contextual features were generated from the KST timestamp rather than UTC.

This ensures that features such as hour of day represent the actual local operating context of the vehicles.

---

# 6. Context Features

Three candidate contextual features were generated.

## `trip_hour`

Definition:

Hour of Trip start time in Korea Standard Time.

Range:

`0–23`

Purpose:

Capture differences in vehicle operation associated with time of day.

---

## `day_of_week`

Definition:

Day of week based on the Trip start timestamp in KST.

Encoding:

- Monday = 0
- Tuesday = 1
- Wednesday = 2
- Thursday = 3
- Friday = 4
- Saturday = 5
- Sunday = 6

Range:

`0–6`

Purpose:

Capture possible differences in operating patterns across weekdays.

---

## `is_weekend`

Definition:

Binary indicator derived from `day_of_week`.

Rule:

`Saturday or Sunday → 1`

`Monday through Friday → 0`

Observed distribution:

- Weekday Trips: 9,594
- Weekend Trips: 329

The dataset is therefore strongly concentrated on weekday operations.

---

# 7. Time-of-Day Distribution

Trip activity is concentrated primarily during daytime operating hours.

The largest Trip counts occurred around:

- 11:00 KST: 1,225 Trips
- 13:00 KST: 1,066 Trips
- 14:00 KST: 1,306 Trips
- 15:00 KST: 1,472 Trips
- 16:00 KST: 1,129 Trips

This indicates a clear operational time-of-day structure in the fleet data.

The predictive usefulness of `trip_hour` will be evaluated during EDA rather than assumed in advance.

---

# 8. Dataset Integrity After Feature Engineering

Final validation:

- Rows: 9,923
- Unique Trip IDs: 9,923
- Duplicate Trip IDs: 0
- Invalid Trip start timestamps: 0
- Missing `trip_hour`: 0
- Missing `day_of_week`: 0
- Missing `is_weekend`: 0

No observations were lost during context feature engineering.

---

# 9. Feature Status

## Existing Core Features

Retained from Week 2:

- `trip_distance_km`
- `trip_duration_min`
- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`
- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`
- `idle_ratio`

## New Candidate Features

Added during Day 14:

- `trip_hour`
- `day_of_week`
- `is_weekend`

These features are retained in the feature dataset but are not automatically approved for the final baseline model.

Their final inclusion will be determined after EDA.

## Excluded / Optional Feature

- Outside air temperature

Reason:

Insufficiently validated signal availability and consistency.

---

# 10. Output Dataset

Created:

`data/processed/trip_ml_features.csv`

The dataset contains the clean Week 2 modeling population plus the newly generated contextual features.
