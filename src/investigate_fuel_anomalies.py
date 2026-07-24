from pathlib import Path
import re
import pandas as pd


RAW_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_FILE = Path("reports/fuel_anomaly_audit.csv")

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

    for sheet_name in xls.sheet_names:

        match = SHEET_PATTERN.match(sheet_name)

        if not match:
            continue

        period = match.group("period")

        print(f"Reading {vehicle_id} | {sheet_name}")

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

        fuel = df[
            df["signal_name"] == "Trip fuel used"
        ].copy()

        if fuel.empty:
            continue

        fuel["value"] = pd.to_numeric(
            fuel["value"],
            errors="coerce"
        )

        values = fuel["value"].dropna()

        records.append({
            "vehicle_id": vehicle_id,
            "period": period,
            "row_count": len(values),

            "min_fuel": values.min(),
            "max_fuel": values.max(),
            "mean_fuel": values.mean(),
            "median_fuel": values.median(),

            "zero_count": int((values == 0).sum()),
            "negative_count": int((values < 0).sum()),

            "fuel_gt_10": int((values > 10).sum()),
            "fuel_gt_20": int((values > 20).sum()),
            "fuel_gt_50": int((values > 50).sum()),
        })


result = pd.DataFrame(records)

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n----------------------------------------")
print("Fuel Anomaly Investigation Completed")
print("----------------------------------------")

print("Overall min:", result["min_fuel"].min())
print("Overall max:", result["max_fuel"].max())

print("Zero values:", result["zero_count"].sum())
print("Negative values:", result["negative_count"].sum())

print("Fuel > 10 L:", result["fuel_gt_10"].sum())
print("Fuel > 20 L:", result["fuel_gt_20"].sum())
print("Fuel > 50 L:", result["fuel_gt_50"].sum())

print("\nHighest fuel groups:\n")

print(
    result.sort_values(
        "max_fuel",
        ascending=False
    )[
        [
            "vehicle_id",
            "period",
            "row_count",
            "min_fuel",
            "max_fuel",
            "mean_fuel",
            "median_fuel",
            "fuel_gt_10",
            "fuel_gt_20",
            "fuel_gt_50",
        ]
    ]
    .head(15)
    .to_string(index=False)
)