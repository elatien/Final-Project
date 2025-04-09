import sql  # Just for the SQL syntax highlighting in your editor
import os
from pathlib import Path

# 1. Delete existing database if it exists
DB_PATH = "FINALPROJECTDB.db"

def delete_database():
    """Completely remove the database file"""
    db_file = Path(DB_PATH)
    if db_file.exists():
        db_file.unlink()  # Delete the file
        print(f"✅ Deleted existing database at {DB_PATH}")
    else:
        print(f"⚠️ No database found at {DB_PATH}")

# 2. Create fresh database
def create_new_database():
    """Initialize a clean database with proper schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executescript("""
    PRAGMA foreign_keys = ON;
    
    CREATE TABLE income (
        zip_code TEXT PRIMARY KEY,
        median_income INTEGER,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE education (
        zip_code TEXT PRIMARY KEY,
        high_school_or_higher REAL,
        bachelors_degree_or_higher REAL,
        graduate_or_professional_degree REAL,
        FOREIGN KEY (zip_code) REFERENCES income(zip_code)
    );
    
    CREATE TABLE restaurants (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        rating REAL NOT NULL,
        review_count INTEGER NOT NULL,
        zip_code TEXT NOT NULL,
        FOREIGN KEY (zip_code) REFERENCES income(zip_code)
    );
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Created new database at {DB_PATH}")

# 3. Manual Verification (Run in DB Browser after creation)
VERIFICATION_SQL = """
SELECT name FROM sqlite_master WHERE type='table';
PRAGMA table_info(income);
PRAGMA table_info(education);
PRAGMA table_info(restaurants);
PRAGMA foreign_key_check;
"""

if __name__ == "__main__":
    delete_database()
    create_new_database()
    print("\nRun this in DB Browser to verify:")
    print(VERIFICATION_SQL)
    initialize_database()