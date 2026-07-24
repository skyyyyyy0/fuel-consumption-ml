# Trip Definition & Target Design

## Objective

Define the final unit of observation for the fuel-consumption machine-learning dataset and establish a reliable target-generation rule.

---

## 1. Primary ML Observation

The primary modeling unit is:

**1 Row = 1 GeoTab-defined Trip**

GeoTab Trip data is used as the source of truth for trip segmentation.

Alternative segmentation methods based on ignition transitions or time gaps were considered but were not selected because GeoTab already provides explicit trip start, trip stop, distance, and duration information.

---

## 2. Final Trip Definition

Each trip is defined using GeoTab Trip information.

Required fields:

- `trip_id`
- `vehicle_id`
- `period`
- `trip_start`
- `trip_stop`
- `trip_duration_min`
- `trip_distance_km`

### Trip Start

`trip_start_utc`

### Trip End

`trip_stop_utc`

### Trip Duration

Calculated as:

`trip_stop - trip_start`

and stored in minutes.

### Trip Distance

Primary distance source:

`distance_km`

from GeoTab Trip data.

GPS Trip Distance is available for all 12 vehicles across the 2026 Before, After, and Final periods.

---

## 3. Trip Segmentation Decision

### Option A — Ignition ON → OFF

Not selected as the primary segmentation method.

Ignition data is available across the fleet, but it is event-driven and would require reconstruction of trip boundaries.

### Option B — GeoTab Trip Information

**Selected**

Advantages:

- Native trip start and stop timestamps
- Trip-level distance
- Driving duration
- Idling duration
- Maximum speed
- Complete 2026 fleet coverage

### Option C — Time-Gap Segmentation

Not required for the primary dataset.

This method may be retained as a fallback if GeoTab Trip information is unavailable in future datasets.

---

# 4. Target Definition

The machine-learning target is:

**Y = trip_fuel_used_liter**

The source signal is:

`Trip fuel used`

Unit:

Liters

---

## 5. Target Timestamp Behavior

Trip Fuel Used events were compared against GeoTab Trip start and stop timestamps.

Fleet-wide validation included:

- 12 vehicles
- Before / After / Final periods
- 36 vehicle-period combinations

Observed alignment:

- Total Trip Fuel records: 13,947
- Total GPS Trips: 15,827
- Median trip-stop timestamp difference: approximately 10.68 seconds
- Match within 30 seconds: approximately 85.8%
- Match within 60 seconds: approximately 91.1%

Trip Fuel Used timestamps align substantially more closely with trip-stop timestamps than trip-start timestamps.

Therefore, target matching will be based on the GeoTab trip-stop timestamp.

---

# 6. Target Matching Rule

Trip Fuel Used events are assigned to GeoTab trips using the following logic.

## Step 1 — Candidate Matching

For each GeoTab trip, identify the nearest Trip Fuel Used event to the trip-stop timestamp.

Maximum candidate tolerance:

`60 seconds`

---

## Step 2 — One-to-One Constraint

Each Trip Fuel Used event may be assigned to a maximum of one GeoTab trip.

A single fuel event cannot be reused across multiple ML observations.

---

## Step 3 — Competing Trip Resolution

When multiple trips compete for the same fuel event:

1. Prefer a valid trip over an invalid zero-distance trip.
2. Among valid trips, prefer the smallest absolute timestamp difference.

This rule prevents short or zero-distance GeoTab micro-trips from incorrectly capturing fuel events belonging to adjacent trips.

---

## Step 4 — Match Confidence

### High Confidence

`absolute timestamp difference <= 30 seconds`

These observations are eligible for the baseline ML dataset.

### Review

`30 < absolute timestamp difference <= 60 seconds`

These observations are retained for analysis but excluded from the initial baseline model.

### Unmatched

`absolute timestamp difference > 60 seconds`

or

no fuel event available within the matching tolerance.

These trips are excluded from the initial supervised training dataset.

---

# 7. Trip Validity

## Invalid Trips

Trips with:

`trip_distance_km <= 0`

are classified as invalid for the baseline ML dataset.

---

## Very Short Trips

Trips with:

`0 < trip_distance_km < 0.1`

are classified as suspicious.

These trips will not be automatically removed during Day 5 because a substantial number of micro-trips exist in the GeoTab data.

A final minimum-distance threshold will be evaluated during the cleaning phase.

---

# 8. Fleet-Wide Matching Results

The proposed target-generation logic was tested across all 12 vehicles and all three 2026 periods.

Results:

- Total GPS Trips: 15,827
- Total Trip Fuel records: 13,947
- High-confidence matches: 12,231
- Review matches: 631
- Rejected duplicate assignments: 253
- Unmatched trips: 2,712
- Zero-distance trips: 142
- Very-short trips: 3,470
- High-confidence valid trips: 12,211

Overall high-confidence usable rate:

**77.2%**

This provides a sufficiently large dataset for initial model development.

---

# 9. Final ML Observation Structure

The initial trip-level dataset will use the following structure:

| Column               | Description                       |
| -------------------- | --------------------------------- |
| trip_id              | Unique anonymized trip identifier |
| vehicle_id           | Anonymized vehicle identifier     |
| period               | Before / After / Final            |
| trip_start           | GeoTab trip start timestamp       |
| trip_stop            | GeoTab trip stop timestamp        |
| trip_duration_min    | Trip duration                     |
| trip_distance_km     | GPS-based trip distance           |
| trip_fuel_used_liter | Fuel consumed during the trip     |

Additional RPM, speed, idling, and driving features will be aggregated within each trip window during feature engineering.

---

# 10. Final Decision

## Trip

**One observation represents one GeoTab-defined vehicle trip.**

## Target Y

**Liters of fuel consumed during the trip.**

The target is generated by one-to-one alignment of `Trip fuel used` telemetry with the corresponding GeoTab trip-stop timestamp.

Only high-confidence matches will be used in the initial baseline ML model.

Review and suspicious observations will remain available for later sensitivity analysis.
