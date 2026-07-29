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

OUTPUT_DIR = Path("reports/modeling")
FIGURE_DIR = Path("reports/figures/model_error_analysis")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


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


MODELS = {
    "original_context": {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 4,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
    },

    "tuned_context": {
        "n_estimators": 200,
        "learning_rate": 0.03,
        "max_depth": 5,
        "subsample": 1.0,
        "colsample_bytree": 1.0,
    },
}


# ============================================================
# Load
# ============================================================

print("Loading datasets...")

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALIDATION_FILE)

print(f"Train rows: {len(train):,}")
print(f"Validation rows: {len(validation):,}")

X_train = train[FEATURES]
y_train = train[TARGET]

X_val = validation[FEATURES]
y_val = validation[TARGET]


# ============================================================
# Metric Helper
# ============================================================

def calculate_metrics(actual, predicted):

    mae = mean_absolute_error(
        actual,
        predicted,
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted,
        )
    )

    r2 = r2_score(
        actual,
        predicted,
    )

    return {
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
    }


# ============================================================
# Error Analysis
# ============================================================

comparison_rows = []

for model_name, params in MODELS.items():

    print("\n========================================")
    print(model_name)
    print("========================================")

    model = XGBRegressor(
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
        **params,
    )

    model.fit(
        X_train,
        y_train,
    )

    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)

    train_metrics = calculate_metrics(
        y_train,
        train_pred,
    )

    val_metrics = calculate_metrics(
        y_val,
        val_pred,
    )


    # --------------------------------------------------------
    # Train vs Validation
    # --------------------------------------------------------

    print("\nTrain:")
    print(f"MAE : {train_metrics['MAE']:.4f}")
    print(f"RMSE: {train_metrics['RMSE']:.4f}")
    print(f"R²  : {train_metrics['R2']:.4f}")

    print("\nValidation:")
    print(f"MAE : {val_metrics['MAE']:.4f}")
    print(f"RMSE: {val_metrics['RMSE']:.4f}")
    print(f"R²  : {val_metrics['R2']:.4f}")

    print("\nGaps:")
    print(
        "MAE gap:",
        round(
            val_metrics["MAE"]
            - train_metrics["MAE"],
            4,
        ),
    )

    print(
        "RMSE gap:",
        round(
            val_metrics["RMSE"]
            - train_metrics["RMSE"],
            4,
        ),
    )

    print(
        "R² gap:",
        round(
            train_metrics["R2"]
            - val_metrics["R2"],
            4,
        ),
    )


    comparison_rows.append({
        "model": model_name,

        "train_MAE":
            train_metrics["MAE"],

        "validation_MAE":
            val_metrics["MAE"],

        "MAE_gap":
            val_metrics["MAE"]
            - train_metrics["MAE"],

        "train_RMSE":
            train_metrics["RMSE"],

        "validation_RMSE":
            val_metrics["RMSE"],

        "RMSE_gap":
            val_metrics["RMSE"]
            - train_metrics["RMSE"],

        "train_R2":
            train_metrics["R2"],

        "validation_R2":
            val_metrics["R2"],

        "R2_gap":
            train_metrics["R2"]
            - val_metrics["R2"],
    })


    # ========================================================
    # Validation Prediction Table
    # ========================================================

    result = validation.copy()

    result["prediction"] = val_pred

    result["residual"] = (
        result[TARGET]
        - result["prediction"]
    )

    result["absolute_error"] = (
        result["residual"].abs()
    )


    # ========================================================
    # Trip Length Groups
    # ========================================================

    result["distance_group"] = pd.cut(
        result["trip_distance_km"],
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

    distance_error = (
        result
        .groupby(
            "distance_group",
            observed=False,
        )
        .agg(
            trips=("trip_id", "count"),
            mean_actual_fuel=(TARGET, "mean"),
            MAE=("absolute_error", "mean"),
            median_absolute_error=(
                "absolute_error",
                "median",
            ),
        )
        .reset_index()
    )


    print("\nDistance-Level Error:")
    print(
        distance_error
        .round(4)
        .to_string(index=False)
    )


    # ========================================================
    # Vehicle-Level Error
    # ========================================================

    vehicle_error = (
        result
        .groupby("vehicle_id")
        .agg(
            trips=("trip_id", "count"),
            mean_actual_fuel=(TARGET, "mean"),
            MAE=("absolute_error", "mean"),
            RMSE=(
                "residual",
                lambda x: np.sqrt(
                    np.mean(x ** 2)
                ),
            ),
        )
        .reset_index()
        .sort_values(
            "MAE",
            ascending=False,
        )
    )


    print("\nVehicle-Level Error:")
    print(
        vehicle_error
        .round(4)
        .to_string(index=False)
    )


    # ========================================================
    # Period-Level Error
    # ========================================================

    period_error = (
        result
        .groupby("period")
        .agg(
            trips=("trip_id", "count"),
            mean_actual_fuel=(TARGET, "mean"),
            MAE=("absolute_error", "mean"),
            RMSE=(
                "residual",
                lambda x: np.sqrt(
                    np.mean(x ** 2)
                ),
            ),
        )
        .reset_index()
        .sort_values(
            "MAE",
            ascending=False,
        )
    )


    print("\nPeriod-Level Error:")
    print(
        period_error
        .round(4)
        .to_string(index=False)
    )


    # ========================================================
    # Extreme Errors
    # ========================================================

    extreme_errors = (
        result
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

    print("\nTop 10 Extreme Errors:")
    print(
        extreme_errors[
            extreme_columns
        ]
        .head(10)
        .round(4)
        .to_string(index=False)
    )


    # ========================================================
    # Save Tables
    # ========================================================

    result.to_csv(
        OUTPUT_DIR
        / f"{model_name}_error_predictions.csv",
        index=False,
    )

    distance_error.to_csv(
        OUTPUT_DIR
        / f"{model_name}_distance_errors.csv",
        index=False,
    )

    vehicle_error.to_csv(
        OUTPUT_DIR
        / f"{model_name}_vehicle_errors.csv",
        index=False,
    )

    period_error.to_csv(
        OUTPUT_DIR
        / f"{model_name}_period_errors.csv",
        index=False,
    )

    extreme_errors[
        extreme_columns
    ].to_csv(
        OUTPUT_DIR
        / f"{model_name}_extreme_errors.csv",
        index=False,
    )


    # ========================================================
    # Figure 1 — Actual vs Predicted
    # ========================================================

    plt.figure(figsize=(7, 6))

    plt.scatter(
        result[TARGET],
        result["prediction"],
        alpha=0.4,
    )

    min_value = min(
        result[TARGET].min(),
        result["prediction"].min(),
    )

    max_value = max(
        result[TARGET].max(),
        result["prediction"].max(),
    )

    plt.plot(
        [min_value, max_value],
        [min_value, max_value],
        linestyle="--",
    )

    plt.xlabel("Actual Fuel Used (L)")
    plt.ylabel("Predicted Fuel Used (L)")
    plt.title(
        f"Actual vs Predicted — {model_name}"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR
        / f"{model_name}_actual_vs_predicted.png",
        dpi=150,
    )

    plt.close()


    # ========================================================
    # Figure 2 — Residual Distribution
    # ========================================================

    plt.figure(figsize=(7, 5))

    plt.hist(
        result["residual"],
        bins=50,
    )

    plt.xlabel(
        "Residual (Actual - Predicted)"
    )

    plt.ylabel("Trips")

    plt.title(
        f"Residual Distribution — {model_name}"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR
        / f"{model_name}_residual_distribution.png",
        dpi=150,
    )

    plt.close()


    # ========================================================
    # Figure 3 — Error vs Distance
    # ========================================================

    plt.figure(figsize=(7, 5))

    plt.scatter(
        result["trip_distance_km"],
        result["absolute_error"],
        alpha=0.35,
    )

    plt.xlabel("Trip Distance (km)")
    plt.ylabel("Absolute Error (L)")

    plt.title(
        f"Absolute Error vs Trip Distance — {model_name}"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR
        / f"{model_name}_error_vs_distance.png",
        dpi=150,
    )

    plt.close()


# ============================================================
# Final Candidate Comparison
# ============================================================

comparison = pd.DataFrame(
    comparison_rows
)

print("\n========================================")
print("Final Candidate Overfitting Comparison")
print("========================================")

print(
    comparison
    .round(4)
    .to_string(index=False)
)

comparison.to_csv(
    OUTPUT_DIR
    / "xgboost_overfitting_comparison.csv",
    index=False,
)


print("\nCreated:")
print(
    "reports/modeling/"
    "xgboost_overfitting_comparison.csv"
)
print(
    "reports/modeling/"
    "*_distance_errors.csv"
)
print(
    "reports/modeling/"
    "*_vehicle_errors.csv"
)
print(
    "reports/modeling/"
    "*_period_errors.csv"
)
print(
    "reports/modeling/"
    "*_extreme_errors.csv"
)
print(
    "reports/figures/model_error_analysis/"
)

print("\n========================================")
print("Overfitting & Error Analysis Completed")
print("========================================")

print(
    "IMPORTANT: Final chronological test set "
    "was not used."
)