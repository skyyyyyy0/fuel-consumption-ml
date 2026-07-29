from pathlib import Path

import pandas as pd


# ============================================================
# Paths
# ============================================================

MODELING_DIR = Path("reports/modeling")
OUTPUT_FILE = Path("reports/model_comparison.csv")


# ============================================================
# Load Existing Results
# ============================================================

print("Loading existing model results...")

baseline = pd.read_csv(
    MODELING_DIR / "baseline_results.csv"
)

linear = pd.read_csv(
    MODELING_DIR / "linear_regression_results.csv"
)

xgb = pd.read_csv(
    MODELING_DIR / "xgboost_results.csv"
)

tuning = pd.read_csv(
    MODELING_DIR / "xgboost_tuning_results.csv"
)


# ============================================================
# Standardize Simple Baseline
# ============================================================

baseline_rows = []

for _, row in baseline.iterrows():

    baseline_rows.append({
        "model": row["model"],
        "feature_set": "None",
        "num_features": 0,
        "train_MAE": None,
        "train_RMSE": None,
        "train_R2": None,
        "validation_MAE": row["MAE"],
        "validation_RMSE": row["RMSE"],
        "validation_R2": row["R2"],
    })

baseline_df = pd.DataFrame(baseline_rows)


# ============================================================
# Standardize Linear Regression
# ============================================================

linear_df = linear[
    [
        "model",
        "feature_set",
        "num_features",
        "train_MAE",
        "train_RMSE",
        "train_R2",
        "validation_MAE",
        "validation_RMSE",
        "validation_R2",
    ]
].copy()


# ============================================================
# Standardize XGBoost
# ============================================================

xgb_df = xgb[
    [
        "model",
        "feature_set",
        "num_features",
        "train_MAE",
        "train_RMSE",
        "train_R2",
        "validation_MAE",
        "validation_RMSE",
        "validation_R2",
    ]
].copy()


# ============================================================
# Add Best Tuned XGBoost
# ============================================================

best_tuned = tuning.sort_values(
    ["validation_MAE", "validation_RMSE"]
).iloc[0]

tuned_df = pd.DataFrame(
    [
        {
            "model": "XGBoost - Tuned Context",
            "feature_set": "Context",
            "num_features": 13,

            "train_MAE": best_tuned["train_MAE"],

            # Tuning output did not store train RMSE / R2.
            "train_RMSE": None,
            "train_R2": None,

            "validation_MAE":
                best_tuned["validation_MAE"],

            "validation_RMSE":
                best_tuned["validation_RMSE"],

            "validation_R2":
                best_tuned["validation_R2"],
        }
    ]
)


# ============================================================
# Combine
# ============================================================

comparison = pd.concat(
    [
        baseline_df,
        linear_df,
        xgb_df,
        tuned_df,
    ],
    ignore_index=True,
)


# ============================================================
# Train / Validation Gap
# ============================================================

comparison["MAE_gap"] = (
    comparison["validation_MAE"]
    - comparison["train_MAE"]
)

comparison["RMSE_gap"] = (
    comparison["validation_RMSE"]
    - comparison["train_RMSE"]
)

comparison["R2_gap"] = (
    comparison["train_R2"]
    - comparison["validation_R2"]
)


# ============================================================
# Rank Models
# ============================================================

comparison["MAE_rank"] = (
    comparison["validation_MAE"]
    .rank(method="min")
    .astype(int)
)

comparison["RMSE_rank"] = (
    comparison["validation_RMSE"]
    .rank(method="min")
    .astype(int)
)

comparison["R2_rank"] = (
    comparison["validation_R2"]
    .rank(
        method="min",
        ascending=False,
    )
    .astype(int)
)


comparison = comparison.sort_values(
    "validation_MAE"
).reset_index(drop=True)


# ============================================================
# Display
# ============================================================

print("\n========================================")
print("Model Comparison")
print("========================================")

display_columns = [
    "model",
    "feature_set",
    "num_features",
    "validation_MAE",
    "validation_RMSE",
    "validation_R2",
    "MAE_gap",
]

print(
    comparison[display_columns]
    .round(4)
    .to_string(index=False)
)


# ============================================================
# Key Comparisons
# ============================================================

print("\n========================================")
print("Key Model Comparisons")
print("========================================")


def get_model(name):
    return comparison[
        comparison["model"] == name
    ].iloc[0]


linear_baseline = get_model(
    "Linear Regression - Baseline"
)

linear_extended = get_model(
    "Linear Regression - Extended"
)

linear_context = get_model(
    "Linear Regression - Context"
)

xgb_baseline = get_model(
    "XGBoost - Baseline"
)

xgb_extended = get_model(
    "XGBoost - Extended"
)

xgb_context = get_model(
    "XGBoost - Context"
)

xgb_tuned = get_model(
    "XGBoost - Tuned Context"
)


# ------------------------------------------------------------
# Linear Regression Feature Value
# ------------------------------------------------------------

print("\nLinear Regression: Baseline -> Extended")

print(
    "MAE improvement:",
    round(
        linear_baseline["validation_MAE"]
        - linear_extended["validation_MAE"],
        4,
    ),
)

print("\nLinear Regression: Extended -> Context")

print(
    "MAE improvement:",
    round(
        linear_extended["validation_MAE"]
        - linear_context["validation_MAE"],
        4,
    ),
)


# ------------------------------------------------------------
# XGBoost Feature Value
# ------------------------------------------------------------

print("\nXGBoost: Baseline -> Extended")

print(
    "MAE improvement:",
    round(
        xgb_baseline["validation_MAE"]
        - xgb_extended["validation_MAE"],
        4,
    ),
)

print(
    "RMSE improvement:",
    round(
        xgb_baseline["validation_RMSE"]
        - xgb_extended["validation_RMSE"],
        4,
    ),
)

print(
    "R² improvement:",
    round(
        xgb_extended["validation_R2"]
        - xgb_baseline["validation_R2"],
        4,
    ),
)


print("\nXGBoost: Extended -> Context")

print(
    "MAE improvement:",
    round(
        xgb_extended["validation_MAE"]
        - xgb_context["validation_MAE"],
        4,
    ),
)

print(
    "RMSE improvement:",
    round(
        xgb_extended["validation_RMSE"]
        - xgb_context["validation_RMSE"],
        4,
    ),
)

print(
    "R² improvement:",
    round(
        xgb_context["validation_R2"]
        - xgb_extended["validation_R2"],
        4,
    ),
)


# ------------------------------------------------------------
# Linear vs XGBoost
# ------------------------------------------------------------

print("\nLinear Baseline -> XGBoost Context")

print(
    "MAE improvement:",
    round(
        linear_baseline["validation_MAE"]
        - xgb_context["validation_MAE"],
        4,
    ),
)

print(
    "MAE reduction (%):",
    round(
        (
            linear_baseline["validation_MAE"]
            - xgb_context["validation_MAE"]
        )
        / linear_baseline["validation_MAE"]
        * 100,
        2,
    ),
)


# ------------------------------------------------------------
# Original vs Tuned XGBoost
# ------------------------------------------------------------

print("\nOriginal Context XGBoost -> Tuned")

print(
    "MAE improvement:",
    round(
        xgb_context["validation_MAE"]
        - xgb_tuned["validation_MAE"],
        4,
    ),
)

print(
    "RMSE improvement:",
    round(
        xgb_context["validation_RMSE"]
        - xgb_tuned["validation_RMSE"],
        4,
    ),
)

print(
    "R² improvement:",
    round(
        xgb_tuned["validation_R2"]
        - xgb_context["validation_R2"],
        4,
    ),
)


# ============================================================
# Best Models
# ============================================================

best_mae = comparison.loc[
    comparison["validation_MAE"].idxmin()
]

best_rmse = comparison.loc[
    comparison["validation_RMSE"].idxmin()
]

best_r2 = comparison.loc[
    comparison["validation_R2"].idxmax()
]


print("\n========================================")
print("Best Validation Models")
print("========================================")

print(
    f"Best MAE : {best_mae['model']} "
    f"({best_mae['validation_MAE']:.4f})"
)

print(
    f"Best RMSE: {best_rmse['model']} "
    f"({best_rmse['validation_RMSE']:.4f})"
)

print(
    f"Best R²  : {best_r2['model']} "
    f"({best_r2['validation_R2']:.4f})"
)


# ============================================================
# Save
# ============================================================

comparison.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\nCreated:")
print(OUTPUT_FILE)

print("\n========================================")
print("Model Comparison Completed")
print("========================================")

print(
    "IMPORTANT: Comparison uses validation results only. "
    "The final chronological test set remains untouched."
)