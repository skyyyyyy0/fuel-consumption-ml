from pathlib import Path
import pandas as pd


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("data/processed/trip_ml_clean.csv")
OUTPUT_FILE = Path("data/processed/trip_ml_features.csv")


# ============================================================
# Load
# ============================================================

print("Loading clean ML dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows: {len(df):,}")
print(f"Vehicles: {df['vehicle_id'].nunique()}")


# ============================================================
# Parse UTC Timestamp
# ============================================================

df["trip_start_utc"] = pd.to_datetime(
    df["trip_start_time"],
    format="mixed",
    utc=True,
    errors="coerce",
)

invalid_timestamp = df["trip_start_utc"].isna().sum()

print(
    f"Invalid trip_start_time after mixed parsing: "
    f"{invalid_timestamp}"
)


# ============================================================
# Convert UTC -> Korea Standard Time
# ============================================================

df["trip_start_kst"] = (
    df["trip_start_utc"]
    .dt.tz_convert("Asia/Seoul")
)


# ============================================================
# Context Features
# ============================================================

df["trip_hour"] = (
    df["trip_start_kst"]
    .dt.hour
    .astype("Int64")
)

df["day_of_week"] = (
    df["trip_start_kst"]
    .dt.dayofweek
    .astype("Int64")
)

# Monday = 0
# ...
# Saturday = 5
# Sunday = 6

df["is_weekend"] = pd.Series(
    pd.NA,
    index=df.index,
    dtype="Int64",
)

valid_day = df["day_of_week"].notna()

df.loc[
    valid_day,
    "is_weekend"
] = (
    df.loc[
        valid_day,
        "day_of_week"
    ] >= 5
).astype(int)


# ============================================================
# Validation
# ============================================================

print("\n========================================")
print("Context Feature Validation")
print("========================================")

print("\nTrip hour range (KST):")

print(
    df["trip_hour"].min(),
    "to",
    df["trip_hour"].max(),
)

print("\nDay-of-week range:")

print(
    df["day_of_week"].min(),
    "to",
    df["day_of_week"].max(),
)


print("\nWeekend distribution:")

print(
    df["is_weekend"]
    .value_counts(
        dropna=False
    )
    .sort_index()
)


print("\nTrips by KST hour:")

print(
    df["trip_hour"]
    .value_counts(
        dropna=False
    )
    .sort_index()
)


print("\nTrips by day of week:")

print(
    df["day_of_week"]
    .value_counts(
        dropna=False
    )
    .sort_index()
)


# ============================================================
# Dataset Integrity
# ============================================================

print("\n========================================")
print("Dataset Integrity")
print("========================================")

print("Rows:", len(df))

print(
    "Unique trip IDs:",
    df["trip_id"].nunique(),
)

print(
    "Duplicate trip IDs:",
    df["trip_id"]
    .duplicated()
    .sum(),
)


# ============================================================
# Missing Context Features
# ============================================================

new_features = [
    "trip_hour",
    "day_of_week",
    "is_weekend",
]

print("\nMissing context features:")

for col in new_features:

    missing = df[col].isna().sum()

    pct = (
        missing / len(df)
        * 100
    )

    print(
        f"{col}: "
        f"{missing:,} "
        f"({pct:.2f}%)"
    )


# ============================================================
# Save
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n========================================")
print("Context Feature Engineering Completed")
print("========================================")

print(f"Created: {OUTPUT_FILE}")