from pathlib import Path

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
FIGURE_DIR = Path("reports/figures/xgboost")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Target
# ============================================================

TARGET = "trip_fuel_used_liter"


# ============================================================
# Feature Sets
# ============================================================

BASELINE_FEATURES = [
    "trip_distance_km",
    "trip_duration_min",
]

EXTENDED_FEATURES = BASELINE_FEATURES + [
    "avg_speed_kmh",
    "max_speed_kmh",
    "speed_std",
    "avg_rpm",
    "max_rpm",
    "rpm_std",
    "high_rpm_ratio",
    "idle_ratio",
]

CONTEXT_FEATURES = EXTENDED_FEATURES + [
    "trip_hour",
    "day_of_week",
    "is_weekend",
]

FEATURE_SETS = {
    "Baseline": BASELINE_FEATURES,
    "Extended": EXTENDED_FEATURES,
    "Context": CONTEXT_FEATURES,
}


# ============================================================
# Load
# ============================================================

print("Loading train and validation datasets...")

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VALIDATION_FILE)

print(f"Train rows: {len(train):,}")
print(f"Validation rows: {len(validation):,}")


# ============================================================
# Training Function
# ============================================================

def train_and_evaluate(name, features):

    print("\n========================================")
    print(f"{name} XGBoost")
    print("========================================")

    X_train = train[features]
    y_train = train[TARGET]

    X_val = validation[features]
    y_val = validation[TARGET]

    model = XGBRegressor(
        objective="reg:squarederror",

        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,

        subsample=0.8,
        colsample_bytree=0.8,

        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)


    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    train_mae = mean_absolute_error(
        y_train,
        train_pred,
    )

    train_rmse = mean_squared_error(
        y_train,
        train_pred,
    ) ** 0.5

    train_r2 = r2_score(
        y_train,
        train_pred,
    )

    val_mae = mean_absolute_error(
        y_val,
        val_pred,
    )

    val_rmse = mean_squared_error(
        y_val,
        val_pred,
    ) ** 0.5

    val_r2 = r2_score(
        y_val,
        val_pred,
    )


    print(f"Features: {len(features)}")

    print("\nTrain:")
    print(f"MAE : {train_mae:.4f}")
    print(f"RMSE: {train_rmse:.4f}")
    print(f"R²  : {train_r2:.4f}")

    print("\nValidation:")
    print(f"MAE : {val_mae:.4f}")
    print(f"RMSE: {val_rmse:.4f}")
    print(f"R²  : {val_r2:.4f}")


    # --------------------------------------------------------
    # Feature Importance
    # --------------------------------------------------------

    importance_df = pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_,
    }).sort_values(
        "importance",
        ascending=False,
    )

    print("\nFeature Importance:")

    print(
        importance_df
        .round(4)
        .to_string(index=False)
    )

    importance_df.to_csv(
        OUTPUT_DIR
        / f"xgboost_{name.lower()}_feature_importance.csv",
        index=False,
    )


    # --------------------------------------------------------
    # Validation predictions
    # --------------------------------------------------------

    residual_df = validation[
        [
            "trip_id",
            "vehicle_id",
            "period",
            TARGET,
        ]
    ].copy()

    residual_df["prediction"] = val_pred

    residual_df["residual"] = (
        residual_df[TARGET]
        - residual_df["prediction"]
    )

    residual_df.to_csv(
        OUTPUT_DIR
        / f"xgboost_{name.lower()}_validation_predictions.csv",
        index=False,
    )


    # --------------------------------------------------------
    # Actual vs Predicted
    # --------------------------------------------------------

    plt.figure(figsize=(7, 6))

    plt.scatter(
        y_val,
        val_pred,
        alpha=0.25,
        s=10,
    )

    minimum = min(
        y_val.min(),
        val_pred.min(),
    )

    maximum = max(
        y_val.max(),
        val_pred.max(),
    )

    plt.plot(
        [minimum, maximum],
        [minimum, maximum],
    )

    plt.xlabel("Actual Fuel (L)")
    plt.ylabel("Predicted Fuel (L)")
    plt.title(
        f"{name} XGBoost\n"
        "Actual vs Predicted"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR
        / f"{name.lower()}_actual_vs_predicted.png",
        dpi=150,
    )

    plt.close()


    # --------------------------------------------------------
    # Residual distribution
    # --------------------------------------------------------

    residuals = y_val - val_pred

    plt.figure(figsize=(7, 5))

    plt.hist(
        residuals,
        bins=60,
    )

    plt.xlabel("Residual (Actual - Predicted)")
    plt.ylabel("Trip Count")
    plt.title(
        f"{name} XGBoost\n"
        "Validation Residual Distribution"
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_DIR
        / f"{name.lower()}_residual_distribution.png",
        dpi=150,
    )

    plt.close()


    return {
        "model": f"XGBoost - {name}",
        "feature_set": name,
        "num_features": len(features),

        "train_MAE": train_mae,
        "train_RMSE": train_rmse,
        "train_R2": train_r2,

        "validation_MAE": val_mae,
        "validation_RMSE": val_rmse,
        "validation_R2": val_r2,
    }


# ============================================================
# Run
# ============================================================

results = []

for name, features in FEATURE_SETS.items():

    result = train_and_evaluate(
        name,
        features,
    )

    results.append(result)


# ============================================================
# Comparison
# ============================================================

results_df = pd.DataFrame(results)

print("\n========================================")
print("XGBoost Comparison")
print("========================================")

print(
    results_df
    .round(4)
    .to_string(index=False)
)


# ============================================================
# Incremental Improvement
# ============================================================

baseline = results_df[
    results_df["feature_set"] == "Baseline"
].iloc[0]

extended = results_df[
    results_df["feature_set"] == "Extended"
].iloc[0]

context = results_df[
    results_df["feature_set"] == "Context"
].iloc[0]


print("\n========================================")
print("Incremental Validation Improvement")
print("========================================")

print("\nBaseline -> Extended")

print(
    "MAE improvement:",
    round(
        baseline["validation_MAE"]
        - extended["validation_MAE"],
        4,
    ),
)

print(
    "RMSE improvement:",
    round(
        baseline["validation_RMSE"]
        - extended["validation_RMSE"],
        4,
    ),
)

print(
    "R² improvement:",
    round(
        extended["validation_R2"]
        - baseline["validation_R2"],
        4,
    ),
)


print("\nExtended -> Context")

print(
    "MAE improvement:",
    round(
        extended["validation_MAE"]
        - context["validation_MAE"],
        4,
    ),
)

print(
    "RMSE improvement:",
    round(
        extended["validation_RMSE"]
        - context["validation_RMSE"],
        4,
    ),
)

print(
    "R² improvement:",
    round(
        context["validation_R2"]
        - extended["validation_R2"],
        4,
    ),
)


# ============================================================
# Save
# ============================================================

results_df.to_csv(
    OUTPUT_DIR / "xgboost_results.csv",
    index=False,
)

print("\nCreated:")
print("reports/modeling/xgboost_results.csv")
print("reports/modeling/xgboost_*_feature_importance.csv")
print("reports/modeling/xgboost_*_validation_predictions.csv")
print("reports/figures/xgboost/")

print("\n========================================")
print("XGBoost Modeling Completed")
print("========================================")