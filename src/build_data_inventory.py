from pathlib import Path
import re
import pandas as pd

RAW_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_DIR = Path("reports")
OUTPUT_FILE = OUTPUT_DIR / "data_inventory.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

excel_files = sorted(
    file for file in RAW_DIR.glob("*.xlsx")
    if not file.name.startswith("~$")
)

vehicle_map = {
    file.name: f"VEH_{idx:02d}"
    for idx, file in enumerate(excel_files, start=1)
}

records = []

sheet_pattern = re.compile(
    r"^(?P<year>2025|2026)_(?P<period>Before|After|Final)_(?P<format>Long|Wide)$"
)

for file in excel_files:
    vehicle_id = vehicle_map[file.name]

    xls = pd.ExcelFile(file, engine="openpyxl")

    for sheet_name in xls.sheet_names:
        match = sheet_pattern.match(sheet_name)

        if not match:
            continue

        year = int(match.group("year"))
        period = match.group("period")
        data_format = match.group("format")

        df = pd.read_excel(file, sheet_name=sheet_name)

        row_count = len(df)

        # find datetime column
        datetime_col = None
        for candidate in ["datetime", "datetime_kst", "timestamp", "date"]:
            if candidate in df.columns:
                datetime_col = candidate
                break

        start_date = None
        end_date = None

        if datetime_col:
            dt = pd.to_datetime(df[datetime_col], errors="coerce")
            if dt.notna().any():
                start_date = dt.min()
                end_date = dt.max()

        records.append(
            {
                "vehicle_id": vehicle_id,
                "year": year,
                "period": period,
                "data_format": data_format,
                "start_date": start_date,
                "end_date": end_date,
                "row_count": row_count,
                "data_source": "GeoTab",
                "source_file_private": file.name,
            }
        )

inventory = pd.DataFrame(records)

inventory = inventory.sort_values(
    ["vehicle_id", "year", "period", "data_format"]
)

inventory.to_csv(OUTPUT_FILE, index=False)

print(f"Created: {OUTPUT_FILE}")
print(f"Vehicles found: {inventory['vehicle_id'].nunique()}")
print(f"Inventory rows: {len(inventory)}")

print("\nRows by vehicle:")
print(
    inventory.groupby("vehicle_id")["row_count"]
    .sum()
    .sort_values(ascending=False)
)

print("\nAvailable periods:")
print(
    inventory[
        ["vehicle_id", "year", "period", "data_format"]
    ].to_string(index=False)
)