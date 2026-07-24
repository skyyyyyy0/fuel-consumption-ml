from pathlib import Path
import pandas as pd


# ==================================================
# Configuration
# ==================================================

INPUT_FILE = Path(
    "reports/trip_target_matching_test.csv"
)

OUTPUT_FILE = Path(
    "reports/trip_duplicate_match_audit.csv"
)


# ==================================================
# 1. Load matching test
# ==================================================

df = pd.read_csv(INPUT_FILE)

datetime_cols = [
    "trip_start",
    "trip_stop",
    "fuel_time",
]

for col in datetime_cols:
    df[col] = pd.to_datetime(
        df[col],
        format="mixed",
        utc=True,
        errors="coerce",
    )


# ==================================================
# 2. Find duplicated fuel assignments
# ==================================================

matched = df[
    df["fuel_time"].notna()
].copy()

fuel_counts = (
    matched["fuel_time"]
    .value_counts()
)

reused_times = fuel_counts[
    fuel_counts > 1
].index

duplicates = matched[
    matched["fuel_time"].isin(reused_times)
].copy()


# ==================================================
# 3. Calculate diagnostic fields
# ==================================================

duplicates["previous_trip_stop"] = (
    duplicates["trip_stop"].shift(1)
)

duplicates["gap_from_previous_trip_sec"] = (
    duplicates["trip_start"]
    - duplicates["previous_trip_stop"]
).dt.total_seconds()

duplicates["fuel_after_stop_sec"] = (
    duplicates["fuel_time"]
    - duplicates["trip_stop"]
).dt.total_seconds()

duplicates["is_zero_distance"] = (
    duplicates["distance_km"] <= 0
)

duplicates["is_under_0_1_km"] = (
    duplicates["distance_km"] < 0.1
)

duplicates["is_under_1_km"] = (
    duplicates["distance_km"] < 1
)


# ==================================================
# 4. Rank competing trips for each fuel record
# ==================================================

duplicates["abs_match_diff_sec"] = (
    duplicates["fuel_after_stop_sec"]
    .abs()
)

duplicates["candidate_rank"] = (
    duplicates
    .groupby("fuel_time")[
        "abs_match_diff_sec"
    ]
    .rank(
        method="first",
        ascending=True,
    )
)


# ==================================================
# 5. Suggested assignment
# ==================================================

duplicates["suggested_action"] = "Reject"

duplicates.loc[
    duplicates["candidate_rank"] == 1,
    "suggested_action"
] = "Keep Closest"


# ==================================================
# 6. Save
# ==================================================

output_columns = [
    "trip_id",
    "trip_start",
    "trip_stop",
    "duration_min",
    "distance_km",
    "trip_validity",
    "fuel_time",
    "fuel_liters",
    "match_diff_sec",
    "fuel_after_stop_sec",
    "abs_match_diff_sec",
    "gap_from_previous_trip_sec",
    "is_zero_distance",
    "is_under_0_1_km",
    "is_under_1_km",
    "candidate_rank",
    "suggested_action",
]

duplicates[
    output_columns
].to_csv(
    OUTPUT_FILE,
    index=False,
)


# ==================================================
# 7. Summary
# ==================================================

print("\n========================================")
print("Duplicate Trip-Fuel Match Investigation")
print("========================================")

print(
    "Duplicate candidate rows:",
    len(duplicates),
)

print(
    "Reused fuel records:",
    len(reused_times),
)

print(
    "Zero-distance candidates:",
    int(
        duplicates[
            "is_zero_distance"
        ].sum()
    ),
)

print(
    "Candidates < 0.1 km:",
    int(
        duplicates[
            "is_under_0_1_km"
        ].sum()
    ),
)

print(
    "Candidates < 1 km:",
    int(
        duplicates[
            "is_under_1_km"
        ].sum()
    ),
)


# ==================================================
# 8. Show every competing pair
# ==================================================

print("\n========================================")
print("Competing Trips")
print("========================================\n")

display_columns = [
    "trip_id",
    "trip_stop",
    "distance_km",
    "fuel_time",
    "fuel_liters",
    "abs_match_diff_sec",
    "candidate_rank",
    "suggested_action",
]

for fuel_time, group in duplicates.groupby(
    "fuel_time"
):

    print("----------------------------------------")
    print("Fuel timestamp:", fuel_time)

    print(
        group[
            display_columns
        ]
        .sort_values(
            "candidate_rank"
        )
        .to_string(index=False)
    )

    print()


print(
    f"Created: {OUTPUT_FILE}"
)