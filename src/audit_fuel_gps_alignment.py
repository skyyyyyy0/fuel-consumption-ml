from pathlib import Path
import pandas as pd


EXCEL_DIR = Path("data/raw/Final_Excel_Files")

TRIP_DIR = Path(
    "/Users/haneuljang/Desktop/Geotab/Validation/"
    "geotab_raw_data_inventory/Results/"
    "Trip_Distance/All_Periods"
)

OUTPUT = Path(
    "reports/fuel_gps_alignment_audit.csv"
)

PERIODS = {
    "Before": "2026_Before_Long",
    "After": "2026_After_Long",
    "Final": "2026_Final_Long",
}


# --------------------------------------------------
# Find Excel files
# --------------------------------------------------

excel_files = sorted(
    f for f in EXCEL_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

print("Excel files found:", len(excel_files))


records = []


# --------------------------------------------------
# Process vehicles
# --------------------------------------------------

for vehicle_number, excel_file in enumerate(
    excel_files,
    start=1,
):
    vehicle_id = f"VEH_{vehicle_number:02d}"

    xls = pd.ExcelFile(
        excel_file,
        engine="openpyxl",
    )

    for period, sheet in PERIODS.items():

        print(
            f"Processing {vehicle_id} | {period}"
        )

        if sheet not in xls.sheet_names:
            print("  Missing Excel sheet")
            continue

        # ------------------------------------------
        # Load fuel
        # ------------------------------------------

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet,
            engine="openpyxl",
        )

        fuel = df.loc[
            df["signal_name"] == "Trip fuel used",
            ["vehicle", "datetime", "value"],
        ].copy()

        if fuel.empty:
            print("  No Trip fuel records")
            continue

        private_vehicle = str(
            fuel["vehicle"].dropna().iloc[0]
        )

        fuel["fuel_time"] = pd.to_datetime(
            fuel["datetime"],
            format="mixed",
            utc=True,
            errors="coerce",
        )

        fuel = fuel.dropna(
            subset=["fuel_time"]
        )

        fuel = fuel.sort_values(
            "fuel_time"
        ).reset_index(drop=True)

        # ------------------------------------------
        # Find corresponding GPS file
        # ------------------------------------------

        trip_files = list(
            TRIP_DIR.rglob(
                f"{private_vehicle}_{period.lower()}_trip_detail.csv"
            )
        )

        if len(trip_files) != 1:
            print(
                f"  GPS file matches: {len(trip_files)}"
            )
            continue

        trip_file = trip_files[0]

        trips = pd.read_csv(
            trip_file
        )

        trips["trip_stop"] = pd.to_datetime(
            trips["trip_stop_utc"],
            format="mixed",
            utc=True,
            errors="coerce",
        )

        trips = trips.dropna(
            subset=["trip_stop"]
        )

        trip_stops = (
            trips[["trip_stop"]]
            .sort_values("trip_stop")
            .reset_index(drop=True)
        )

        # ------------------------------------------
        # Nearest stop matching
        # ------------------------------------------

        matched = pd.merge_asof(
            fuel[["fuel_time"]],
            trip_stops,
            left_on="fuel_time",
            right_on="trip_stop",
            direction="nearest",
        )

        matched["diff_sec"] = (
            matched["fuel_time"]
            - matched["trip_stop"]
        ).abs().dt.total_seconds()

        total = len(matched)

        within_5 = int(
            (matched["diff_sec"] <= 5).sum()
        )

        within_10 = int(
            (matched["diff_sec"] <= 10).sum()
        )

        within_30 = int(
            (matched["diff_sec"] <= 30).sum()
        )

        within_60 = int(
            (matched["diff_sec"] <= 60).sum()
        )

        records.append({
            "vehicle_id": vehicle_id,
            "period": period,
            "fuel_records": total,
            "gps_trips": len(trips),
            "median_stop_diff_sec":
                matched["diff_sec"].median(),
            "within_5_sec_pct":
                within_5 / total * 100,
            "within_10_sec_pct":
                within_10 / total * 100,
            "within_30_sec_pct":
                within_30 / total * 100,
            "within_60_sec_pct":
                within_60 / total * 100,
        })


# --------------------------------------------------
# Save results
# --------------------------------------------------

result = pd.DataFrame(records)

result.to_csv(
    OUTPUT,
    index=False,
)


# --------------------------------------------------
# Fleet summary
# --------------------------------------------------

print("\n========================================")
print("Fleet Fuel ↔ GPS Alignment Audit")
print("========================================")

print("Vehicle-periods:", len(result))

print(
    "Total fuel records:",
    result["fuel_records"].sum()
)

print(
    "Total GPS trips:",
    result["gps_trips"].sum()
)

print(
    "\nMedian of group median stop difference:",
    round(
        result["median_stop_diff_sec"].median(),
        3,
    ),
    "seconds",
)

for column in [
    "within_5_sec_pct",
    "within_10_sec_pct",
    "within_30_sec_pct",
    "within_60_sec_pct",
]:
    print(
        column,
        ":",
        round(result[column].mean(), 1),
        "%",
    )


print("\nLowest 30-second match groups:\n")

print(
    result.sort_values(
        "within_30_sec_pct"
    ).head(10).to_string(index=False)
)

print(
    f"\nCreated: {OUTPUT}"
)