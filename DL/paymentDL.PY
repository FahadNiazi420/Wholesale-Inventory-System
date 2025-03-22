# paymentDL.py
from BL import backupManager
from DL.database import getDbConnection

def getShopkeeperTotalPaidAndDue(shopkeeper_id):
    """Fetch total paid and total due for a given shopkeeper, ensuring no None values."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COALESCE((SELECT SUM(Amount) FROM Payments WHERE Shopkeeper_ID = ? AND IsDeleted = 0), 0) AS TotalPaid,
                COALESCE((SELECT Total_Due FROM Khata WHERE Shopkeeper_ID = ?), 0) AS TotalDue
        """, (shopkeeper_id, shopkeeper_id))
        
        result = cursor.fetchone()
        total_paid = result[0] if result else 0
        total_due = result[1] if result else 0
        
        return total_paid, total_due, None
    except Exception as e:
        return 0, 0, str(e)  # Default to 0 if any error occurs
    finally:
        conn.close()




def getDistinctShopkeepersFromOrders():
    """Fetch distinct shopkeepers who have placed orders."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT s.ID, s.Name 
            FROM Orders o
            JOIN Shopkeepers s ON o.Shopkeeper_ID = s.ID
            WHERE o.IsDeleted = 0
        """)
        shopkeepers = cursor.fetchall()
        return shopkeepers, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def getOrdersByShopkeeper(shopkeeper_id):
    """Fetch orders for a given shopkeeper including Order_ID and Order_Info."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Order_ID, Order_Info FROM Orders 
            WHERE Shopkeeper_ID = ? AND IsDeleted = 0
        """, (shopkeeper_id,))
        orders = cursor.fetchall()
        return orders, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def getShopkeeperBrand(shopkeeper_id):
    """Fetch the brand corresponding to a given shopkeeper."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Brand FROM Shopkeepers WHERE ID = ? AND IsDeleted = 0
        """, (shopkeeper_id,))
        brand = cursor.fetchone()
        return (brand[0] if brand else None), None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def getSalesmanByOrder(order_id):
    """Fetch salesman details for a given order."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.ID, s.Name FROM Orders o
            JOIN Salesmen s ON o.Salesman_ID = s.ID
            WHERE o.Order_ID = ?
        """, (order_id,))
        salesman = cursor.fetchone()
        return salesman, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def getOrderTotalAmount(order_id):
    """Fetch total amount for a given order."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Total_Amount FROM Orders WHERE Order_ID = ?
        """, (order_id,))
        total_amount = cursor.fetchone()
        return total_amount[0] if total_amount else 0, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def getLastSubmissionDate(shopkeeper_id):
    """Fetch the last payment submission date for a shopkeeper."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MAX(Payment_Date) FROM Payments WHERE Shopkeeper_ID = ?
        """, (shopkeeper_id,))
        last_date = cursor.fetchone()
        return last_date[0] if last_date and last_date[0] else "N/A", None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()
