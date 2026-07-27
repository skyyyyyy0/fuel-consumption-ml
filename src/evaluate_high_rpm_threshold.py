from pathlib import Path
import pandas as pd


EXCEL_DIR = Path("data/raw/Final_Excel_Files")

THRESHOLDS = [
    2500,
    3000,
    3500,
    4000,
]

excel_files = sorted(
    f for f in EXCEL_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

records = []

for idx, file in enumerate(
    excel_files,
    start=1,
):
    vehicle_id = f"VEH_{idx:02d}"

    for period in [
        "Before",
        "After",
        "Final",
    ]:

        sheet = f"2026_{period}_Long"

        print(
            f"Reading {vehicle_id} | {period}"
        )

        df = pd.read_excel(
            file,
            sheet_name=sheet,
            engine="openpyxl",
            usecols=[
                "signal_name",
                "value",
            ],
        )

        rpm = pd.to_numeric(
            df.loc[
                df["signal_name"] == "Engine speed",
                "value",
            ],
            errors="coerce",
        ).dropna()

        if rpm.empty:
            continue

        row = {
            "vehicle_id": vehicle_id,
            "period": period,
            "rpm_count": len(rpm),
            "mean_rpm": rpm.mean(),
            "p90_rpm": rpm.quantile(0.90),
            "p95_rpm": rpm.quantile(0.95),
            "p99_rpm": rpm.quantile(0.99),
            "max_rpm": rpm.max(),
        }

        for threshold in THRESHOLDS:
            row[
                f"pct_gt_{threshold}"
            ] = (
                (rpm > threshold).mean()
                * 100
            )

        records.append(row)


result = pd.DataFrame(records)

print("\n========================================")
print("High RPM Threshold Evaluation")
print("========================================")

print("\nFleet percentile summary:")

for col in [
    "mean_rpm",
    "p90_rpm",
    "p95_rpm",
    "p99_rpm",
    "max_rpm",
]:
    print(
        col,
        ":",
        round(result[col].median(), 1)
    )


print("\nAverage percentage above threshold:")

for threshold in THRESHOLDS:

    column = f"pct_gt_{threshold}"

    print(
        f"> {threshold} RPM:",
        f"{result[column].mean():.2f}%"
    )


print("\nVehicle-level >3000 RPM rate:")

vehicle_summary = (
    result.groupby("vehicle_id")
    ["pct_gt_3000"]
    .mean()
    .sort_values(ascending=False)
)

print(
    vehicle_summary.round(2).to_string()
)