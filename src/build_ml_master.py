from pathlib import Path
import pandas as pd


# ============================================================
# 1. Paths
# ============================================================

PROCESSED_DIR = Path("data/processed")

TARGET_FILE = PROCESSED_DIR / "trips_with_target.csv"
ENGINE_FILE = PROCESSED_DIR / "trip_features_engine.csv"
STATE_FILE = PROCESSED_DIR / "trip_features_state.csv"

OUTPUT_FILE = PROCESSED_DIR / "trip_ml_master.csv"


# ============================================================
# 2. Load datasets
# ============================================================

print("Loading datasets...")

trips = pd.read_csv(TARGET_FILE)
engine = pd.read_csv(ENGINE_FILE)
state = pd.read_csv(STATE_FILE)

print(f"Trips + Target: {len(trips):,}")
print(f"Engine Features: {len(engine):,}")
print(f"State Features: {len(state):,}")


# ============================================================
# 3. Validate source uniqueness
# ============================================================

print("\n========================================")
print("Source Validation")
print("========================================")

for name, df in [
    ("Trips + Target", trips),
    ("Engine Features", engine),
    ("State Features", state),
]:
    duplicate_ids = df["trip_id"].duplicated().sum()

    print(
        f"{name}: "
        f"rows={len(df):,}, "
        f"unique_trip_ids={df['trip_id'].nunique():,}, "
        f"duplicate_trip_ids={duplicate_ids:,}"
    )

    if duplicate_ids > 0:
        raise ValueError(
            f"{name} contains duplicate trip_id values."
        )


# ============================================================
# 4. Select required columns
# ============================================================

trip_columns = [
    "vehicle_id",
    "trip_id",
    "period",
    "trip_start_time",
    "trip_end_time",
    "trip_duration_min",
    "trip_distance_km",
    "trip_fuel_used_liter",
    "fuel_match_diff_sec",
    "fuel_match_confidence",
]

engine_columns = [
    "trip_id",
    "avg_speed_kmh",
    "max_speed_kmh",
    "speed_std",
    "avg_rpm",
    "max_rpm",
    "rpm_std",
    "high_rpm_ratio",
]

state_columns = [
    "trip_id",
    "idle_ratio",
]


# Make sure expected columns exist

for col in trip_columns:
    if col not in trips.columns:
        raise ValueError(
            f"Missing column in trips_with_target.csv: {col}"
        )

for col in engine_columns:
    if col not in engine.columns:
        raise ValueError(
            f"Missing column in trip_features_engine.csv: {col}"
        )

for col in state_columns:
    if col not in state.columns:
        raise ValueError(
            f"Missing column in trip_features_state.csv: {col}"
        )


trips = trips[trip_columns].copy()
engine = engine[engine_columns].copy()
state = state[state_columns].copy()


# ============================================================
# 5. Merge
# ============================================================

print("\nMerging engine features...")

master = trips.merge(
    engine,
    on="trip_id",
    how="left",
    validate="one_to_one",
)

print(f"Rows after engine merge: {len(master):,}")


print("Merging state features...")

master = master.merge(
    state,
    on="trip_id",
    how="left",
    validate="one_to_one",
)

print(f"Rows after state merge: {len(master):,}")


# ============================================================
# 6. Row multiplication validation
# ============================================================

if len(master) != len(trips):
    raise ValueError(
        "Row count changed during merge. "
        "Possible row multiplication detected."
    )

if master["trip_id"].duplicated().any():
    raise ValueError(
        "Duplicate trip IDs detected after merge."
    )


# ============================================================
# 7. Core schema order
# ============================================================

final_columns = [
    # Metadata
    "vehicle_id",
    "trip_id",
    "period",
    "trip_start_time",
    "trip_end_time",

    # Trip features
    "trip_distance_km",
    "trip_duration_min",

    # Speed features
    "avg_speed_kmh",
    "max_speed_kmh",
    "speed_std",

    # RPM features
    "avg_rpm",
    "max_rpm",
    "rpm_std",
    "high_rpm_ratio",

    # Vehicle-state feature
    "idle_ratio",

    # Target
    "trip_fuel_used_liter",

    # Target quality metadata
    "fuel_match_diff_sec",
    "fuel_match_confidence",
]

master = master[final_columns].copy()


# ============================================================
# 8. Validation
# ============================================================

print("\n========================================")
print("Master ML Dataset Validation")
print("========================================")

print(f"Rows: {len(master):,}")
print(f"Unique trip IDs: {master['trip_id'].nunique():,}")
print(
    f"Duplicate trip IDs: "
    f"{master['trip_id'].duplicated().sum():,}"
)

print(f"Vehicles: {master['vehicle_id'].nunique()}")
print(
    "Vehicle-periods:",
    master[["vehicle_id", "period"]]
    .drop_duplicates()
    .shape[0],
)


# ============================================================
# 9. Missing values
# ============================================================

important_columns = [
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

print("\nMissing values:")

for col in important_columns:
    missing = master[col].isna().sum()
    pct = missing / len(master) * 100

    print(
        f"{col}: {missing:,} "
        f"({pct:.1f}%)"
    )


# ============================================================
# 10. Target confidence
# ============================================================

print("\nFuel target confidence:")

print(
    master["fuel_match_confidence"]
    .value_counts(dropna=False)
)


# ============================================================
# 11. High-confidence modeling candidates
# ============================================================

high_conf = master[
    master["fuel_match_confidence"] == "High"
].copy()

print(
    "\nHigh-confidence target trips:",
    f"{len(high_conf):,}"
)

complete_core = high_conf.dropna(
    subset=[
        "trip_distance_km",
        "trip_duration_min",
        "avg_speed_kmh",
        "avg_rpm",
        "idle_ratio",
        "trip_fuel_used_liter",
    ]
)

print(
    "High-confidence trips with complete core features:",
    f"{len(complete_core):,}"
)


# ============================================================
# 12. Counts by vehicle
# ============================================================

print("\nRows by vehicle:")

print(
    master.groupby("vehicle_id")
    .size()
    .to_string()
)


# ============================================================
# 13. Counts by period
# ============================================================

print("\nRows by period:")

print(
    master.groupby("period")
    .size()
    .to_string()
)


# ============================================================
# 14. Basic physical validation
# ============================================================

print("\nPhysical validation:")

print(
    "Negative distance:",
    (master["trip_distance_km"] < 0).sum()
)

print(
    "Negative duration:",
    (master["trip_duration_min"] < 0).sum()
)

print(
    "Negative speed:",
    (master["avg_speed_kmh"] < 0).sum()
)

print(
    "Negative RPM:",
    (master["avg_rpm"] < 0).sum()
)

print(
    "Idle ratio outside 0-1:",
    (
        (master["idle_ratio"] < 0)
        | (master["idle_ratio"] > 1)
    ).sum()
)

print(
    "Fuel <= 0:",
    (master["trip_fuel_used_liter"] <= 0).sum()
)


# ============================================================
# 15. Save
# ============================================================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

master.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n========================================")
print("Master ML Dataset Completed")
print("========================================")

print(f"Created: {OUTPUT_FILE}")