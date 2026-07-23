from pathlib import Path
import re

import pandas as pd


# --------------------------------------------------
# Paths
# --------------------------------------------------

RAW_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_DIR = Path("reports")
OUTPUT_FILE = OUTPUT_DIR / "signal_inventory_raw.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Find Excel files
# --------------------------------------------------

# Excel temporary files (~$...) are excluded.
excel_files = sorted(
    file
    for file in RAW_DIR.glob("*.xlsx")
    if not file.name.startswith("~$")
)

if not excel_files:
    raise FileNotFoundError(
        f"No Excel files were found in: {RAW_DIR.resolve()}"
    )


# --------------------------------------------------
# Vehicle anonymization
# --------------------------------------------------

vehicle_map = {
    file.name: f"VEH_{idx:02d}"
    for idx, file in enumerate(excel_files, start=1)
}


# --------------------------------------------------
# Long-sheet pattern
# --------------------------------------------------

sheet_pattern = re.compile(
    r"^(?P<year>2025|2026)_(?P<period>Before|After|Final)_Long$"
)


# --------------------------------------------------
# Build signal inventory
# --------------------------------------------------

records = []

for file in excel_files:
    vehicle_id = vehicle_map[file.name]

    try:
        xls = pd.ExcelFile(file, engine="openpyxl")
    except Exception as exc:
        print(f"ERROR opening {vehicle_id}: {exc}")
        continue

    for sheet_name in xls.sheet_names:
        match = sheet_pattern.match(sheet_name)

        if not match:
            continue

        year = int(match.group("year"))
        period = match.group("period")

        print(f"Reading {vehicle_id} | {sheet_name}")

        try:
            df = pd.read_excel(
                file,
                sheet_name=sheet_name,
                engine="openpyxl",
            )
        except Exception as exc:
            print(
                f"WARNING: Could not read "
                f"{vehicle_id} | {sheet_name}: {exc}"
            )
            continue

        # --------------------------------------------------
        # Validate required Long-table columns
        # --------------------------------------------------

        required_columns = {
            "signal_name",
            "value",
            "unit",
        }

        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            print(
                f"WARNING: Missing columns in "
                f"{vehicle_id} | {sheet_name}: "
                f"{sorted(missing_columns)}"
            )
            print("Available columns:", list(df.columns))
            continue

        # --------------------------------------------------
        # Clean signal names
        # --------------------------------------------------

        df["signal_name"] = (
            df["signal_name"]
            .astype("string")
            .str.strip()
        )

        valid_signal_rows = df["signal_name"].notna()

        signal_df = df.loc[
            valid_signal_rows,
            ["signal_name", "value", "unit"]
        ].copy()

        if signal_df.empty:
            print(
                f"WARNING: No signal records found in "
                f"{vehicle_id} | {sheet_name}"
            )
            continue

        # --------------------------------------------------
        # Summarize each signal
        # --------------------------------------------------

        for signal_name, group in signal_df.groupby(
            "signal_name",
            dropna=True,
        ):
            row_count = len(group)

            missing_value_count = group["value"].isna().sum()

            missing_pct = (
                missing_value_count / row_count * 100
                if row_count > 0
                else None
            )

            # Detect available units.
            units = (
                group["unit"]
                .dropna()
                .astype(str)
                .str.strip()
                .replace("", pd.NA)
                .dropna()
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
                    "year": year,
                    "period": period,
                    "signal": signal_name,
                    "row_count": int(row_count),
                    "missing_value_count": int(
                        missing_value_count
                    ),
                    "missing_pct": round(
                        float(missing_pct), 4
                    ),
                    "unit": unit,
                }
            )


# --------------------------------------------------
# Create output
# --------------------------------------------------

result = pd.DataFrame(records)

if result.empty:
    raise ValueError(
        "No signals were found. "
        "Check the Long dataset structure."
    )

result = result.sort_values(
    [
        "vehicle_id",
        "year",
        "period",
        "signal",
    ]
).reset_index(drop=True)

result.to_csv(
    OUTPUT_FILE,
    index=False,
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n----------------------------------------")
print("Signal Inventory Completed")
print("----------------------------------------")

print(f"Created: {OUTPUT_FILE}")
print(
    f"Vehicles found: "
    f"{result['vehicle_id'].nunique()}"
)
print(
    f"Inventory rows: "
    f"{len(result):,}"
)
print(
    f"Unique signals: "
    f"{result['signal'].nunique()}"
)

print("\nUnique signal names:")

for signal in sorted(result["signal"].unique()):
    print(f"- {signal}")

print("\nSignal vehicle coverage:")

coverage = (
    result.groupby("signal")["vehicle_id"]
    .nunique()
    .sort_values(ascending=False)
)

for signal, vehicle_count in coverage.items():
    print(
        f"- {signal}: "
        f"{vehicle_count}/"
        f"{result['vehicle_id'].nunique()} vehicles"
    )