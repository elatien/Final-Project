#census.py
# we used chatGPT to debug and get structure of the code

import sqlite3
import requests
from datetime import datetime

API_KEY = "1940a3de74a60828d1309f8e708577a080d4aa34"

# Full list of 100 Michigan ZIP codes
all_zip_codes = [
    "48103", "48104", "48105", "48108", "48109", "48197", "48198", "48201", "48202", "48203",
    "48204", "48205", "48206", "48207", "48208", "48209", "48210", "48211", "48212", "48213",
    "48214", "48215", "48216", "48217", "48218", "48219", "48220", "48221", "48223", "48224",
    "48225", "48226", "48227", "48228", "48229", "48230", "48233", "48234", "48235", "48236",
    "48009", "48030", "48067", "48069", "48073", "48076", "48083", "48084", "48085", "48098",
    "48089", "48091", "48092", "48093", "48094", "48095", "48101", "48111", "48124", "48125",
    "48126", "48127", "48128", "48135", "48141", "48146", "48150", "48152", "48154", "48161",
    "48162", "48164", "48167", "48170", "48174", "48180", "48183", "48184", "48186", "48187",
    "48188", "48237", "48301", "48302", "48304", "48306", "48307", "48309", "48310", "48312",
    "48313", "48314", "48315", "48316", "48317", "48322", "48323", "48324", "48326", "48327"
]

def fetch_income_data(zip_codes):
    conn = sqlite3.connect("FINALPROJECTDB.db")

    # Check for already-saved ZIPs
    existing_zips = set(row[0] for row in conn.execute("SELECT zip_code FROM income"))
    
    count = 0  # Count new inserts this run

    for zip_code in zip_codes:
        if zip_code in existing_zips:
            print(f" Skipping ZIP {zip_code} (already in database)")
            continue

        try:
            url = f"https://api.census.gov/data/2021/acs/acs5?get=B19013_001E&for=zip%20code%20tabulation%20area:{zip_code}&key={API_KEY}"
            response = requests.get(url)
            data = response.json()

            median_income = int(data[1][0])
            last_updated = datetime.now().strftime("%Y-%m-%d")

            conn.execute("""
                INSERT OR REPLACE INTO income 
                VALUES (?, ?, ?)
            """, (zip_code, median_income, last_updated))

            print(f"{zip_code}: ${median_income}, updated {last_updated}")
            count += 1

            # Stop after 25 new inserts
            if count >= 25:
                print("Limit of 25 new ZIPs reached for this run.")
                break

        except Exception as e:
            print(f" Failed for ZIP {zip_code}: {e}")

    conn.commit()
    conn.close()
    print(f"\n Inserted {count} new income records this run.")

if __name__ == "__main__":
    fetch_income_data(all_zip_codes)
