#  yelp.py 
# we used chatGPT to debug and get structure of the code

import sqlite3
import requests
import time

API_KEY = "Yzkti7a-ZCT0XIK_zJp-cb0fmCoTL6gV2N8mIaPJYmvb6BhgOyjmYxka6-alH9oJInH1MrQzFM9OEMjjZGQ6VWaa4W_s8tUMnuroB5Q-Vw3w06t8ELNBaJlczdDqZ3Yx"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def fetch_yelp_data(zip_codes):
    conn = sqlite3.connect("FINALPROJECTDB.db")
    cur = conn.cursor()

    existing_ids = set(row[0] for row in cur.execute("SELECT id FROM restaurants"))
    count = 0

    for zip_code in zip_codes:
        if count >= 25:
            print("Limit of 25 new restaurants reached")
            break

        params = {
            "location": zip_code,
            "term": "restaurants",
            "limit": 10
        }

        try:
            response = requests.get(
                "https://api.yelp.com/v3/businesses/search",
                headers=HEADERS,
                params=params
            )
            businesses = response.json().get("businesses", [])

            for biz in businesses:
                if biz["id"] in existing_ids:
                    continue

                cur.execute("""
                    INSERT OR REPLACE INTO restaurants
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    biz["id"],
                    biz["name"],
                    biz["rating"],
                    biz["review_count"],
                    zip_code
                ))

                existing_ids.add(biz["id"])
                count += 1

                if count >= 25:
                    break

        except Exception as e:
            print(f" Cannot get data for ZIP {zip_code}: {e}")

        time.sleep(0.4)  # No rate limits

    conn.commit()
    conn.close()
    print(f" Added {count} new Yelp restaurants this run.")


if __name__ == "__main__":
    fetch_yelp_data([
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
    ])
