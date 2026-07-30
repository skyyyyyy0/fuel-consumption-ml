from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "modeling"
    / "expected_vs_actual.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "modeling"
    / "vehicle_efficiency.csv"
)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# Analysis rules
# ============================================================

INEFFICIENT_THRESHOLD_PCT = 5.0
EFFICIENT_THRESHOLD_PCT = -5.0
MIN_ELIGIBLE_TRIPS = 30

REQUIRED_COLUMNS = [
    "vehicle_id",
    "actual_fuel_liter",
    "expected_fuel_liter",
    "fuel_residual_liter",
    "absolute_error_liter",
    "fuel_difference_pct",
    "small_expected_fuel_flag",
    "is_out_of_sample",
]


# ============================================================
# Validation
# ============================================================

def validate_input(df: pd.DataFrame) -> None:
    """Validate the Expected vs. Actual dataset."""

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    core_columns = [
        "vehicle_id",
        "actual_fuel_liter",
        "expected_fuel_liter",
        "fuel_residual_liter",
        "absolute_error_liter",
    ]

    if df[core_columns].isna().any().any():
        missing_counts = (
            df[core_columns]
            .isna()
            .sum()
        )

        missing_counts = missing_counts[
            missing_counts > 0
        ]

        raise ValueError(
            "Missing values found in core columns:\n"
            f"{missing_counts}"
        )


# ============================================================
# Efficiency classification
# ============================================================

def classify_vehicle(
    fuel_deviation_pct: float,
) -> str:
    """Classify vehicle efficiency using screening thresholds."""

    if fuel_deviation_pct >= INEFFICIENT_THRESHOLD_PCT:
        return "Higher Fuel Use Than Expected"

    if fuel_deviation_pct <= EFFICIENT_THRESHOLD_PCT:
        return "Lower Fuel Use Than Expected"

    return "Within Expected Range"


# ============================================================
# Vehicle aggregation
# ============================================================

def calculate_vehicle_efficiency(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate out-of-sample residuals by vehicle."""

    # Use only out-of-sample predictions.
    out_of_sample_df = df[
        df["is_out_of_sample"] == True
    ].copy()

    if out_of_sample_df.empty:
        raise ValueError(
            "No out-of-sample rows were found."
        )

    # General residual metrics use all out-of-sample trips.
    residual_metrics = (
        out_of_sample_df
        .groupby("vehicle_id", as_index=False)
        .agg(
            total_oos_trips=(
                "vehicle_id",
                "size",
            ),
            mean_residual_liter=(
                "fuel_residual_liter",
                "mean",
            ),
            median_residual_liter=(
                "fuel_residual_liter",
                "median",
            ),
            mae_liter=(
                "absolute_error_liter",
                "mean",
            ),
            residual_std_liter=(
                "fuel_residual_liter",
                "std",
            ),
        )
    )

    # Exclude very small Expected Fuel trips from percentage-
    # based calculations.
    percentage_df = out_of_sample_df[
        out_of_sample_df["small_expected_fuel_flag"] == False
    ].copy()

    if percentage_df.empty:
        raise ValueError(
            "No valid rows remained for percentage analysis."
        )

    fuel_totals = (
        percentage_df
        .groupby("vehicle_id", as_index=False)
        .agg(
            eligible_trips=(
                "vehicle_id",
                "size",
            ),
            total_actual_fuel_liter=(
                "actual_fuel_liter",
                "sum",
            ),
            total_expected_fuel_liter=(
                "expected_fuel_liter",
                "sum",
            ),
            total_residual_fuel_liter=(
                "fuel_residual_liter",
                "sum",
            ),
            mean_trip_difference_pct=(
                "fuel_difference_pct",
                "mean",
            ),
            median_trip_difference_pct=(
                "fuel_difference_pct",
                "median",
            ),
        )
    )

    vehicle_df = residual_metrics.merge(
        fuel_totals,
        on="vehicle_id",
        how="left",
        validate="one_to_one",
    )

    # Primary ranking metric:
    # aggregate deviation, not mean trip-level percentage.
    vehicle_df["fuel_deviation_pct"] = (
        vehicle_df["total_residual_fuel_liter"]
        / vehicle_df["total_expected_fuel_liter"]
        * 100
    )

    vehicle_df["actual_to_expected_ratio"] = (
        vehicle_df["total_actual_fuel_liter"]
        / vehicle_df["total_expected_fuel_liter"]
    )

    vehicle_df["excluded_small_fuel_trips"] = (
        vehicle_df["total_oos_trips"]
        - vehicle_df["eligible_trips"]
    )

    vehicle_df["eligible_trip_share_pct"] = (
        vehicle_df["eligible_trips"]
        / vehicle_df["total_oos_trips"]
        * 100
    )

    vehicle_df["ranking_reliability"] = np.where(
        vehicle_df["eligible_trips"] >= MIN_ELIGIBLE_TRIPS,
        "Sufficient Trips",
        "Limited Trips",
    )

    vehicle_df["efficiency_status"] = (
        vehicle_df["fuel_deviation_pct"]
        .apply(classify_vehicle)
    )

    # Lower deviation means lower actual fuel use relative
    # to model expectation.
    vehicle_df = vehicle_df.sort_values(
        by=[
            "fuel_deviation_pct",
            "eligible_trips",
        ],
        ascending=[
            True,
            False,
        ],
    ).reset_index(drop=True)

    vehicle_df["efficiency_rank"] = np.arange(
        1,
        len(vehicle_df) + 1,
    )

    output_columns = [
        "efficiency_rank",
        "vehicle_id",
        "efficiency_status",
        "ranking_reliability",
        "total_oos_trips",
        "eligible_trips",
        "excluded_small_fuel_trips",
        "eligible_trip_share_pct",
        "total_actual_fuel_liter",
        "total_expected_fuel_liter",
        "total_residual_fuel_liter",
        "fuel_deviation_pct",
        "actual_to_expected_ratio",
        "mean_residual_liter",
        "median_residual_liter",
        "mae_liter",
        "residual_std_liter",
        "mean_trip_difference_pct",
        "median_trip_difference_pct",
    ]

    vehicle_df = vehicle_df[output_columns]

    numeric_columns = vehicle_df.select_dtypes(
        include="number"
    ).columns

    vehicle_df[numeric_columns] = (
        vehicle_df[numeric_columns]
        .round(4)
    )

    return vehicle_df


# ============================================================
# Main
# ============================================================

def main() -> None:
    """Run vehicle efficiency analysis."""

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}"
        )

    print("Loading Expected vs. Actual dataset...")

    df = pd.read_csv(INPUT_PATH)

    validate_input(df)

    out_of_sample_df = df[
        df["is_out_of_sample"] == True
    ]

    percentage_df = out_of_sample_df[
        out_of_sample_df["small_expected_fuel_flag"] == False
    ]

    print(f"Total input rows:        {len(df):,}")
    print(
        f"Out-of-sample rows:      "
        f"{len(out_of_sample_df):,}"
    )
    print(
        f"Percentage-valid rows:   "
        f"{len(percentage_df):,}"
    )
    print(
        f"Excluded small-fuel rows:"
        f" {len(out_of_sample_df) - len(percentage_df):,}"
    )

    vehicle_df = calculate_vehicle_efficiency(df)

    vehicle_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\nVehicle efficiency ranking:")
    print(
        vehicle_df[
            [
                "efficiency_rank",
                "vehicle_id",
                "fuel_deviation_pct",
                "mean_residual_liter",
                "median_residual_liter",
                "mae_liter",
                "eligible_trips",
                "efficiency_status",
            ]
        ].to_string(index=False)
    )

    print("\nStatus counts:")
    print(
        vehicle_df["efficiency_status"]
        .value_counts()
        .to_string()
    )

    print("\nSaved file:")
    print(f"- {OUTPUT_PATH}")


if __name__ == "__main__":
    main()