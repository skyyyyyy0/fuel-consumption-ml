from pathlib import Path
import re

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

RAW_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_DIR = Path("reports")
OUTPUT_FILE = OUTPUT_DIR / "signal_value_audit.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_SIGNALS = [
    "Engine speed",
    "Engine road speed",
    "Trip fuel used",
    "Total fuel used (since telematics device install)",
    "Ignition",
    "Vehicle active (idle or driving)",
]

# Primary ML dataset only
SHEET_PATTERN = re.compile(
    r"^2026_(?P<period>Before|After|Final)_Long$"
)


# --------------------------------------------------
# Find files
# --------------------------------------------------

excel_files = sorted(
    f for f in RAW_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

vehicle_map = {
    file.name: f"VEH_{idx:02d}"
    for idx, file in enumerate(excel_files, start=1)
}


# --------------------------------------------------
# Read telemetry
# --------------------------------------------------

records = []

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
            usecols=[
                "signal_name",
                "value",
                "unit",
            ],
        )

        df["signal_name"] = (
            df["signal_name"]
            .astype("string")
            .str.strip()
        )

        df = df[
            df["signal_name"].isin(TARGET_SIGNALS)
        ].copy()

        for signal, group in df.groupby("signal_name"):

            numeric = pd.to_numeric(
                group["value"],
                errors="coerce",
            )

            total_rows = len(group)

            numeric_rows = numeric.notna().sum()

            non_numeric_rows = (
                total_rows - numeric_rows
            )

            valid_numeric = numeric.dropna()

            if len(valid_numeric) > 0:

                min_value = valid_numeric.min()
                max_value = valid_numeric.max()
                mean_value = valid_numeric.mean()
                median_value = valid_numeric.median()

                zero_count = (
                    valid_numeric == 0
                ).sum()

                negative_count = (
                    valid_numeric < 0
                ).sum()

            else:

                min_value = None
                max_value = None
                mean_value = None
                median_value = None
                zero_count = None
                negative_count = None

            units = (
                group["unit"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
            )

            unit = (
                " | ".join(sorted(units))
                if len(units) > 0
                else None
            )

            records.append(
                {
                    "vehicle_id": vehicle_id,
                    "period": period,
                    "signal": signal,

                    "row_count": total_rows,

                    "numeric_rows": int(
                        numeric_rows
                    ),

                    "non_numeric_rows": int(
                        non_numeric_rows
                    ),

                    "min": min_value,
                    "max": max_value,
                    "mean": mean_value,
                    "median": median_value,

                    "zero_count": zero_count,
                    "negative_count": negative_count,

                    "unit": unit,
                }
            )


# --------------------------------------------------
# Save detailed audit
# --------------------------------------------------

result = pd.DataFrame(records)

result = result.sort_values(
    [
        "signal",
        "vehicle_id",
        "period",
    ]
).reset_index(drop=True)

result.to_csv(
    OUTPUT_FILE,
    index=False,
)


# --------------------------------------------------
# Fleet-level summary
# --------------------------------------------------

print("\n----------------------------------------")
print("2026 Signal Value Audit Completed")
print("----------------------------------------")

print(f"Created: {OUTPUT_FILE}")

print("\nFleet-level numeric summary:\n")

for signal in TARGET_SIGNALS:

    signal_df = result[
        result["signal"] == signal
    ]

    if signal_df.empty:
        print(f"\n{signal}: NOT FOUND")
        continue

    print(f"\n{signal}")
    print(
        "Vehicle-periods:",
        len(signal_df)
    )

    print(
        "Total rows:",
        f"{signal_df['row_count'].sum():,}"
    )

    print(
        "Non-numeric rows:",
        f"{signal_df['non_numeric_rows'].sum():,}"
    )

    if signal_df["min"].notna().any():

        print(
            "Overall min:",
            signal_df["min"].min()
        )

        print(
            "Overall max:",
            signal_df["max"].max()
        )

        print(
            "Negative values:",
            int(
                signal_df[
                    "negative_count"
                ].fillna(0).sum()
            )
        )

        print(
            "Zero values:",
            int(
                signal_df[
                    "zero_count"
                ].fillna(0).sum()
            )
        )

    units = (
        signal_df["unit"]
        .dropna()
        .unique()
    )

    print(
        "Units:",
        list(units)
    )