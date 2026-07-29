from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from xgboost import XGBRegressor
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
TEST_FILE = Path("data/modeling/test.csv")

OUTPUT_DIR = Path("reports/modeling")
FIGURE_DIR = Path("reports/figures/final_model")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Final Frozen Configuration
# ============================================================

TARGET = "trip_fuel_used_liter"

FEATURES = [
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

FINAL_PARAMS = {
    "n_estimators": 200,
    "learning_rate": 0.03,
    "max_depth": 5,
    "subsample": 1.0,
    "colsample_bytree": 1.0,
    "random_state": 42,
}


# ============================================================
# Load Data
# ============================================================

print("Loading frozen development and test datasets...")

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALIDATION_FILE)
test = pd.read_csv(TEST_FILE)

development = pd.concat(
    [train, validation],
    ignore_index=True,
)

print(f"Train rows: {len(train):,}")
print(f"Validation rows: {len(validation):,}")
print(f"Development rows: {len(development):,}")
print(f"Test rows: {len(test):,}")

print(f"Development vehicles: {development['vehicle_id'].nunique()}")
print(f"Test vehicles: {test['vehicle_id'].nunique()}")


# ============================================================
# Prepare X / y
# ============================================================

X_dev = development[FEATURES]
y_dev = development[TARGET]

X_test = test[FEATURES]
y_test = test[TARGET]


# ============================================================
# Train Frozen Final Model
# ============================================================

print("\n========================================")
print("Training Frozen Final Model")
print("========================================")

print("Model: Tuned Context XGBoost")
print(f"Features: {len(FEATURES)}")

model = XGBRegressor(
    objective="reg:squarederror",
    n_jobs=-1,
    **FINAL_PARAMS,
)

model.fit(
    X_dev,
    y_dev,
)


# ============================================================
# Final Test Prediction
# ============================================================

test_pred = model.predict(X_test)

test_mae = mean_absolute_error(
    y_test,
    test_pred,
)

test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        test_pred,
    )
)

test_r2 = r2_score(
    y_test,
    test_pred,
)


print("\n========================================")
print("FINAL TEST RESULTS")
print("========================================")

print(f"MAE : {test_mae:.4f} L")
print(f"RMSE: {test_rmse:.4f} L")
print(f"R²  : {test_r2:.4f}")


# ============================================================
# Prediction Table
# ============================================================

results = test.copy()

results["prediction"] = test_pred

results["residual"] = (
    results[TARGET]
    - results["prediction"]
)

results["absolute_error"] = (
    results["residual"].abs()
)

results["squared_error"] = (
    results["residual"] ** 2
)


# ============================================================
# Vehicle-Level Performance
# ============================================================

vehicle_rows = []

for vehicle_id, group in results.groupby("vehicle_id"):

    vehicle_mae = mean_absolute_error(
        group[TARGET],
        group["prediction"],
    )

    vehicle_rmse = np.sqrt(
        mean_squared_error(
            group[TARGET],
            group["prediction"],
        )
    )

    if len(group) > 1:
        vehicle_r2 = r2_score(
            group[TARGET],
            group["prediction"],
        )
    else:
        vehicle_r2 = np.nan

    vehicle_rows.append({
        "vehicle_id": vehicle_id,
        "trips": len(group),
        "mean_actual_fuel": group[TARGET].mean(),
        "median_actual_fuel": group[TARGET].median(),
        "MAE": vehicle_mae,
        "RMSE": vehicle_rmse,
        "R2": vehicle_r2,
    })


vehicle_results = pd.DataFrame(
    vehicle_rows
).sort_values(
    "MAE",
    ascending=False,
)


print("\n========================================")
print("Vehicle-Level Test Performance")
print("========================================")

print(
    vehicle_results
    .round(4)
    .to_string(index=False)
)


# ============================================================
# Distance-Level Performance
# ============================================================

results["distance_group"] = pd.cut(
    results["trip_distance_km"],
    bins=[
        0,
        0.5,
        1,
        5,
        20,
        50,
        np.inf,
    ],
    labels=[
        "0-0.5 km",
        "0.5-1 km",
        "1-5 km",
        "5-20 km",
        "20-50 km",
        "50+ km",
    ],
    include_lowest=True,
)

distance_results = (
    results
    .groupby(
        "distance_group",
        observed=False,
    )
    .agg(
        trips=(TARGET, "size"),
        mean_actual_fuel=(TARGET, "mean"),
        MAE=("absolute_error", "mean"),
        median_absolute_error=(
            "absolute_error",
            "median",
        ),
    )
    .reset_index()
)


print("\n========================================")
print("Distance-Level Test Performance")
print("========================================")

print(
    distance_results
    .round(4)
    .to_string(index=False)
)


# ============================================================
# Largest Final Test Errors
# ============================================================

extreme_errors = (
    results
    .sort_values(
        "absolute_error",
        ascending=False,
    )
    .head(20)
)

extreme_columns = [
    "trip_id",
    "vehicle_id",
    "period",
    "trip_distance_km",
    "trip_duration_min",
    TARGET,
    "prediction",
    "residual",
    "absolute_error",
]


print("\n========================================")
print("Top 10 Final Test Errors")
print("========================================")

print(
    extreme_errors[
        extreme_columns
    ]
    .head(10)
    .round(4)
    .to_string(index=False)
)


# ============================================================
# Feature Importance
# ============================================================

feature_importance = pd.DataFrame({
    "feature": FEATURES,
    "importance": model.feature_importances_,
}).sort_values(
    "importance",
    ascending=False,
)


print("\n========================================")
print("Final Model Feature Importance")
print("========================================")

print(
    feature_importance
    .round(4)
    .to_string(index=False)
)


# ============================================================
# Save Final Results
# ============================================================

summary = pd.DataFrame([
    {
        "model": "Tuned Context XGBoost",
        "development_rows": len(development),
        "test_rows": len(test),
        "num_features": len(FEATURES),
        "test_MAE": test_mae,
        "test_RMSE": test_rmse,
        "test_R2": test_r2,
    }
])

summary.to_csv(
    OUTPUT_DIR / "final_test_results.csv",
    index=False,
)

results.to_csv(
    OUTPUT_DIR / "final_test_predictions.csv",
    index=False,
)

vehicle_results.to_csv(
    OUTPUT_DIR / "final_test_vehicle_results.csv",
    index=False,
)

distance_results.to_csv(
    OUTPUT_DIR / "final_test_distance_results.csv",
    index=False,
)

extreme_errors[
    extreme_columns
].to_csv(
    OUTPUT_DIR / "final_test_extreme_errors.csv",
    index=False,
)

feature_importance.to_csv(
    OUTPUT_DIR / "final_model_feature_importance.csv",
    index=False,
)


# ============================================================
# Figure — Actual vs Predicted
# ============================================================

plt.figure(figsize=(7, 6))

plt.scatter(
    results[TARGET],
    results["prediction"],
    alpha=0.4,
)

min_value = min(
    results[TARGET].min(),
    results["prediction"].min(),
)

max_value = max(
    results[TARGET].max(),
    results["prediction"].max(),
)

plt.plot(
    [min_value, max_value],
    [min_value, max_value],
    linestyle="--",
)

plt.xlabel("Actual Fuel Used (L)")
plt.ylabel("Predicted Fuel Used (L)")
plt.title("Final Test — Actual vs Predicted")

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "actual_vs_predicted.png",
    dpi=150,
)

plt.close()


# ============================================================
# Figure — Residual Distribution
# ============================================================

plt.figure(figsize=(7, 5))

plt.hist(
    results["residual"],
    bins=50,
)

plt.xlabel("Residual (Actual - Predicted)")
plt.ylabel("Trips")
plt.title("Final Test — Residual Distribution")

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "residual_distribution.png",
    dpi=150,
)

plt.close()


# ============================================================
# Figure — Absolute Error vs Distance
# ============================================================

plt.figure(figsize=(7, 5))

plt.scatter(
    results["trip_distance_km"],
    results["absolute_error"],
    alpha=0.35,
)

plt.xlabel("Trip Distance (km)")
plt.ylabel("Absolute Error (L)")
plt.title("Final Test — Absolute Error vs Distance")

plt.tight_layout()

plt.savefig(
    FIGURE_DIR / "absolute_error_vs_distance.png",
    dpi=150,
)

plt.close()


# ============================================================
# Complete
# ============================================================

print("\nCreated:")
print("reports/modeling/final_test_results.csv")
print("reports/modeling/final_test_predictions.csv")
print("reports/modeling/final_test_vehicle_results.csv")
print("reports/modeling/final_test_distance_results.csv")
print("reports/modeling/final_test_extreme_errors.csv")
print("reports/modeling/final_model_feature_importance.csv")
print("reports/figures/final_model/")

print("\n========================================")
print("FINAL TEST EVALUATION COMPLETED")
print("========================================")

print(
    "The frozen final model has now been evaluated "
    "on the untouched chronological Test set."
)

print(
    "Do NOT perform additional tuning based on these results."
)