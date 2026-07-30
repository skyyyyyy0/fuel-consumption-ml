import pandas as pd
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("reports/modeling/expected_vs_actual.csv")
OUTPUT_FILE = Path("reports/modeling/high_residual_trips.csv")

TOP_PERCENT = 0.05

# ============================================================
# Load
# ============================================================

print("Loading Expected vs. Actual dataset...")

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "vehicle_id",
    "trip_id",
    "actual_fuel_liter",
    "expected_fuel_liter",
    "fuel_residual_liter",
    "absolute_error_liter",
    "is_out_of_sample",
    "small_expected_fuel_flag",
    "trip_distance_km",
    "trip_duration_min",
    "avg_speed_kmh",
    "max_speed_kmh",
    "speed_std",
    "avg_rpm",
    "max_rpm",
    "rpm_std",
    "high_rpm_ratio",
    "idle_ratio",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# ============================================================
# Filter eligible out-of-sample trips
# ============================================================

oos_df = df[
    df["is_out_of_sample"].eq(True)
].copy()

eligible_df = oos_df[
    oos_df["small_expected_fuel_flag"].eq(False)
].copy()

print(f"Total input rows:          {len(df):,}")
print(f"Out-of-sample rows:        {len(oos_df):,}")
print(f"Eligible analysis rows:    {len(eligible_df):,}")
print(
    f"Excluded small-fuel rows: {len(oos_df) - len(eligible_df):,}"
)

if eligible_df.empty:
    raise ValueError(
        "No eligible out-of-sample trips were found."
    )

# ============================================================
# Identify high-residual trips
# ============================================================

residual_threshold = eligible_df[
    "absolute_error_liter"
].quantile(1 - TOP_PERCENT)

high_residual_df = eligible_df[
    eligible_df["absolute_error_liter"] >= residual_threshold
].copy()

high_residual_df["residual_type"] = pd.cut(
    high_residual_df["fuel_residual_liter"],
    bins=[float("-inf"), 0, float("inf")],
    labels=[
        "High Negative Residual",
        "High Positive Residual",
    ],
    include_lowest=True,
)

high_residual_df["residual_interpretation"] = (
    high_residual_df["fuel_residual_liter"]
    .apply(
        lambda value:
        "Actual fuel was higher than expected"
        if value > 0
        else "Actual fuel was lower than expected"
    )
)

# ============================================================
# Select output columns
# ============================================================

output_columns = [
    "vehicle_id",
    "trip_id",
    "period",
    "trip_start_time",
    "trip_end_time",
    "prediction_scope",
    "actual_fuel_liter",
    "expected_fuel_liter",
    "fuel_residual_liter",
    "absolute_error_liter",
    "fuel_difference_pct",
    "residual_type",
    "residual_interpretation",
    "trip_distance_km",
    "trip_duration_min",
    "avg_speed_kmh",
    "max_speed_kmh",
    "speed_std",
    "avg_rpm",
    "max_rpm",
    "rpm_std",
    "high_rpm_ratio",
    "idle_ratio",
]

output_columns = [
    column for column in output_columns
    if column in high_residual_df.columns
]

high_residual_df = high_residual_df[
    output_columns
].sort_values(
    by="absolute_error_liter",
    ascending=False,
).reset_index(drop=True)

high_residual_df.insert(
    0,
    "residual_rank",
    range(1, len(high_residual_df) + 1),
)

# ============================================================
# Save
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

high_residual_df.to_csv(
    OUTPUT_FILE,
    index=False,
)

# ============================================================
# Print summary
# ============================================================

positive_df = high_residual_df[
    high_residual_df["fuel_residual_liter"] > 0
]

negative_df = high_residual_df[
    high_residual_df["fuel_residual_liter"] < 0
]

print("\nHigh-residual trip summary:")
print(f"Top residual percentage:   {TOP_PERCENT:.0%}")
print(f"Residual threshold:         {residual_threshold:.4f} L")
print(f"Selected trips:             {len(high_residual_df):,}")
print(f"High positive residuals:    {len(positive_df):,}")
print(f"High negative residuals:    {len(negative_df):,}")

print("\nHigh-residual trips by vehicle:")
print(
    high_residual_df["vehicle_id"]
    .value_counts()
    .rename_axis("vehicle_id")
    .to_string()
)

print("\nTop 10 highest absolute residual trips:")
print(
    high_residual_df[
        [
            "residual_rank",
            "vehicle_id",
            "trip_id",
            "fuel_residual_liter",
            "absolute_error_liter",
            "avg_rpm",
            "avg_speed_kmh",
            "idle_ratio",
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nSaved file:")
print(f"- {OUTPUT_FILE.resolve()}")