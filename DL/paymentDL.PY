# paymentDL.py
from BL import backupManager
from DL.database import getDbConnection

def addPayment(shopkeeper_id, order_id, salesman_id, amount_paid):
    """Adds a new payment record to the database."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        # Insert the payment record
        cursor.execute("""
            INSERT INTO Payments (Shopkeeper_ID, Order_ID, Salesman_ID, Amount_Paid, Payment_Date, IsDeleted)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 0)
        """, (shopkeeper_id, order_id, salesman_id, amount_paid))

        conn.commit()
        backupManager.backupDatabaseTable("Payments")  # Backup only this 
        backupManager.backupDatabaseTable("Khata")  # Backup only this table
        return True, "Payment added successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# paymentDL.updatePayment(self.current_payment_id, shopkeeper_id, order_id, salesman_id, amount_paid)
def updatePayment(payment_id, shopkeeper_id, order_id, salesman_id, amount_paid):
    """Updates an existing payment record in the database."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        # Update the payment record
        cursor.execute("""
            UPDATE Payments
            SET Shopkeeper_ID = ?, Order_ID = ?, Salesman_ID = ?, Amount_Paid = ?
            WHERE Payment_ID = ?
        """, (shopkeeper_id, order_id, salesman_id, amount_paid, payment_id))

        conn.commit()
        backupManager.backupDatabaseTable("Payments")  # Backup only this table
        return True, "Payment updated successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# paymentDL.getPayments()
# getPayments
def getPayments():
    """Fetch all payment records from the database."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()
        cursor.execute("""
            WITH PaymentsOrdered AS (
            SELECT 
                P.Payment_ID,
                P.Shopkeeper_ID,
                S.Name AS Shopkeeper_Name,
                K.Brand,
                K.Total_Due AS Khata_Value, -- Added Khata value
                P.Order_ID,
                O.Total_Amount,
                O.Order_Info,
                COALESCE(D.Discount_Amount, 0) AS Discount_Percentage,
                (O.Total_Amount * (1 - COALESCE(D.Discount_Amount, 0) / 100)) AS Initial_Discounted_Total,
                P.Amount_Paid,
                P.Payment_Date
            FROM Payments P
            JOIN Shopkeepers S ON P.Shopkeeper_ID = S.ID
            JOIN Orders O ON P.Order_ID = O.Order_ID
            LEFT JOIN Discounts D ON P.Order_ID = D.Order_ID AND D.IsDeleted = 0
            LEFT JOIN Khata K ON P.Shopkeeper_ID = K.Shopkeeper_ID -- Get Khata amount from Khata table
            WHERE P.IsDeleted = 0
        ),
        CumulativePayments AS (
            SELECT 
                P.Payment_ID,
                P.Shopkeeper_ID,
                P.Shopkeeper_Name,
                P.Brand,
                P.Khata_Value, -- Included Khata value
                P.Order_ID,
                P.Order_Info,
                P.Total_Amount,
                P.Discount_Percentage,
                P.Initial_Discounted_Total AS Discounted_Total,
                P.Amount_Paid,
                SUM(P.Amount_Paid) OVER (PARTITION BY P.Shopkeeper_ID, P.Order_ID ORDER BY P.Payment_Date) AS Cumulative_Paid,
                (P.Initial_Discounted_Total - 
                SUM(P.Amount_Paid) OVER (PARTITION BY P.Shopkeeper_ID, P.Order_ID ORDER BY P.Payment_Date)) AS Remaining_Due,
                P.Payment_Date
            FROM PaymentsOrdered P
        )
        SELECT * FROM CumulativePayments ORDER BY Shopkeeper_ID, Order_ID, Payment_Date;

        """)
        payments = cursor.fetchall()
        return payments, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def getPaymentById(payment_id):
    """Fetch shopkeeper, order, last payment, and amount paid for editing."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        query = """
        SELECT 
            s.name AS shopkeeper_name, 
            o.order_info, 
            p.amount_paid, 
            p.payment_date 
        FROM payments p
        JOIN shopkeepers s ON p.shopkeeper_id = s.ID
        JOIN orders o ON p.order_id = o.order_id
        WHERE p.payment_id = ? AND p.IsDeleted = 0
        ORDER BY p.payment_date DESC
        LIMIT 1;
        """
        cursor.execute(query, (payment_id,))
        paymentDetails = cursor.fetchone()

        cursor.close()
        conn.close()

        if not paymentDetails:
            return None, "No payment details found for this payment ID."

        return paymentDetails, None  # Return fetched payment details

    except Exception as e:
        return None, str(e)

def getPaymentByOrderId(orderID):
    """Fetches payment details for a given order ID from the database."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        query = """
        SELECT 
            p.payment_id, s.shopkeeper_name, b.brand_name, o.order_info, 
            p.total_amount, p.discount_percentage, p.discounted_total, 
            p.amount_paid, p.cumulative_paid, p.remaining_due, p.payment_date
        FROM payments p
        JOIN shopkeepers s ON p.shopkeeper_id = s.shopkeeper_id
        JOIN orders o ON p.order_id = o.order_id
        JOIN brands b ON o.brand_id = b.brand_id
        WHERE p.order_id = ? AND p.is_deleted = 0
        """
        cursor.execute(query, (orderID,))
        paymentDetails = cursor.fetchone()

        cursor.close()
        conn.close()

        if not paymentDetails:
            return None, "No payment details found for this order."

        return paymentDetails, None  # Return fetched payment details

    except Exception as e:
        return None, str(e)

def deletePayment(payment_id):
        """Marks a payment as deleted in the database."""
        try:
            conn = getDbConnection()
            cursor = conn.cursor()

            # Mark the payment as deleted
            cursor.execute("""
                UPDATE Payments
                SET IsDeleted = 1
                WHERE Payment_ID = ?
            """, (payment_id,))

            conn.commit()
            return True, "Payment deleted successfully."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

def getShopkeeperTotalPaidAndDue(shopkeeper_id):
    """Fetch total paid and total due for a given shopkeeper, ensuring no None values."""
    print("Func getShopkeeperTotalPaidAndDue : ", shopkeeper_id)
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        # Fetch total paid amount
        cursor.execute("SELECT COALESCE(SUM(Amount_Paid), 0) FROM Payments WHERE Shopkeeper_ID = ? AND IsDeleted = 0", (shopkeeper_id,))
        total_paid = cursor.fetchone()[0]  # Ensure a valid value

        # Fetch total due amount
        cursor.execute("SELECT COALESCE(Total_Due, 0) FROM Khata WHERE Shopkeeper_ID = ? AND IsDeleted = 0", (shopkeeper_id,))
        total_due_result = cursor.fetchone()
        total_due = total_due_result[0] if total_due_result else 0  # Handle missing row

        # print("Func getShopkeeperTotalPaidAndDue : ", shopkeeper_id, total_paid, total_due)
        return total_paid, total_due, None

    except Exception as e:
        return 0, 0, str(e)  # Default to 0 if any error occurs

    finally:
        conn.close()

def getOrderTotalAmount(order_id):
    """Fetch total amount for a given order after applying discount and subtracting payments."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        # Get the total order amount
        cursor.execute("""
            SELECT Total_Amount FROM Orders WHERE Order_ID = ?
        """, (order_id,))
        total_amount = cursor.fetchone()
        if not total_amount:
            return 0, "Order not found"

        total_amount = total_amount[0]

        # Get the discount percentage for this order (if any)
        cursor.execute("""
            SELECT Discount_Amount FROM Discounts WHERE Order_ID = ? AND IsDeleted = 0
        """, (order_id,))
        discount = cursor.fetchone()
        discount_percentage = discount[0] if discount else 0

        # Apply discount to the total amount
        discounted_amount = total_amount * (1 - (discount_percentage / 100))

        # Get the total paid amount for this order
        cursor.execute("""
            SELECT COALESCE(SUM(Amount_Paid), 0) FROM Payments 
            WHERE Order_ID = ? AND IsDeleted = 0
        """, (order_id,))
        total_paid = cursor.fetchone()[0]

        # Final amount due after discount and payments
        final_due = max(discounted_amount - total_paid, 0)

        return final_due, None

    except Exception as e:
        return None, str(e)

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
        # print("getDistinctShopkeepersFromOrders Funcs : ",shopkeepers)
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
