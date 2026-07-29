import pandas as pd


DATA_PATH = "data/processed/trip_ml_features.csv"

TARGET = "trip_fuel_used_liter"

BASELINE = [
    "trip_distance_km",
    "trip_duration_min",
]

DRIVING = [
    "avg_speed_kmh",
    "max_speed_kmh",
    "speed_std",
    "avg_rpm",
    "max_rpm",
    "rpm_std",
    "high_rpm_ratio",
    "idle_ratio",
]

CONTEXT = [
    "trip_hour",
    "day_of_week",
    "is_weekend",
]

METADATA = [
    "trip_id",
    "vehicle_id",
    "period",
    "trip_start_time",
    "trip_end_time",
]

LEAKAGE_COLUMNS = [
    TARGET,
    "total_fuel_used",
    "trip_idle_fuel_used",
    "total_idle_fuel_used",
    "fuel_match_time_diff",
    "fuel_match_confidence",
]


print("Loading feature dataset...")

df = pd.read_csv(DATA_PATH)

extended = BASELINE + DRIVING
context_model = extended + CONTEXT


print("\n========================================")
print("Final Feature Selection Validation")
print("========================================")

print(f"Rows: {len(df):,}")
print(f"Vehicles: {df['vehicle_id'].nunique()}")

print("\nFeature sets:")
print(f"Baseline: {len(BASELINE)}")
print(f"Extended: {len(extended)}")
print(f"Context: {len(context_model)}")


# ------------------------------------------------------------
# Required columns
# ------------------------------------------------------------

required = (
    context_model
    + METADATA
    + [TARGET]
)

missing_columns = [
    col
    for col in required
    if col not in df.columns
]

print("\nMissing required columns:")
print(missing_columns)


# ------------------------------------------------------------
# Missing predictor values
# ------------------------------------------------------------

print("\nMissing values in candidate predictors:")

for col in context_model:
    missing = df[col].isna().sum()

    print(
        f"{col}: "
        f"{missing:,} "
        f"({missing / len(df) * 100:.2f}%)"
    )


# ------------------------------------------------------------
# Leakage check
# ------------------------------------------------------------

print("\nLeakage check:")

for name, features in {
    "Baseline": BASELINE,
    "Extended": extended,
    "Context": context_model,
}.items():

    leakage = [
        col
        for col in features
        if col in LEAKAGE_COLUMNS
    ]

    metadata_leak = [
        col
        for col in features
        if col in METADATA
    ]

    print(
        f"{name}: "
        f"leakage={leakage}, "
        f"metadata_in_X={metadata_leak}"
    )


# ------------------------------------------------------------
# Duplicate features
# ------------------------------------------------------------

duplicates = (
    pd.Series(context_model)
    .duplicated()
    .sum()
)

print(
    f"\nDuplicate feature definitions: "
    f"{duplicates}"
)


# ------------------------------------------------------------
# Final decision
# ------------------------------------------------------------

passed = (
    len(missing_columns) == 0
    and duplicates == 0
    and TARGET not in context_model
    and not any(
        col in METADATA
        for col in context_model
    )
)

print("\n========================================")

if passed:
    print("FINAL DECISION: PASS")
    print(
        "Candidate feature sets are ready "
        "for split strategy and modeling."
    )
else:
    print("FINAL DECISION: REVIEW REQUIRED")

print("========================================")