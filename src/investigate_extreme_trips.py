from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/processed/trip_ml_master.csv")

df = pd.read_csv(INPUT_FILE)

# Baseline population
df = df[
    df["fuel_match_confidence"] == "High"
].copy()

core = [
    "trip_distance_km",
    "trip_duration_min",
    "trip_fuel_used_liter",
    "avg_speed_kmh",
    "max_speed_kmh",
    "avg_rpm",
    "max_rpm",
    "idle_ratio",
]

df = df.dropna(subset=core)

# Exclude clearly invalid / unstable micro-trips
df = df[
    df["trip_distance_km"] >= 0.1
].copy()


# Diagnostic metrics
df["fuel_per_100km"] = (
    df["trip_fuel_used_liter"]
    / df["trip_distance_km"]
    * 100
)


columns = [
    "vehicle_id",
    "trip_id",
    "period",
    "trip_distance_km",
    "trip_duration_min",
    "trip_fuel_used_liter",
    "fuel_per_100km",
    "avg_speed_kmh",
    "max_speed_kmh",
    "avg_rpm",
    "max_rpm",
    "idle_ratio",
]


def show_cases(title, mask):
    cases = df.loc[mask, columns].copy()

    print("\n========================================")
    print(title)
    print("========================================")
    print("Count:", len(cases))

    if len(cases) > 0:
        print(
            cases
            .sort_values(
                "trip_fuel_used_liter",
                ascending=False,
            )
            .to_string(index=False)
        )


show_cases(
    "Fuel > 50 L",
    df["trip_fuel_used_liter"] > 50,
)

show_cases(
    "Distance > 100 km",
    df["trip_distance_km"] > 100,
)

show_cases(
    "Duration > 120 min",
    df["trip_duration_min"] > 120,
)

show_cases(
    "Max RPM > 4000",
    df["max_rpm"] > 4000,
)

show_cases(
    "Average RPM = 0",
    df["avg_rpm"] == 0,
)

show_cases(
    "Idle Ratio = 1",
    df["idle_ratio"] == 1,
)


print("\n========================================")
print("Extreme Trip Investigation Completed")
print("========================================")