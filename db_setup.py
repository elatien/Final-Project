# db_setup.py
# we used chatGPT to debug and get structure of the code

import sqlite3
import os

def initialize_db():
    if os.path.exists("FINALPROJECTDB.db"):
        os.remove("FINALPROJECTDB.db")
    
    conn = sqlite3.connect("FINALPROJECTDB.db")
    cursor = conn.cursor()
    
    cursor.executescript("""
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE income (
        zip_code TEXT PRIMARY KEY,
        median_income INTEGER
    );
    
    CREATE TABLE education (
        zip_code TEXT PRIMARY KEY,
        high_school REAL,
        bachelors REAL,
        graduate REAL,
        FOREIGN KEY (zip_code) REFERENCES income(zip_code)
    );
    
    CREATE TABLE restaurants (
        id TEXT PRIMARY KEY,
        name TEXT,
        rating REAL,
        review_count INTEGER,
        zip_code TEXT,
        FOREIGN KEY (zip_code) REFERENCES income(zip_code)
    );
    """)
    
    print("Database created with 3 tables")
    conn.close()

if __name__ == "__main__":
    initialize_db()