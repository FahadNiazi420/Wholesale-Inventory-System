SELECT 
    O.Order_ID, 
    SK.Name AS Shopkeeper_Name, 
    SM.Name AS Salesman_Name, 
    O.Order_Date, 
    O.Total_Amount, 
    OI.Order_Item_ID, 
    P.Name AS Product_Name, 
    P.Brand, 
    P.Size, 
    OI.Quantity, 
    OI.Price
FROM Orders O
JOIN Order_Items OI ON O.Order_ID = OI.Order_ID
JOIN Shopkeepers SK ON O.Shopkeeper_ID = SK.ID
JOIN Salesmen SM ON O.Salesman_ID = SM.ID
JOIN Products P ON OI.Product_SKU = P.SKU;
