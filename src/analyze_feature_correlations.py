from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("data/processed/trip_ml_features.csv")

OUTPUT_DIR = Path(
    "reports/figures/correlation_feature_analysis"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TARGET = "trip_fuel_used_liter"

NUMERIC_FEATURES = [
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

    "trip_hour",
    "day_of_week",
    "is_weekend",
]


# ============================================================
# Load
# ============================================================

print("Loading feature dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows: {len(df):,}")
print(f"Vehicles: {df['vehicle_id'].nunique()}")
print(f"Periods: {df['period'].nunique()}")


# ============================================================
# 1. Numeric Correlation Matrix
# ============================================================

corr_columns = (
    NUMERIC_FEATURES
    + [TARGET]
)

corr = (
    df[corr_columns]
    .corr()
)

corr.to_csv(
    OUTPUT_DIR / "numeric_correlation_matrix.csv"
)


print("\n========================================")
print("Feature ↔ Target Correlation")
print("========================================")

target_corr = (
    corr[TARGET]
    .drop(TARGET)
    .sort_values(
        key=lambda x: x.abs(),
        ascending=False,
    )
)

print(
    target_corr.to_string()
)

target_corr.rename(
    "target_correlation"
).to_csv(
    OUTPUT_DIR / "feature_target_correlations.csv"
)


# ============================================================
# 2. Correlation Heatmap
# ============================================================

plt.figure(
    figsize=(12, 10)
)

plt.imshow(
    corr,
    aspect="auto",
)

plt.colorbar(
    label="Pearson Correlation"
)

plt.xticks(
    range(len(corr.columns)),
    corr.columns,
    rotation=90,
)

plt.yticks(
    range(len(corr.index)),
    corr.index,
)

plt.title(
    "Numeric Feature Correlation Matrix"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "correlation_heatmap.png",
    dpi=150,
)

plt.close()


# ============================================================
# 3. Highly Correlated Feature Pairs
# ============================================================

pairs = []

for i, col1 in enumerate(NUMERIC_FEATURES):

    for col2 in NUMERIC_FEATURES[i + 1:]:

        value = corr.loc[col1, col2]

        pairs.append({
            "feature_1": col1,
            "feature_2": col2,
            "correlation": value,
            "abs_correlation": abs(value),
        })


pair_df = pd.DataFrame(
    pairs
).sort_values(
    "abs_correlation",
    ascending=False,
)

pair_df.to_csv(
    OUTPUT_DIR
    / "feature_pair_correlations.csv",
    index=False,
)


print("\n========================================")
print("Highest Feature ↔ Feature Correlations")
print("========================================")

print(
    pair_df.head(25)[
        [
            "feature_1",
            "feature_2",
            "correlation",
        ]
    ].to_string(index=False)
)


# ============================================================
# 4. Multicollinearity Candidates
# ============================================================

HIGH_CORR_THRESHOLD = 0.80

high_corr = pair_df[
    pair_df["abs_correlation"]
    >= HIGH_CORR_THRESHOLD
].copy()


print("\n========================================")
print("Multicollinearity Candidates")
print(f"|correlation| >= {HIGH_CORR_THRESHOLD}")
print("========================================")

if high_corr.empty:
    print("None")

else:
    print(
        high_corr[
            [
                "feature_1",
                "feature_2",
                "correlation",
            ]
        ].to_string(index=False)
    )


high_corr.to_csv(
    OUTPUT_DIR
    / "multicollinearity_candidates.csv",
    index=False,
)


# ============================================================
# 5. Key Trip / Speed Relationships
# ============================================================

key_pairs = [
    (
        "trip_distance_km",
        "trip_duration_min",
    ),
    (
        "trip_distance_km",
        "avg_speed_kmh",
    ),
    (
        "trip_distance_km",
        "max_speed_kmh",
    ),
    (
        "trip_duration_min",
        "avg_speed_kmh",
    ),
    (
        "trip_duration_min",
        "max_speed_kmh",
    ),
    (
        "avg_speed_kmh",
        "max_speed_kmh",
    ),
    (
        "avg_speed_kmh",
        "speed_std",
    ),
    (
        "max_speed_kmh",
        "speed_std",
    ),
]


print("\n========================================")
print("Distance / Duration / Speed Relationships")
print("========================================")

for a, b in key_pairs:

    value = corr.loc[a, b]

    print(
        f"{a} ↔ {b}: "
        f"{value:.4f}"
    )


# ============================================================
# 6. RPM Redundancy
# ============================================================

rpm_pairs = [
    (
        "avg_rpm",
        "max_rpm",
    ),
    (
        "avg_rpm",
        "rpm_std",
    ),
    (
        "max_rpm",
        "rpm_std",
    ),
    (
        "max_rpm",
        "high_rpm_ratio",
    ),
    (
        "rpm_std",
        "high_rpm_ratio",
    ),
]


print("\n========================================")
print("RPM Feature Relationships")
print("========================================")

for a, b in rpm_pairs:

    value = corr.loc[a, b]

    print(
        f"{a} ↔ {b}: "
        f"{value:.4f}"
    )


# ============================================================
# 7. Vehicle Effect
# ============================================================

vehicle_summary = (
    df.groupby("vehicle_id")
    .agg(
        trips=("trip_id", "count"),

        mean_fuel=(
            TARGET,
            "mean",
        ),

        median_fuel=(
            TARGET,
            "median",
        ),

        mean_distance=(
            "trip_distance_km",
            "mean",
        ),

        mean_duration=(
            "trip_duration_min",
            "mean",
        ),

        mean_avg_speed=(
            "avg_speed_kmh",
            "mean",
        ),

        mean_avg_rpm=(
            "avg_rpm",
            "mean",
        ),

        mean_idle_ratio=(
            "idle_ratio",
            "mean",
        ),
    )
    .reset_index()
)


print("\n========================================")
print("Vehicle Effect Summary")
print("========================================")

print(
    vehicle_summary
    .round(3)
    .to_string(index=False)
)

vehicle_summary.to_csv(
    OUTPUT_DIR
    / "vehicle_effect_summary.csv",
    index=False,
)


# ============================================================
# 8. Period Effect
# ============================================================

period_summary = (
    df.groupby("period")
    .agg(
        trips=("trip_id", "count"),

        mean_fuel=(
            TARGET,
            "mean",
        ),

        median_fuel=(
            TARGET,
            "median",
        ),

        mean_distance=(
            "trip_distance_km",
            "mean",
        ),

        mean_duration=(
            "trip_duration_min",
            "mean",
        ),

        mean_avg_speed=(
            "avg_speed_kmh",
            "mean",
        ),

        mean_avg_rpm=(
            "avg_rpm",
            "mean",
        ),

        mean_idle_ratio=(
            "idle_ratio",
            "mean",
        ),
    )
    .reset_index()
)


print("\n========================================")
print("Period Effect Summary")
print("========================================")

print(
    period_summary
    .round(3)
    .to_string(index=False)
)

period_summary.to_csv(
    OUTPUT_DIR
    / "period_effect_summary.csv",
    index=False,
)


# ============================================================
# 9. Context Feature Correlations
# ============================================================

print("\n========================================")
print("Context Feature ↔ Fuel")
print("========================================")

for feature in [
    "trip_hour",
    "day_of_week",
    "is_weekend",
]:

    print(
        f"{feature}: "
        f"{df[feature].corr(df[TARGET]):.4f}"
    )


# ============================================================
# Complete
# ============================================================

print("\n========================================")
print("Correlation & Feature Analysis Completed")
print("========================================")

print(
    f"Outputs created in: {OUTPUT_DIR}"
)