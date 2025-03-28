-- Update_Total_Sales_After_Order	Updates Total_Sales when a new order is added
-- Update_Total_Sales_After_Discount	Updates Total_Sales when a discount is applied/updated
-- Update_Total_Collections_After_Payment	Updates Total_Collections when a payment is made
-- Update_Total_Collections_After_Return	Adjusts Total_Collections when a return is recorded
-- Update_Total_Sales_After_Order_Delete	Adjusts Total_Sales if an order is marked as deleted
-- Update_Total_Collections_After_Payment_Delete	Adjusts Total_Collections if a payment is deleted

CREATE TRIGGER Update_Total_Sales_After_Order
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    UPDATE Salesmen
    SET Total_Sales = (
        SELECT COALESCE(SUM(O.Total_Amount * (1 - COALESCE(D.Discount_Amount, 0) / 100)), 0)
        FROM Orders O
        LEFT JOIN Discounts D ON O.Order_ID = D.Order_ID AND D.IsDeleted = 0
        WHERE O.Salesman_ID = NEW.Salesman_ID AND O.IsDeleted = 0
    )
    WHERE ID = NEW.Salesman_ID;
END;


CREATE TRIGGER Update_Total_Sales_After_Discount
AFTER INSERT OR UPDATE ON Discounts
FOR EACH ROW
BEGIN
    UPDATE Salesmen
    SET Total_Sales = (
        SELECT COALESCE(SUM(O.Total_Amount * (1 - COALESCE(D.Discount_Amount, 0) / 100)), 0)
        FROM Orders O
        LEFT JOIN Discounts D ON O.Order_ID = D.Order_ID AND D.IsDeleted = 0
        WHERE O.Salesman_ID = (SELECT Salesman_ID FROM Orders WHERE Order_ID = NEW.Order_ID) 
          AND O.IsDeleted = 0
    )
    WHERE ID = (SELECT Salesman_ID FROM Orders WHERE Order_ID = NEW.Order_ID);
END;


CREATE TRIGGER Update_Total_Collections_After_Payment
AFTER INSERT ON Payments
FOR EACH ROW
BEGIN
    UPDATE Salesmen
    SET Total_Collections = (
        SELECT COALESCE(SUM(P.Amount_Paid), 0)
        FROM Payments P
        WHERE P.Salesman_ID = NEW.Salesman_ID AND P.IsDeleted = 0
    )
    WHERE ID = NEW.Salesman_ID;
END;


CREATE TRIGGER Update_Total_Collections_After_Return
AFTER INSERT ON Returns
FOR EACH ROW
BEGIN
    UPDATE Salesmen
    SET Total_Collections = (
        (SELECT COALESCE(SUM(P.Amount_Paid), 0) 
         FROM Payments P 
         WHERE P.Salesman_ID = (SELECT Salesman_ID FROM Orders WHERE Order_ID = NEW.Order_ID) 
           AND P.IsDeleted = 0)
        - 
        (SELECT COALESCE(SUM(R.Return_Value), 0) 
         FROM Returns R 
         WHERE R.Order_ID = NEW.Order_ID AND R.IsDeleted = 0)
    )
    WHERE ID = (SELECT Salesman_ID FROM Orders WHERE Order_ID = NEW.Order_ID);
END;


CREATE TRIGGER Update_Total_Sales_After_Order_Delete
AFTER UPDATE ON Orders
FOR EACH ROW
WHEN OLD.IsDeleted = 0 AND NEW.IsDeleted = 1
BEGIN
    UPDATE Salesmen
    SET Total_Sales = (
        SELECT COALESCE(SUM(O.Total_Amount * (1 - COALESCE(D.Discount_Amount, 0) / 100)), 0)
        FROM Orders O
        LEFT JOIN Discounts D ON O.Order_ID = D.Order_ID AND D.IsDeleted = 0
        WHERE O.Salesman_ID = OLD.Salesman_ID AND O.IsDeleted = 0
    )
    WHERE ID = OLD.Salesman_ID;
END;


CREATE TRIGGER Update_Total_Collections_After_Payment_Delete
AFTER UPDATE ON Payments
FOR EACH ROW
WHEN OLD.IsDeleted = 0 AND NEW.IsDeleted = 1
BEGIN
    UPDATE Salesmen
    SET Total_Collections = (
        SELECT COALESCE(SUM(P.Amount_Paid), 0)
        FROM Payments P
        WHERE P.Salesman_ID = OLD.Salesman_ID AND P.IsDeleted = 0
    )
    WHERE ID = OLD.Salesman_ID;
END;
