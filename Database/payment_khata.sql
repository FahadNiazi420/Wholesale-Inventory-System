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
