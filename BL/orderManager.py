from DL import orderDL
from BL import backupManager

def addOrder(shopkeeper_id, salesman_id, order_info, discount):
    """Handles order creation and ensures backup."""
    success, message, order_id = orderDL.addOrder(shopkeeper_id, salesman_id, order_info, discount)
    if success:
        backupManager.backupDatabaseTable("Orders")  # Backup Orders table
        backupManager.backupDatabaseTable("Discounts")  # Backup Discounts table
    return success, message, order_id


def addOrderItem(orderID, productSKU, quantity, price):
    """Adds an item to the order and triggers backup."""
    try:
        success, message = orderDL.addOrderItem(orderID, productSKU, quantity, price)
        if success:
            backupManager.backupDatabaseTable("Order_Items")
        return success, message
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def applyDiscount(orderID, shopkeeperID, discountAmount, appliedBy):
    """Applies a discount to an order and triggers backup."""
    try:
        success, message = orderDL.applyDiscount(orderID, shopkeeperID, discountAmount, appliedBy)
        if success:
            backupManager.backupDatabaseTable("Discounts")
        return success, message
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def finalizeOrder(orderID):
    """Finalizes the order by updating totals and the khata."""
    try:
        success, message = orderDL.finalizeOrder(orderID)
        if success:
            backupManager.backupDatabaseTable("Orders")
            backupManager.backupDatabaseTable("Khata")
        return success, message
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
    


def getOrders():
    """Fetch all orders with their details."""
    orders, error = orderDL.getOrders()
    if error:
        return None, error
    return orders, None

def getOrderDetails(orderID):
    """Fetches details of a specific order."""
    details, error = orderDL.getOrderDetails(orderID)
    if error:
        return None, error
    return details, None

def deleteOrder(orderID):
    """Deletes an order and its related records, then triggers a backup."""
    success, error = orderDL.deleteOrder(orderID)
    if success:
        backupManager.backupDatabaseTable("Orders")
        backupManager.backupDatabaseTable("Order_Items")
        backupManager.backupDatabaseTable("Discounts")
    if error:
        return False, error
    return True, None


