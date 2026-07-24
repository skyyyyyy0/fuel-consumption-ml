from pathlib import Path
import re

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

RAW_DIR = Path("data/raw/Final_Excel_Files")

OUTPUT_FILE = Path(
    "reports/data_structure_audit.csv"
)

SHEET_PATTERN = re.compile(
    r"^2026_(?P<period>Before|After|Final)_Long$"
)

excel_files = sorted(
    f for f in RAW_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

vehicle_map = {
    file.name: f"VEH_{idx:02d}"
    for idx, file in enumerate(excel_files, start=1)
}

records = []


# --------------------------------------------------
# Process each vehicle / period
# --------------------------------------------------

for file in excel_files:

    vehicle_id = vehicle_map[file.name]

    xls = pd.ExcelFile(
        file,
        engine="openpyxl",
    )

    for sheet_name in xls.sheet_names:

        match = SHEET_PATTERN.match(sheet_name)

        if not match:
            continue

        period = match.group("period")

        print(
            f"Reading {vehicle_id} | {sheet_name}"
        )

        df = pd.read_excel(
            file,
            sheet_name=sheet_name,
            engine="openpyxl",
        )

        # ------------------------------------------
        # Parse timestamps
        # ------------------------------------------

        df["datetime_utc"] = pd.to_datetime(
            df["datetime"],
            format="mixed",
            utc=True,
            errors="coerce",
        )

        df["datetime_kst"] = pd.to_datetime(
            df["datetime_kst_excel"],
            format="mixed",
            errors="coerce",
        )

        # ------------------------------------------
        # Missing timestamps
        # ------------------------------------------

        missing_utc = int(
            df["datetime_utc"].isna().sum()
        )

        missing_kst = int(
            df["datetime_kst"].isna().sum()
        )

        # ------------------------------------------
        # Duplicate records
        # ------------------------------------------

        duplicate_count = int(
            df.duplicated(
                subset=[
                    "datetime",
                    "signal_name",
                    "value",
                    "unit",
                ]
            ).sum()
        )

        # ------------------------------------------
        # Timestamp ordering
        # ------------------------------------------

        utc_valid = df[
            "datetime_utc"
        ].dropna()

        timestamp_order_violations = int(
            (
                utc_valid.diff()
                .dropna()
                < pd.Timedelta(0)
            ).sum()
        )

        # ------------------------------------------
        # UTC → KST consistency
        # ------------------------------------------

        compare = df[
            ["datetime_utc", "datetime_kst"]
        ].dropna().copy()

        if not compare.empty:

            expected_kst = (
                compare["datetime_utc"]
                .dt.tz_convert("Asia/Seoul")
                .dt.tz_localize(None)
            )

            kst_diff_sec = (
                expected_kst
                - compare["datetime_kst"]
            ).abs().dt.total_seconds()

            kst_mismatch_count = int(
                (kst_diff_sec > 1).sum()
            )

            max_kst_diff_sec = float(
                kst_diff_sec.max()
            )

        else:

            kst_mismatch_count = None
            max_kst_diff_sec = None

        # ------------------------------------------
        # Signal-level sampling gaps
        # ------------------------------------------

        max_gap_sec = 0
        gap_gt_5_min_count = 0
        gap_gt_30_min_count = 0
        gap_gt_2_hr_count = 0

        for _, signal_group in df.groupby(
            "signal_name"
        ):

            times = (
                signal_group["datetime_utc"]
                .dropna()
                .sort_values()
            )

            if len(times) < 2:
                continue

            gaps = (
                times.diff()
                .dropna()
                .dt.total_seconds()
            )

            if len(gaps) == 0:
                continue

            max_gap_sec = max(
                max_gap_sec,
                float(gaps.max()),
            )

            gap_gt_5_min_count += int(
                (gaps > 300).sum()
            )

            gap_gt_30_min_count += int(
                (gaps > 1800).sum()
            )

            gap_gt_2_hr_count += int(
                (gaps > 7200).sum()
            )

        # ------------------------------------------
        # Outside temperature
        # ------------------------------------------

        temp = df[
            df["signal_name"]
            == "Outside air temperature"
        ].copy()

        temp_values = pd.to_numeric(
            temp["value"],
            errors="coerce",
        ).dropna()

        if len(temp_values) > 0:

            temp_min = float(
                temp_values.min()
            )

            temp_max = float(
                temp_values.max()
            )

            temp_lt_minus_30 = int(
                (temp_values < -30).sum()
            )

            temp_gt_60 = int(
                (temp_values > 60).sum()
            )

        else:

            temp_min = None
            temp_max = None
            temp_lt_minus_30 = None
            temp_gt_60 = None

        # ------------------------------------------
        # Save
        # ------------------------------------------

        records.append({
            "vehicle_id": vehicle_id,
            "period": period,
            "row_count": len(df),

            "missing_utc_timestamp": missing_utc,
            "missing_kst_timestamp": missing_kst,

            "duplicate_count": duplicate_count,
            "timestamp_order_violations":
                timestamp_order_violations,

            "kst_mismatch_count":
                kst_mismatch_count,

            "max_kst_diff_sec":
                max_kst_diff_sec,

            "max_signal_gap_sec":
                max_gap_sec,

            "gap_gt_5_min_count":
                gap_gt_5_min_count,

            "gap_gt_30_min_count":
                gap_gt_30_min_count,

            "gap_gt_2_hr_count":
                gap_gt_2_hr_count,

            "outside_temp_min":
                temp_min,

            "outside_temp_max":
                temp_max,

            "outside_temp_lt_minus_30":
                temp_lt_minus_30,

            "outside_temp_gt_60":
                temp_gt_60,
        })


# --------------------------------------------------
# Save result
# --------------------------------------------------

result = pd.DataFrame(records)

result.to_csv(
    OUTPUT_FILE,
    index=False,
)


# --------------------------------------------------
# Fleet summary
# --------------------------------------------------

print("\n========================================")
print("Data Structure Audit Completed")
print("========================================")

print(
    "Vehicle-periods:",
    len(result),
)

print(
    "Total rows:",
    f"{result['row_count'].sum():,}",
)

print(
    "Duplicate records:",
    int(result["duplicate_count"].sum()),
)

print(
    "Timestamp order violations:",
    int(
        result[
            "timestamp_order_violations"
        ].sum()
    ),
)

print(
    "UTC/KST mismatches:",
    int(
        result[
            "kst_mismatch_count"
        ].fillna(0).sum()
    ),
)

print(
    "Missing UTC timestamps:",
    int(
        result[
            "missing_utc_timestamp"
        ].sum()
    ),
)

print(
    "Missing KST timestamps:",
    int(
        result[
            "missing_kst_timestamp"
        ].sum()
    ),
)

print(
    "Gaps > 5 min:",
    int(
        result[
            "gap_gt_5_min_count"
        ].sum()
    ),
)

print(
    "Gaps > 30 min:",
    int(
        result[
            "gap_gt_30_min_count"
        ].sum()
    ),
)

print(
    "Gaps > 2 hr:",
    int(
        result[
            "gap_gt_2_hr_count"
        ].sum()
    ),
)

print("\nLargest signal-gap groups:\n")

print(
    result.sort_values(
        "max_signal_gap_sec",
        ascending=False,
    )[
        [
            "vehicle_id",
            "period",
            "max_signal_gap_sec",
            "gap_gt_30_min_count",
            "gap_gt_2_hr_count",
            "duplicate_count",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nOutside temperature ranges:\n")

temp_summary = result[
    result["outside_temp_min"].notna()
][
    [
        "vehicle_id",
        "period",
        "outside_temp_min",
        "outside_temp_max",
        "outside_temp_lt_minus_30",
        "outside_temp_gt_60",
    ]
]

if temp_summary.empty:
    print("No outside temperature data.")
else:
    print(
        temp_summary.to_string(
            index=False
        )
    )

print(
    f"\nCreated: {OUTPUT_FILE}"
)