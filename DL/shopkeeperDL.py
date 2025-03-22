import sqlite3
from DL.database import getDbConnection

def insertShopkeeper(name, contactInfo, brand):
    """Insert a new shopkeeper into the database and return success status and message."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO Shopkeepers (Name, Contact_Info, Brand)
            VALUES (?, ?, ?)
        ''', (name, contactInfo, brand))

        conn.commit()
        return True, "Shopkeeper added successfully."

    except sqlite3.IntegrityError:
        return False, "A shopkeeper with this information already exists."
    except sqlite3.Error as e:
        return False, f"Database error occurred while adding the shopkeeper: {e}"
    finally:
        conn.close()

def updateShopkeeper(shopkeeperId, name, contactInfo, brand):
    """Updates an existing shopkeeper in the database."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE Shopkeepers
            SET Name = ?, Contact_Info = ?, Brand = ?
            WHERE ID = ?
        ''', (name, contactInfo, brand, shopkeeperId))

        if cursor.rowcount == 0:
            return False, "Shopkeeper not found."

        conn.commit()
        return True, "Shopkeeper updated successfully."
    except sqlite3.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()


def fetchShopkeepers():
    """Fetch all shopkeeper data from the database."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        # print("Fetching shopkeepers...")
        query = '''
            SELECT s.ID, s.Name, s.Brand, s.Contact_Info, 
                   COALESCE(k.Total_Due, 0) AS Total_Due,
                   COALESCE(SUM(p.Amount_Paid), 0) AS Paid_Amount,
                   (COALESCE(k.Total_Due, 0) - COALESCE(SUM(p.Amount_Paid), 0)) AS Remaining,
                   MAX(k.Last_Payment_Date) AS Last_Submission, s.IsDeleted
            FROM Shopkeepers s
            LEFT JOIN Khata k ON s.ID = k.Shopkeeper_ID
            LEFT JOIN Payments p ON s.ID = p.Shopkeeper_ID
            GROUP BY s.ID, s.Name, s.Brand, s.Contact_Info, k.Total_Due, s.IsDeleted
        '''
        cursor.execute(query)
        shopkeepers = cursor.fetchall()
        conn.close()
        print("Shopkeepers fetched successfully.")

        return shopkeepers, None  # No error, return data

    except sqlite3.Error as e:
        return None, f"Database Error: {e}"
    except Exception as e:
        return None, f"Unexpected Error: {e}"

def deleteShopkeeper(shopkeeperId):
    """Marks a shopkeeper as deleted in the database."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Shopkeepers
            SET IsDeleted = 1
            WHERE ID = ?
        ''', (shopkeeperId,))
        if cursor.rowcount == 0:
            return False, "Shopkeeper not found."

        conn.commit()
        conn.close()
        return True, "Shopkeeper deleted successfully."

    except sqlite3.Error as e:
        return False, f"Database Error: {e}"
    except Exception as e:
        return False, f"Unexpected Error: {e}"

# def updateShopkeeper(shopkeeperId, name, contactInfo):
#     """Updates an existing shopkeeper in the database."""
#     try:
#         conn = getDbConnection()
#         cursor = conn.cursor()

#         cursor.execute('''
#             UPDATE Shopkeepers
#             SET Name = ?, Contact_Info = ?
#             WHERE ID = ?
#         ''', (name, contactInfo, shopkeeperId))

#         if cursor.rowcount == 0:
#             return False, "Shopkeeper not found."

#         conn.commit()
#         return True, "Shopkeeper updated successfully."
#     except sqlite3.Error as e:
#         return False, f"Database Error: {e}"
#     finally:
#         conn.close()
