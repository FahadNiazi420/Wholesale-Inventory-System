# SalesmenDL.py
from DL.database import getDbConnection
from BL import backupManager

def getSalesmen():
    """Fetch all salesmen records from the database."""
    try:
        with getDbConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ID, Name, Contact_Info, Total_Sales, Total_Collections, IsDeleted
                FROM Salesmen
            """)
            salesmen = cursor.fetchall()
            return salesmen, None
    except Exception as e:
        return None, str(e)

def addSalesman(name, contact_info):
    """Add a new salesman to the database."""
    try:
        with getDbConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Salesmen (Name, Contact_Info, Total_Sales, Total_Collections, IsDeleted)
                VALUES (?, ?, 0, 0, 0)
            """, (name, contact_info))
            conn.commit()
            backupManager.backupDatabaseTable("Salesmen")  # Backup the Salesmen table
            return True, "Salesman added successfully."
    except Exception as e:
        return False, str(e)

def updateSalesman(salesman_id, name, contact_info):
    """Update an existing salesman in the database."""
    try:
        with getDbConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Salesmen
                SET Name = ?, Contact_Info = ?
                WHERE ID = ?
            """, (name, contact_info, salesman_id))
            conn.commit()
            backupManager.backupDatabaseTable("Salesmen")  # Backup the Salesmen table
            return True, "Salesman updated successfully."
    except Exception as e:
        return False, str(e)

def deleteSalesman(salesman_id):
    """Mark a salesman as deleted in the database."""
    try:
        with getDbConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Salesmen
                SET IsDeleted = 1
                WHERE ID = ?
            """, (salesman_id,))
            conn.commit()
            backupManager.backupDatabaseTable("Salesmen")  # Backup the Salesmen table
            return True, "Salesman deleted successfully."
    except Exception as e:
        return False, str(e)
