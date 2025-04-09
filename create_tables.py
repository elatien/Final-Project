import sqlite3

def create_tables():
    # Connect to your SQLite database
    conn = sqlite3.connect("FINALPROJECTDB.db")  # Correct your DB name here
    cur = conn.cursor()

    # Create the 'restaurants' table if it doesn't exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rating REAL NOT NULL,
        review_count INTEGER NOT NULL,
        zip_code TEXT NOT NULL
    );
    """)

    # Create the 'income' table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS income (
        zip_code TEXT PRIMARY KEY,
        median_income INTEGER NOT NULL
    );
    """)

    # Create the 'housing_prices' table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS housing_prices (
        zip_code TEXT PRIMARY KEY,
        median_price INTEGER NOT NULL
    );
    """)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Tables created successfully!")

# Run the script if this file is executed directly
if __name__ == "__main__":
    create_tables()
