# Initial ML Dataset Schema

## 1. Objective

This document defines the initial trip-level dataset structure for the fuel-consumption prediction model.

The dataset design is based on the Week 1 data inventory, signal coverage analysis, data-quality audit, and trip-target validation.

The modeling unit is:

**1 Row = 1 GeoTab-defined Trip**

The prediction target is:

**Y = trip_fuel_used_liter**

---

# 2. Dataset Structure

## Metadata

These columns identify and describe each observation but are not automatically used as model features.

| Column          | Description                       | Model Feature        |
| --------------- | --------------------------------- | -------------------- |
| vehicle_id      | Anonymized vehicle identifier     | No / grouping        |
| trip_id         | Unique anonymized trip identifier | No                   |
| period          | Before / After / Final            | Analysis / splitting |
| trip_start_time | Trip start timestamp              | No                   |
| trip_end_time   | Trip end timestamp                | No                   |

---

# 3. Core ML Features

These features have sufficient coverage and are planned for the initial baseline dataset.

## Trip Features

| Feature           | Description             | Source      |
| ----------------- | ----------------------- | ----------- |
| trip_distance_km  | GPS-based trip distance | GeoTab Trip |
| trip_duration_min | Trip duration           | GeoTab Trip |

## Speed Features

| Feature       | Description                          | Source            |
| ------------- | ------------------------------------ | ----------------- |
| avg_speed_kmh | Mean valid road speed during trip    | Engine road speed |
| max_speed_kmh | Maximum valid road speed during trip | Engine road speed |
| speed_std     | Standard deviation of road speed     | Engine road speed |

Only records with the actual speed unit:

`UnitOfMeasureKilometersPerHourId`

will be treated as road-speed observations.

Records reported with:

`UnitOfMeasureMetersId`

will not be interpreted as vehicle speed.

## RPM Features

| Feature        | Description                                                          | Source       |
| -------------- | -------------------------------------------------------------------- | ------------ |
| avg_rpm        | Mean engine RPM during trip                                          | Engine speed |
| max_rpm        | Maximum engine RPM during trip                                       | Engine speed |
| rpm_std        | Standard deviation of RPM                                            | Engine speed |
| high_rpm_ratio | Proportion of RPM observations above the selected high-RPM threshold | Engine speed |

The final high-RPM threshold will be defined during feature engineering.

## Vehicle-State Features

| Feature    | Description                               | Source                       |
| ---------- | ----------------------------------------- | ---------------------------- |
| idle_ratio | Estimated proportion of trip spent idling | Vehicle active / speed / RPM |

The exact idle calculation will be finalized during Week 2.

---

# 4. Optional Features

These variables may be evaluated after the baseline model.

## Outside Temperature

Coverage:

**5 / 12 vehicles**

Decision:

**Optional**

Reason:

Fleet coverage is insufficient for the primary baseline model.

Observed values above 60°C were also found for several vehicles and require additional validation before use.

---

## Gear Position

Coverage:

**11 / 12 vehicles**

Decision:

**Optional**

Reason:

Coverage is relatively high, but encoding and cross-vehicle consistency must be validated before feature engineering.

---

## Vehicle Type

Decision:

**Optional / Recommended for later testing**

Vehicle-level differences may explain substantial variation in fuel consumption.

Vehicle type may therefore be evaluated as a categorical feature after the baseline model is established.

---

# 5. Excluded Features

## Odometer

Coverage:

**6 / 12 vehicles**

Decision:

**Exclude from baseline ML features**

Reason:

Odometer coverage is inconsistent across the fleet.

GPS-based `trip_distance_km` will be used as the primary distance feature.

Manual odometer measurements may be retained for validation but will not be used as the primary model input.

---

## Coolant Temperature

Coverage:

**0 / 12 vehicles**

Decision:

**Excluded**

Reason:

Signal unavailable.

---

## Engine Load

Coverage:

**0 / 12 vehicles**

Decision:

**Excluded**

Reason:

Signal unavailable.

---

# 6. Leakage-Sensitive Features

The following signals will not be used as baseline model inputs.

## Trip Fuel Used

Decision:

**Target only**

`trip_fuel_used_liter` is the dependent variable Y.

---

## Total Fuel Used

Decision:

**Exclude**

Reason:

This is a cumulative fuel measurement directly related to the prediction target and could introduce target leakage.

---

## Trip Idle Fuel Used

Decision:

**Exclude from baseline X**

Reason:

Trip idle fuel is a direct component of total trip fuel consumption and would provide the model with information derived from the outcome being predicted.

---

## Total Fuel Used While Idling

Decision:

**Exclude**

Reason:

This is a cumulative fuel-consumption measurement and creates a significant leakage risk.

---

# 7. Initial Dataset Schema

The initial processed dataset will contain:

| Column               | Role         |
| -------------------- | ------------ |
| vehicle_id           | Metadata     |
| trip_id              | Metadata     |
| period               | Metadata     |
| trip_start_time      | Metadata     |
| trip_end_time        | Metadata     |
| trip_distance_km     | Core Feature |
| trip_duration_min    | Core Feature |
| avg_speed_kmh        | Core Feature |
| max_speed_kmh        | Core Feature |
| speed_std            | Core Feature |
| avg_rpm              | Core Feature |
| max_rpm              | Core Feature |
| rpm_std              | Core Feature |
| high_rpm_ratio       | Core Feature |
| idle_ratio           | Core Feature |
| outside_temperature  | Optional     |
| gear_position        | Optional     |
| vehicle_type         | Optional     |
| trip_fuel_used_liter | Target       |

---

# 8. Baseline Feature Set

The initial baseline model will start with:

X:

- trip_distance_km
- trip_duration_min
- avg_speed_kmh
- max_speed_kmh
- speed_std
- avg_rpm
- max_rpm
- rpm_std
- high_rpm_ratio
- idle_ratio

Y:

- trip_fuel_used_liter

Optional features will be evaluated separately after the baseline model is established.

---

# 9. Dataset Inclusion Rule

For the initial supervised ML dataset, a trip must satisfy:

1. GeoTab Trip information is available.
2. `trip_distance_km > 0`.
3. A Trip Fuel Used event is matched one-to-one with the trip.
4. Fuel-to-trip-stop timestamp difference is <= 30 seconds.
5. Fuel value is numeric and positive.
6. The observation passes the finalized Week 2 cleaning rules.

Trips between 0 and 0.1 km remain flagged as suspicious and will be evaluated before the final cleaning threshold is selected.

---

# 10. Initial Modeling Principle

The baseline model will intentionally use a relatively small and interpretable feature set.

Additional features will only be added when they:

- have sufficient coverage,
- have consistent physical meaning,
- improve validation performance,
- and do not introduce target leakage.

This provides a clear baseline before more complex feature engineering is introduced.
