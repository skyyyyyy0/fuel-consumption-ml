from pathlib import Path
import pandas as pd


INPUT_FILE = Path("reports/signal_inventory_raw.csv")
OUTPUT_FILE = Path("reports/signal_coverage_summary.csv")

TOTAL_VEHICLES = 12

df = pd.read_csv(INPUT_FILE)

# --------------------------------------------------
# Basic validation
# --------------------------------------------------

required = {
    "vehicle_id",
    "year",
    "period",
    "signal",
    "row_count",
    "missing_value_count",
    "missing_pct",
    "unit",
}

missing = required - set(df.columns)

if missing:
    raise ValueError(
        f"Missing required columns: {sorted(missing)}"
    )


# --------------------------------------------------
# Create vehicle-period identifier
# --------------------------------------------------

df["vehicle_period"] = (
    df["vehicle_id"].astype(str)
    + "_"
    + df["year"].astype(str)
    + "_"
    + df["period"].astype(str)
)

# 12 vehicles × 5 periods
TOTAL_VEHICLE_PERIODS = 60


# --------------------------------------------------
# Aggregate by signal
# --------------------------------------------------

records = []

for signal, group in df.groupby("signal"):

    vehicles_available = group["vehicle_id"].nunique()

    vehicle_periods_available = group["vehicle_period"].nunique()

    total_rows = group["row_count"].sum()
    total_missing = group["missing_value_count"].sum()

    overall_missing_pct = (
        total_missing / total_rows * 100
        if total_rows > 0
        else None
    )

    units = (
        group["unit"]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
    )

    unit = (
        " | ".join(sorted(units))
        if len(units) > 0
        else None
    )

    before_available = (
        group.loc[group["period"] == "Before", "vehicle_id"]
        .nunique()
    )

    after_available = (
        group.loc[group["period"] == "After", "vehicle_id"]
        .nunique()
    )

    final_available = (
        group.loc[group["period"] == "Final", "vehicle_id"]
        .nunique()
    )

    records.append(
        {
            "signal": signal,

            "vehicles_available": vehicles_available,

            "vehicle_coverage_pct": round(
                vehicles_available / TOTAL_VEHICLES * 100,
                2
            ),

            "vehicle_periods_available": vehicle_periods_available,

            "vehicle_period_coverage_pct": round(
                vehicle_periods_available
                / TOTAL_VEHICLE_PERIODS
                * 100,
                2
            ),

            "before_vehicles": before_available,

            "after_vehicles": after_available,

            "final_vehicles": final_available,

            "total_rows": int(total_rows),

            "missing_pct": round(
                float(overall_missing_pct),
                4
            ),

            "unit": unit,
        }
    )


result = pd.DataFrame(records)

result = result.sort_values(
    [
        "vehicle_coverage_pct",
        "vehicle_period_coverage_pct",
        "signal",
    ],
    ascending=[False, False, True]
).reset_index(drop=True)


# --------------------------------------------------
# Save
# --------------------------------------------------

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Print
# --------------------------------------------------

print("\n----------------------------------------")
print("Signal Coverage Analysis Completed")
print("----------------------------------------")

print(f"Created: {OUTPUT_FILE}")
print(f"Signals analyzed: {len(result)}")

print("\nCoverage Summary:\n")

print(
    result[
        [
            "signal",
            "vehicles_available",
            "vehicle_periods_available",
            "missing_pct",
            "unit",
        ]
    ].to_string(index=False)
)