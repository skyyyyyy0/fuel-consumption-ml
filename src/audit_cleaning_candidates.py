from pathlib import Path
import pandas as pd


# ============================================================
# Paths
# ============================================================

INPUT_FILE = Path("data/processed/trip_ml_master.csv")

print("Loading master dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows: {len(df):,}")


# ============================================================
# Basic target filtering context
# ============================================================

high = df[
    df["fuel_match_confidence"] == "High"
].copy()

print("\n========================================")
print("High-Confidence Baseline Population")
print("========================================")

print(f"All trips: {len(df):,}")
print(f"High-confidence trips: {len(high):,}")

print(
    "High-confidence with positive fuel:",
    (
        (high["trip_fuel_used_liter"].notna())
        & (high["trip_fuel_used_liter"] > 0)
    ).sum()
)


# ============================================================
# Helper
# ============================================================

def describe_feature(data, column):
    s = data[column].dropna()

    print(f"\n--- {column} ---")
    print(f"Missing: {data[column].isna().sum():,}")

    if len(s) == 0:
        return

    print(f"Min: {s.min():.6f}")
    print(f"P01: {s.quantile(0.01):.6f}")
    print(f"P05: {s.quantile(0.05):.6f}")
    print(f"Median: {s.median():.6f}")
    print(f"P95: {s.quantile(0.95):.6f}")
    print(f"P99: {s.quantile(0.99):.6f}")
    print(f"Max: {s.max():.6f}")


# ============================================================
# Distribution review
# ============================================================

print("\n========================================")
print("Feature Distribution Audit")
print("High-Confidence Trips Only")
print("========================================")

features = [
    "trip_distance_km",
    "trip_duration_min",
    "trip_fuel_used_liter",
    "avg_speed_kmh",
    "max_speed_kmh",
    "avg_rpm",
    "max_rpm",
    "idle_ratio",
]

for feature in features:
    describe_feature(high, feature)


# ============================================================
# Distance candidate rules
# ============================================================

print("\n========================================")
print("Distance Candidates")
print("========================================")

distance = high["trip_distance_km"]

print("Distance <= 0:",
      (distance <= 0).sum())

print("0 < distance < 0.1 km:",
      ((distance > 0) & (distance < 0.1)).sum())

print("0.1 <= distance < 0.5 km:",
      ((distance >= 0.1) & (distance < 0.5)).sum())

print("0.5 <= distance < 1 km:",
      ((distance >= 0.5) & (distance < 1)).sum())

print("Distance > 50 km:",
      (distance > 50).sum())

print("Distance > 100 km:",
      (distance > 100).sum())

print("Distance > 150 km:",
      (distance > 150).sum())


# ============================================================
# Duration candidate rules
# ============================================================

print("\n========================================")
print("Duration Candidates")
print("========================================")

duration = high["trip_duration_min"]

print("Duration <= 0:",
      (duration <= 0).sum())

print("0 < duration < 0.5 min:",
      ((duration > 0) & (duration < 0.5)).sum())

print("0.5 <= duration < 1 min:",
      ((duration >= 0.5) & (duration < 1)).sum())

print("Duration > 60 min:",
      (duration > 60).sum())

print("Duration > 120 min:",
      (duration > 120).sum())

print("Duration > 240 min:",
      (duration > 240).sum())


# ============================================================
# Fuel candidate rules
# ============================================================

print("\n========================================")
print("Fuel Candidates")
print("========================================")

fuel = high["trip_fuel_used_liter"]

print("Missing fuel:",
      fuel.isna().sum())

print("Fuel <= 0:",
      (fuel <= 0).sum())

print("Fuel > 10 L:",
      (fuel > 10).sum())

print("Fuel > 20 L:",
      (fuel > 20).sum())

print("Fuel > 50 L:",
      (fuel > 50).sum())


# ============================================================
# Speed validation
# ============================================================

print("\n========================================")
print("Speed Candidates")
print("========================================")

print(
    "Missing avg speed:",
    high["avg_speed_kmh"].isna().sum()
)

print(
    "Negative avg speed:",
    (high["avg_speed_kmh"] < 0).sum()
)

print(
    "Max speed > 160 km/h:",
    (high["max_speed_kmh"] > 160).sum()
)

print(
    "Max speed > 200 km/h:",
    (high["max_speed_kmh"] > 200).sum()
)


# ============================================================
# RPM validation
# ============================================================

print("\n========================================")
print("RPM Candidates")
print("========================================")

print(
    "Missing avg RPM:",
    high["avg_rpm"].isna().sum()
)

print(
    "Negative avg RPM:",
    (high["avg_rpm"] < 0).sum()
)

print(
    "Average RPM = 0:",
    (high["avg_rpm"] == 0).sum()
)

print(
    "Max RPM > 4000:",
    (high["max_rpm"] > 4000).sum()
)

print(
    "Max RPM > 5000:",
    (high["max_rpm"] > 5000).sum()
)


# ============================================================
# Idle validation
# ============================================================

print("\n========================================")
print("Idle Candidates")
print("========================================")

print(
    "Missing idle ratio:",
    high["idle_ratio"].isna().sum()
)

print(
    "Idle ratio < 0:",
    (high["idle_ratio"] < 0).sum()
)

print(
    "Idle ratio > 1:",
    (high["idle_ratio"] > 1).sum()
)

print(
    "Idle ratio = 1:",
    (high["idle_ratio"] == 1).sum()
)


# ============================================================
# Missing core features
# ============================================================

core_features = [
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
    "trip_fuel_used_liter",
]

missing_any = high[core_features].isna().any(axis=1)

print("\n========================================")
print("Core Feature Completeness")
print("========================================")

print(
    "High-confidence trips:",
    f"{len(high):,}"
)

print(
    "Missing >= 1 core feature:",
    f"{missing_any.sum():,}"
)

print(
    "Complete core features:",
    f"{(~missing_any).sum():,}"
)

print(
    "Complete rate:",
    f"{(~missing_any).mean() * 100:.1f}%"
)


# ============================================================
# Complete cases by vehicle
# ============================================================

high["complete_core"] = ~missing_any

coverage = (
    high.groupby("vehicle_id")
    .agg(
        trips=("trip_id", "size"),
        complete_trips=("complete_core", "sum"),
    )
)

coverage["complete_pct"] = (
    coverage["complete_trips"]
    / coverage["trips"]
    * 100
)

print("\n========================================")
print("Complete Core Coverage by Vehicle")
print("========================================")

print(coverage.to_string())


print("\n========================================")
print("Cleaning Candidate Audit Completed")
print("========================================")