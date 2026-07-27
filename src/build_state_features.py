from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# Configuration
# ============================================================

RAW_DIR = Path("data/raw/Final_Excel_Files")
TRIP_FILE = Path("data/processed/trips_with_target.csv")
OUTPUT_FILE = Path("data/processed/trip_features_state.csv")

SPEED_SIGNAL = "Engine road speed"
RPM_SIGNAL = "Engine speed"

SPEED_UNIT = "UnitOfMeasureKilometersPerHourId"

IDLE_SPEED_THRESHOLD = 1.0
IDLE_RPM_THRESHOLD = 500.0

RPM_MATCH_TOLERANCE_SEC = 30
STATE_DURATION_CAP_SEC = 30


# ============================================================
# Load Trips
# ============================================================

print("Loading trip dataset...")

trips = pd.read_csv(TRIP_FILE)

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
# Locate Excel Files
# ============================================================

files = sorted(
    f for f in RAW_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

if len(files) != 12:
    print(
        f"WARNING: Expected 12 Excel files, "
        f"found {len(files)}"
    )


# ============================================================
# Feature Storage
# ============================================================

feature_records = []


# ============================================================
# Process Vehicle / Period
# ============================================================

for file_idx, file in enumerate(files, start=1):

    vehicle_id = f"VEH_{file_idx:02d}"

    for period in ["Before", "After", "Final"]:

        vehicle_trips = trips[
            (trips["vehicle_id"] == vehicle_id)
            & (trips["period"] == period)
        ].copy()

        print(
            f"Processing {vehicle_id} | "
            f"{period} | Trips: {len(vehicle_trips)}"
        )

        if vehicle_trips.empty:
            continue

        sheet = f"2026_{period}_Long"

        # ----------------------------------------------------
        # Read telemetry
        # ----------------------------------------------------

        try:
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

        except Exception as e:
            print(f"  ERROR reading {sheet}: {e}")
            continue

        df["timestamp"] = pd.to_datetime(
            df["datetime"],
            format="mixed",
            utc=True,
            errors="coerce",
        )

        df["value"] = pd.to_numeric(
            df["value"],
            errors="coerce",
        )

        # ----------------------------------------------------
        # Speed
        # ----------------------------------------------------

        speed = df[
            (df["signal_name"] == SPEED_SIGNAL)
            & (df["unit"] == SPEED_UNIT)
        ][["timestamp", "value"]].copy()

        speed = speed.rename(
            columns={"value": "speed_kmh"}
        )

        speed = (
            speed
            .dropna(subset=["timestamp", "speed_kmh"])
            .sort_values("timestamp")
            .drop_duplicates(
                subset=["timestamp"],
                keep="last",
            )
            .reset_index(drop=True)
        )

        # ----------------------------------------------------
        # RPM
        # ----------------------------------------------------

        rpm = df[
            df["signal_name"] == RPM_SIGNAL
        ][["timestamp", "value"]].copy()

        rpm = rpm.rename(
            columns={
                "timestamp": "rpm_timestamp",
                "value": "rpm",
            }
        )

        rpm = (
            rpm
            .dropna(subset=["rpm_timestamp", "rpm"])
            .sort_values("rpm_timestamp")
            .drop_duplicates(
                subset=["rpm_timestamp"],
                keep="last",
            )
            .reset_index(drop=True)
        )

        # ----------------------------------------------------
        # Match nearest RPM to each Speed observation
        # ----------------------------------------------------

        if not speed.empty and not rpm.empty:

            state = pd.merge_asof(
                speed.sort_values("timestamp"),
                rpm.sort_values("rpm_timestamp"),
                left_on="timestamp",
                right_on="rpm_timestamp",
                direction="nearest",
                tolerance=pd.Timedelta(
                    seconds=RPM_MATCH_TOLERANCE_SEC
                ),
            )

            state["rpm_diff_sec"] = (
                state["timestamp"]
                - state["rpm_timestamp"]
            ).abs().dt.total_seconds()

        else:

            state = speed.copy()
            state["rpm_timestamp"] = pd.NaT
            state["rpm"] = np.nan
            state["rpm_diff_sec"] = np.nan

        # ----------------------------------------------------
        # Idle classification
        # ----------------------------------------------------

        state["rpm_valid"] = (
            state["rpm"].notna()
            & (
                state["rpm_diff_sec"]
                <= RPM_MATCH_TOLERANCE_SEC
            )
        )

        state["is_idle"] = (
            (state["speed_kmh"] < IDLE_SPEED_THRESHOLD)
            & state["rpm_valid"]
            & (state["rpm"] > IDLE_RPM_THRESHOLD)
        )

        # ----------------------------------------------------
        # Calculate Trip-level features
        # ----------------------------------------------------

        for _, trip in vehicle_trips.iterrows():

            trip_id = trip["trip_id"]
            start = trip["trip_start_time"]
            end = trip["trip_end_time"]

            base_record = {
                "vehicle_id": vehicle_id,
                "trip_id": trip_id,
                "period": period,
            }

            if (
                pd.isna(start)
                or pd.isna(end)
                or start >= end
                or state.empty
            ):

                base_record.update({
                    "idle_duration_min": np.nan,
                    "valid_state_duration_min": np.nan,
                    "idle_ratio": np.nan,
                    "state_obs_count": 0,
                    "idle_obs_count": 0,
                })

                feature_records.append(base_record)
                continue

            trip_state = state[
                (state["timestamp"] >= start)
                & (state["timestamp"] <= end)
            ].copy()

            if trip_state.empty:

                base_record.update({
                    "idle_duration_min": np.nan,
                    "valid_state_duration_min": np.nan,
                    "idle_ratio": np.nan,
                    "state_obs_count": 0,
                    "idle_obs_count": 0,
                })

                feature_records.append(base_record)
                continue

            trip_state = (
                trip_state
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

            # Next speed observation
            trip_state["next_timestamp"] = (
                trip_state["timestamp"].shift(-1)
            )

            # Last observation can extend only to Trip end
            trip_state.loc[
                trip_state.index[-1],
                "next_timestamp"
            ] = end

            # Raw duration represented by each Speed state
            trip_state["state_duration_sec"] = (
                trip_state["next_timestamp"]
                - trip_state["timestamp"]
            ).dt.total_seconds()

            # Prevent negative durations
            trip_state.loc[
                trip_state["state_duration_sec"] < 0,
                "state_duration_sec"
            ] = 0

            # Cap event-driven gaps at 30 sec
            trip_state["state_duration_sec"] = (
                trip_state["state_duration_sec"]
                .clip(
                    lower=0,
                    upper=STATE_DURATION_CAP_SEC,
                )
            )

            # Only observations with sufficiently fresh RPM
            # contribute to valid idle/driving state duration.
            valid_state = trip_state[
                trip_state["rpm_valid"]
            ].copy()

            valid_duration_sec = (
                valid_state["state_duration_sec"].sum()
            )

            idle_duration_sec = (
                valid_state.loc[
                    valid_state["is_idle"],
                    "state_duration_sec",
                ].sum()
            )

            if valid_duration_sec > 0:

                idle_ratio = (
                    idle_duration_sec
                    / valid_duration_sec
                )

            else:
                idle_ratio = np.nan

            base_record.update({
                "idle_duration_min":
                    idle_duration_sec / 60,

                "valid_state_duration_min":
                    valid_duration_sec / 60,

                "idle_ratio":
                    idle_ratio,

                "state_obs_count":
                    len(trip_state),

                "idle_obs_count":
                    int(
                        valid_state["is_idle"].sum()
                    ),
            })

            feature_records.append(base_record)


# ============================================================
# Build Dataset
# ============================================================

features = pd.DataFrame(feature_records)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

features.to_csv(
    OUTPUT_FILE,
    index=False,
)


# ============================================================
# Validation
# ============================================================

print("\n========================================")
print("Vehicle-State Feature Validation")
print("========================================")

print("Feature rows:", len(features))

print(
    "Unique trip IDs:",
    features["trip_id"].nunique(),
)

print("\nMissing features:")

for col in [
    "idle_duration_min",
    "valid_state_duration_min",
    "idle_ratio",
]:

    missing = features[col].isna().sum()

    pct = (
        missing / len(features) * 100
        if len(features)
        else 0
    )

    print(
        f"{col}: {missing} "
        f"({pct:.1f}%)"
    )


print("\nIdle ratio validation:")

valid_idle = features["idle_ratio"].dropna()

if not valid_idle.empty:

    print(
        "Min:",
        valid_idle.min()
    )

    print(
        "Median:",
        valid_idle.median()
    )

    print(
        "Mean:",
        valid_idle.mean()
    )

    print(
        "P95:",
        valid_idle.quantile(0.95)
    )

    print(
        "Max:",
        valid_idle.max()
    )

    print(
        "Outside 0-1:",
        (
            (valid_idle < 0)
            | (valid_idle > 1)
        ).sum()
    )


# ============================================================
# Coverage by Vehicle
# ============================================================

coverage_vehicle = (
    features
    .groupby("vehicle_id")
    .agg(
        trips=("trip_id", "count"),
        state_trips=(
            "idle_ratio",
            lambda x: x.notna().sum(),
        ),
        median_idle_ratio=(
            "idle_ratio",
            "median",
        ),
        mean_idle_ratio=(
            "idle_ratio",
            "mean",
        ),
    )
)

coverage_vehicle[
    "state_coverage_pct"
] = (
    coverage_vehicle["state_trips"]
    / coverage_vehicle["trips"]
    * 100
)

print("\nCoverage by vehicle:")

print(
    coverage_vehicle[
        [
            "trips",
            "state_trips",
            "state_coverage_pct",
            "median_idle_ratio",
            "mean_idle_ratio",
        ]
    ].to_string()
)


# ============================================================
# Coverage by Period
# ============================================================

coverage_period = (
    features
    .groupby("period")
    .agg(
        trips=("trip_id", "count"),
        state_trips=(
            "idle_ratio",
            lambda x: x.notna().sum(),
        ),
        median_idle_ratio=(
            "idle_ratio",
            "median",
        ),
    )
)

coverage_period[
    "state_coverage_pct"
] = (
    coverage_period["state_trips"]
    / coverage_period["trips"]
    * 100
)

print("\nCoverage by period:")

print(
    coverage_period.to_string()
)


print(
    f"\nCreated: {OUTPUT_FILE}"
)