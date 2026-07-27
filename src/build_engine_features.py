from pathlib import Path
import pandas as pd


# ============================================================
# Configuration
# ============================================================

TRIPS_FILE = Path("data/processed/trips_with_target.csv")
EXCEL_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_FILE = Path("data/processed/trip_features_engine.csv")

HIGH_RPM_THRESHOLD = 3000

VALID_SPEED_UNIT = "UnitOfMeasureKilometersPerHourId"

PERIOD_TO_SHEET = {
    "Before": "2026_Before_Long",
    "After": "2026_After_Long",
    "Final": "2026_Final_Long",
}


# ============================================================
# Load trips
# ============================================================

print("Loading trip dataset...")

trips = pd.read_csv(TRIPS_FILE)

trips["trip_start_time"] = pd.to_datetime(
    trips["trip_start_time"],
    format="mixed",
    utc=True,
    errors="coerce",
)

trips["trip_end_time"] = pd.to_datetime(
    trips["trip_end_time"],
    format="mixed",
    utc=True,
    errors="coerce",
)

print("Trips loaded:", len(trips))


# ============================================================
# Find Excel files
# ============================================================

excel_files = sorted(
    f for f in EXCEL_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

if len(excel_files) != 12:
    raise ValueError(
        f"Expected 12 Excel files, found {len(excel_files)}"
    )

vehicle_files = {
    f"VEH_{idx:02d}": file
    for idx, file in enumerate(excel_files, start=1)
}


# ============================================================
# Build features
# ============================================================

records = []

for vehicle_id, excel_file in vehicle_files.items():

    vehicle_trips = trips[
        trips["vehicle_id"] == vehicle_id
    ].copy()

    if vehicle_trips.empty:
        continue

    for period, sheet_name in PERIOD_TO_SHEET.items():

        period_trips = vehicle_trips[
            vehicle_trips["period"] == period
        ].copy()

        if period_trips.empty:
            continue

        print(
            f"Processing {vehicle_id} | {period} "
            f"| Trips: {len(period_trips)}"
        )

        telemetry = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            engine="openpyxl",
            usecols=[
                "datetime",
                "signal_name",
                "value",
                "unit",
            ],
        )

        telemetry["timestamp"] = pd.to_datetime(
            telemetry["datetime"],
            format="mixed",
            utc=True,
            errors="coerce",
        )

        telemetry["value_numeric"] = pd.to_numeric(
            telemetry["value"],
            errors="coerce",
        )

        # ----------------------------------------------------
        # Valid Speed only
        # ----------------------------------------------------

        speed = telemetry[
            (telemetry["signal_name"] == "Engine road speed")
            & (telemetry["unit"] == VALID_SPEED_UNIT)
        ][
            ["timestamp", "value_numeric"]
        ].dropna()

        speed = speed.sort_values("timestamp")

        # ----------------------------------------------------
        # RPM
        # ----------------------------------------------------

        rpm = telemetry[
            telemetry["signal_name"] == "Engine speed"
        ][
            ["timestamp", "value_numeric"]
        ].dropna()

        rpm = rpm.sort_values("timestamp")

        # ----------------------------------------------------
        # Aggregate each trip
        # ----------------------------------------------------

        for _, trip in period_trips.iterrows():

            trip_id = trip["trip_id"]
            start = trip["trip_start_time"]
            end = trip["trip_end_time"]

            if pd.isna(start) or pd.isna(end) or start >= end:
                records.append({
                    "trip_id": trip_id,
                    "vehicle_id": vehicle_id,
                    "period": period,

                    "speed_obs_count": 0,
                    "avg_speed_kmh": None,
                    "max_speed_kmh": None,
                    "speed_std": None,

                    "rpm_obs_count": 0,
                    "avg_rpm": None,
                    "max_rpm": None,
                    "rpm_std": None,
                    "high_rpm_ratio": None,
                })
                continue

            # ----------------------------------------------
            # Speed within Trip
            # ----------------------------------------------

            trip_speed = speed[
                (speed["timestamp"] >= start)
                & (speed["timestamp"] <= end)
            ]["value_numeric"]

            # ----------------------------------------------
            # RPM within Trip
            # ----------------------------------------------

            trip_rpm = rpm[
                (rpm["timestamp"] >= start)
                & (rpm["timestamp"] <= end)
            ]["value_numeric"]

            # ----------------------------------------------
            # Speed features
            # ----------------------------------------------

            speed_count = len(trip_speed)

            if speed_count > 0:
                avg_speed = trip_speed.mean()
                max_speed = trip_speed.max()

                speed_std = (
                    trip_speed.std(ddof=0)
                    if speed_count > 1
                    else 0.0
                )
            else:
                avg_speed = None
                max_speed = None
                speed_std = None

            # ----------------------------------------------
            # RPM features
            # ----------------------------------------------

            rpm_count = len(trip_rpm)

            if rpm_count > 0:
                avg_rpm = trip_rpm.mean()
                max_rpm = trip_rpm.max()

                rpm_std = (
                    trip_rpm.std(ddof=0)
                    if rpm_count > 1
                    else 0.0
                )

                high_rpm_ratio = (
                    (trip_rpm > HIGH_RPM_THRESHOLD)
                    .mean()
                )
            else:
                avg_rpm = None
                max_rpm = None
                rpm_std = None
                high_rpm_ratio = None

            records.append({
                "trip_id": trip_id,
                "vehicle_id": vehicle_id,
                "period": period,

                "speed_obs_count": speed_count,
                "avg_speed_kmh": avg_speed,
                "max_speed_kmh": max_speed,
                "speed_std": speed_std,

                "rpm_obs_count": rpm_count,
                "avg_rpm": avg_rpm,
                "max_rpm": max_rpm,
                "rpm_std": rpm_std,
                "high_rpm_ratio": high_rpm_ratio,
            })


# ============================================================
# Create final feature table
# ============================================================

features = pd.DataFrame(records)

features = features.sort_values(
    ["vehicle_id", "period", "trip_id"]
).reset_index(drop=True)


# ============================================================
# Validation
# ============================================================

print("\n========================================")
print("Engine Feature Validation")
print("========================================")

print("Feature rows:", len(features))
print("Unique trip IDs:", features["trip_id"].nunique())

print("\nMissing feature counts:")

for col in [
    "avg_speed_kmh",
    "max_speed_kmh",
    "speed_std",
    "avg_rpm",
    "max_rpm",
    "rpm_std",
    "high_rpm_ratio",
]:
    missing = features[col].isna().sum()

    pct = (
        missing / len(features) * 100
        if len(features) > 0
        else 0
    )

    print(
        f"{col}: {missing:,} "
        f"({pct:.1f}%)"
    )


print("\nSpeed range:")

print(
    "avg_speed_kmh:",
    features["avg_speed_kmh"].min(),
    "to",
    features["avg_speed_kmh"].max(),
)

print(
    "max_speed_kmh:",
    features["max_speed_kmh"].min(),
    "to",
    features["max_speed_kmh"].max(),
)


print("\nRPM range:")

print(
    "avg_rpm:",
    features["avg_rpm"].min(),
    "to",
    features["avg_rpm"].max(),
)

print(
    "max_rpm:",
    features["max_rpm"].min(),
    "to",
    features["max_rpm"].max(),
)


print("\nHigh RPM ratio range:")

print(
    features["high_rpm_ratio"].min(),
    "to",
    features["high_rpm_ratio"].max(),
)


# ============================================================
# Coverage by Vehicle
# ============================================================

coverage_vehicle = (
    features
    .assign(
        speed_available=
        features["avg_speed_kmh"].notna(),

        rpm_available=
        features["avg_rpm"].notna(),
    )
    .groupby("vehicle_id")
    .agg(
        trips=("trip_id", "size"),
        speed_trips=("speed_available", "sum"),
        rpm_trips=("rpm_available", "sum"),
    )
)

coverage_vehicle["speed_coverage_pct"] = (
    coverage_vehicle["speed_trips"]
    / coverage_vehicle["trips"]
    * 100
)

coverage_vehicle["rpm_coverage_pct"] = (
    coverage_vehicle["rpm_trips"]
    / coverage_vehicle["trips"]
    * 100
)

print("\nCoverage by vehicle:")

print(
    coverage_vehicle
    .round(1)
    .to_string()
)


# ============================================================
# Coverage by Period
# ============================================================

coverage_period = (
    features
    .assign(
        speed_available=
        features["avg_speed_kmh"].notna(),

        rpm_available=
        features["avg_rpm"].notna(),
    )
    .groupby("period")
    .agg(
        trips=("trip_id", "size"),
        speed_trips=("speed_available", "sum"),
        rpm_trips=("rpm_available", "sum"),
    )
)

coverage_period["speed_coverage_pct"] = (
    coverage_period["speed_trips"]
    / coverage_period["trips"]
    * 100
)

coverage_period["rpm_coverage_pct"] = (
    coverage_period["rpm_trips"]
    / coverage_period["trips"]
    * 100
)

print("\nCoverage by period:")

print(
    coverage_period
    .round(1)
    .to_string()
)


# ============================================================
# Save
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

features.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nCreated:", OUTPUT_FILE)