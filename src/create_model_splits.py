from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/trip_ml_features.csv")
OUTPUT_DIR = Path("data/modeling")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


print("Loading modeling dataset...")

df = pd.read_csv(INPUT_FILE)

df["trip_start_time"] = pd.to_datetime(
    df["trip_start_time"],
    format="mixed",
    utc=True,
    errors="raise",
)

df = (
    df.sort_values(
        ["trip_start_time", "trip_id"]
    )
    .reset_index(drop=True)
)

n = len(df)

train_end = int(n * 0.60)
validation_end = int(n * 0.80)

train = df.iloc[:train_end].copy()
validation = df.iloc[
    train_end:validation_end
].copy()
test = df.iloc[
    validation_end:
].copy()


# ------------------------------------------------------------
# Add split labels
# ------------------------------------------------------------

train["model_split"] = "train"
validation["model_split"] = "validation"
test["model_split"] = "test"


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

print("\n========================================")
print("Model Split Validation")
print("========================================")

for name, split in [
    ("Train", train),
    ("Validation", validation),
    ("Test", test),
]:
    print(f"\n{name}")
    print(f"Rows: {len(split):,}")
    print(f"Vehicles: {split['vehicle_id'].nunique()}")
    print(f"Start: {split['trip_start_time'].min()}")
    print(f"End: {split['trip_start_time'].max()}")


assert len(train) == 5953
assert len(validation) == 1985
assert len(test) == 1985

assert (
    train["trip_start_time"].max()
    < validation["trip_start_time"].min()
)

assert (
    validation["trip_start_time"].max()
    < test["trip_start_time"].min()
)

assert train["vehicle_id"].nunique() == 12
assert validation["vehicle_id"].nunique() == 12
assert test["vehicle_id"].nunique() == 12

assert train["trip_id"].duplicated().sum() == 0
assert validation["trip_id"].duplicated().sum() == 0
assert test["trip_id"].duplicated().sum() == 0

assert (
    set(train["trip_id"])
    .isdisjoint(validation["trip_id"])
)

assert (
    set(train["trip_id"])
    .isdisjoint(test["trip_id"])
)

assert (
    set(validation["trip_id"])
    .isdisjoint(test["trip_id"])
)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

train.to_csv(
    OUTPUT_DIR / "train.csv",
    index=False,
)

validation.to_csv(
    OUTPUT_DIR / "validation.csv",
    index=False,
)

test.to_csv(
    OUTPUT_DIR / "test.csv",
    index=False,
)

print("\n========================================")
print("Model Splits Created")
print("========================================")

print("Created:")
print("- data/modeling/train.csv")
print("- data/modeling/validation.csv")
print("- data/modeling/test.csv")

print(
    "\nIMPORTANT: test.csv is reserved "
    "for final evaluation."
)