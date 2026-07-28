from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# Configuration
# ============================================================

MASTER_FILE = Path("data/processed/trip_ml_clean.csv")
OUTPUT_FILE = Path("reports/temperature_feature_audit.csv")

# Change this only if your source directory differs
DATA_DIR = Path("data")

TEMP_SIGNAL = "Outside air temperature"


# ============================================================
# Find source Excel files
# ============================================================

print("Loading clean ML dataset...")

trips = pd.read_csv(MASTER_FILE)

trips["trip_start_time"] = pd.to_datetime(
    trips["trip_start_time"],
    utc=True,
    errors="coerce"
)

trips["trip_end_time"] = pd.to_datetime(
    trips["trip_end_time"],
    utc=True,
    errors="coerce"
)

print(f"Clean trips: {len(trips):,}")
print(f"Vehicles: {trips['vehicle_id'].nunique()}")


# ============================================================
# First inspect available source files
# ============================================================

excel_files = list(DATA_DIR.rglob("*.xlsx"))

print(f"\nExcel files found: {len(excel_files)}")

if not excel_files:
    print(
        "\nNo Excel files found under data/.\n"
        "Check the source-data directory before continuing."
    )
    raise SystemExit


# ============================================================
# Inspect sheets and temperature availability
# ============================================================

results = []

for file in excel_files:

    try:
        xls = pd.ExcelFile(file)
    except Exception:
        continue

    for sheet in xls.sheet_names:

        # We only care about the 2026 Long datasets
        if "2026" not in sheet or "Long" not in sheet:
            continue

        print(f"Reading: {file.name} | {sheet}")

        try:
            df = pd.read_excel(
                file,
                sheet_name=sheet
            )
        except Exception as e:
            print("  Failed:", e)
            continue

        # Detect likely signal-name column
        signal_col = None

        for candidate in [
            "DiagnosticName",
            "diagnostic_name",
            "Signal",
            "signal",
            "Name",
            "name",
        ]:
            if candidate in df.columns:
                signal_col = candidate
                break

        if signal_col is None:
            continue

        temp = df[
            df[signal_col]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq(TEMP_SIGNAL.lower())
        ].copy()

        if len(temp) == 0:
            continue

        # Detect value column
        value_col = None

        for candidate in [
            "Data",
            "data",
            "Value",
            "value",
        ]:
            if candidate in temp.columns:
                value_col = candidate
                break

        if value_col is None:
            continue

        values = pd.to_numeric(
            temp[value_col],
            errors="coerce"
        ).dropna()

        if len(values) == 0:
            continue

        results.append({
            "source_file": file.name,
            "sheet": sheet,
            "temperature_rows": len(values),
            "temp_min": values.min(),
            "temp_p01": values.quantile(0.01),
            "temp_p05": values.quantile(0.05),
            "temp_median": values.median(),
            "temp_mean": values.mean(),
            "temp_p95": values.quantile(0.95),
            "temp_p99": values.quantile(0.99),
            "temp_max": values.max(),
            "temp_gt_50_count": (values > 50).sum(),
            "temp_gt_60_count": (values > 60).sum(),
            "temp_lt_minus_20_count": (values < -20).sum(),
        })


# ============================================================
# Results
# ============================================================

audit = pd.DataFrame(results)

print("\n========================================")
print("Temperature Feature Audit")
print("========================================")

if audit.empty:

    print("No usable Outside air temperature signal found.")

else:

    print(f"Source groups with temperature: {len(audit)}")

    print("\nTemperature ranges:")

    display_cols = [
        "source_file",
        "sheet",
        "temperature_rows",
        "temp_min",
        "temp_median",
        "temp_p95",
        "temp_max",
        "temp_gt_60_count",
    ]

    print(
        audit[display_cols]
        .to_string(index=False)
    )

    print("\n========================================")
    print("Fleet Summary")
    print("========================================")

    print(
        "Groups with >60 C observations:",
        int((audit["temp_gt_60_count"] > 0).sum())
    )

    print(
        "Overall minimum:",
        audit["temp_min"].min()
    )

    print(
        "Overall maximum:",
        audit["temp_max"].max()
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    audit.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"\nCreated: {OUTPUT_FILE}")