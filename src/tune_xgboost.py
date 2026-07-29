from itertools import product
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


# ============================================================
# Load
# ============================================================

print("Loading train and validation datasets...")

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALIDATION_FILE)

X_train = train[FEATURES]
y_train = train[TARGET]

X_val = validation[FEATURES]
y_val = validation[TARGET]

print(f"Train rows: {len(train):,}")
print(f"Validation rows: {len(validation):,}")


# ============================================================
# Small Parameter Grid
#
# Keep tuning intentionally limited.
# ============================================================

param_grid = {
    "n_estimators": [200, 300, 500],
    "learning_rate": [0.03, 0.05, 0.08],
    "max_depth": [3, 4, 5],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
}


combinations = list(
    product(
        param_grid["n_estimators"],
        param_grid["learning_rate"],
        param_grid["max_depth"],
        param_grid["subsample"],
        param_grid["colsample_bytree"],
    )
)

print(f"\nParameter combinations: {len(combinations)}")


# ============================================================
# Tuning
# ============================================================

results = []

for i, (
    n_estimators,
    learning_rate,
    max_depth,
    subsample,
    colsample_bytree,
) in enumerate(combinations, start=1):

    print(
        f"[{i}/{len(combinations)}] "
        f"n={n_estimators}, "
        f"lr={learning_rate}, "
        f"depth={max_depth}, "
        f"subsample={subsample}, "
        f"colsample={colsample_bytree}"
    )

    model = XGBRegressor(
        objective="reg:squarederror",

        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,

        subsample=subsample,
        colsample_bytree=colsample_bytree,

        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)

    train_mae = mean_absolute_error(
        y_train,
        train_pred,
    )

    val_mae = mean_absolute_error(
        y_val,
        val_pred,
    )

    val_rmse = (
        mean_squared_error(
            y_val,
            val_pred,
        )
        ** 0.5
    )

    val_r2 = r2_score(
        y_val,
        val_pred,
    )

    results.append({
        "n_estimators": n_estimators,
        "learning_rate": learning_rate,
        "max_depth": max_depth,
        "subsample": subsample,
        "colsample_bytree": colsample_bytree,

        "train_MAE": train_mae,
        "validation_MAE": val_mae,
        "validation_RMSE": val_rmse,
        "validation_R2": val_r2,

        "mae_gap": val_mae - train_mae,
    })


# ============================================================
# Results
# ============================================================

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    [
        "validation_MAE",
        "validation_RMSE",
    ]
).reset_index(drop=True)


print("\n========================================")
print("Top 15 Parameter Combinations")
print("========================================")

print(
    results_df
    .head(15)
    .round(5)
    .to_string(index=False)
)


# ============================================================
# Best Model
# ============================================================

best = results_df.iloc[0]

print("\n========================================")
print("Best Hyperparameters")
print("========================================")

print(
    f"n_estimators     : {int(best['n_estimators'])}"
)

print(
    f"learning_rate    : {best['learning_rate']}"
)

print(
    f"max_depth        : {int(best['max_depth'])}"
)

print(
    f"subsample        : {best['subsample']}"
)

print(
    f"colsample_bytree : {best['colsample_bytree']}"
)

print("\nValidation Performance:")

print(
    f"MAE : {best['validation_MAE']:.4f}"
)

print(
    f"RMSE: {best['validation_RMSE']:.4f}"
)

print(
    f"R²  : {best['validation_R2']:.4f}"
)

print(
    f"Train-Validation MAE Gap: "
    f"{best['mae_gap']:.4f}"
)


# ============================================================
# Compare Against Current XGBoost
# ============================================================

CURRENT_MAE = 0.3791
CURRENT_RMSE = 1.6833
CURRENT_R2 = 0.9102

print("\n========================================")
print("Improvement vs Current Context XGBoost")
print("========================================")

print(
    "MAE improvement:",
    round(
        CURRENT_MAE
        - best["validation_MAE"],
        4,
    ),
)

print(
    "RMSE improvement:",
    round(
        CURRENT_RMSE
        - best["validation_RMSE"],
        4,
    ),
)

print(
    "R² improvement:",
    round(
        best["validation_R2"]
        - CURRENT_R2,
        4,
    ),
)


# ============================================================
# Save
# ============================================================

results_df.to_csv(
    OUTPUT_DIR / "xgboost_tuning_results.csv",
    index=False,
)

best.to_frame().T.to_csv(
    OUTPUT_DIR / "xgboost_best_parameters.csv",
    index=False,
)

print("\nCreated:")
print("reports/modeling/xgboost_tuning_results.csv")
print("reports/modeling/xgboost_best_parameters.csv")

print("\n========================================")
print("XGBoost Hyperparameter Tuning Completed")
print("========================================")

print(
    "IMPORTANT: Test set was not used "
    "during hyperparameter tuning."
)