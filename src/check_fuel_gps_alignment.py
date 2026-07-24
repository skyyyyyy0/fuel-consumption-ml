from pathlib import Path

import pandas as pd


# --------------------------------------------------
# File paths
# --------------------------------------------------

EXCEL_FILE = Path(
    "data/raw/Final_Excel_Files/"
    "83머5742_final_2025_2026_dataset.xlsx"
)

TRIP_FILE = Path(
    "/Users/haneuljang/Desktop/Geotab/Validation/"
    "geotab_raw_data_inventory/Results/"
    "Trip_Distance/All_Periods/"
    "83머5742/"
    "83머5742_after_trip_detail.csv"
)


# --------------------------------------------------
# Load fuel data
# --------------------------------------------------

df = pd.read_excel(
    EXCEL_FILE,
    sheet_name="2026_After_Long",
    engine="openpyxl",
)

fuel = df.loc[
    df["signal_name"] == "Trip fuel used",
    ["datetime", "value"],
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

fuel = fuel.dropna(
    subset=["fuel_time", "fuel_liters"]
)

fuel = fuel.sort_values(
    "fuel_time"
)

fuel = fuel.reset_index(
    drop=True
)


# --------------------------------------------------
# Load GPS trip data
# --------------------------------------------------

trips = pd.read_csv(TRIP_FILE)

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

trips = trips.dropna(
    subset=["trip_start", "trip_stop"]
)


# --------------------------------------------------
# Prepare start and stop tables
# --------------------------------------------------

start_table = trips[
    ["trip_start", "distance_km"]
].copy()

start_table = start_table.sort_values(
    "trip_start"
).reset_index(drop=True)


stop_table = trips[
    ["trip_stop", "distance_km"]
].copy()

stop_table = stop_table.sort_values(
    "trip_stop"
).reset_index(drop=True)


# --------------------------------------------------
# Match nearest trip start
# --------------------------------------------------

start_match = pd.merge_asof(
    fuel[["fuel_time", "fuel_liters"]],
    start_table,
    left_on="fuel_time",
    right_on="trip_start",
    direction="nearest",
)

start_match["start_diff_sec"] = (
    start_match["fuel_time"]
    - start_match["trip_start"]
).abs().dt.total_seconds()


# --------------------------------------------------
# Match nearest trip stop
# --------------------------------------------------

stop_match = pd.merge_asof(
    fuel[["fuel_time", "fuel_liters"]],
    stop_table,
    left_on="fuel_time",
    right_on="trip_stop",
    direction="nearest",
)

stop_match["stop_diff_sec"] = (
    stop_match["fuel_time"]
    - stop_match["trip_stop"]
).abs().dt.total_seconds()


# --------------------------------------------------
# Build result
# --------------------------------------------------

result = pd.DataFrame()

result["fuel_time"] = fuel["fuel_time"]
result["fuel_liters"] = fuel["fuel_liters"]

result["nearest_start"] = start_match["trip_start"]
result["start_diff_sec"] = start_match["start_diff_sec"]

result["nearest_stop"] = stop_match["trip_stop"]
result["stop_diff_sec"] = stop_match["stop_diff_sec"]

result["distance_km"] = stop_match["distance_km"]


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n========================================")
print("Trip Fuel vs GPS Timestamp Alignment")
print("========================================")

print(f"Fuel records: {len(result)}")
print(f"GPS trips: {len(trips)}")

print("\nMedian difference:")

print(
    "START:",
    round(result["start_diff_sec"].median(), 3),
    "seconds",
)

print(
    "STOP :",
    round(result["stop_diff_sec"].median(), 3),
    "seconds",
)


# --------------------------------------------------
# Matching rates
# --------------------------------------------------

thresholds = [1, 5, 10, 30, 60]

for threshold in thresholds:
    start_count = int(
        (result["start_diff_sec"] <= threshold).sum()
    )

    stop_count = int(
        (result["stop_diff_sec"] <= threshold).sum()
    )

    start_pct = (
        start_count / len(result) * 100
    )

    stop_pct = (
        stop_count / len(result) * 100
    )

    print(f"\nWithin {threshold} seconds:")

    print(
        f"START: {start_count}/{len(result)} "
        f"({start_pct:.1f}%)"
    )

    print(
        f"STOP : {stop_count}/{len(result)} "
        f"({stop_pct:.1f}%)"
    )


# --------------------------------------------------
# Sample
# --------------------------------------------------

print("\n========================================")
print("First 20 Comparisons")
print("========================================\n")

print(
    result.head(20).to_string(index=False)
)