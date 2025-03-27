WITH PaymentsOrdered AS (
    SELECT 
        P.Payment_ID,
        P.Shopkeeper_ID,
        S.Name AS Shopkeeper_Name,
        K.Brand,
        P.Order_ID,
        O.Total_Amount,
        O.Order_Info,  -- Added Order_Info
        COALESCE(D.Discount_Amount, 0) AS Discount_Percentage,
        (O.Total_Amount * (1 - COALESCE(D.Discount_Amount, 0) / 100)) AS Initial_Discounted_Total,
        P.Amount_Paid,
        P.Payment_Date
    FROM Payments P
    JOIN Shopkeepers S ON P.Shopkeeper_ID = S.ID
    JOIN Orders O ON P.Order_ID = O.Order_ID
    LEFT JOIN Discounts D ON P.Order_ID = D.Order_ID AND D.IsDeleted = 0
    LEFT JOIN Khata K ON P.Shopkeeper_ID = K.Shopkeeper_ID
    WHERE P.IsDeleted = 0
    ORDER BY P.Shopkeeper_ID, P.Order_ID, P.Payment_Date
),
CumulativePayments AS (
    SELECT 
        Payment_ID,
        Shopkeeper_ID,
        Shopkeeper_Name,
        Brand,
        Order_ID,
        Order_Info,  -- Included Order_Info
        Total_Amount,
        Discount_Percentage,
        Initial_Discounted_Total AS Discounted_Total,
        Amount_Paid,
        Amount_Paid AS Cumulative_Paid,
        (Initial_Discounted_Total - Amount_Paid) AS Remaining_Due,
        Payment_Date
    FROM PaymentsOrdered
    WHERE Payment_ID = (SELECT MIN(Payment_ID) FROM PaymentsOrdered PO WHERE PO.Shopkeeper_ID = PaymentsOrdered.Shopkeeper_ID AND PO.Order_ID = PaymentsOrdered.Order_ID)

    UNION ALL

    SELECT 
        P.Payment_ID,
        P.Shopkeeper_ID,
        P.Shopkeeper_Name,
        P.Brand,
        P.Order_ID,
        P.Order_Info,  -- Included Order_Info
        P.Total_Amount,
        P.Discount_Percentage,
        CP.Remaining_Due AS Discounted_Total,
        P.Amount_Paid,
        CP.Cumulative_Paid + P.Amount_Paid AS Cumulative_Paid,
        (CP.Remaining_Due - P.Amount_Paid) AS Remaining_Due,
        P.Payment_Date
    FROM PaymentsOrdered P
    JOIN CumulativePayments CP 
    ON P.Shopkeeper_ID = CP.Shopkeeper_ID AND P.Order_ID = CP.Order_ID
    WHERE P.Payment_ID > CP.Payment_ID
)
SELECT * FROM CumulativePayments ORDER BY Payment_Date;
