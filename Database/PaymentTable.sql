SELECT 
    K.ID AS Khata_ID,
    SK.Name AS Shopkeeper_Name,
    K.Brand,
    K.Total_Due,
	P.Amount_Paid,
    K.Last_Payment_Date,
    O.Order_Date,
    P.Payment_Date,
	SM.Name AS Salesman_Name
FROM Khata K
JOIN Payments P ON K.Shopkeeper_ID = P.Shopkeeper_ID
JOIN Shopkeepers SK ON K.Shopkeeper_ID = SK.ID
JOIN Salesmen SM ON P.Salesman_ID = SM.ID
JOIN Orders O ON P.Order_ID = O.Order_ID;
