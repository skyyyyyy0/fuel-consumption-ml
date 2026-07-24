from pathlib import Path
import re

import pandas as pd


RAW_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_DIR = Path("reports")
OUTPUT_FILE = OUTPUT_DIR / "speed_anomaly_audit.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SHEET_PATTERN = re.compile(
    r"^2026_(?P<period>Before|After|Final)_Long$"
)

# 아직 cleaning threshold가 아니라 조사용 기준
SUSPICIOUS_SPEED = 160


# --------------------------------------------------
# Find Excel files
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
# Investigate Engine Road Speed
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

        print(f"Reading {vehicle_id} | {sheet_name}")

        df = pd.read_excel(
            file,
            sheet_name=sheet_name,
            engine="openpyxl",
            usecols=[
                "datetime",
                "datetime_kst_excel",
                "signal_name",
                "value",
                "unit",
            ],
        )

        speed = df[
            df["signal_name"] == "Engine road speed"
        ].copy()

        if speed.empty:
            continue

        speed["value_numeric"] = pd.to_numeric(
            speed["value"],
            errors="coerce",
        )

        # Summary by unit
        for unit, group in speed.groupby(
            "unit",
            dropna=False,
        ):

            numeric = group["value_numeric"].dropna()

            if numeric.empty:
                continue

            records.append(
                {
                    "vehicle_id": vehicle_id,
                    "period": period,
                    "unit": unit,
                    "row_count": len(group),
                    "min_speed": numeric.min(),
                    "max_speed": numeric.max(),
                    "mean_speed": numeric.mean(),
                    "speed_gt_160_count": int(
                        (numeric > SUSPICIOUS_SPEED).sum()
                    ),
                    "speed_gt_200_count": int(
                        (numeric > 200).sum()
                    ),
                    "speed_gt_300_count": int(
                        (numeric > 300).sum()
                    ),
                    "negative_count": int(
                        (numeric < 0).sum()
                    ),
                }
            )


result = pd.DataFrame(records)

result = result.sort_values(
    [
        "max_speed",
        "vehicle_id",
        "period",
    ],
    ascending=[False, True, True],
)

result.to_csv(
    OUTPUT_FILE,
    index=False,
)


# --------------------------------------------------
# Print suspicious groups
# --------------------------------------------------

print("\n----------------------------------------")
print("Speed Anomaly Investigation Completed")
print("----------------------------------------")

print(f"Created: {OUTPUT_FILE}")

print("\nGroups with speed > 160:\n")

suspicious = result[
    result["max_speed"] > SUSPICIOUS_SPEED
]

if suspicious.empty:

    print("None")

else:

    print(
        suspicious[
            [
                "vehicle_id",
                "period",
                "unit",
                "row_count",
                "max_speed",
                "speed_gt_160_count",
                "speed_gt_200_count",
                "speed_gt_300_count",
            ]
        ].to_string(index=False)
    )


print("\nUnit distribution:\n")

print(
    result.groupby("unit", dropna=False)["row_count"]
    .sum()
    .sort_values(ascending=False)
)


print("\nTop 10 maximum-speed groups:\n")

print(
    result[
        [
            "vehicle_id",
            "period",
            "unit",
            "max_speed",
        ]
    ]
    .head(10)
    .to_string(index=False)
)