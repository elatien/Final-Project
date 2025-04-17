# education.py
# we used chatGPT to debug and get structure of the code
import sqlite3
from bs4 import BeautifulSoup
import requests


def scrape_education_stats(zip_codes=[
    "48103", "48104", "48105", "48108", "48109", "48197", "48198", "48201", "48202", "48203",
    "48204", "48205", "48206", "48207", "48208", "48209", "48210", "48211", "48212", "48213",
    "48214", "48215", "48216", "48217", "48218", "48219", "48220", "48221", "48223", "48224",
    "48225", "48226", "48227", "48228", "48229", "48230", "48233", "48234", "48235", "48236",
    "48009", "48030", "48067", "48069", "48073", "48076", "48083", "48084", "48085", "48098",
    "48089", "48091", "48092", "48093", "48094", "48095", "48101", "48111", "48124", "48125",
    "48126", "48127", "48128", "48135", "48141", "48146", "48150", "48152", "48154", "48161",
    "48162", "48164", "48167", "48170", "48174", "48180", "48183", "48184", "48186", "48187",
    "48188", "48237", "48301", "48302", "48304", "48306", "48307", "48309", "48310", "48312",
    "48313", "48314", "48315", "48316", "48317", "48322", "48323", "48324", "48326", "48327"]):

    conn = sqlite3.connect("FINALPROJECTDB.db")
    failed_zips = []

    for zip_code in zip_codes:
        try:
            url = f"https://www.city-data.com/zips/{zip_code}.html"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            edu_section = soup.find('h3', string=lambda t: t and "population 25 years and over" in t.lower())
            if not edu_section:
                failed_zips.append(zip_code)
                continue

            data = {}
            ul = edu_section.find_next_sibling("ul")
            for li in ul.find_all("li"):
                text = li.get_text(strip=True)
                if ':' in text:
                    k, v = text.split(':', 1)
                    data[k.strip()] = v.strip()

            high_school = float(data.get("High school or higher", "0%").replace('%', ''))
            bachelors = float(data.get("Bachelor's degree or higher", "0%").replace('%', ''))
            graduate = float(data.get("Graduate or professional degree", "0%").replace('%', ''))

            conn.execute("""
            INSERT OR REPLACE INTO education
            VALUES (?, ?, ?, ?)
            """, (zip_code, high_school, bachelors, graduate))

        except Exception as e:
            failed_zips.append(zip_code)

    conn.commit()
    conn.close()
    print(f"Saved education data for {len(zip_codes) - len(failed_zips)} ZIPs")

    # Write failures to file
    if failed_zips:
        with open("missing_education_data.txt", "w") as f:
            f.write("The following ZIP codes could not be processed:\n")
            f.write("\n".join(failed_zips))
        print(f"⚠️ Logged {len(failed_zips)} missing ZIPs to missing_education_data.txt")


if __name__ == "__main__":
    scrape_education_stats()