from pathlib import Path

import pandas as pd


RAW_DIR = Path("data/raw/Final_Excel_Files")
OUTPUT_FILE = Path("reports/distance_coverage.csv")

excel_files = sorted(
    f for f in RAW_DIR.glob("*.xlsx")
    if not f.name.startswith("~$")
)

vehicle_map = {
    file.name: f"VEH_{idx:02d}"
    for idx, file in enumerate(excel_files, start=1)
}

records = []

for file in excel_files:
    vehicle_id = vehicle_map[file.name]

    xls = pd.ExcelFile(file, engine="openpyxl")

    distance_sheets = [
        sheet
        for sheet in xls.sheet_names
        if "Distance" in sheet or "distance" in sheet
    ]

    print(f"\n{vehicle_id}")
    print("Distance sheets:", distance_sheets)

    if not distance_sheets:
        records.append(
            {
                "vehicle_id": vehicle_id,
                "distance_sheet_available": False,
                "sheet_name": None,
                "row_count": 0,
                "columns": None,
            }
        )
        continue

    for sheet in distance_sheets:
        df = pd.read_excel(
            file,
            sheet_name=sheet,
            engine="openpyxl",
        )

        print(f"  Sheet: {sheet}")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")

        # 작은 summary sheet일 가능성이 높으므로 내용도 출력
        print(df.to_string(index=False))

        records.append(
            {
                "vehicle_id": vehicle_id,
                "distance_sheet_available": True,
                "sheet_name": sheet,
                "row_count": len(df),
                "columns": " | ".join(map(str, df.columns)),
            }
        )

result = pd.DataFrame(records)

result.to_csv(
    OUTPUT_FILE,
    index=False,
)

print("\n----------------------------------------")
print("Distance Coverage Check Completed")
print("----------------------------------------")

print(f"Vehicles found: {len(excel_files)}")

available = (
    result.loc[result["distance_sheet_available"], "vehicle_id"]
    .nunique()
)

print(
    f"Vehicles with distance summary: "
    f"{available}/{len(excel_files)}"
)

print(f"Created: {OUTPUT_FILE}")