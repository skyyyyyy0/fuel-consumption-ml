from pathlib import Path
import pandas as pd


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("data/processed/trip_ml_clean.csv")

EXPECTED_ROWS = 9923
EXPECTED_VEHICLES = 12
EXPECTED_VEHICLE_PERIODS = 36

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
]

TARGET = "trip_fuel_used_liter"

LEAKAGE_COLUMNS = [
    "Total fuel used (since telematics device install)",
    "Trip idle fuel used",
    "Total fuel used while idling (since telematics device install)",
]


# ============================================================
# Load
# ============================================================

print("Loading clean ML dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded: {len(df):,}")


# ============================================================
# 1. Dataset Integrity
# ============================================================

print("\n========================================")
print("1. Dataset Integrity")
print("========================================")

row_count = len(df)
vehicle_count = df["vehicle_id"].nunique()

vehicle_period_count = (
    df[
        ["vehicle_id", "period"]
    ]
    .drop_duplicates()
    .shape[0]
)

duplicate_trip_ids = (
    df["trip_id"]
    .duplicated()
    .sum()
)

missing_target = (
    df[TARGET]
    .isna()
    .sum()
)

negative_fuel = (
    df[TARGET] < 0
).sum()

nonpositive_fuel = (
    df[TARGET] <= 0
).sum()

missing_core = (
    df[CORE_FEATURES]
    .isna()
    .any(axis=1)
    .sum()
)

print("Rows:", row_count)
print("Vehicles:", vehicle_count)
print("Vehicle-periods:", vehicle_period_count)
print("Duplicate trip IDs:", duplicate_trip_ids)
print("Missing target:", missing_target)
print("Missing core-feature rows:", missing_core)
print("Negative fuel:", negative_fuel)
print("Fuel <= 0:", nonpositive_fuel)


# ============================================================
# 2. Physical Validation
# ============================================================

print("\n========================================")
print("2. Physical Validation")
print("========================================")

checks = {
    "Distance < 0.1 km":
        (df["trip_distance_km"] < 0.1).sum(),

    "Duration <= 0":
        (df["trip_duration_min"] <= 0).sum(),

    "Negative avg speed":
        (df["avg_speed_kmh"] < 0).sum(),

    "Max speed > 160 km/h":
        (df["max_speed_kmh"] > 160).sum(),

    "Negative avg RPM":
        (df["avg_rpm"] < 0).sum(),

    "Max RPM > 5000":
        (df["max_rpm"] > 5000).sum(),

    "Idle ratio < 0":
        (df["idle_ratio"] < 0).sum(),

    "Idle ratio > 1":
        (df["idle_ratio"] > 1).sum(),
}

for label, value in checks.items():
    print(f"{label}: {int(value)}")


# ============================================================
# 3. Distribution Check
# ============================================================

print("\n========================================")
print("3. Distribution Check")
print("========================================")

distribution_columns = [
    TARGET,
    "trip_distance_km",
    "trip_duration_min",
    "avg_speed_kmh",
    "max_speed_kmh",
    "avg_rpm",
    "max_rpm",
    "idle_ratio",
]

for col in distribution_columns:

    s = df[col].dropna()

    print(f"\n--- {col} ---")

    print(f"Count: {len(s):,}")
    print(f"Min: {s.min():.6f}")
    print(f"P01: {s.quantile(0.01):.6f}")
    print(f"P05: {s.quantile(0.05):.6f}")
    print(f"Median: {s.median():.6f}")
    print(f"Mean: {s.mean():.6f}")
    print(f"P95: {s.quantile(0.95):.6f}")
    print(f"P99: {s.quantile(0.99):.6f}")
    print(f"Max: {s.max():.6f}")


# ============================================================
# 4. Vehicle-Level Validation
# ============================================================

print("\n========================================")
print("4. Vehicle-Level Validation")
print("========================================")

vehicle_summary = (
    df.groupby("vehicle_id")
    .agg(
        trips=("trip_id", "size"),

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

        median_distance_km=(
            "trip_distance_km",
            "median",
        ),
    )
)

print(
    vehicle_summary
    .round(3)
    .to_string()
)


# ============================================================
# 5. Period-Level Validation
# ============================================================

print("\n========================================")
print("5. Period-Level Validation")
print("========================================")

period_summary = (
    df.groupby("period")
    .agg(
        trips=("trip_id", "size"),

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

        median_distance_km=(
            "trip_distance_km",
            "median",
        ),
    )
)

print(
    period_summary
    .round(3)
    .to_string()
)


# ============================================================
# 6. Feature Missing %
# ============================================================

print("\n========================================")
print("6. Feature Missing Percentage")
print("========================================")

for col in CORE_FEATURES + [TARGET]:

    missing = df[col].isna().sum()

    pct = (
        missing / len(df) * 100
        if len(df) > 0
        else 0
    )

    print(
        f"{col}: "
        f"{missing:,} "
        f"({pct:.2f}%)"
    )


# ============================================================
# 7. Leakage Check
# ============================================================

print("\n========================================")
print("7. Leakage Check")
print("========================================")

present_leakage = [
    col for col in LEAKAGE_COLUMNS
    if col in df.columns
]

print(
    "Known leakage columns present:",
    present_leakage
)

print(
    "Target column exists:",
    TARGET in df.columns
)

print(
    "trip_id exists as metadata:",
    "trip_id" in df.columns
)


# ============================================================
# 8. Approved Modeling Matrix
# ============================================================

MODEL_FEATURES = [
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
]

print("\nApproved X columns:")

for col in MODEL_FEATURES:
    print("-", col)

print("\nTarget Y:")
print("-", TARGET)

print(
    "\ntrip_id included in X:",
    "trip_id" in MODEL_FEATURES
)

print(
    "Target included in X:",
    TARGET in MODEL_FEATURES
)


# ============================================================
# 9. Automated GO / NO-GO
# ============================================================

print("\n========================================")
print("8. Week 2 GO / NO-GO")
print("========================================")

failures = []

if row_count != EXPECTED_ROWS:
    failures.append(
        f"Unexpected row count: {row_count}"
    )

if vehicle_count != EXPECTED_VEHICLES:
    failures.append(
        f"Expected 12 vehicles, found {vehicle_count}"
    )

if vehicle_period_count != EXPECTED_VEHICLE_PERIODS:
    failures.append(
        "Missing vehicle-period coverage"
    )

if duplicate_trip_ids != 0:
    failures.append(
        "Duplicate trip IDs detected"
    )

if missing_target != 0:
    failures.append(
        "Missing targets detected"
    )

if missing_core != 0:
    failures.append(
        "Missing core features detected"
    )

if nonpositive_fuel != 0:
    failures.append(
        "Non-positive fuel targets detected"
    )

if checks["Distance < 0.1 km"] != 0:
    failures.append(
        "Invalid short-distance trips detected"
    )

if checks["Duration <= 0"] != 0:
    failures.append(
        "Invalid durations detected"
    )

if checks["Negative avg speed"] != 0:
    failures.append(
        "Negative speed detected"
    )

if checks["Max speed > 160 km/h"] != 0:
    failures.append(
        "Impossible speed detected"
    )

if checks["Negative avg RPM"] != 0:
    failures.append(
        "Negative RPM detected"
    )

if checks["Max RPM > 5000"] != 0:
    failures.append(
        "Impossible RPM detected"
    )

if checks["Idle ratio < 0"] != 0:
    failures.append(
        "Idle ratio below 0 detected"
    )

if checks["Idle ratio > 1"] != 0:
    failures.append(
        "Idle ratio above 1 detected"
    )

if present_leakage:
    failures.append(
        "Known leakage columns detected"
    )

if failures:

    print("FINAL DECISION: NO-GO")

    print("\nFailures:")

    for failure in failures:
        print("-", failure)

else:

    print("FINAL DECISION: GO")

    print(
        "\nDataset is ready for "
        "train / validation / test splitting."
    )


print("\n========================================")
print("Week 2 Validation Completed")
print("========================================")