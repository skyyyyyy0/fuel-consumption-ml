from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw/Final_Excel_Files")

SIGNALS = [
    "Vehicle Active",
    "Engine speed",
    "Engine road speed",
]

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

        try:
            df = pd.read_excel(
                file,
                sheet_name=sheet,
                engine="openpyxl",
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        # Keep only relevant signals
        state = df[df["signal_name"].isin(SIGNALS)].copy()

        if state.empty:
            continue

        state["value"] = pd.to_numeric(
            state["value"],
            errors="coerce"
        )

        # --------------------------------------------------
        # Vehicle Active
        # --------------------------------------------------

        active = state[
            state["signal_name"] == "Vehicle Active"
        ]

        active_values = (
            active["value"]
            .dropna()
            .value_counts()
            .to_dict()
        )

        # --------------------------------------------------
        # Speed
        # --------------------------------------------------

        speed = state[
            (state["signal_name"] == "Engine road speed")
            & (
                state["unit"]
                == "UnitOfMeasureKilometersPerHourId"
            )
        ]

        # --------------------------------------------------
        # RPM
        # --------------------------------------------------

        rpm = state[
            state["signal_name"] == "Engine speed"
        ]

        record = {
            "vehicle_id": vehicle_id,
            "period": period,

            "vehicle_active_rows": len(active),
            "vehicle_active_values": str(active_values),

            "speed_rows": len(speed),
            "speed_zero_rows": int(
                (speed["value"] == 0).sum()
            ),
            "speed_positive_rows": int(
                (speed["value"] > 0).sum()
            ),

            "rpm_rows": len(rpm),
            "rpm_zero_rows": int(
                (rpm["value"] == 0).sum()
            ),
            "rpm_positive_rows": int(
                (rpm["value"] > 0).sum()
            ),
            "rpm_gt_500_rows": int(
                (rpm["value"] > 500).sum()
            ),
        }

        records.append(record)


result = pd.DataFrame(records)

output = Path(
    "reports/vehicle_state_signal_audit.csv"
)

result.to_csv(output, index=False)


print("\n========================================")
print("Vehicle-State Signal Audit")
print("========================================")

print(f"Vehicle-periods: {len(result)}")

print("\nVehicle Active value patterns:")

if not result.empty:
    print(
        result[
            [
                "vehicle_id",
                "period",
                "vehicle_active_rows",
                "vehicle_active_values",
            ]
        ].to_string(index=False)
    )

print("\n========================================")
print("Speed / RPM Summary")
print("========================================")

if not result.empty:

    print(
        "Speed observations:",
        result["speed_rows"].sum()
    )

    print(
        "Speed = 0:",
        result["speed_zero_rows"].sum()
    )

    print(
        "Speed > 0:",
        result["speed_positive_rows"].sum()
    )

    print(
        "RPM observations:",
        result["rpm_rows"].sum()
    )

    print(
        "RPM = 0:",
        result["rpm_zero_rows"].sum()
    )

    print(
        "RPM > 0:",
        result["rpm_positive_rows"].sum()
    )

    print(
        "RPM > 500:",
        result["rpm_gt_500_rows"].sum()
    )

print(f"\nCreated: {output}")