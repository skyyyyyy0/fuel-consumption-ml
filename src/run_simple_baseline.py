from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# ============================================================
# Paths
# ============================================================

TRAIN_FILE = Path("data/modeling/train.csv")
VALIDATION_FILE = Path("data/modeling/validation.csv")

TARGET = "trip_fuel_used_liter"


# ============================================================
# Load
# ============================================================

print("Loading train and validation datasets...")

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALIDATION_FILE)

print(f"Train rows: {len(train):,}")
print(f"Validation rows: {len(validation):,}")


# ============================================================
# Simple Baseline
#
# Predict every validation trip using the mean fuel consumption
# observed in the TRAINING set only.
# ============================================================

train_mean = train[TARGET].mean()
train_median = train[TARGET].median()

print("\n========================================")
print("Training Target Statistics")
print("========================================")

print(f"Train mean fuel: {train_mean:.4f} L")
print(f"Train median fuel: {train_median:.4f} L")


# ============================================================
# Mean Baseline
# ============================================================

validation["prediction_mean_baseline"] = train_mean

mae_mean = mean_absolute_error(
    validation[TARGET],
    validation["prediction_mean_baseline"],
)

rmse_mean = mean_squared_error(
    validation[TARGET],
    validation["prediction_mean_baseline"],
) ** 0.5

r2_mean = r2_score(
    validation[TARGET],
    validation["prediction_mean_baseline"],
)


# ============================================================
# Median Baseline
#
# Also evaluate median because the target is strongly skewed.
# ============================================================

validation["prediction_median_baseline"] = train_median

mae_median = mean_absolute_error(
    validation[TARGET],
    validation["prediction_median_baseline"],
)

rmse_median = mean_squared_error(
    validation[TARGET],
    validation["prediction_median_baseline"],
) ** 0.5

r2_median = r2_score(
    validation[TARGET],
    validation["prediction_median_baseline"],
)


# ============================================================
# Results
# ============================================================

results = pd.DataFrame(
    [
        {
            "model": "Mean Baseline",
            "MAE": mae_mean,
            "RMSE": rmse_mean,
            "R2": r2_mean,
        },
        {
            "model": "Median Baseline",
            "MAE": mae_median,
            "RMSE": rmse_median,
            "R2": r2_median,
        },
    ]
)


print("\n========================================")
print("Simple Baseline Validation Results")
print("========================================")

print(
    results
    .round(4)
    .to_string(index=False)
)


# ============================================================
# Save
# ============================================================

OUTPUT_DIR = Path("reports/modeling")
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

results.to_csv(
    OUTPUT_DIR / "baseline_results.csv",
    index=False,
)

print("\nCreated:")
print("reports/modeling/baseline_results.csv")

print("\n========================================")
print("Baseline Modeling Completed")
print("========================================")