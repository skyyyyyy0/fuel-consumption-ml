from pathlib import Path
import unicodedata

import pandas as pd


# ============================================================
# Configuration
# ============================================================

EXCEL_DIR = Path("data/raw/Final_Excel_Files")

TRIP_DIR = Path(
    "/Users/haneuljang/Desktop/Geotab/Validation/"
    "geotab_raw_data_inventory/Results/Trip_Distance/All_Periods"
)


# ============================================================
# Helper
# ============================================================

def normalize_text(value):
    if pd.isna(value):
        return None

    return unicodedata.normalize(
        "NFC",
        str(value).strip()
    )


# ============================================================
# 1. Rebuild Week 1 mapping
#    Week 1 used sorted Excel files
# ============================================================

excel_files = sorted(
    f for f in EXCEL_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

week1_mapping = {}

for idx, file in enumerate(excel_files, start=1):

    df = pd.read_excel(
        file,
        sheet_name="2026_Before_Long",
        engine="openpyxl",
        usecols=["vehicle"],
    )

    actual_vehicle = normalize_text(
        df["vehicle"]
        .dropna()
        .iloc[0]
    )

    vehicle_id = f"VEH_{idx:02d}"

    week1_mapping[actual_vehicle] = vehicle_id


# ============================================================
# 2. Rebuild Day 7 mapping
#    Day 7 used sorted unique vehicle values
# ============================================================

trip_files = sorted(
    TRIP_DIR.rglob("*_trip_detail.csv")
)

trip_vehicle_names = []

for file in trip_files:

    sample = pd.read_csv(
        file,
        usecols=["vehicle"],
        nrows=5,
    )

    names = (
        sample["vehicle"]
        .dropna()
        .map(normalize_text)
        .unique()
    )

    trip_vehicle_names.extend(names)

trip_vehicle_names = sorted(
    set(trip_vehicle_names)
)

day7_mapping = {
    vehicle: f"VEH_{idx:02d}"
    for idx, vehicle in enumerate(
        trip_vehicle_names,
        start=1,
    )
}


# ============================================================
# 3. Compare
# ============================================================

all_vehicles = sorted(
    set(week1_mapping)
    | set(day7_mapping)
)

records = []

for vehicle in all_vehicles:

    week1_id = week1_mapping.get(vehicle)
    day7_id = day7_mapping.get(vehicle)

    records.append({
        "week1_vehicle_id": week1_id,
        "day7_vehicle_id": day7_id,
        "mapping_match": week1_id == day7_id,
    })


result = pd.DataFrame(records)


# ============================================================
# 4. Results
# ============================================================

print("\n========================================")
print("Vehicle Mapping Validation")
print("========================================")

print("Week 1 vehicles:", len(week1_mapping))
print("Day 7 vehicles:", len(day7_mapping))

matches = int(
    result["mapping_match"].sum()
)

mismatches = int(
    (~result["mapping_match"]).sum()
)

print("Matching mappings:", matches)
print("Mapping mismatches:", mismatches)


print("\nID Comparison:")

print(
    result[
        [
            "week1_vehicle_id",
            "day7_vehicle_id",
            "mapping_match",
        ]
    ].to_string(index=False)
)


if mismatches == 0:

    print("\nRESULT: PASS")
    print(
        "Week 1 and Day 7 vehicle mappings are identical."
    )

else:

    print("\nRESULT: FAIL")
    print(
        "Vehicle mapping mismatch detected. "
        "Do not proceed until corrected."
    )