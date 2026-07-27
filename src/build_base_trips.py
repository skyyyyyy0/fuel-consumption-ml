from pathlib import Path
import pandas as pd
import unicodedata


# ============================================================
# Configuration
# ============================================================

TRIP_DIR = Path(
    "/Users/haneuljang/Desktop/Geotab/Validation/"
    "geotab_raw_data_inventory/Results/Trip_Distance/All_Periods"
)

OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "base_trips.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Helper
# ============================================================

def normalize_text(value):
    """Normalize Unicode text for reliable vehicle-name matching."""
    if pd.isna(value):
        return value

    return unicodedata.normalize("NFC", str(value).strip())


# ============================================================
# 1. Find Trip files
# ============================================================

files = sorted(TRIP_DIR.rglob("*_trip_detail.csv"))

print(f"Trip files found: {len(files)}")

if len(files) == 0:
    raise FileNotFoundError(
        f"No *_trip_detail.csv files found under:\n{TRIP_DIR}"
    )


# ============================================================
# 2. Determine vehicle mapping
# ============================================================

vehicle_names = []

for file in files:
    df_sample = pd.read_csv(
        file,
        usecols=["vehicle"],
        nrows=10
    )

    names = (
        df_sample["vehicle"]
        .dropna()
        .map(normalize_text)
        .unique()
        .tolist()
    )

    vehicle_names.extend(names)


vehicle_names = sorted(set(vehicle_names))

print(f"Vehicles found: {len(vehicle_names)}")

if len(vehicle_names) != 12:
    raise ValueError(
        f"Expected 12 vehicles, but found {len(vehicle_names)}"
    )


vehicle_map = {
    vehicle: f"VEH_{i:02d}"
    for i, vehicle in enumerate(vehicle_names, start=1)
}


# ============================================================
# 3. Load and standardize Trip data
# ============================================================

all_trips = []

for file in files:

    print(f"Reading: {file.name}")

    df = pd.read_csv(file)

    required_columns = [
        "vehicle",
        "period",
        "trip_start_utc",
        "trip_stop_utc",
        "distance_km",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{file.name} missing columns: {missing_columns}"
        )

    # --------------------------------------------------------
    # Vehicle ID
    # --------------------------------------------------------

    df["vehicle_normalized"] = (
        df["vehicle"]
        .map(normalize_text)
    )

    df["vehicle_id"] = (
        df["vehicle_normalized"]
        .map(vehicle_map)
    )

    if df["vehicle_id"].isna().any():
        raise ValueError(
            f"Vehicle mapping failed in {file.name}"
        )

    # --------------------------------------------------------
    # Period
    # --------------------------------------------------------

    df["period"] = (
        df["period"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    # --------------------------------------------------------
    # UTC timestamps
    # --------------------------------------------------------

    df["trip_start_time"] = pd.to_datetime(
        df["trip_start_utc"],
        utc=True,
        format="mixed",
        errors="coerce",
    )

    df["trip_end_time"] = pd.to_datetime(
        df["trip_stop_utc"],
        utc=True,
        format="mixed",
        errors="coerce",
    )

    # --------------------------------------------------------
    # Duration
    # --------------------------------------------------------

    df["trip_duration_min"] = (
        (
            df["trip_end_time"]
            - df["trip_start_time"]
        )
        .dt.total_seconds()
        / 60
    )

    # --------------------------------------------------------
    # Distance
    # --------------------------------------------------------

    df["trip_distance_km"] = pd.to_numeric(
        df["distance_km"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Keep only public / standardized fields
    # --------------------------------------------------------

    standardized = df[
        [
            "vehicle_id",
            "period",
            "trip_start_time",
            "trip_end_time",
            "trip_duration_min",
            "trip_distance_km",
        ]
    ].copy()

    all_trips.append(standardized)


# ============================================================
# 4. Combine all vehicle-periods
# ============================================================

base = pd.concat(
    all_trips,
    ignore_index=True
)

base = base.sort_values(
    [
        "vehicle_id",
        "period",
        "trip_start_time",
        "trip_end_time",
    ]
).reset_index(drop=True)


# ============================================================
# 5. Create unique Trip IDs
# ============================================================

base["trip_number"] = (
    base.groupby(
        ["vehicle_id", "period"]
    )
    .cumcount()
    .add(1)
)

base["trip_id"] = (
    base["vehicle_id"]
    + "_"
    + base["period"].str.upper()
    + "_"
    + base["trip_number"]
        .astype(str)
        .str.zfill(4)
)


# ============================================================
# 6. Quality flags
# ============================================================

base["zero_distance_flag"] = (
    base["trip_distance_km"] <= 0
)

base["invalid_time_flag"] = (
    base["trip_start_time"].isna()
    | base["trip_end_time"].isna()
    | (
        base["trip_start_time"]
        >= base["trip_end_time"]
    )
)


# ============================================================
# 7. Final column order
# ============================================================

base = base[
    [
        "vehicle_id",
        "trip_id",
        "period",
        "trip_start_time",
        "trip_end_time",
        "trip_duration_min",
        "trip_distance_km",
        "zero_distance_flag",
        "invalid_time_flag",
    ]
]


# ============================================================
# 8. Validation
# ============================================================

vehicle_count = base["vehicle_id"].nunique()

vehicle_period_count = (
    base[
        ["vehicle_id", "period"]
    ]
    .drop_duplicates()
    .shape[0]
)

duplicate_trip_ids = (
    base["trip_id"]
    .duplicated()
    .sum()
)

duplicate_trip_rows = (
    base.duplicated(
        subset=[
            "vehicle_id",
            "period",
            "trip_start_time",
            "trip_end_time",
        ]
    )
    .sum()
)

invalid_times = (
    base["invalid_time_flag"]
    .sum()
)

zero_distance = (
    base["zero_distance_flag"]
    .sum()
)

missing_distance = (
    base["trip_distance_km"]
    .isna()
    .sum()
)


# ============================================================
# 9. Save
# ============================================================

base.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 10. Report
# ============================================================

print("\n========================================")
print("Base Trip Dataset Completed")
print("========================================")

print(f"Vehicles: {vehicle_count}")
print(f"Vehicle-periods: {vehicle_period_count}")
print(f"Total trips: {len(base):,}")

print(f"Duplicate trip IDs: {duplicate_trip_ids}")
print(f"Duplicate trip rows: {duplicate_trip_rows}")

print(f"Invalid timestamps: {invalid_times}")
print(f"Missing distance: {missing_distance}")
print(f"Zero-distance trips: {zero_distance}")

print("\nTrips by period:")
print(
    base.groupby("period")
    .size()
)

print("\nTrips by vehicle:")
print(
    base.groupby("vehicle_id")
    .size()
)

print(f"\nCreated: {OUTPUT_FILE}")