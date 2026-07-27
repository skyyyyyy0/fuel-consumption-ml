from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/Final_Excel_Files")

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

        df["datetime"] = pd.to_datetime(
            df["datetime"],
            format="mixed",
            utc=True,
            errors="coerce",
        )

        df["value"] = pd.to_numeric(
            df["value"],
            errors="coerce",
        )

        # ---------------------------------------------
        # Speed
        # ---------------------------------------------

        speed = df[
            (df["signal_name"] == "Engine road speed")
            & (
                df["unit"]
                == "UnitOfMeasureKilometersPerHourId"
            )
        ][["datetime", "value"]].copy()

        speed = speed.rename(
            columns={
                "datetime": "speed_time",
                "value": "speed_kmh",
            }
        )

        # We care primarily about near-zero speed states.
        speed = speed[
            speed["speed_kmh"] < 1
        ].copy()

        # ---------------------------------------------
        # RPM
        # ---------------------------------------------

        rpm = df[
            df["signal_name"] == "Engine speed"
        ][["datetime", "value"]].copy()

        rpm = rpm.rename(
            columns={
                "datetime": "rpm_time",
                "value": "rpm",
            }
        )

        speed = speed.dropna().sort_values("speed_time")
        rpm = rpm.dropna().sort_values("rpm_time")

        if speed.empty or rpm.empty:
            continue

        # ---------------------------------------------
        # Match each zero-speed event to nearest RPM
        # ---------------------------------------------

        matched = pd.merge_asof(
            speed,
            rpm,
            left_on="speed_time",
            right_on="rpm_time",
            direction="nearest",
        )

        matched["time_diff_sec"] = (
            matched["speed_time"]
            - matched["rpm_time"]
        ).abs().dt.total_seconds()

        record = {
            "vehicle_id": vehicle_id,
            "period": period,

            "zero_speed_events": len(matched),

            "median_rpm_diff_sec":
                matched["time_diff_sec"].median(),

            "within_1_sec_pct":
                (matched["time_diff_sec"] <= 1).mean() * 100,

            "within_5_sec_pct":
                (matched["time_diff_sec"] <= 5).mean() * 100,

            "within_10_sec_pct":
                (matched["time_diff_sec"] <= 10).mean() * 100,

            "within_30_sec_pct":
                (matched["time_diff_sec"] <= 30).mean() * 100,

            "rpm_gt_500_pct":
                (matched["rpm"] > 500).mean() * 100,
        }

        records.append(record)


result = pd.DataFrame(records)

output = Path(
    "reports/idle_signal_alignment_audit.csv"
)

result.to_csv(output, index=False)


print("\n========================================")
print("Idle Signal Alignment Audit")
print("========================================")

print("Vehicle-periods:", len(result))

if not result.empty:

    print(
        "\nTotal zero-speed observations:",
        result["zero_speed_events"].sum(),
    )

    print(
        "\nMedian of group median RPM differences:",
        round(
            result["median_rpm_diff_sec"].median(),
            3
        ),
        "seconds",
    )

    for col in [
        "within_1_sec_pct",
        "within_5_sec_pct",
        "within_10_sec_pct",
        "within_30_sec_pct",
        "rpm_gt_500_pct",
    ]:

        print(
            f"{col}:",
            round(result[col].mean(), 2),
            "%",
        )

    print("\nLowest alignment groups:")

    print(
        result.sort_values(
            "within_10_sec_pct"
        )[
            [
                "vehicle_id",
                "period",
                "zero_speed_events",
                "median_rpm_diff_sec",
                "within_5_sec_pct",
                "within_10_sec_pct",
                "within_30_sec_pct",
                "rpm_gt_500_pct",
            ]
        ]
        .head(12)
        .to_string(index=False)
    )

print(f"\nCreated: {output}")