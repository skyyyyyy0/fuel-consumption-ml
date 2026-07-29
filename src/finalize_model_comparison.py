from pathlib import Path
import pandas as pd

COMPARISON_FILE = Path("reports/model_comparison.csv")

df = pd.read_csv(COMPARISON_FILE)

# Add final-test columns if they do not exist
for col in ["test_MAE", "test_RMSE", "test_R2"]:
    if col not in df.columns:
        df[col] = None

# Remove an existing final row so the script can be safely rerun
df = df[
    df["model"] != "FINAL - Tuned Context XGBoost"
].copy()

final_row = {
    "model": "FINAL - Tuned Context XGBoost",
    "feature_set": "Context",
    "num_features": 13,
    "validation_MAE": 0.3506,
    "validation_RMSE": 1.7868,
    "validation_R2": 0.8989,
    "test_MAE": 0.3573,
    "test_RMSE": 1.6166,
    "test_R2": 0.9032,
}

df = pd.concat(
    [df, pd.DataFrame([final_row])],
    ignore_index=True
)

df.to_csv(COMPARISON_FILE, index=False)

print("Updated:", COMPARISON_FILE)
print("\nFinal model:")
print("Validation MAE: 0.3506 L")
print("Test MAE:       0.3573 L")
print("Test RMSE:      1.6166 L")
print("Test R²:        0.9032")