import pandas as pd

DATA_PATH = "data/processed/trip_ml_features.csv"

print("Loading modeling dataset...")
df = pd.read_csv(DATA_PATH)

print(f"Rows: {len(df):,}")
print(f"Vehicles: {df['vehicle_id'].nunique()}")

# Parse timestamps
df["trip_start_time"] = pd.to_datetime(
    df["trip_start_time"],
    format="mixed",
    errors="coerce",
    utc=True
)

print("\n========================================")
print("Timestamp Validation")
print("========================================")

print("Missing timestamps:", df["trip_start_time"].isna().sum())
print("Earliest trip:", df["trip_start_time"].min())
print("Latest trip:", df["trip_start_time"].max())

# Monthly distribution
df["year_month"] = df["trip_start_time"].dt.to_period("M")

print("\n========================================")
print("Trips by Month")
print("========================================")

print(
    df.groupby("year_month", observed=True)
      .size()
      .rename("trips")
)

# Vehicle time coverage
vehicle_coverage = (
    df.groupby("vehicle_id")
      .agg(
          trips=("trip_id", "count"),
          first_trip=("trip_start_time", "min"),
          last_trip=("trip_start_time", "max")
      )
)

print("\n========================================")
print("Vehicle Time Coverage")
print("========================================")

print(vehicle_coverage)

# Period time coverage
period_coverage = (
    df.groupby("period")
      .agg(
          trips=("trip_id", "count"),
          first_trip=("trip_start_time", "min"),
          last_trip=("trip_start_time", "max")
      )
)

print("\n========================================")
print("Period Time Coverage")
print("========================================")

print(period_coverage)

print("\n========================================")
print("Split Investigation Completed")
print("========================================")

print("\n========================================")
print("Exact Period Boundaries")
print("========================================")

period_boundaries = (
    df.groupby("period")
      .agg(
          trips=("trip_id", "count"),
          first_trip=("trip_start_time", "min"),
          last_trip=("trip_start_time", "max"),
          vehicles=("vehicle_id", "nunique")
      )
)

print(period_boundaries.to_string())

before = df[df["period"] == "Before"]
after = df[df["period"] == "After"]
final = df[df["period"] == "Final"]

print("\nChronological boundary checks:")
print("Before max:", before["trip_start_time"].max())
print("After min :", after["trip_start_time"].min())
print("Before < After:", before["trip_start_time"].max() < after["trip_start_time"].min())

print()

print("After max :", after["trip_start_time"].max())
print("Final min :", final["trip_start_time"].min())
print("After < Final:", after["trip_start_time"].max() < final["trip_start_time"].min())

print("\nVehicle coverage:")
print("Before:", before["vehicle_id"].nunique())
print("After :", after["vehicle_id"].nunique())
print("Final :", final["vehicle_id"].nunique())

# ========================================
# Candidate Chronological Split
# ========================================

print("\n========================================")
print("Candidate 60 / 20 / 20 Time Split")
print("========================================")

df_sorted = df.sort_values("trip_start_time").reset_index(drop=True)

n = len(df_sorted)

train_end_idx = int(n * 0.60)
val_end_idx = int(n * 0.80)

train = df_sorted.iloc[:train_end_idx]
val = df_sorted.iloc[train_end_idx:val_end_idx]
test = df_sorted.iloc[val_end_idx:]

def summarize_split(name, data):
    print(f"\n{name}")
    print(f"Rows: {len(data):,} ({len(data) / n * 100:.1f}%)")
    print(f"Start: {data['trip_start_time'].min()}")
    print(f"End:   {data['trip_start_time'].max()}")
    print(f"Vehicles: {data['vehicle_id'].nunique()}")
    print(f"Mean fuel: {data['trip_fuel_used_liter'].mean():.3f}")
    print(f"Median fuel: {data['trip_fuel_used_liter'].median():.3f}")
    print(f"Mean distance: {data['trip_distance_km'].mean():.3f}")
    print(f"Median distance: {data['trip_distance_km'].median():.3f}")

summarize_split("TRAIN", train)
summarize_split("VALIDATION", val)
summarize_split("TEST", test)

print("\nChronological checks:")
print(
    "Train max < Validation min:",
    train["trip_start_time"].max()
    < val["trip_start_time"].min()
)

print(
    "Validation max < Test min:",
    val["trip_start_time"].max()
    < test["trip_start_time"].min()
)

print("\nVehicle coverage by split:")

coverage = pd.DataFrame({
    "train": train.groupby("vehicle_id").size(),
    "validation": val.groupby("vehicle_id").size(),
    "test": test.groupby("vehicle_id").size()
}).fillna(0).astype(int)

print(coverage)