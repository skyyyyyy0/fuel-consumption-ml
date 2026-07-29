from pathlib import Path

import pandas as pd
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

OUTPUT_DIR = Path("reports/modeling")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Configuration
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


# Best tuned parameters from validation tuning
BEST_PARAMS = {
    "n_estimators": 200,
    "learning_rate": 0.03,
    "max_depth": 5,
    "subsample": 1.0,
    "colsample_bytree": 1.0,
}


# ============================================================
# Load development data
#
# Train + Validation can now be combined for this separate
# vehicle-generalization experiment.
#
# test.csv remains untouched.
# ============================================================

print("Loading development datasets...")

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALIDATION_FILE)

development = pd.concat(
    [train, validation],
    ignore_index=True,
)

print(f"Development rows: {len(development):,}")
print(f"Vehicles: {development['vehicle_id'].nunique()}")


# ============================================================
# Leave-One-Vehicle-Out Evaluation
# ============================================================

vehicles = sorted(
    development["vehicle_id"].unique()
)

results = []
all_predictions = []


for vehicle in vehicles:

    print("\n========================================")
    print(f"Holdout Vehicle: {vehicle}")
    print("========================================")

    train_vehicle = development[
        development["vehicle_id"] != vehicle
    ].copy()

    holdout = development[
        development["vehicle_id"] == vehicle
    ].copy()

    X_train = train_vehicle[FEATURES]
    y_train = train_vehicle[TARGET]

    X_holdout = holdout[FEATURES]
    y_holdout = holdout[TARGET]


    model = XGBRegressor(
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
        **BEST_PARAMS,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_holdout
    )


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    mae = mean_absolute_error(
        y_holdout,
        predictions,
    )

    rmse = (
        mean_squared_error(
            y_holdout,
            predictions,
        )
        ** 0.5
    )

    r2 = r2_score(
        y_holdout,
        predictions,
    )


    print(f"Holdout rows: {len(holdout):,}")
    print(f"MAE : {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²  : {r2:.4f}")


    results.append({
        "vehicle_id": vehicle,
        "holdout_rows": len(holdout),
        "actual_mean_fuel": y_holdout.mean(),
        "actual_median_fuel": y_holdout.median(),
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
    })


    # --------------------------------------------------------
    # Save prediction-level results
    # --------------------------------------------------------

    prediction_df = holdout[
        [
            "trip_id",
            "vehicle_id",
            "period",
            TARGET,
        ]
    ].copy()

    prediction_df["prediction"] = predictions

    prediction_df["residual"] = (
        prediction_df[TARGET]
        - prediction_df["prediction"]
    )

    prediction_df["absolute_error"] = (
        prediction_df["residual"].abs()
    )

    all_predictions.append(
        prediction_df
    )


# ============================================================
# Results
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    "MAE"
).reset_index(drop=True)


print("\n========================================")
print("Vehicle Holdout Results")
print("========================================")

print(
    results_df
    .round(4)
    .to_string(index=False)
)


# ============================================================
# Overall Holdout Performance
# ============================================================

predictions_df = pd.concat(
    all_predictions,
    ignore_index=True,
)

overall_mae = mean_absolute_error(
    predictions_df[TARGET],
    predictions_df["prediction"],
)

overall_rmse = (
    mean_squared_error(
        predictions_df[TARGET],
        predictions_df["prediction"],
    )
    ** 0.5
)

overall_r2 = r2_score(
    predictions_df[TARGET],
    predictions_df["prediction"],
)


print("\n========================================")
print("Overall Unseen-Vehicle Performance")
print("========================================")

print(f"MAE : {overall_mae:.4f}")
print(f"RMSE: {overall_rmse:.4f}")
print(f"R²  : {overall_r2:.4f}")

print(
    f"Median vehicle MAE: "
    f"{results_df['MAE'].median():.4f}"
)

print(
    f"Best vehicle MAE: "
    f"{results_df['MAE'].min():.4f}"
)

print(
    f"Worst vehicle MAE: "
    f"{results_df['MAE'].max():.4f}"
)


# ============================================================
# Save
# ============================================================

results_df.to_csv(
    OUTPUT_DIR / "vehicle_holdout_results.csv",
    index=False,
)

predictions_df.to_csv(
    OUTPUT_DIR / "vehicle_holdout_predictions.csv",
    index=False,
)


print("\nCreated:")
print(
    "reports/modeling/"
    "vehicle_holdout_results.csv"
)

print(
    "reports/modeling/"
    "vehicle_holdout_predictions.csv"
)

print("\n========================================")
print("Vehicle Holdout Test Completed")
print("========================================")

print(
    "IMPORTANT: Final chronological "
    "test.csv was not used."
)