from DL import shopkeeperDL
from BL import backupManager

def addShopkeeper(name, contact_info, brand):
    """Validates and adds a shopkeeper to the database, then triggers backup."""
    try:
        success, message = shopkeeperDL.insertShopkeeper(name, contact_info, brand)
        if success:
            backupManager.backupDatabaseTable("Shopkeepers")  # Backup only this table
        return success, message
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def updateShopkeeper(shopkeeper_id, name, contact_info, brand):
    """Updates an existing shopkeeper in the database."""
    try:
        success, message = shopkeeperDL.updateShopkeeper(shopkeeper_id, name, contact_info, brand)
        if success:
            backupManager.backupDatabaseTable("Shopkeepers")  # Backup only this table
            return True, "Shopkeeper updated successfully!"
        return False, message
    except Exception as e:
        return False, f"Unexpected error: {e}"


def getShopkeepers():
    """Retrieve shopkeeper data for the UI table."""
    shopkeepers, error = shopkeeperDL.fetchShopkeepers()
    if error:
        return None, error
    return shopkeepers, None

def deleteShopkeeper(shopkeeper_id):
    """Deletes a shopkeeper and returns success status."""
    success, error = shopkeeperDL.deleteShopkeeper(shopkeeper_id)
    if success:
        backupManager.backupDatabaseTable("Shopkeepers")  # Backup after deletion
    if error:
        return False, error
    return True, None
