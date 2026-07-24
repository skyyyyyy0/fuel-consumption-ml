from pathlib import Path
import re

import pandas as pd


RAW_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_FILE = Path("reports/duplicate_audit.csv")

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

for file in excel_files:

    vehicle_id = vehicle_map[file.name]
    xls = pd.ExcelFile(file, engine="openpyxl")

    for sheet in xls.sheet_names:

        match = SHEET_PATTERN.match(sheet)

        if not match:
            continue

        period = match.group("period")

        print(f"Reading {vehicle_id} | {period}")

        df = pd.read_excel(
            file,
            sheet_name=sheet,
            engine="openpyxl",
        )

        duplicate_mask = df.duplicated(
            subset=[
                "datetime",
                "signal_name",
                "value",
                "unit",
            ],
            keep=False,
        )

        dup = df[duplicate_mask].copy()

        if dup.empty:
            continue

        summary = (
            dup.groupby("signal_name")
            .size()
            .reset_index(name="duplicate_rows")
        )

        for _, row in summary.iterrows():

            records.append({
                "vehicle_id": vehicle_id,
                "period": period,
                "signal": row["signal_name"],
                "duplicate_rows": int(
                    row["duplicate_rows"]
                ),
            })


result = pd.DataFrame(records)

result.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n========================================")
print("Duplicate Investigation")
print("========================================")

if result.empty:

    print("No duplicate records found.")

else:

    print("\nDuplicates by signal:\n")

    print(
        result.groupby("signal")["duplicate_rows"]
        .sum()
        .sort_values(ascending=False)
        .to_string()
    )

    print("\nLargest duplicate groups:\n")

    print(
        result.sort_values(
            "duplicate_rows",
            ascending=False,
        )
        .head(20)
        .to_string(index=False)
    )

print(f"\nCreated: {OUTPUT_FILE}")