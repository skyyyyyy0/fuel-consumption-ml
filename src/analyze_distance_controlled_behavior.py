from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("data/processed/trip_ml_features.csv")
OUTPUT_DIR = Path("reports/figures/engine_behavior_eda")

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TARGET = "trip_fuel_used_liter"
DISTANCE = "trip_distance_km"

FEATURES = [
    "avg_rpm",
    "max_rpm",
    "avg_speed_kmh",
    "max_speed_kmh",
    "idle_ratio",
    "high_rpm_ratio",
]


# ============================================================
# Load
# ============================================================

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows: {len(df):,}")
print(f"Vehicles: {df['vehicle_id'].nunique()}")


# ============================================================
# Helper: Residualize Y against X
# ============================================================

def residualize(y, x):
    """
    Fit simple linear relationship:
        y = a + b*x

    Return:
        y residual = actual y - predicted y
    """

    valid = (
        y.notna()
        & x.notna()
    )

    result = pd.Series(
        np.nan,
        index=y.index,
        dtype=float,
    )

    if valid.sum() < 2:
        return result

    x_valid = x.loc[valid].astype(float)
    y_valid = y.loc[valid].astype(float)

    slope, intercept = np.polyfit(
        x_valid,
        y_valid,
        deg=1,
    )

    predicted = (
        intercept
        + slope * x_valid
    )

    result.loc[valid] = (
        y_valid - predicted
    )

    return result


# ============================================================
# 1. Fleet-Level Distance-Controlled Fuel Residual
# ============================================================

df["fuel_residual_after_distance"] = residualize(
    df[TARGET],
    df[DISTANCE],
)


print("\n========================================")
print("Fleet-Level Distance-Controlled Analysis")
print("========================================")

fleet_rows = []

for feature in FEATURES:

    valid = df[
        [
            feature,
            "fuel_residual_after_distance",
        ]
    ].dropna()

    if (
        len(valid) < 2
        or valid[feature].std() == 0
    ):
        corr = np.nan

    else:
        corr = valid[feature].corr(
            valid["fuel_residual_after_distance"]
        )

    fleet_rows.append({
        "feature": feature,
        "distance_controlled_fuel_corr": corr,
    })

    print(
        f"{feature}: "
        f"{corr:.4f}"
        if pd.notna(corr)
        else f"{feature}: NaN"
    )


fleet_result = pd.DataFrame(
    fleet_rows
)

fleet_result.to_csv(
    OUTPUT_DIR
    / "distance_controlled_fleet_correlations.csv",
    index=False,
)


# ============================================================
# 2. Vehicle-Specific Residualization
# ============================================================

vehicle_results = []

vehicle_frames = []

for vehicle_id, vehicle_df in df.groupby("vehicle_id"):

    vehicle_df = vehicle_df.copy()

    vehicle_df[
        "vehicle_fuel_residual_after_distance"
    ] = residualize(
        vehicle_df[TARGET],
        vehicle_df[DISTANCE],
    )

    vehicle_frames.append(vehicle_df)

    row = {
        "vehicle_id": vehicle_id,
        "trips": len(vehicle_df),
        "distance_fuel_corr":
            vehicle_df[DISTANCE]
            .corr(vehicle_df[TARGET]),
    }

    for feature in FEATURES:

        valid = vehicle_df[
            [
                feature,
                "vehicle_fuel_residual_after_distance",
            ]
        ].dropna()

        if (
            len(valid) < 2
            or valid[feature].std() == 0
        ):
            corr = np.nan

        else:
            corr = valid[feature].corr(
                valid[
                    "vehicle_fuel_residual_after_distance"
                ]
            )

        row[
            f"{feature}_controlled_corr"
        ] = corr

    vehicle_results.append(row)


vehicle_result = pd.DataFrame(
    vehicle_results
)

print("\n========================================")
print("Vehicle-Level Distance-Controlled Analysis")
print("========================================")

print(
    vehicle_result.to_string(
        index=False
    )
)

vehicle_result.to_csv(
    OUTPUT_DIR
    / "distance_controlled_vehicle_correlations.csv",
    index=False,
)


# ============================================================
# 3. Vehicle-Controlled Fleet Residual
#
# Remove each vehicle's own fuel-vs-distance relationship.
# Then pool the residuals together.
# ============================================================

vehicle_residual_df = pd.concat(
    vehicle_frames,
    ignore_index=True,
)


print("\n========================================")
print("Vehicle + Distance Controlled Fleet Analysis")
print("========================================")

controlled_rows = []

for feature in FEATURES:

    valid = vehicle_residual_df[
        [
            feature,
            "vehicle_fuel_residual_after_distance",
        ]
    ].dropna()

    if (
        len(valid) < 2
        or valid[feature].std() == 0
    ):
        corr = np.nan

    else:
        corr = valid[feature].corr(
            valid[
                "vehicle_fuel_residual_after_distance"
            ]
        )

    controlled_rows.append({
        "feature": feature,
        "vehicle_distance_controlled_corr": corr,
    })

    print(
        f"{feature}: "
        f"{corr:.4f}"
        if pd.notna(corr)
        else f"{feature}: NaN"
    )


controlled_result = pd.DataFrame(
    controlled_rows
)

controlled_result.to_csv(
    OUTPUT_DIR
    / "vehicle_distance_controlled_correlations.csv",
    index=False,
)


# ============================================================
# 4. Compare Raw vs Controlled
# ============================================================

comparison_rows = []

for feature in FEATURES:

    raw_corr = df[feature].corr(
        df[TARGET]
    )

    distance_corr = (
        fleet_result.loc[
            fleet_result["feature"] == feature,
            "distance_controlled_fuel_corr",
        ]
        .iloc[0]
    )

    vehicle_distance_corr = (
        controlled_result.loc[
            controlled_result["feature"] == feature,
            "vehicle_distance_controlled_corr",
        ]
        .iloc[0]
    )

    comparison_rows.append({
        "feature": feature,
        "raw_fuel_corr": raw_corr,
        "distance_controlled_corr": distance_corr,
        "vehicle_distance_controlled_corr":
            vehicle_distance_corr,
    })


comparison = pd.DataFrame(
    comparison_rows
)

print("\n========================================")
print("Raw vs Controlled Correlation Comparison")
print("========================================")

print(
    comparison.to_string(
        index=False
    )
)

comparison.to_csv(
    OUTPUT_DIR
    / "raw_vs_controlled_correlations.csv",
    index=False,
)


# ============================================================
# Complete
# ============================================================

print("\n========================================")
print("Distance-Controlled Analysis Completed")
print("========================================")

print(
    f"Outputs created in: {OUTPUT_DIR}"
)