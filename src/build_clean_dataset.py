from pathlib import Path
import pandas as pd


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("data/processed/trip_ml_master.csv")
OUTPUT_FILE = Path("data/processed/trip_ml_clean.csv")

MIN_DISTANCE_KM = 0.1

CONFIRMED_INVALID_TRIP_IDS = {
    "VEH_05_FINAL_0036",
}

CORE_FEATURES = [
    "trip_distance_km",
    "trip_duration_min",
    "avg_speed_kmh",
    "max_speed_kmh",
    "speed_std",
    "avg_rpm",
    "max_rpm",
    "rpm_std",
    "high_rpm_ratio",
    "idle_ratio",
    "trip_fuel_used_liter",
]


# ============================================================
# Load
# ============================================================

print("Loading master dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Initial rows: {len(df):,}")


# ============================================================
# Cleaning flags
# ============================================================

df["keep_high_confidence"] = (
    df["fuel_match_confidence"] == "High"
)

df["keep_positive_fuel"] = (
    df["trip_fuel_used_liter"].notna()
    & (df["trip_fuel_used_liter"] > 0)
)

df["keep_complete_core"] = (
    ~df[CORE_FEATURES].isna().any(axis=1)
)

df["keep_valid_distance"] = (
    df["trip_distance_km"] >= MIN_DISTANCE_KM
)

df["keep_valid_duration"] = (
    df["trip_duration_min"] > 0
)

df["keep_nonnegative_speed"] = (
    df["avg_speed_kmh"] >= 0
)

df["keep_nonnegative_rpm"] = (
    df["avg_rpm"] >= 0
)

df["keep_valid_idle_ratio"] = (
    df["idle_ratio"].between(0, 1)
)

df["keep_not_confirmed_anomaly"] = (
    ~df["trip_id"].isin(CONFIRMED_INVALID_TRIP_IDS)
)


# ============================================================
# Sequential audit
# ============================================================

print("\n========================================")
print("Sequential Cleaning Audit")
print("========================================")

mask = pd.Series(True, index=df.index)

rules = [
    ("High-confidence target", "keep_high_confidence"),
    ("Positive fuel", "keep_positive_fuel"),
    ("Complete core features", "keep_complete_core"),
    ("Distance >= 0.1 km", "keep_valid_distance"),
    ("Duration > 0", "keep_valid_duration"),
    ("Nonnegative speed", "keep_nonnegative_speed"),
    ("Nonnegative RPM", "keep_nonnegative_rpm"),
    ("Idle ratio in [0,1]", "keep_valid_idle_ratio"),
    ("Remove confirmed anomaly", "keep_not_confirmed_anomaly"),
]

for label, column in rules:
    before = int(mask.sum())

    mask &= df[column]

    after = int(mask.sum())
    removed = before - after

    print(
        f"{label}: "
        f"{before:,} -> {after:,} "
        f"(removed {removed:,})"
    )


# ============================================================
# Build clean dataset
# ============================================================

clean = df.loc[mask].copy()

print("\n========================================")
print("Final Clean Dataset")
print("========================================")

print(f"Rows: {len(clean):,}")
print(f"Vehicles: {clean['vehicle_id'].nunique()}")

vehicle_periods = (
    clean[
        ["vehicle_id", "period"]
    ]
    .drop_duplicates()
    .shape[0]
)

print(f"Vehicle-periods: {vehicle_periods}")
print(
    "Duplicate trip IDs:",
    int(clean["trip_id"].duplicated().sum())
)


# ============================================================
# Final physical checks
# ============================================================

print("\nPhysical validation:")

print(
    "Distance < 0.1 km:",
    int((clean["trip_distance_km"] < 0.1).sum())
)

print(
    "Duration <= 0:",
    int((clean["trip_duration_min"] <= 0).sum())
)

print(
    "Fuel <= 0:",
    int((clean["trip_fuel_used_liter"] <= 0).sum())
)

print(
    "Negative speed:",
    int((clean["avg_speed_kmh"] < 0).sum())
)

print(
    "Negative RPM:",
    int((clean["avg_rpm"] < 0).sum())
)

print(
    "Idle ratio outside 0-1:",
    int(
        (
            (clean["idle_ratio"] < 0)
            | (clean["idle_ratio"] > 1)
        ).sum()
    )
)

print(
    "Missing core features:",
    int(clean[CORE_FEATURES].isna().any(axis=1).sum())
)


# ============================================================
# Distribution
# ============================================================

print("\n========================================")
print("Clean Dataset Distribution")
print("========================================")

for col in [
    "trip_distance_km",
    "trip_duration_min",
    "trip_fuel_used_liter",
    "avg_speed_kmh",
    "max_speed_kmh",
    "avg_rpm",
    "max_rpm",
    "idle_ratio",
]:

    print(f"\n{col}")

    print(
        clean[col][
            clean[col].notna()
        ]
        .describe(
            percentiles=[
                0.01,
                0.05,
                0.50,
                0.95,
                0.99,
            ]
        )
        .to_string()
    )


# ============================================================
# Vehicle counts
# ============================================================

print("\nRows by vehicle:")

print(
    clean.groupby("vehicle_id")
    .size()
    .to_string()
)


# ============================================================
# Period counts
# ============================================================

print("\nRows by period:")

print(
    clean.groupby("period")
    .size()
    .to_string()
)


# ============================================================
# Remove temporary audit flags from final output
# ============================================================

flag_columns = [
    col for col in clean.columns
    if col.startswith("keep_")
]

clean = clean.drop(
    columns=flag_columns
)


# ============================================================
# Save
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

clean.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n========================================")
print("Clean Dataset Completed")
print("========================================")

print(f"Created: {OUTPUT_FILE}")