SELECT s.ID, s.Name, k.Brand, s.Contact_Info, 
                       COALESCE(k.Total_Due, 0) AS Total_Due,
                       COALESCE(SUM(p.Amount_Paid), 0) AS Paid_Amount,
                       (COALESCE(k.Total_Due, 0) - COALESCE(SUM(p.Amount_Paid), 0)) AS Remaining,
                       MAX(p.Payment_Date) AS Last_Submission, s.IsDeleted
                FROM Shopkeepers s
                LEFT JOIN Khata k ON s.ID = k.Shopkeeper_ID
                LEFT JOIN Payments p ON s.ID = p.Shopkeeper_ID
                GROUP BY s.ID, s.Name, s.Contact_Info, k.Brand, k.Total_Due