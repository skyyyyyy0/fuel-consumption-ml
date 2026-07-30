from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from xgboost import XGBRegressor


# ============================================================
# 1. Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_PATH = PROJECT_ROOT / "data" / "modeling" / "train.csv"
VALIDATION_PATH = PROJECT_ROOT / "data" / "modeling" / "validation.csv"
TEST_PATH = PROJECT_ROOT / "data" / "modeling" / "test.csv"

MODELING_OUTPUT_DIR = PROJECT_ROOT / "reports" / "modeling"
FIGURE_OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "shap"

SHAP_VALUES_PATH = MODELING_OUTPUT_DIR / "shap_values.csv"
SHAP_IMPORTANCE_PATH = (
    MODELING_OUTPUT_DIR / "shap_global_importance.csv"
)
WATERFALL_TRIP_PATH = (
    MODELING_OUTPUT_DIR / "shap_waterfall_trip.csv"
)

MODELING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. Final model configuration
# ============================================================

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

TARGET = "trip_fuel_used_liter"

METADATA_COLUMNS = [
    "vehicle_id",
    "trip_id",
    "period",
    "trip_start_time",
    "trip_end_time",
    "model_split",
]


# ============================================================
# 3. Validation functions
# ============================================================

def validate_columns(
    df: pd.DataFrame,
    dataset_name: str,
) -> None:
    """Check that the dataset contains all required columns."""

    required_columns = FEATURES + [TARGET]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing columns: "
            f"{missing_columns}"
        )


def load_datasets() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Load the existing chronological datasets."""

    for path in [TRAIN_PATH, VALIDATION_PATH, TEST_PATH]:
        if not path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {path}"
            )

    train_df = pd.read_csv(TRAIN_PATH)
    validation_df = pd.read_csv(VALIDATION_PATH)
    test_df = pd.read_csv(TEST_PATH)

    validate_columns(train_df, "Train dataset")
    validate_columns(validation_df, "Validation dataset")
    validate_columns(test_df, "Test dataset")

    return train_df, validation_df, test_df


# ============================================================
# 4. Final model
# ============================================================

def train_final_model(
    train_validation_df: pd.DataFrame,
) -> XGBRegressor:
    """Train the frozen final XGBoost model."""

    model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.03,
        max_depth=5,
        subsample=1.0,
        colsample_bytree=1.0,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        train_validation_df[FEATURES],
        train_validation_df[TARGET],
    )

    return model


# ============================================================
# 5. SHAP outputs
# ============================================================

def create_shap_output(
    shap_values: shap.Explanation,
    test_df: pd.DataFrame,
    model_predictions: np.ndarray,
) -> pd.DataFrame:
    """Save trip-level SHAP values and prediction metadata."""

    shap_feature_columns = [
        f"shap_{feature}"
        for feature in FEATURES
    ]

    shap_df = pd.DataFrame(
        shap_values.values,
        columns=shap_feature_columns,
    )

    available_metadata = [
        column
        for column in METADATA_COLUMNS
        if column in test_df.columns
    ]

    output_df = pd.concat(
        [
            test_df[available_metadata].reset_index(drop=True),
            test_df[[TARGET]].reset_index(drop=True),
            test_df[FEATURES].reset_index(drop=True),
            shap_df.reset_index(drop=True),
        ],
        axis=1,
    )

    output_df["shap_base_value"] = np.asarray(
        shap_values.base_values
    ).reshape(-1)

    output_df["predicted_fuel_liter"] = (
        model_predictions
    )

    output_df["shap_reconstructed_prediction"] = (
        output_df["shap_base_value"]
        + shap_df.sum(axis=1).to_numpy()
    )

    output_df["prediction_reconstruction_diff"] = (
        output_df["predicted_fuel_liter"]
        - output_df["shap_reconstructed_prediction"]
    )

    output_df.to_csv(
        SHAP_VALUES_PATH,
        index=False,
    )

    return output_df


def create_global_importance(
    shap_values: shap.Explanation,
) -> pd.DataFrame:
    """Calculate global SHAP feature importance."""

    importance_df = pd.DataFrame(
        {
            "feature": FEATURES,
            "mean_abs_shap": np.abs(
                shap_values.values
            ).mean(axis=0),
            "mean_shap": shap_values.values.mean(axis=0),
        }
    )

    importance_df = importance_df.sort_values(
        "mean_abs_shap",
        ascending=False,
    ).reset_index(drop=True)

    importance_df["importance_rank"] = (
        np.arange(1, len(importance_df) + 1)
    )

    importance_df.to_csv(
        SHAP_IMPORTANCE_PATH,
        index=False,
    )

    return importance_df


# ============================================================
# 6. SHAP plots
# ============================================================

def save_beeswarm_plot(
    shap_values: shap.Explanation,
) -> None:
    """Save global SHAP beeswarm plot."""

    shap.plots.beeswarm(
        shap_values,
        max_display=len(FEATURES),
        show=False,
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_OUTPUT_DIR
        / "shap_summary_beeswarm.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


def save_bar_plot(
    shap_values: shap.Explanation,
) -> None:
    """Save global SHAP bar plot."""

    shap.plots.bar(
        shap_values,
        max_display=len(FEATURES),
        show=False,
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_OUTPUT_DIR
        / "shap_global_bar.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()


def save_waterfall_plot(
    shap_values: shap.Explanation,
    test_df: pd.DataFrame,
    predictions: np.ndarray,
) -> None:
    """Save a waterfall plot for a representative trip."""

    median_prediction = np.median(predictions)

    selected_position = int(
        np.argmin(
            np.abs(
                predictions - median_prediction
            )
        )
    )

    selected_shap = shap_values[selected_position]

    shap.plots.waterfall(
        selected_shap,
        max_display=len(FEATURES),
        show=False,
    )

    plt.tight_layout()

    plt.savefig(
        FIGURE_OUTPUT_DIR
        / "shap_waterfall_typical_trip.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    selected_columns = [
        column
        for column in (
            METADATA_COLUMNS
            + [TARGET]
            + FEATURES
        )
        if column in test_df.columns
    ]

    selected_trip = test_df.iloc[
        [selected_position]
    ][selected_columns].copy()

    selected_trip["predicted_fuel_liter"] = (
        predictions[selected_position]
    )

    selected_trip["shap_base_value"] = (
        np.asarray(
            selected_shap.base_values
        ).reshape(-1)[0]
    )

    selected_trip.to_csv(
        WATERFALL_TRIP_PATH,
        index=False,
    )


# ============================================================
# 7. Main execution
# ============================================================

def main() -> None:
    """Run the full SHAP analysis."""

    print("Loading modeling datasets...")

    train_df, validation_df, test_df = (
        load_datasets()
    )

    print(f"Train rows:      {len(train_df):,}")
    print(f"Validation rows: {len(validation_df):,}")
    print(f"Test rows:       {len(test_df):,}")

    train_validation_df = pd.concat(
        [train_df, validation_df],
        ignore_index=True,
    )

    print(
        "\nTraining final frozen XGBoost model "
        "using Train + Validation..."
    )

    model = train_final_model(
        train_validation_df
    )

    X_test = test_df[FEATURES].copy()

    predictions = model.predict(X_test)

    print("Generating SHAP values...")

    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_test)

    shap_output_df = create_shap_output(
        shap_values=shap_values,
        test_df=test_df,
        model_predictions=predictions,
    )

    importance_df = create_global_importance(
        shap_values
    )

    print("Generating SHAP figures...")

    save_beeswarm_plot(shap_values)
    save_bar_plot(shap_values)

    save_waterfall_plot(
        shap_values=shap_values,
        test_df=test_df,
        predictions=predictions,
    )

    max_reconstruction_difference = (
        shap_output_df[
            "prediction_reconstruction_diff"
        ]
        .abs()
        .max()
    )

    print("\nTop SHAP features:")
    print(
        importance_df.head(10).to_string(
            index=False
        )
    )

    print(
        "\nMaximum SHAP prediction "
        "reconstruction difference:"
    )
    print(
        f"{max_reconstruction_difference:.10f}"
    )

    print("\nSaved files:")
    print(f"- {SHAP_VALUES_PATH}")
    print(f"- {SHAP_IMPORTANCE_PATH}")
    print(f"- {WATERFALL_TRIP_PATH}")
    print(f"- {FIGURE_OUTPUT_DIR}")

    print(
        f"\nTotal explained test trips: "
        f"{len(shap_output_df):,}"
    )


if __name__ == "__main__":
    main()