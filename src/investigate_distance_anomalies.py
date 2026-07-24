from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TRIP_DIR = Path(
    "/Users/haneuljang/Desktop/Geotab/Validation/"
    "geotab_raw_data_inventory/Results/"
    "Trip_Distance/All_Periods"
)

OUTPUT_FILE = Path("reports/distance_anomaly_audit.csv")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Find trip files
# --------------------------------------------------

files = sorted(TRIP_DIR.rglob("*_trip_detail.csv"))

print(f"Trip files found: {len(files)}")

records = []


# --------------------------------------------------
# Audit each file
# --------------------------------------------------

for file in files:

    print(f"Reading: {file.name}")

    df = pd.read_csv(file)

    if "distance_km" not in df.columns:
        print("  WARNING: distance_km not found")
        continue

    distance = pd.to_numeric(
        df["distance_km"],
        errors="coerce"
    )

    valid = distance.dropna()

    if valid.empty:
        continue

    # Use anonymized sequential ID later;
    # do not write private vehicle names to output.
    records.append({
        "source_index": len(records) + 1,

        "trip_count": len(valid),

        "min_distance_km": valid.min(),
        "max_distance_km": valid.max(),
        "mean_distance_km": valid.mean(),
        "median_distance_km": valid.median(),

        "missing_count": int(distance.isna().sum()),
        "negative_count": int((valid < 0).sum()),
        "zero_count": int((valid == 0).sum()),

        "distance_lt_0_1": int(
            ((valid > 0) & (valid < 0.1)).sum()
        ),

        "distance_lt_1": int(
            ((valid > 0) & (valid < 1)).sum()
        ),

        "distance_gt_100": int(
            (valid > 100).sum()
        ),

        "distance_gt_300": int(
            (valid > 300).sum()
        ),

        "distance_gt_500": int(
            (valid > 500).sum()
        ),
    })


# --------------------------------------------------
# Create result
# --------------------------------------------------

result = pd.DataFrame(records)

result.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Fleet-level summary
# --------------------------------------------------

print("\n----------------------------------------")
print("GPS Distance Audit Completed")
print("----------------------------------------")

print(f"Created: {OUTPUT_FILE}")

print("\nOverall statistics:")

print(
    "Total trips:",
    f"{result['trip_count'].sum():,}"
)

print(
    "Overall min:",
    result["min_distance_km"].min()
)

print(
    "Overall max:",
    result["max_distance_km"].max()
)

print(
    "Missing:",
    result["missing_count"].sum()
)

print(
    "Negative:",
    result["negative_count"].sum()
)

print(
    "Zero distance:",
    result["zero_count"].sum()
)

print(
    "0 < distance < 0.1 km:",
    result["distance_lt_0_1"].sum()
)

print(
    "0 < distance < 1 km:",
    result["distance_lt_1"].sum()
)

print(
    "Distance > 100 km:",
    result["distance_gt_100"].sum()
)

print(
    "Distance > 300 km:",
    result["distance_gt_300"].sum()
)

print(
    "Distance > 500 km:",
    result["distance_gt_500"].sum()
)


print("\nHighest-distance groups:\n")

print(
    result.sort_values(
        "max_distance_km",
        ascending=False
    )[
        [
            "source_index",
            "trip_count",
            "min_distance_km",
            "max_distance_km",
            "mean_distance_km",
            "median_distance_km",
            "zero_count",
            "distance_lt_0_1",
            "distance_gt_100",
            "distance_gt_300",
        ]
    ]
    .head(15)
    .to_string(index=False)
)