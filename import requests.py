import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime

# ================== CONFIGURATION ==================
DB_PATH = "FINALPROJECTDB.db"
CENSUS_API_KEY = "1940a3de74a60828d1309f8e708577a080d4aa34"
YELP_API_KEY = "Yzkti7a-ZCT0XIK_zJp-cb0fmCoTL6gV2N8mIaPJYmvb6BhgOyjmYxka6-alH9oJInH1MrQzFM9OEMjjZGQ6VWaa4W_s8tUMnuroB5Q-Vw3w06t8ELNBaJlczdDqZ3Yx"

# ================== DATABASE SETUP ==================
def initialize_database():
    """Create all tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS education_data (
        zip_code TEXT PRIMARY KEY,
        high_school_or_higher REAL,
        bachelors_degree_or_higher REAL,
        graduate_or_professional_degree REAL,
        unemployed REAL,
        mean_commute_time REAL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS income (
        zip_code TEXT PRIMARY KEY,
        median_income INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (zip_code) REFERENCES education_data(zip_code)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        rating REAL,
        review_count INTEGER,
        zip_code TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (zip_code) REFERENCES education_data(zip_code)
    )
    ''')
    
    conn.commit()
    conn.close()

# ================== DATA COLLECTION ==================
def scrape_education_data(zip_code):
    """Scrape education data from City-Data.com"""
    url = f"https://www.city-data.com/zips/{zip_code}.html"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        education_header = soup.find('h3', string=lambda text: text and "population 25 years and over" in text)
        
        if not education_header:
            return {"error": "Education section not found"}
        
        education_data = {}
        current_element = education_header.next_sibling
        
        while current_element:
            if current_element.name == 'ul':
                for li in current_element.find_all('li', recursive=False):
                    if li.text.strip():
                        parts = li.text.split(':')
                        if len(parts) >= 2:
                            category = parts[0].strip()
                            value = parts[1].strip()
                            education_data[category] = value
                break
            current_element = current_element.next_sibling
        
        return education_data if education_data else {"error": "No education data found"}
    
    except Exception as e:
        return {"error": str(e)}

def get_census_data(zip_codes):
    """Fetch median income data from Census API"""
    BASE_URL = "https://api.census.gov/data/2020/acs/acs5"
    data = []
    
    for zip_code in zip_codes:
        try:
            url = f"{BASE_URL}?get=B19013_001E&for=zip+code+tabulation+area:{zip_code}&key={CENSUS_API_KEY}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                json_data = response.json()
                if len(json_data) > 1:
                    median_income = json_data[1][0]
                    data.append((zip_code, median_income))
        except Exception as e:
            print(f"Error for {zip_code}: {str(e)}")
    
    return data

def get_yelp_data(zip_code):
    """Fetch restaurant data from Yelp API"""
    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    BASE_URL = "https://api.yelp.com/v3/businesses/search"
    
    try:
        params = {
            "location": zip_code,
            "term": "restaurants",
            "limit": 25
        }
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        return [
            (biz["name"], biz["rating"], biz["review_count"], zip_code)
            for biz in data.get("businesses", [])
        ]
    except Exception as e:
        print(f"Yelp error for {zip_code}: {str(e)}")
        return []

# ================== DATA SAVING ==================
def save_education_data(data, zip_code):
    """Save education data to database"""
    conn = None
    try:
        db_data = {
            'zip_code': zip_code,
            'high_school_or_higher': float(data.get('High school or higher', '0%').replace('%', '')),
            'bachelors_degree_or_higher': float(data.get("Bachelor's degree or higher", '0%').replace('%', '')),
            'graduate_or_professional_degree': float(data.get('Graduate or professional degree', '0%').replace('%', '')),
            'unemployed': float(data.get('Unemployed', '0%').replace('%', '')),
            'mean_commute_time': float(data.get('Mean travel time to work (commute)', '0 minutes').replace('minutes', '').strip())
        }
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO education_data 
        (zip_code, high_school_or_higher, bachelors_degree_or_higher, 
         graduate_or_professional_degree, unemployed, mean_commute_time)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', tuple(db_data.values()))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Education data save error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def save_census_data(data):
    """Save census data to database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for zip_code, median_income in data:
            cursor.execute('''
            INSERT OR REPLACE INTO income 
            (zip_code, median_income)
            VALUES (?, ?)
            ''', (zip_code, median_income))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Census data save error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def save_yelp_data(restaurants):
    """Save Yelp data to database"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.executemany(
            "INSERT INTO restaurants (name, rating, review_count, zip_code) VALUES (?, ?, ?, ?)", 
            restaurants
        )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Yelp data save error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

# ================== FOCUSED VISUALIZATIONS ==================
def create_focused_visualizations():
    """Create visualizations focusing on education, income, and Yelp reviews"""
    conn = sqlite3.connect(DB_PATH)
    
    # Load and merge all data
    edu_df = pd.read_sql('SELECT * FROM education_data', conn)
    income_df = pd.read_sql('SELECT * FROM income', conn)
    rest_df = pd.read_sql('''
        SELECT zip_code, 
               AVG(rating) as avg_rating, 
               AVG(review_count) as avg_reviews,
               COUNT(*) as num_restaurants
        FROM restaurants 
        GROUP BY zip_code
    ''', conn)
    
    conn.close()
    
    # Merge all datasets
    df = pd.merge(edu_df, income_df, on='zip_code', how='left')
    df = pd.merge(df, rest_df, on='zip_code', how='left')
    
    if df.empty:
        print("Not enough data for visualizations")
        return
    
    # Set style
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    # ================ VISUALIZATION 1: EDUCATION VS YELP RATINGS ================
    plt.figure(figsize=(12, 6))
    sns.lmplot(
        data=df,
        x='bachelors_degree_or_higher',
        y='avg_rating',
        hue='zip_code',
        height=6,
        aspect=1.5,
        ci=None,
        scatter_kws={'s': 100}
    )
    plt.title('Education Level (Bachelor\'s+) vs Yelp Restaurant Ratings', pad=20)
    plt.xlabel('Percentage with Bachelor\'s Degree or Higher')
    plt.ylabel('Average Yelp Rating')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig('education_vs_yelp.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # ================ VISUALIZATION 2: INCOME VS YELP RATINGS ================
    plt.figure(figsize=(12, 6))
    sns.regplot(
        data=df,
        x='median_income',
        y='avg_rating',
        scatter_kws={'s': 100, 'color': 'blue'},
        line_kws={'color': 'red'}
    )
    plt.title('Median Income vs Yelp Restaurant Ratings', pad=20)
    plt.xlabel('Median Income ($)')
    plt.ylabel('Average Yelp Rating')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig('income_vs_yelp.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # ================ VISUALIZATION 3: EDUCATION VS INCOME ================
    plt.figure(figsize=(12, 6))
    sns.scatterplot(
        data=df,
        x='bachelors_degree_or_higher',
        y='median_income',
        hue='avg_rating',
        size='avg_reviews',
        sizes=(50, 200),
        palette='coolwarm'
    )
    plt.title('Education Level vs Median Income (Colored by Yelp Rating)', pad=20)
    plt.xlabel('Percentage with Bachelor\'s Degree or Higher')
    plt.ylabel('Median Income ($)')
    plt.legend(title='Yelp Rating', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig('education_vs_income.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # ================ VISUALIZATION 4: CORRELATION HEATMAP ================
    plt.figure(figsize=(10, 8))
    corr = df[['high_school_or_higher', 'bachelors_degree_or_higher',
              'graduate_or_professional_degree', 'median_income',
              'avg_rating', 'avg_reviews']].corr()
    
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
    
    sns.heatmap(
        corr, 
        mask=mask, 
        cmap=cmap, 
        vmax=1, 
        center=0,
        square=True, 
        linewidths=.5, 
        cbar_kws={"shrink": .5},
        annot=True,
        annot_kws={"size": 10}
    )
    plt.title('Correlation Between Education, Income, and Yelp Reviews', pad=20)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()

# ================== MAIN PROGRAM ==================
def main():
    # Initialize database
    initialize_database()
    
    # ZIP codes to analyze
    zip_codes = ["48103", "48104", "48105", "48108"]
    
    # Collect and save all data
    print("=== Collecting Education Data ===")
    for zip_code in zip_codes:
        data = scrape_education_data(zip_code)
        if "error" not in data:
            save_education_data(data, zip_code)
    
    print("\n=== Collecting Census Data ===")
    census_data = get_census_data(zip_codes)
    if census_data:
        save_census_data(census_data)
    
    print("\n=== Collecting Yelp Data ===")
    for zip_code in zip_codes:
        restaurants = get_yelp_data(zip_code)
        if restaurants:
            save_yelp_data(restaurants)
    
    # Create visualizations
    print("\n=== Generating Visualizations ===")
    create_focused_visualizations()
    print("Visualizations saved as PNG files in your working directory")

if __name__ == "__main__":
    # Set matplotlib backend
    import matplotlib
    matplotlib.use('TkAgg')  # Alternatives: 'Qt5Agg', 'Agg'
    
    # Run the program
    main()