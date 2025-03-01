SELECT 
    SKU, 
    Name, 
    Brand, 
    Size, 
    Quantity, 
    Price AS "Total Price", 
    ROUND(Price / NULLIF(Quantity, 0), 2) AS "Per Item Price"
FROM Products;
