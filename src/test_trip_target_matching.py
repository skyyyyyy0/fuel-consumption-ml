from pathlib import Path
import pandas as pd


# ==================================================
# Configuration
# ==================================================

EXCEL_DIR = Path("data/raw/Final_Excel_Files")

TRIP_DIR = Path(
    "/Users/haneuljang/Desktop/Geotab/Validation/"
    "geotab_raw_data_inventory/Results/"
    "Trip_Distance/All_Periods"
)

TEST_VEHICLE_INDEX = 0
TEST_PERIOD = "After"

MAX_MATCH_SEC = 60


# ==================================================
# 1. Find Excel files
# ==================================================

excel_files = sorted(
    f for f in EXCEL_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

if not excel_files:
    raise FileNotFoundError(
        f"No Excel files found in {EXCEL_DIR}"
    )

excel_file = excel_files[TEST_VEHICLE_INDEX]
vehicle_id = f"VEH_{TEST_VEHICLE_INDEX + 1:02d}"

print("\n========================================")
print("Trip Target Matching Test")
print("========================================")

print("Vehicle:", vehicle_id)
print("Period:", TEST_PERIOD)
print("Excel:", excel_file.name)


# ==================================================
# 2. Read Trip Fuel Used
# ==================================================

sheet_name = f"2026_{TEST_PERIOD}_Long"

fuel = pd.read_excel(
    excel_file,
    sheet_name=sheet_name,
    engine="openpyxl",
)

fuel = fuel[
    fuel["signal_name"] == "Trip fuel used"
].copy()

fuel["fuel_time"] = pd.to_datetime(
    fuel["datetime"],
    format="mixed",
    utc=True,
    errors="coerce",
)

fuel["fuel_liters"] = pd.to_numeric(
    fuel["value"],
    errors="coerce",
)

fuel = (
    fuel[
        ["fuel_time", "fuel_liters"]
    ]
    .dropna()
    .sort_values("fuel_time")
    .reset_index(drop=True)
)

print("Trip Fuel records:", len(fuel))


# ==================================================
# 3. Determine actual vehicle name
# ==================================================

vehicle_col = pd.read_excel(
    excel_file,
    sheet_name=sheet_name,
    engine="openpyxl",
    usecols=["vehicle"],
)

actual_vehicle = str(
    vehicle_col["vehicle"]
    .dropna()
    .iloc[0]
)

print("Source vehicle located.")


# ==================================================
# 4. Find corresponding GPS Trip file
# ==================================================

period_lower = TEST_PERIOD.lower()

trip_files = list(
    TRIP_DIR.glob(
        f"**/{actual_vehicle}_{period_lower}_trip_detail.csv"
    )
)

if len(trip_files) != 1:
    raise RuntimeError(
        f"Expected 1 trip file, found {len(trip_files)}"
    )

trip_file = trip_files[0]

print("GPS Trip file located.")


# ==================================================
# 5. Read GPS Trips
# ==================================================

trips = pd.read_csv(trip_file)

trips["trip_start"] = pd.to_datetime(
    trips["trip_start_utc"],
    format="mixed",
    utc=True,
    errors="coerce",
)

trips["trip_stop"] = pd.to_datetime(
    trips["trip_stop_utc"],
    format="mixed",
    utc=True,
    errors="coerce",
)

trips["distance_km"] = pd.to_numeric(
    trips["distance_km"],
    errors="coerce",
)

trips = (
    trips[
        [
            "trip_start",
            "trip_stop",
            "distance_km",
        ]
    ]
    .dropna(
        subset=[
            "trip_start",
            "trip_stop",
            "distance_km",
        ]
    )
    .sort_values("trip_stop")
    .reset_index(drop=True)
)

trips["trip_id"] = [
    f"{vehicle_id}_{TEST_PERIOD.upper()}_{i:04d}"
    for i in range(1, len(trips) + 1)
]

trips["duration_min"] = (
    (
        trips["trip_stop"]
        - trips["trip_start"]
    )
    .dt.total_seconds()
    / 60
)

print("GPS Trips:", len(trips))


# ==================================================
# 6. Match each trip to nearest fuel record
# ==================================================

matched = pd.merge_asof(
    trips.sort_values("trip_stop"),
    fuel.sort_values("fuel_time"),
    left_on="trip_stop",
    right_on="fuel_time",
    direction="nearest",
    tolerance=pd.Timedelta(
        seconds=MAX_MATCH_SEC
    ),
)

matched["match_diff_sec"] = (
    matched["fuel_time"]
    - matched["trip_stop"]
).abs().dt.total_seconds()


# ==================================================
# 7. Detect duplicate fuel matches
# ==================================================

matched_fuel = matched[
    matched["fuel_time"].notna()
].copy()

fuel_usage_counts = (
    matched_fuel["fuel_time"]
    .value_counts()
)

reused_fuel_times = set(
    fuel_usage_counts[
        fuel_usage_counts > 1
    ].index
)

matched["fuel_record_reused"] = (
    matched["fuel_time"]
    .isin(reused_fuel_times)
)


# ==================================================
# 8. Match confidence
# ==================================================

def classify_match(row):

    if pd.isna(row["fuel_time"]):
        return "Unmatched"

    if row["fuel_record_reused"]:
        return "Duplicate Match"

    if row["match_diff_sec"] <= 30:
        return "High"

    if row["match_diff_sec"] <= 60:
        return "Review"

    return "Unmatched"


matched["match_status"] = matched.apply(
    classify_match,
    axis=1,
)


# ==================================================
# 9. Basic trip validity
# ==================================================

matched["trip_validity"] = "Valid"

matched.loc[
    matched["distance_km"] <= 0,
    "trip_validity"
] = "Invalid Distance"

matched.loc[
    (
        (matched["distance_km"] > 0)
        & (matched["distance_km"] < 0.1)
    ),
    "trip_validity"
] = "Very Short"


# ==================================================
# 10. Summary
# ==================================================

print("\n========================================")
print("Matching Summary")
print("========================================")

print("Total GPS trips:", len(matched))

print(
    "Fuel records:",
    len(fuel),
)

print("\nMatch status:")

print(
    matched["match_status"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nTrip validity:")

print(
    matched["trip_validity"]
    .value_counts(dropna=False)
    .to_string()
)

print(
    "\nUnique fuel records matched:",
    matched_fuel["fuel_time"].nunique(),
)

print(
    "Fuel records reused:",
    len(reused_fuel_times),
)

valid_target = matched[
    (matched["match_status"] == "High")
    & (matched["trip_validity"] == "Valid")
]

print(
    "\nHigh-confidence valid ML trips:",
    len(valid_target),
)

if len(matched) > 0:
    print(
        "Usable trip rate:",
        f"{len(valid_target) / len(matched) * 100:.1f}%"
    )


# ==================================================
# 11. Sample inspection
# ==================================================

print("\n========================================")
print("First 20 Trips")
print("========================================\n")

columns = [
    "trip_id",
    "trip_start",
    "trip_stop",
    "duration_min",
    "distance_km",
    "fuel_time",
    "fuel_liters",
    "match_diff_sec",
    "match_status",
    "trip_validity",
]

print(
    matched[columns]
    .head(20)
    .to_string(index=False)
)


# ==================================================
# 12. Save internal test result
# ==================================================

output = Path(
    "reports/trip_target_matching_test.csv"
)

matched[columns].to_csv(
    output,
    index=False,
)

print(f"\nCreated: {output}")