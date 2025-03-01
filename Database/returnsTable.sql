WITH ReturnAmounts AS (
    -- Calculate total return value per order considering multiple items
    SELECT 
        r.Order_ID, 
        SUM(r.Quantity_Returned * (oi.Price / oi.Quantity)) AS Total_Return_Value
    FROM Returns r
    JOIN Order_Items oi 
        ON r.Order_ID = oi.Order_ID 
        AND r.Product_SKU = oi.Product_SKU
    GROUP BY r.Order_ID
)
SELECT 
    o.Order_ID, 
    s.Name AS Shopkeeper_Name, 
    sm.Name AS Salesman_Name, 
    o.Order_Date, 
    o.Total_Amount AS Original_Order_Total, 
    COALESCE(ra.Total_Return_Value, 0) AS Total_Returns, 
    (o.Total_Amount - COALESCE(ra.Total_Return_Value, 0)) AS Updated_Order_Total
FROM Orders o
JOIN Shopkeepers s ON o.Shopkeeper_ID = s.ID
JOIN Salesmen sm ON o.Salesman_ID = sm.ID
LEFT JOIN ReturnAmounts ra ON o.Order_ID = ra.Order_ID
ORDER BY o.Order_Date DESC;
