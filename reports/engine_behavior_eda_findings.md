# Engine & Driving Behavior EDA Findings

## 1. Objective

This analysis examined how engine and driving-behavior features relate to trip-level fuel consumption.

The primary variables investigated were:

- Average RPM
- Maximum RPM
- Average speed
- Maximum speed
- Idle ratio
- High-RPM ratio

The analysis also evaluated whether apparent fleet-level relationships remained after controlling for trip distance and vehicle-specific differences.

---

# 2. Dataset

The analysis used the cleaned ML feature dataset:

`data/processed/trip_ml_features.csv`

Dataset characteristics:

- Trips: 9,923
- Vehicles: 12
- Vehicle-period combinations: 36
- Missing core features: 0

Target:

`trip_fuel_used_liter`

---

# 3. Fleet-Level Relationships

The raw correlations with trip fuel consumption were:

| Feature        | Fuel Correlation |
| -------------- | ---------------: |
| Average RPM    |           -0.154 |
| Maximum RPM    |           -0.222 |
| Average Speed  |            0.708 |
| Maximum Speed  |            0.538 |
| Idle Ratio     |           -0.262 |
| High-RPM Ratio |           -0.042 |

Average and maximum speed showed relatively strong positive relationships with total trip fuel consumption.

RPM and idle ratio showed negative fleet-level correlations.

However, these raw correlations should not be interpreted as direct behavioral effects because trip length and vehicle characteristics vary substantially across the fleet.

---

# 4. Vehicle-Level Differences

Substantial differences were observed across vehicles.

Several vehicles, particularly `VEH_05`, `VEH_06`, `VEH_11`, and `VEH_12`, had substantially longer average trips and higher trip-level fuel consumption than the rest of the fleet.

For example:

| Vehicle | Avg Fuel (L) | Avg Distance (km) | Avg RPM |
| ------- | -----------: | ----------------: | ------: |
| VEH_05  |       11.663 |            38.650 |  1000.5 |
| VEH_06  |        9.572 |            34.682 |  1040.4 |
| VEH_11  |       13.725 |            55.305 |  1058.2 |
| VEH_12  |        8.078 |            31.076 |  1003.5 |

These vehicles consumed substantially more fuel while operating at lower average RPM than many shorter-trip vehicles.

This explains why fleet-level RPM correlations can be misleading.

---

# 5. Fuel vs. Distance Within Vehicles

Trip distance was strongly correlated with fuel consumption within every vehicle.

Vehicle-level distance-fuel correlations ranged approximately from:

`0.74 to 0.98`

Examples:

- VEH_01: 0.977
- VEH_03: 0.984
- VEH_08: 0.981
- VEH_10: 0.952
- VEH_11: 0.972
- VEH_12: 0.937

This confirms that trip distance is one of the dominant predictors of total trip fuel consumption.

---

# 6. Distance-Controlled Analysis

To determine whether driving-behavior variables contained information beyond trip distance, fuel consumption was residualized against trip distance.

Fleet-level distance-controlled correlations were:

| Feature        | Controlled Correlation |
| -------------- | ---------------------: |
| Average RPM    |                 -0.234 |
| Maximum RPM    |                 -0.276 |
| Average Speed  |                 -0.091 |
| Maximum Speed  |                 -0.177 |
| Idle Ratio     |                 -0.055 |
| High-RPM Ratio |                 -0.083 |

The strong raw speed relationships weakened substantially after accounting for distance.

This indicates that much of the original speed-fuel relationship was associated with differences in trip length.

---

# 7. Vehicle + Distance Controlled Analysis

A second analysis removed each vehicle's own fuel-versus-distance relationship before pooling the residuals.

Results:

| Feature        | Vehicle + Distance Controlled Correlation |
| -------------- | ----------------------------------------: |
| Average RPM    |                                     0.093 |
| Maximum RPM    |                                     0.043 |
| Average Speed  |                                     0.008 |
| Maximum Speed  |                                     0.030 |
| Idle Ratio     |                                    -0.009 |
| High-RPM Ratio |                                     0.015 |

After controlling for both vehicle identity and trip distance, all relationships became weak.

This indicates that much of the apparent fleet-level relationship between driving behavior and total fuel consumption is explained by:

1. Trip distance
2. Vehicle-specific characteristics

rather than driving behavior alone.

---

# 8. Within-Vehicle Driving Behavior

Although pooled controlled correlations were weak, some vehicle-level relationships remained.

For example:

- VEH_07 Average RPM: 0.269
- VEH_10 Maximum RPM: 0.256
- VEH_11 Maximum RPM: 0.310
- VEH_08 Maximum RPM: 0.289

This suggests that RPM-related features may still provide incremental predictive information within individual vehicle operating patterns.

Therefore, these features should not be removed solely based on fleet-level correlation.

---

# 9. High-RPM Ratio

High-RPM activity was rare across the fleet.

Several vehicles had no meaningful observations above the selected high-RPM threshold, resulting in undefined vehicle-level correlations.

This is expected when a feature has zero or near-zero variance within a vehicle.

High-RPM ratio will remain a candidate feature but should be evaluated for incremental predictive value during modeling.

---

# 10. Feature Decision

## Primary Trip Features

The strongest physically interpretable predictors remain:

- `trip_distance_km`
- `trip_duration_min`

## Candidate Driving Features

The following features will remain in the candidate feature set:

- `avg_speed_kmh`
- `max_speed_kmh`
- `speed_std`
- `avg_rpm`
- `max_rpm`
- `rpm_std`
- `high_rpm_ratio`
- `idle_ratio`

These variables will be evaluated through model comparison rather than removed based only on pairwise correlations.

---

# 11. Modeling Implication

A useful modeling comparison will be:

### Baseline Model

Trip-level information only:

- Distance
- Duration

### Extended Model

Trip-level information plus:

- Speed features
- RPM features
- Idle behavior
- Context features

This comparison will determine whether engine and driving-behavior variables improve prediction beyond basic trip characteristics.

---

# 12. Key Finding

Raw fleet-level correlations can be misleading when vehicles have substantially different operating patterns.

The analysis showed that:

> Trip distance and vehicle-specific characteristics explain a large portion of the apparent relationship between driving behavior and total fuel consumption.

After controlling for both factors, most driving-behavior correlations became weak.

However, some within-vehicle RPM relationships remained, supporting the decision to retain these variables as candidate ML features.

---

## Final Decision

**Engine & Driving Behavior EDA Complete**

Proceed to correlation analysis and final feature evaluation.
