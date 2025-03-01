import os
import sqlite3
import pandas as pd

dbPath = os.path.join("Database", "inventory.db")
backupFolder = "Backup"

def backupDatabase():
    """Exports all database tables to separate Excel files in the backup folder."""
    try:
        if not os.path.exists(backupFolder):
            os.makedirs(backupFolder)

        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()

        # Fetch all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

            if not df.empty:  # Only save if the table has data
                filePath = os.path.join(backupFolder, f"{table}.xlsx")
                df.to_excel(filePath, index=False)
                print(f"Backup saved: {filePath}")
            else:
                print(f"Skipped empty table: {table}")

        conn.close()
        print("Backup completed successfully.")

    except sqlite3.Error as e:
        print(f"Database Error during backup: {e}")
    except Exception as e:
        print(f"Unexpected Error during backup: {e}")


def backupDatabaseTable(tableName):
    """Exports only the updated table to an Excel file in the backup folder."""
    try:
        if not os.path.exists(backupFolder):
            os.makedirs(backupFolder)

        conn = sqlite3.connect(dbPath)

        # Check if the table exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
        if not cursor.fetchone():
            print(f"Table '{tableName}' does not exist in the database.")
            return
        
        # Export only the updated table
        df = pd.read_sql_query(f"SELECT * FROM {tableName}", conn)
        filePath = os.path.join(backupFolder, f"{tableName}.xlsx")
        df.to_excel(filePath, index=False, engine="openpyxl")

        conn.close()
        print(f"Backup for '{tableName}' completed successfully.")
    
    except sqlite3.Error as e:
        print(f"Database Error during backup: {e}")
    except Exception as e:
        print(f"Unexpected Error during backup: {e}")
