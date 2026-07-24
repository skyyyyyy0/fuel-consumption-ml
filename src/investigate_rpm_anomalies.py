from pathlib import Path
import re
import pandas as pd


RAW_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_FILE = Path("reports/rpm_anomaly_audit.csv")

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

        rpm = df[
            df["signal_name"] == "Engine speed"
        ].copy()

        if rpm.empty:
            continue

        rpm["value"] = pd.to_numeric(
            rpm["value"],
            errors="coerce"
        )

        values = rpm["value"].dropna()

        records.append({
            "vehicle_id": vehicle_id,
            "period": period,
            "row_count": len(values),

            "min_rpm": values.min(),
            "max_rpm": values.max(),
            "mean_rpm": values.mean(),
            "median_rpm": values.median(),

            "zero_count": int((values == 0).sum()),
            "negative_count": int((values < 0).sum()),

            "rpm_gt_3000": int((values > 3000).sum()),
            "rpm_gt_4000": int((values > 4000).sum()),
            "rpm_gt_5000": int((values > 5000).sum()),
        })


result = pd.DataFrame(records)

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n----------------------------------------")
print("RPM Anomaly Investigation Completed")
print("----------------------------------------")

print("Overall min:", result["min_rpm"].min())
print("Overall max:", result["max_rpm"].max())

print(
    "Zero RPM:",
    result["zero_count"].sum()
)

print(
    "Negative RPM:",
    result["negative_count"].sum()
)

print(
    "RPM > 3000:",
    result["rpm_gt_3000"].sum()
)

print(
    "RPM > 4000:",
    result["rpm_gt_4000"].sum()
)

print(
    "RPM > 5000:",
    result["rpm_gt_5000"].sum()
)

print("\nHighest RPM groups:\n")

print(
    result.sort_values(
        "max_rpm",
        ascending=False
    )[
        [
            "vehicle_id",
            "period",
            "max_rpm",
            "mean_rpm",
            "rpm_gt_3000",
            "rpm_gt_4000",
        ]
    ]
    .head(15)
    .to_string(index=False)
)