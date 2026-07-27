from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw/Final_Excel_Files")

OUTPUT_FILE = Path(
    "reports/state_time_gap_audit.csv"
)

VALID_SPEED_UNIT = "UnitOfMeasureKilometersPerHourId"

files = sorted(
    f for f in RAW_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

records = []


for file_idx, file in enumerate(files, start=1):

    vehicle_id = f"VEH_{file_idx:02d}"

    for period in ["Before", "After", "Final"]:

        sheet = f"2026_{period}_Long"

        print(f"Reading {vehicle_id} | {period}")

        df = pd.read_excel(
            file,
            sheet_name=sheet,
            engine="openpyxl",
            usecols=[
                "datetime",
                "signal_name",
                "value",
                "unit",
            ],
        )

        df["timestamp"] = pd.to_datetime(
            df["datetime"],
            format="mixed",
            utc=True,
            errors="coerce",
        )

        speed = df[
            (df["signal_name"] == "Engine road speed")
            & (df["unit"] == VALID_SPEED_UNIT)
        ][["timestamp", "value"]].copy()

        speed["speed_kmh"] = pd.to_numeric(
            speed["value"],
            errors="coerce",
        )

        speed = (
            speed
            .dropna(subset=["timestamp", "speed_kmh"])
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        if len(speed) < 2:
            continue

        speed["gap_sec"] = (
            speed["timestamp"]
            .diff()
            .dt.total_seconds()
        )

        gaps = speed["gap_sec"].dropna()

        if gaps.empty:
            continue

        records.append({
            "vehicle_id": vehicle_id,
            "period": period,
            "speed_events": len(speed),

            "gap_p50_sec": gaps.quantile(0.50),
            "gap_p75_sec": gaps.quantile(0.75),
            "gap_p90_sec": gaps.quantile(0.90),
            "gap_p95_sec": gaps.quantile(0.95),
            "gap_p99_sec": gaps.quantile(0.99),

            "max_gap_sec": gaps.max(),

            "gap_gt_10_sec_pct":
                (gaps > 10).mean() * 100,

            "gap_gt_30_sec_pct":
                (gaps > 30).mean() * 100,

            "gap_gt_60_sec_pct":
                (gaps > 60).mean() * 100,

            "gap_gt_300_sec_pct":
                (gaps > 300).mean() * 100,
        })


result = pd.DataFrame(records)

result.to_csv(
    OUTPUT_FILE,
    index=False,
)


print("\n========================================")
print("State Time Gap Audit")
print("========================================")

print("Vehicle-periods:", len(result))

print("\nMedian fleet percentiles:")

for col in [
    "gap_p50_sec",
    "gap_p75_sec",
    "gap_p90_sec",
    "gap_p95_sec",
    "gap_p99_sec",
]:

    print(
        col,
        ":",
        round(result[col].median(), 3),
        "sec"
    )


print("\nAverage gap exceedance:")

for col in [
    "gap_gt_10_sec_pct",
    "gap_gt_30_sec_pct",
    "gap_gt_60_sec_pct",
    "gap_gt_300_sec_pct",
]:

    print(
        col,
        ":",
        round(result[col].mean(), 2),
        "%"
    )


print("\nLargest P95 groups:\n")

print(
    result.sort_values(
        "gap_p95_sec",
        ascending=False
    )[
        [
            "vehicle_id",
            "period",
            "speed_events",
            "gap_p50_sec",
            "gap_p90_sec",
            "gap_p95_sec",
            "gap_p99_sec",
            "max_gap_sec",
        ]
    ]
    .head(12)
    .to_string(index=False)
)


print(f"\nCreated: {OUTPUT_FILE}")