from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("data/processed/trip_ml_features.csv")
OUTPUT_DIR = Path("reports/figures/day15")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Load
# ============================================================

print("Loading feature dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows: {len(df):,}")
print(f"Vehicles: {df['vehicle_id'].nunique()}")


# ============================================================
# Helper
# ============================================================

def describe_feature(column):

    s = df[column].dropna()

    print(f"\n--- {column} ---")
    print(f"Count: {len(s):,}")
    print(f"Mean: {s.mean():.4f}")
    print(f"Median: {s.median():.4f}")
    print(f"Std: {s.std():.4f}")
    print(f"Min: {s.min():.4f}")
    print(f"P01: {s.quantile(0.01):.4f}")
    print(f"P05: {s.quantile(0.05):.4f}")
    print(f"P95: {s.quantile(0.95):.4f}")
    print(f"P99: {s.quantile(0.99):.4f}")
    print(f"Max: {s.max():.4f}")
    print(f"Skewness: {s.skew():.4f}")


# ============================================================
# 1. Distribution Summary
# ============================================================

print("\n========================================")
print("Target & Trip Distribution")
print("========================================")

for column in [
    "trip_fuel_used_liter",
    "trip_distance_km",
    "trip_duration_min",
]:
    describe_feature(column)


# ============================================================
# 2. Correlations
# ============================================================

print("\n========================================")
print("Basic Relationships")
print("========================================")

print(
    "Fuel vs Distance correlation:",
    round(
        df["trip_fuel_used_liter"].corr(
            df["trip_distance_km"]
        ),
        4,
    ),
)

print(
    "Fuel vs Duration correlation:",
    round(
        df["trip_fuel_used_liter"].corr(
            df["trip_duration_min"]
        ),
        4,
    ),
)

print(
    "Distance vs Duration correlation:",
    round(
        df["trip_distance_km"].corr(
            df["trip_duration_min"]
        ),
        4,
    ),
)


# ============================================================
# 3. Trip Length Groups
# ============================================================

bins = [
    0.1,
    0.5,
    1,
    5,
    20,
    50,
    np.inf,
]

labels = [
    "0.1-0.5 km",
    "0.5-1 km",
    "1-5 km",
    "5-20 km",
    "20-50 km",
    "50+ km",
]

df["distance_group"] = pd.cut(
    df["trip_distance_km"],
    bins=bins,
    labels=labels,
    right=False,
)

trip_group_summary = (
    df.groupby(
        "distance_group",
        observed=True,
    )
    .agg(
        trips=("trip_id", "count"),
        median_distance_km=("trip_distance_km", "median"),
        median_duration_min=("trip_duration_min", "median"),
        mean_fuel_liter=("trip_fuel_used_liter", "mean"),
        median_fuel_liter=("trip_fuel_used_liter", "median"),
    )
)

print("\n========================================")
print("Trip Length Comparison")
print("========================================")

print(trip_group_summary)


# ============================================================
# 4. Fuel Distribution
# ============================================================

plt.figure(figsize=(8, 5))

plt.hist(
    df["trip_fuel_used_liter"],
    bins=60,
)

plt.xlabel("Trip Fuel Used (L)")
plt.ylabel("Trip Count")
plt.title("Trip Fuel Consumption Distribution")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "fuel_distribution.png",
    dpi=150,
)

plt.close()


# ============================================================
# 5. Distance Distribution
# ============================================================

plt.figure(figsize=(8, 5))

plt.hist(
    df["trip_distance_km"],
    bins=60,
)

plt.xlabel("Trip Distance (km)")
plt.ylabel("Trip Count")
plt.title("Trip Distance Distribution")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "distance_distribution.png",
    dpi=150,
)

plt.close()


# ============================================================
# 6. Duration Distribution
# ============================================================

plt.figure(figsize=(8, 5))

plt.hist(
    df["trip_duration_min"],
    bins=60,
)

plt.xlabel("Trip Duration (min)")
plt.ylabel("Trip Count")
plt.title("Trip Duration Distribution")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "duration_distribution.png",
    dpi=150,
)

plt.close()


# ============================================================
# 7. Fuel vs Distance
# ============================================================

plt.figure(figsize=(8, 5))

plt.scatter(
    df["trip_distance_km"],
    df["trip_fuel_used_liter"],
    alpha=0.25,
    s=10,
)

plt.xlabel("Trip Distance (km)")
plt.ylabel("Trip Fuel Used (L)")
plt.title("Fuel Consumption vs Trip Distance")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "fuel_vs_distance.png",
    dpi=150,
)

plt.close()


# ============================================================
# 8. Fuel vs Duration
# ============================================================

plt.figure(figsize=(8, 5))

plt.scatter(
    df["trip_duration_min"],
    df["trip_fuel_used_liter"],
    alpha=0.25,
    s=10,
)

plt.xlabel("Trip Duration (min)")
plt.ylabel("Trip Fuel Used (L)")
plt.title("Fuel Consumption vs Trip Duration")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "fuel_vs_duration.png",
    dpi=150,
)

plt.close()


# ============================================================
# 9. Log Target Investigation
# ============================================================

df["log_fuel_target"] = np.log1p(
    df["trip_fuel_used_liter"]
)

raw_skew = df["trip_fuel_used_liter"].skew()
log_skew = df["log_fuel_target"].skew()

print("\n========================================")
print("Target Transformation Investigation")
print("========================================")

print(f"Raw target skewness: {raw_skew:.4f}")
print(f"log1p target skewness: {log_skew:.4f}")


plt.figure(figsize=(8, 5))

plt.hist(
    df["log_fuel_target"],
    bins=60,
)

plt.xlabel("log1p(Trip Fuel Used)")
plt.ylabel("Trip Count")
plt.title("Log-Transformed Fuel Target Distribution")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "log_fuel_distribution.png",
    dpi=150,
)

plt.close()


# ============================================================
# 10. Save Summary
# ============================================================

trip_group_summary.to_csv(
    OUTPUT_DIR / "trip_length_summary.csv"
)


print("\n========================================")
print("Day 15 EDA Completed")
print("========================================")

print(f"Figures created in: {OUTPUT_DIR}")