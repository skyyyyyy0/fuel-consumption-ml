from pathlib import Path
import pandas as pd


INPUT_FILE = Path(
    "data/processed/trip_ml_master.csv"
)

df = pd.read_csv(INPUT_FILE)

# Baseline candidate population
df = df[
    df["fuel_match_confidence"] == "High"
].copy()

core = [
    "trip_distance_km",
    "trip_duration_min",
    "trip_fuel_used_liter",
    "avg_speed_kmh",
    "avg_rpm",
    "idle_ratio",
]

df = df.dropna(subset=core)


# --------------------------------------------------
# Distance groups
# --------------------------------------------------

df["distance_group"] = pd.cut(
    df["trip_distance_km"],
    bins=[
        -0.001,
        0,
        0.1,
        0.5,
        1,
        5,
        20,
        50,
        float("inf"),
    ],
    labels=[
        "0 km",
        "0-0.1 km",
        "0.1-0.5 km",
        "0.5-1 km",
        "1-5 km",
        "5-20 km",
        "20-50 km",
        "50+ km",
    ],
)


# --------------------------------------------------
# Fuel intensity
# Only for diagnostic purposes
# --------------------------------------------------

df["liter_per_km"] = (
    df["trip_fuel_used_liter"]
    / df["trip_distance_km"]
)

df["liter_per_100km"] = (
    df["liter_per_km"] * 100
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

summary = (
    df.groupby(
        "distance_group",
        observed=True,
    )
    .agg(
        trips=("trip_id", "size"),
        median_distance_km=(
            "trip_distance_km",
            "median",
        ),
        median_duration_min=(
            "trip_duration_min",
            "median",
        ),
        median_fuel_liter=(
            "trip_fuel_used_liter",
            "median",
        ),
        median_l_per_100km=(
            "liter_per_100km",
            "median",
        ),
        p95_l_per_100km=(
            "liter_per_100km",
            lambda x: x.quantile(0.95),
        ),
    )
)


print("\n========================================")
print("Short Trip Investigation")
print("========================================")

print(summary.to_string())


# --------------------------------------------------
# Very short trip details
# --------------------------------------------------

short = df[
    (df["trip_distance_km"] > 0)
    & (df["trip_distance_km"] < 0.1)
].copy()

print("\n========================================")
print("Trips < 0.1 km")
print("========================================")

print("Trips:", len(short))

print(
    "Median distance:",
    short["trip_distance_km"].median(),
)

print(
    "Median duration:",
    short["trip_duration_min"].median(),
)

print(
    "Median fuel:",
    short["trip_fuel_used_liter"].median(),
)

print(
    "Median L/100km:",
    short["liter_per_100km"].median(),
)

print(
    "P95 L/100km:",
    short["liter_per_100km"].quantile(0.95),
)


print("\nVery short trips by vehicle:")

print(
    short.groupby("vehicle_id")
    .size()
    .sort_values(ascending=False)
    .to_string()
)