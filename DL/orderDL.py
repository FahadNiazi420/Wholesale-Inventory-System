from datetime import datetime
from BL import backupManager
from DL.database import getDbConnection

def addOrder(shopkeeper_id, salesman_id, order_info, discount):
    """Creates a new order and applies a discount."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        # Insert into Orders table
        cursor.execute("""
            INSERT INTO Orders (Shopkeeper_ID, Salesman_ID, Total_Amount, Order_Info)
            VALUES (?, ?, 0,?)
        """, (shopkeeper_id, salesman_id,order_info))
        order_id = cursor.lastrowid  # Get the generated order ID

        # Insert into Discounts table
        cursor.execute("""
            INSERT INTO Discounts (Shopkeeper_ID, Order_ID, Discount_Amount, Applied_By)
            VALUES (?, ?, ?, ?)
        """, (shopkeeper_id, order_id, discount, "System"))

        conn.commit()
        return True, "Order created successfully!", order_id  # Return order_id
    except Exception as e:
        return False, str(e), None
    finally:
        conn.close()


def addOrderItem(order_id, product_sku, quantity, price):
    """Adds an item to an order and updates total amount."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        # Insert order item
        cursor.execute("""
            INSERT INTO Order_Items (Order_ID, Product_SKU, Quantity, Price)
            VALUES (?, ?, ?, ?)
        """, (order_id, product_sku, quantity, price))

        # Update order total
        cursor.execute("""
            UPDATE Orders
            SET Total_Amount = Total_Amount + ?
            WHERE Order_ID = ?
        """, (quantity * price, order_id))

        conn.commit()
        return True, "Item added successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def updateOrder(order_id, shopkeeper_id, salesman_id, order_info, discount):
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Orders
            SET Shopkeeper_ID = ?, Salesman_ID = ?,Order_Info = ?
            WHERE Order_ID = ?
        """, (shopkeeper_id, salesman_id,order_info, order_id))

        cursor.execute("""
            UPDATE Discounts
            SET Discount_Amount = ?, Applied_By = ?
            WHERE Order_ID = ?
        """, (discount, "System", order_id))
        backupManager.backupDatabaseTable("Discounts")  # Backup Discounts table
        conn.commit()
        return True, "Order updated successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def finalizeOrder(order_id):
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Orders
            SET IsDeleted = 0
            WHERE Order_ID = ?
        """, (order_id,))

        conn.commit()
        return True, "Order finished successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def getOrders():
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.Order_ID,o.Order_Info , s.Name AS Shopkeeper, sm.Name AS Salesman, o.Order_Date, o.Total_Amount, 
               (o.Total_Amount * d.Discount_Amount / 100) AS Discount_Amount, o.Total_Amount-(o.Total_Amount * d.Discount_Amount / 100) AS Grand_Total
            FROM Orders o
            JOIN Shopkeepers s ON o.Shopkeeper_ID = s.ID
            JOIN Salesmen sm ON o.Salesman_ID = sm.ID
            LEFT JOIN Discounts d ON o.Order_ID = d.Order_ID
            WHERE o.IsDeleted = 0
        """)
        orders = cursor.fetchall()
        return orders, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def getOrderDetails(order_id):
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.Order_ID, s.Name AS Shopkeeper, sm.Name AS Salesman, o.Order_Date, o.Total_Amount, d.Discount_Amount
            FROM Orders o
            JOIN Shopkeepers s ON o.Shopkeeper_ID = s.ID
            JOIN Salesmen sm ON o.Salesman_ID = sm.ID
            LEFT JOIN Discounts d ON o.Order_ID = d.Order_ID
            WHERE o.Order_ID = ?
        """, (order_id,))
        order_details = cursor.fetchone()
        return order_details, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

# def getOrderItems(order_id):
#     try:
#         conn = getDbConnection()
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT oi.Product_SKU, p.Name, oi.Quantity, oi.Price, (oi.Quantity * oi.Price) AS Total
#             FROM Order_Items oi
#             JOIN Products p ON oi.Product_SKU = p.SKU
#             WHERE oi.Order_ID = ? AND oi.IsDeleted = 0
#         """, (order_id,))
#         order_items = cursor.fetchall()
#         return order_items, None
#     except Exception as e:
#         return None, str(e)
#     finally:
#         conn.close()

def deleteOrder(order_id):
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Orders
            SET IsDeleted = 1
            WHERE Order_ID = ?
        """, (order_id,))
        conn.commit()
        return True, "Order deleted successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def getOrderById(order_id):
    """Fetch a single order by its ID."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.Order_ID, o.Order_Info, s.Name AS Shopkeeper, sm.Name AS Salesman, o.Order_Date, o.Total_Amount, 
                   (o.Total_Amount * d.Discount_Amount / 100) AS Discount_Amount, o.Total_Amount-(o.Total_Amount * d.Discount_Amount / 100) AS Grand_Total
            FROM Orders o
            JOIN Shopkeepers s ON o.Shopkeeper_ID = s.ID
            JOIN Salesmen sm ON o.Salesman_ID = sm.ID
            LEFT JOIN Discounts d ON o.Order_ID = d.Order_ID
            WHERE o.Order_ID = ? AND o.IsDeleted = 0
        """, (order_id,))
        order = cursor.fetchone()
        return order, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def calculateOrderTotals(order_id):
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(oi.Price) AS Total_Amount, d.Discount_Amount
            FROM Order_Items oi
            LEFT JOIN Discounts d ON oi.Order_ID = d.Order_ID
            WHERE oi.Order_ID = ? AND oi.IsDeleted = 0
        """, (order_id,))
        result = cursor.fetchone()
        total_amount = result[0] if result[0] else 0
        discount = (result[1] / 100) * total_amount if result[1] else 0
        grand_total = total_amount - discount
        return total_amount,discount, grand_total
    except Exception as e:
        return None, None, None, str(e)
    finally:
        conn.close()

def getShopkeepers():
    """Fetch all active shopkeepers with their IDs for the combo box."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID, Name, Brand FROM Shopkeepers WHERE IsDeleted = 0
        """)
        shopkeepers = cursor.fetchall()
        return shopkeepers, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def getProductsByBrand(brand):
    """Fetch products for the given brand."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SKU, Name, Size FROM Products WHERE Brand = ? AND IsDeleted = 0
        """, (brand,))
        products = cursor.fetchall()
        return products, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def getSalesmen():
    """Fetch all active salesmen with their IDs for the combo box."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID, Name FROM Salesmen WHERE IsDeleted = 0
        """)
        salesmen = cursor.fetchall()
        return salesmen, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def getProducts():
    """Fetch all products with SKU, name, and size for the combo box."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SKU, Name, Size FROM Products
        """)
        products = cursor.fetchall()
        return products, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def getProductPrice(sku):
    """Fetch product price per item and available quantity based on SKU."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT Price, Quantity FROM Products WHERE SKU = ?", (sku,))
        result = cursor.fetchone()
        
        if result:
            price, quantity = result
            pricePerItem = price / quantity if quantity > 0 else 0
            # print(pricePerItem)
            return price ,quantity # Returning both price and available quantity
        else:
            return None, "Product not found"
    
    except Exception as e:
        return None, str(e)
    
    finally:
        conn.close()

def getOrderItems(order_id):
    """Fetch order items for a given order."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT oi.Order_Item_ID, p.Name, oi.Quantity,  oi.Price AS Bill
            FROM Order_Items oi
            JOIN Products p ON oi.Product_SKU = p.SKU
            WHERE oi.Order_ID = ? AND oi.IsDeleted = 0
        """, (order_id,))

        items = cursor.fetchall()
        # print(f"Fetched {len(items)} items for Order ID {order_id}: {items}")  # Debugging line
        return items  
    except Exception as e:
        print(f"Error fetching order items: {e}")  # Debugging line
        return []
    finally:
        conn.close()


def getOrderItemById(order_item_id):
    """Fetch a single order item for editing."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT oi.Product_SKU, oi.Quantity, oi.Quantity * oi.Price AS Bill
            FROM Order_Items oi
            WHERE oi.Order_Item_ID = ? AND oi.IsDeleted = 0
        """, (order_item_id,))
        return cursor.fetchone()
    except Exception as e:
        return None
    finally:
        conn.close()

def removeOrderItem(order_item_id):
    """Marks an order item as deleted and updates order total."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        # Get item details before deletion
        cursor.execute("""
            SELECT Order_ID, Quantity * Price FROM Order_Items WHERE Order_Item_ID = ?
        """, (order_item_id,))
        order_details = cursor.fetchone()

        if not order_details:
            return False, "Item not found"

        order_id, item_total = order_details

        # Mark item as deleted
        cursor.execute("UPDATE Order_Items SET IsDeleted = 1 WHERE Order_Item_ID = ?", (order_item_id,))

        # Reduce order total
        cursor.execute("""
            UPDATE Orders
            SET Total_Amount = Total_Amount - ?
            WHERE Order_ID = ?
        """, (item_total, order_id))

        conn.commit()
        return True, "Item removed successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

