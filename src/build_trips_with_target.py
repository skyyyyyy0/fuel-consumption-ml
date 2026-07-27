from pathlib import Path
import unicodedata

import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

BASE_TRIPS_PATH = Path("data/processed/base_trips.csv")
EXCEL_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_PATH = Path("data/processed/trips_with_target.csv")

MAX_TOLERANCE_SEC = 60
HIGH_CONFIDENCE_SEC = 30

PERIODS = ["Before", "After", "Final"]


# ============================================================
# Helpers
# ============================================================

def normalize_text(value):
    if pd.isna(value):
        return None

    return unicodedata.normalize(
        "NFC",
        str(value).strip()
    )


def parse_utc(series):
    """
    Parse mixed ISO-8601 timestamps and standardize to UTC.
    """
    return pd.to_datetime(
        series,
        format="mixed",
        utc=True,
        errors="coerce"
    )


# ============================================================
# 1. Load Base Trips
# ============================================================

print("Loading base trips...")

trips = pd.read_csv(BASE_TRIPS_PATH)

trips["trip_start_time"] = parse_utc(
    trips["trip_start_time"]
)

trips["trip_end_time"] = parse_utc(
    trips["trip_end_time"]
)

print("Base trips:", len(trips))
print("Vehicles:", trips["vehicle_id"].nunique())


# ============================================================
# 2. Rebuild Vehicle Mapping from Excel Files
# ============================================================

excel_files = sorted(
    f for f in EXCEL_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

if len(excel_files) != 12:
    raise ValueError(
        f"Expected 12 Excel files, found {len(excel_files)}"
    )


vehicle_mapping = {}

for idx, file in enumerate(excel_files, start=1):

    sample = pd.read_excel(
        file,
        sheet_name="2026_Before_Long",
        engine="openpyxl",
        usecols=["vehicle"],
    )

    values = sample["vehicle"].dropna()

    if values.empty:
        raise ValueError(
            f"No vehicle value found in {file.name}"
        )

    actual_vehicle = normalize_text(
        values.iloc[0]
    )

    vehicle_id = f"VEH_{idx:02d}"

    vehicle_mapping[actual_vehicle] = {
        "vehicle_id": vehicle_id,
        "excel_file": file,
    }


print("Vehicle mappings:", len(vehicle_mapping))


# ============================================================
# 3. Extract Trip Fuel Used Events
# ============================================================

fuel_frames = []

for actual_vehicle, info in vehicle_mapping.items():

    vehicle_id = info["vehicle_id"]
    file = info["excel_file"]

    for period in PERIODS:

        sheet = f"2026_{period}_Long"

        print(
            f"Reading fuel: {vehicle_id} | {period}"
        )

        df = pd.read_excel(
            file,
            sheet_name=sheet,
            engine="openpyxl",
            usecols=[
                "datetime",
                "signal_name",
                "value",
            ],
        )

        fuel = df[
            df["signal_name"].eq("Trip fuel used")
        ].copy()

        fuel["fuel_time"] = parse_utc(
            fuel["datetime"]
        )

        fuel["trip_fuel_used_liter"] = pd.to_numeric(
            fuel["value"],
            errors="coerce"
        )

        fuel["vehicle_id"] = vehicle_id
        fuel["period"] = period

        fuel = fuel[
            [
                "vehicle_id",
                "period",
                "fuel_time",
                "trip_fuel_used_liter",
            ]
        ]

        # Remove unusable target events
        fuel = fuel.dropna(
            subset=[
                "fuel_time",
                "trip_fuel_used_liter",
            ]
        )

        fuel_frames.append(fuel)


fuel_events = pd.concat(
    fuel_frames,
    ignore_index=True
)

# Unique internal event ID
fuel_events["fuel_event_id"] = [
    f"FUEL_{i:06d}"
    for i in range(1, len(fuel_events) + 1)
]


print("\nFuel events:", len(fuel_events))
print(
    "Negative fuel:",
    int(
        (
            fuel_events["trip_fuel_used_liter"] < 0
        ).sum()
    )
)

print(
    "Zero fuel:",
    int(
        (
            fuel_events["trip_fuel_used_liter"] == 0
        ).sum()
    )
)


# ============================================================
# 4. Match Trips to Fuel Events
# ============================================================

results = []


for (vehicle_id, period), trip_group in trips.groupby(
    ["vehicle_id", "period"],
    sort=True
):

    print(
        f"Matching: {vehicle_id} | {period}"
    )

    trip_group = trip_group.copy()

    fuel_group = fuel_events[
        (fuel_events["vehicle_id"] == vehicle_id)
        & (fuel_events["period"] == period)
    ].copy()

    # Valid timestamps only
    trip_group = trip_group.sort_values(
        "trip_end_time"
    )

    fuel_group = fuel_group.sort_values(
        "fuel_time"
    )

    # --------------------------------------------------------
    # Generate all candidate pairs within 60 seconds
    # --------------------------------------------------------

    candidates = []

    for trip_idx, trip_row in trip_group.iterrows():

        trip_end = trip_row["trip_end_time"]

        if pd.isna(trip_end):
            continue

        diffs = (
            fuel_group["fuel_time"] - trip_end
        ).abs().dt.total_seconds()

        valid_candidates = fuel_group[
            diffs <= MAX_TOLERANCE_SEC
        ].copy()

        if valid_candidates.empty:
            continue

        valid_candidates["match_diff_sec"] = (
            valid_candidates["fuel_time"] - trip_end
        ).abs().dt.total_seconds()

        for _, fuel_row in valid_candidates.iterrows():

            # Prefer structurally valid trips when conflicts occur.
            invalid_time = bool(
                trip_row.get(
                    "invalid_time_flag",
                    False
                )
            )

            zero_distance = bool(
                trip_row.get(
                    "zero_distance_flag",
                    False
                )
            )

            valid_priority = (
                1 if invalid_time or zero_distance else 0
            )

            candidates.append({
                "trip_index": trip_idx,
                "trip_id": trip_row["trip_id"],
                "fuel_event_id": fuel_row["fuel_event_id"],
                "fuel_time": fuel_row["fuel_time"],
                "trip_fuel_used_liter":
                    fuel_row["trip_fuel_used_liter"],
                "fuel_match_diff_sec":
                    fuel_row["match_diff_sec"],
                "valid_priority": valid_priority,
            })


    # --------------------------------------------------------
    # One-to-one greedy assignment
    #
    # Priority:
    # 1. Valid trip
    # 2. Smallest timestamp difference
    # --------------------------------------------------------

    if candidates:

        candidate_df = pd.DataFrame(candidates)

        candidate_df = candidate_df.sort_values(
            [
                "valid_priority",
                "fuel_match_diff_sec",
                "trip_id",
                "fuel_event_id",
            ]
        )

        assigned_trips = set()
        assigned_fuel = set()
        assignments = {}

        for _, row in candidate_df.iterrows():

            trip_idx = row["trip_index"]
            fuel_id = row["fuel_event_id"]

            if trip_idx in assigned_trips:
                continue

            if fuel_id in assigned_fuel:
                continue

            assignments[trip_idx] = {
                "fuel_event_id": fuel_id,
                "fuel_time": row["fuel_time"],
                "trip_fuel_used_liter":
                    row["trip_fuel_used_liter"],
                "fuel_match_diff_sec":
                    row["fuel_match_diff_sec"],
            }

            assigned_trips.add(trip_idx)
            assigned_fuel.add(fuel_id)

    else:
        assignments = {}


    # --------------------------------------------------------
    # Add results to each trip
    # --------------------------------------------------------

    for trip_idx, trip_row in trip_group.iterrows():

        record = trip_row.to_dict()

        assignment = assignments.get(trip_idx)

        if assignment is None:

            record["fuel_event_id"] = pd.NA
            record["fuel_time"] = pd.NaT
            record["trip_fuel_used_liter"] = np.nan
            record["fuel_match_diff_sec"] = np.nan
            record["fuel_match_confidence"] = "Unmatched"

        else:

            diff = assignment[
                "fuel_match_diff_sec"
            ]

            if diff <= HIGH_CONFIDENCE_SEC:
                confidence = "High"

            elif diff <= MAX_TOLERANCE_SEC:
                confidence = "Review"

            else:
                confidence = "Unmatched"

            record["fuel_event_id"] = assignment[
                "fuel_event_id"
            ]

            record["fuel_time"] = assignment[
                "fuel_time"
            ]

            record["trip_fuel_used_liter"] = assignment[
                "trip_fuel_used_liter"
            ]

            record["fuel_match_diff_sec"] = diff
            record["fuel_match_confidence"] = confidence

        results.append(record)


# ============================================================
# 5. Build Final Dataset
# ============================================================

result = pd.DataFrame(results)

result = result.sort_values(
    [
        "vehicle_id",
        "period",
        "trip_start_time",
    ]
).reset_index(drop=True)


# ============================================================
# 6. Validation
# ============================================================

print("\n========================================")
print("Trips With Target Validation")
print("========================================")

print("Total trips:", len(result))

print(
    "Unique trip IDs:",
    result["trip_id"].nunique()
)

print(
    "Matched fuel events:",
    result["fuel_event_id"].notna().sum()
)

print(
    "Unique matched fuel events:",
    result["fuel_event_id"].dropna().nunique()
)

duplicate_targets = (
    result["fuel_event_id"]
    .dropna()
    .duplicated()
    .sum()
)

print(
    "Duplicate fuel assignments:",
    duplicate_targets
)


print("\nMatch confidence:")

print(
    result["fuel_match_confidence"]
    .value_counts(dropna=False)
)


print("\nFuel validation:")

matched = result[
    result["trip_fuel_used_liter"].notna()
]

print(
    "Fuel <= 0:",
    int(
        (
            matched["trip_fuel_used_liter"] <= 0
        ).sum()
    )
)

print(
    "Negative fuel:",
    int(
        (
            matched["trip_fuel_used_liter"] < 0
        ).sum()
    )
)


# ============================================================
# 7. Coverage by Vehicle
# ============================================================

vehicle_coverage = (
    result
    .assign(
        target_available=
        result["trip_fuel_used_liter"].notna(),

        high_confidence=
        result["fuel_match_confidence"].eq("High")
    )
    .groupby("vehicle_id")
    .agg(
        trips=("trip_id", "size"),
        targets=("target_available", "sum"),
        high_targets=("high_confidence", "sum"),
    )
)

vehicle_coverage["target_coverage_pct"] = (
    vehicle_coverage["targets"]
    / vehicle_coverage["trips"]
    * 100
)

vehicle_coverage["high_coverage_pct"] = (
    vehicle_coverage["high_targets"]
    / vehicle_coverage["trips"]
    * 100
)


print("\nCoverage by vehicle:")

print(
    vehicle_coverage
    .round(1)
    .to_string()
)


# ============================================================
# 8. Coverage by Period
# ============================================================

period_coverage = (
    result
    .assign(
        target_available=
        result["trip_fuel_used_liter"].notna(),

        high_confidence=
        result["fuel_match_confidence"].eq("High")
    )
    .groupby("period")
    .agg(
        trips=("trip_id", "size"),
        targets=("target_available", "sum"),
        high_targets=("high_confidence", "sum"),
    )
)

period_coverage["target_coverage_pct"] = (
    period_coverage["targets"]
    / period_coverage["trips"]
    * 100
)

period_coverage["high_coverage_pct"] = (
    period_coverage["high_targets"]
    / period_coverage["trips"]
    * 100
)


print("\nCoverage by period:")

print(
    period_coverage
    .round(1)
    .to_string()
)


# ============================================================
# 9. Save
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nCreated:", OUTPUT_PATH)