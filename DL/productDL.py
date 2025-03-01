import sqlite3
from DL.database import getDbConnection

def insertProduct(sku, name, brand, size, quantity, price):
    """Insert a new product into the database and return success status and message."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        cursor.execute("SELECT SKU FROM Products WHERE SKU = ?", (sku,))
        if cursor.fetchone():
            return False, "A product with this SKU already exists. Please use a unique SKU."

        cursor.execute('''
            INSERT INTO Products (SKU, Name, Brand, Size, Quantity, Price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (sku, name, brand, size, quantity, price))

        conn.commit()
        return True, "Product added successfully."

    except sqlite3.IntegrityError:
        return False, "A product with this SKU already exists. Try using a different SKU."
    except sqlite3.Error as e:
        return False, "Database error occurred while adding the product. Please try again."
    finally:
        conn.close()
def fetchProducts():
    """Fetch all product data from the database."""
    try:
        conn = getDbConnection()
        if not conn:
            return None, "Database connection failed."

        cursor = conn.cursor()
        query = """
        SELECT 
            SKU, 
            Name, 
            Brand, 
            Size, 
            Quantity, 
            Price AS "Total Price", 
            ROUND(Price / NULLIF(Quantity, 0), 2) AS "Per Item Price"
        FROM Products;
        """
        cursor.execute(query)
        products = cursor.fetchall()
        conn.close()

        return products, None  # No error, return data

    except sqlite3.Error as e:
        return None, f"Database Error: {e}"
    except Exception as e:
        return None, f"Unexpected Error: {e}"
def deleteProduct(sku):
    """Deletes a product from the database based on SKU."""
    try:
        conn = getDbConnection()
        if not conn:
            return False, "Database connection failed."

        cursor = conn.cursor()
        cursor.execute("DELETE FROM Products WHERE SKU = ?", (sku,))
        if cursor.rowcount == 0:
            return False, "Product not found."

        conn.commit()
        conn.close()
        return True, None  # No error, deletion successful

    except sqlite3.Error as e:
        return False, f"Database Error: {e}"
    except Exception as e:
        return False, f"Unexpected Error: {e}"

def updateProduct(oldSku, sku, name, brand, size, quantity, price):
    """Updates an existing product in the database."""
    try:
        conn = getDbConnection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE Products
            SET sku = ?, name = ?, brand = ?, size = ?, quantity = ?, price = ?
            WHERE sku = ?
        ''', (sku, name, brand, size, quantity, price, oldSku))

        if cursor.rowcount == 0:
            return False  # No rows updated, meaning product was not found

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return False
    finally:
        conn.close()