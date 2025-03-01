import sqlite3
import os

dbPath = os.path.join("Database", "inventory.db")

def initializeDb():
    """Ensure the database exists and create tables if necessary."""
    try:
        if not os.path.exists("Database"):
            os.makedirs("Database")

        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()

        cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Products (
            sku TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            size TEXT,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            lastUpdated DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE Shopkeepers (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Contact_Info TEXT);
)
        ''')

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    finally:
        conn.close()

def getDbConnection():
    """Returns a database connection."""
    return sqlite3.connect(dbPath)
