from pathlib import Path
import pandas as pd


EXCEL_DIR = Path("data/raw/Final_Excel_Files")

TRIP_DIR = Path(
    "/Users/haneuljang/Desktop/Geotab/Validation/"
    "geotab_raw_data_inventory/Results/"
    "Trip_Distance/All_Periods"
)

OUTPUT_FILE = Path(
    "reports/trip_target_fleet_audit.csv"
)

PERIODS = {
    "Before": "2026_Before_Long",
    "After": "2026_After_Long",
    "Final": "2026_Final_Long",
}

MAX_MATCH_SEC = 60


excel_files = sorted(
    f for f in EXCEL_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

records = []


for idx, excel_file in enumerate(
    excel_files,
    start=1,
):
    vehicle_id = f"VEH_{idx:02d}"

    xls = pd.ExcelFile(
        excel_file,
        engine="openpyxl",
    )

    for period, sheet_name in PERIODS.items():

        print(f"Processing {vehicle_id} | {period}")

        # ------------------------------------------
        # Fuel
        # ------------------------------------------

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            engine="openpyxl",
        )

        fuel = df.loc[
            df["signal_name"] == "Trip fuel used",
            ["vehicle", "datetime", "value"],
        ].copy()

        actual_vehicle = str(
            fuel["vehicle"]
            .dropna()
            .iloc[0]
        )

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

        # ------------------------------------------
        # GPS trip file
        # ------------------------------------------

        matches = list(
            TRIP_DIR.rglob(
                f"{actual_vehicle}_"
                f"{period.lower()}_trip_detail.csv"
            )
        )

        if len(matches) != 1:
            print(
                f"  WARNING: GPS files found = {len(matches)}"
            )
            continue

        trips = pd.read_csv(matches[0])

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
            .dropna()
            .sort_values("trip_stop")
            .reset_index(drop=True)
        )

        # ------------------------------------------
        # Initial nearest match
        # ------------------------------------------

        matched = pd.merge_asof(
            trips,
            fuel,
            left_on="trip_stop",
            right_on="fuel_time",
            direction="nearest",
            tolerance=pd.Timedelta(
                seconds=MAX_MATCH_SEC
            ),
        )

        matched["diff_sec"] = (
            matched["fuel_time"]
            - matched["trip_stop"]
        ).abs().dt.total_seconds()

        # ------------------------------------------
        # Trip validity
        # ------------------------------------------

        matched["trip_valid"] = (
            matched["distance_km"] > 0
        )

        matched["very_short"] = (
            (matched["distance_km"] > 0)
            & (matched["distance_km"] < 0.1)
        )

        # ------------------------------------------
        # One fuel record can only be used once
        # ------------------------------------------

        candidates = matched[
            matched["fuel_time"].notna()
        ].copy()

        # Valid trip first, then smallest time difference.
        candidates["valid_priority"] = (
            candidates["trip_valid"]
            .astype(int)
        )

        candidates = candidates.sort_values(
            [
                "fuel_time",
                "valid_priority",
                "diff_sec",
            ],
            ascending=[
                True,
                False,
                True,
            ],
        )

        candidates["fuel_rank"] = (
            candidates
            .groupby("fuel_time")
            .cumcount()
            + 1
        )

        matched["selected"] = False

        selected_indices = candidates.loc[
            candidates["fuel_rank"] == 1
        ].index

        matched.loc[
            selected_indices,
            "selected"
        ] = True

        # ------------------------------------------
        # Match status
        # ------------------------------------------

        matched["match_status"] = "Unmatched"

        matched.loc[
            matched["selected"]
            & (matched["diff_sec"] <= 30),
            "match_status",
        ] = "High"

        matched.loc[
            matched["selected"]
            & (matched["diff_sec"] > 30)
            & (matched["diff_sec"] <= 60),
            "match_status",
        ] = "Review"

        matched.loc[
            matched["fuel_time"].notna()
            & (~matched["selected"]),
            "match_status",
        ] = "Rejected Duplicate"

        # ------------------------------------------
        # Summary
        # ------------------------------------------

        total_trips = len(matched)

        high = int(
            (matched["match_status"] == "High").sum()
        )

        review = int(
            (matched["match_status"] == "Review").sum()
        )

        unmatched = int(
            (matched["match_status"] == "Unmatched").sum()
        )

        rejected_duplicate = int(
            (
                matched["match_status"]
                == "Rejected Duplicate"
            ).sum()
        )

        zero_distance = int(
            (matched["distance_km"] <= 0).sum()
        )

        very_short = int(
            matched["very_short"].sum()
        )

        usable = int(
            (
                (matched["match_status"] == "High")
                & matched["trip_valid"]
            ).sum()
        )

        records.append({
            "vehicle_id": vehicle_id,
            "period": period,
            "gps_trips": total_trips,
            "fuel_records": len(fuel),
            "high_matches": high,
            "review_matches": review,
            "unmatched": unmatched,
            "rejected_duplicate": rejected_duplicate,
            "zero_distance_trips": zero_distance,
            "very_short_trips": very_short,
            "usable_high_confidence_trips": usable,
            "usable_rate_pct": (
                usable / total_trips * 100
                if total_trips > 0
                else 0
            ),
        })


result = pd.DataFrame(records)

result.to_csv(
    OUTPUT_FILE,
    index=False,
)


print("\n========================================")
print("Fleet Trip Target Audit")
print("========================================")

print("Vehicle-periods:", len(result))

print(
    "Total GPS trips:",
    int(result["gps_trips"].sum())
)

print(
    "Total fuel records:",
    int(result["fuel_records"].sum())
)

print(
    "High matches:",
    int(result["high_matches"].sum())
)

print(
    "Review matches:",
    int(result["review_matches"].sum())
)

print(
    "Rejected duplicate:",
    int(result["rejected_duplicate"].sum())
)

print(
    "Unmatched:",
    int(result["unmatched"].sum())
)

print(
    "Zero-distance trips:",
    int(result["zero_distance_trips"].sum())
)

print(
    "Very-short trips:",
    int(result["very_short_trips"].sum())
)

print(
    "Usable high-confidence trips:",
    int(
        result[
            "usable_high_confidence_trips"
        ].sum()
    )
)

overall_rate = (
    result[
        "usable_high_confidence_trips"
    ].sum()
    / result["gps_trips"].sum()
    * 100
)

print(
    "Overall usable rate:",
    f"{overall_rate:.1f}%"
)

print("\nLowest usable-rate groups:\n")

print(
    result.sort_values(
        "usable_rate_pct"
    )
    .head(10)
    .to_string(index=False)
)

print(
    f"\nCreated: {OUTPUT_FILE}"
)