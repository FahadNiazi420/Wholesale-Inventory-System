from DL import productDL
from BL import backupManager

def addProduct(sku, name, brand, size, quantity, price):
    """Validates and adds product to the database, then triggers backup."""
    try:
        success, message = productDL.insertProduct(sku, name, brand, size, quantity, price)
        if success:
            backupManager.backupDatabaseTable("Products")  # Backup only this table
        return success, message
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
def updateProduct(oldSku, sku, name, brand, size, quantity, price):
    """Updates an existing product in the database."""
    try:
        success = productDL.updateProduct(oldSku, sku, name, brand, size, quantity, price)
        if success:
            backupManager.backupDatabaseTable("Products")  # Backup only this table
            return True, "Product updated successfully!"
        return False, "Failed to update product. SKU might already exist."
    except Exception as e:
        return False, f"Unexpected error: {e}"
def getProducts():
    """Retrieve product data for the UI table."""
    products, error = productDL.fetchProducts()
    if error:
        return None, error
    return products, None

def deleteProduct(sku):
    """Deletes a product and returns success status."""
    success, error = productDL.deleteProduct(sku)
    if success:
        backupManager.backupDatabaseTable("Products")
    if error:
        return False, error
    return True, None
