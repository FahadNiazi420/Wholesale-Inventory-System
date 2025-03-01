SELECT 
    P.SKU,
    P.Name,
    P.Brand,
    P.Size,
    P.Quantity,
    P.Price,
    P.Last_Updated,
    CASE 
        WHEN P.Quantity < 10 THEN 'Low Stock' 
        ELSE 'Sufficient Stock' 
    END AS Stock_Status,
    -- Total number of inventory updates for this product
    (SELECT COUNT(*) 
     FROM Inventory_Updates IU 
     WHERE IU.Product_SKU = P.SKU) AS Update_Count,
    -- Date of the most recent inventory update
    (SELECT MAX(IU.Update_Date) 
     FROM Inventory_Updates IU 
     WHERE IU.Product_SKU = P.SKU) AS Last_Update_Date,
    -- Total quantity returned for this product (if any)
    COALESCE(
      (SELECT SUM(R.Quantity_Returned) 
       FROM Returns R 
       WHERE R.Product_SKU = P.SKU), 0) AS Total_Returned
FROM Products P;
