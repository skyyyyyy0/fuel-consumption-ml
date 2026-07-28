from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("data/processed/trip_ml_features.csv")

OUTPUT_DIR = Path(
    "reports/figures/engine_behavior_eda"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Load Dataset
# ============================================================

print("Loading ML feature dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows: {len(df):,}")
print(f"Vehicles: {df['vehicle_id'].nunique()}")


# ============================================================
# Features
# ============================================================

FEATURES = [
    "avg_rpm",
    "max_rpm",
    "avg_speed_kmh",
    "max_speed_kmh",
    "idle_ratio",
    "high_rpm_ratio",
]

TARGET = "trip_fuel_used_liter"


# ============================================================
# 1. Correlation with Fuel
# ============================================================

print("\n========================================")
print("Fuel vs Driving Behavior Correlations")
print("========================================")

correlation_rows = []

for feature in FEATURES:

    corr = df[feature].corr(
        df[TARGET]
    )

    correlation_rows.append(
        {
            "feature": feature,
            "fuel_correlation": corr,
        }
    )

    print(
        f"{feature}: {corr:.4f}"
    )


correlation_df = pd.DataFrame(
    correlation_rows
).sort_values(
    "fuel_correlation",
    ascending=False,
)

correlation_df.to_csv(
    OUTPUT_DIR / "fuel_feature_correlations.csv",
    index=False,
)


# ============================================================
# 2. Scatter Plots
# ============================================================

plot_titles = {
    "avg_rpm": "Fuel vs Average RPM",
    "max_rpm": "Fuel vs Maximum RPM",
    "avg_speed_kmh": "Fuel vs Average Speed",
    "max_speed_kmh": "Fuel vs Maximum Speed",
    "idle_ratio": "Fuel vs Idle Ratio",
    "high_rpm_ratio": "Fuel vs High RPM Ratio",
}

x_labels = {
    "avg_rpm": "Average RPM",
    "max_rpm": "Maximum RPM",
    "avg_speed_kmh": "Average Speed (km/h)",
    "max_speed_kmh": "Maximum Speed (km/h)",
    "idle_ratio": "Idle Ratio",
    "high_rpm_ratio": "High RPM Ratio",
}


for feature in FEATURES:

    plt.figure(figsize=(8, 5))

    plt.scatter(
        df[feature],
        df[TARGET],
        alpha=0.20,
        s=10,
    )

    plt.xlabel(
        x_labels[feature]
    )

    plt.ylabel(
        "Trip Fuel Used (L)"
    )

    plt.title(
        plot_titles[feature]
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / f"fuel_vs_{feature}.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# 3. Vehicle-Level Summary
# ============================================================

vehicle_summary = (
    df.groupby("vehicle_id")
    .agg(
        trips=("trip_id", "count"),

        avg_fuel_liter=(
            TARGET,
            "mean",
        ),

        median_fuel_liter=(
            TARGET,
            "median",
        ),

        avg_distance_km=(
            "trip_distance_km",
            "mean",
        ),

        avg_duration_min=(
            "trip_duration_min",
            "mean",
        ),

        avg_speed_kmh=(
            "avg_speed_kmh",
            "mean",
        ),

        avg_rpm=(
            "avg_rpm",
            "mean",
        ),

        avg_idle_ratio=(
            "idle_ratio",
            "mean",
        ),

        avg_high_rpm_ratio=(
            "high_rpm_ratio",
            "mean",
        ),
    )
    .reset_index()
)


print("\n========================================")
print("Vehicle-Level Summary")
print("========================================")

print(
    vehicle_summary.to_string(
        index=False
    )
)


vehicle_summary.to_csv(
    OUTPUT_DIR / "vehicle_behavior_summary.csv",
    index=False,
)


# ============================================================
# 4. Fuel Distribution by Vehicle
# ============================================================

vehicle_order = sorted(
    df["vehicle_id"].unique()
)

fuel_by_vehicle = [
    df.loc[
        df["vehicle_id"] == vehicle,
        TARGET,
    ].values
    for vehicle in vehicle_order
]


plt.figure(figsize=(12, 6))

plt.boxplot(
    fuel_by_vehicle,
    tick_labels=vehicle_order,
    showfliers=False,
)

plt.xlabel("Vehicle")
plt.ylabel("Trip Fuel Used (L)")
plt.title("Fuel Consumption by Vehicle")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "fuel_distribution_by_vehicle.png",
    dpi=150,
)

plt.close()


# ============================================================
# 5. Distance by Vehicle
# ============================================================

distance_by_vehicle = [
    df.loc[
        df["vehicle_id"] == vehicle,
        "trip_distance_km",
    ].values
    for vehicle in vehicle_order
]


plt.figure(figsize=(12, 6))

plt.boxplot(
    distance_by_vehicle,
    tick_labels=vehicle_order,
    showfliers=False,
)

plt.xlabel("Vehicle")
plt.ylabel("Trip Distance (km)")
plt.title("Trip Distance by Vehicle")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "distance_distribution_by_vehicle.png",
    dpi=150,
)

plt.close()


# ============================================================
# 6. Fuel vs Distance by Vehicle
# ============================================================

plt.figure(figsize=(10, 7))

for vehicle in vehicle_order:

    vehicle_df = df[
        df["vehicle_id"] == vehicle
    ]

    plt.scatter(
        vehicle_df["trip_distance_km"],
        vehicle_df[TARGET],
        alpha=0.25,
        s=10,
        label=vehicle,
    )


plt.xlabel("Trip Distance (km)")
plt.ylabel("Trip Fuel Used (L)")

plt.title(
    "Fuel vs Distance by Vehicle"
)

plt.legend(
    fontsize=7,
    ncol=2,
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "fuel_vs_distance_by_vehicle.png",
    dpi=150,
)

plt.close()


# ============================================================
# 7. Vehicle-Level Correlations
# ============================================================

vehicle_corr_rows = []

for vehicle in vehicle_order:

    vehicle_df = df[
        df["vehicle_id"] == vehicle
    ]

    row = {
        "vehicle_id": vehicle,
        "trips": len(vehicle_df),
    }

    for feature in FEATURES:

        row[
            f"{feature}_fuel_corr"
        ] = (
            vehicle_df[feature]
            .corr(
                vehicle_df[TARGET]
            )
        )

    row[
        "distance_fuel_corr"
    ] = (
        vehicle_df[
            "trip_distance_km"
        ]
        .corr(
            vehicle_df[TARGET]
        )
    )

    vehicle_corr_rows.append(
        row
    )


vehicle_corr_df = pd.DataFrame(
    vehicle_corr_rows
)


print("\n========================================")
print("Vehicle-Level Fuel Correlations")
print("========================================")

print(
    vehicle_corr_df.to_string(
        index=False
    )
)


vehicle_corr_df.to_csv(
    OUTPUT_DIR
    / "vehicle_fuel_correlations.csv",
    index=False,
)


# ============================================================
# 8. Period-Level Summary
# ============================================================

period_summary = (
    df.groupby("period")
    .agg(
        trips=("trip_id", "count"),

        avg_fuel_liter=(
            TARGET,
            "mean",
        ),

        median_fuel_liter=(
            TARGET,
            "median",
        ),

        avg_distance_km=(
            "trip_distance_km",
            "mean",
        ),

        avg_speed_kmh=(
            "avg_speed_kmh",
            "mean",
        ),

        avg_rpm=(
            "avg_rpm",
            "mean",
        ),

        avg_idle_ratio=(
            "idle_ratio",
            "mean",
        ),
    )
)


print("\n========================================")
print("Period-Level Summary")
print("========================================")

print(period_summary)


period_summary.to_csv(
    OUTPUT_DIR
    / "period_behavior_summary.csv"
)


# ============================================================
# Complete
# ============================================================

print("\n========================================")
print("Engine & Driving Behavior EDA Completed")
print("========================================")

print(
    f"Outputs created in: {OUTPUT_DIR}"
)