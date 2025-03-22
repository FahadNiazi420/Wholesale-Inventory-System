
CREATE TRIGGER create_khata_on_shopkeeper_insert
AFTER INSERT ON Shopkeepers
FOR EACH ROW
BEGIN
    INSERT INTO Khata (Shopkeeper_ID, Brand, Total_Due, Last_Payment_Date, IsDeleted)
    VALUES (NEW.ID, NEW.Brand, 0, DATE('now'), 0);
END;

CREATE TRIGGER update_khata_on_payment_insert
AFTER INSERT ON Payments
FOR EACH ROW
BEGIN
    -- Update the total due by subtracting the payment amount
    UPDATE Khata
    SET Total_Due = Total_Due - NEW.Amount_Paid,
        Last_Payment_Date = NEW.Payment_Date
    WHERE Shopkeeper_ID = NEW.Shopkeeper_ID
    AND Brand = (SELECT Brand FROM Shopkeepers WHERE ID = NEW.Shopkeeper_ID);
END;
CREATE TRIGGER update_khata_on_payment_update
AFTER UPDATE ON Payments
FOR EACH ROW
BEGIN
    -- Add back old payment amount before subtracting new payment amount
    UPDATE Khata
    SET Total_Due = Total_Due + OLD.Amount_Paid - NEW.Amount_Paid,
        Last_Payment_Date = NEW.Payment_Date
    WHERE Shopkeeper_ID = NEW.Shopkeeper_ID
    AND Brand = (SELECT Brand FROM Shopkeepers WHERE ID = NEW.Shopkeeper_ID);
END;
CREATE TRIGGER update_khata_on_payment_delete
AFTER UPDATE OF IsDeleted ON Payments
FOR EACH ROW
WHEN NEW.IsDeleted = 1 AND OLD.IsDeleted = 0  -- Only trigger when marking as deleted
BEGIN
    UPDATE Khata
    SET Total_Due = Total_Due + OLD.Amount_Paid
    WHERE Shopkeeper_ID = OLD.Shopkeeper_ID
    AND Brand = (SELECT Brand FROM Shopkeepers WHERE ID = OLD.Shopkeeper_ID);
END;



CREATE TRIGGER update_khata_on_order_insert
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    -- Insert or update `Khata` with discounted amount
    INSERT INTO Khata (Shopkeeper_ID, Brand, Total_Due, Last_Payment_Date, IsDeleted)
    VALUES (
        NEW.Shopkeeper_ID,
        (SELECT Brand FROM Shopkeepers WHERE ID = NEW.Shopkeeper_ID),
        NEW.Total_Amount - COALESCE((SELECT SUM(Discount_Amount) 
                                     FROM Discounts 
                                     WHERE Order_ID = NEW.Order_ID 
                                     AND IsDeleted = 0), 0),
        NULL,
        0
    )
    ON CONFLICT(Shopkeeper_ID, Brand) 
    DO UPDATE SET 
        Total_Due = Khata.Total_Due + 
                    (NEW.Total_Amount - COALESCE((SELECT SUM(Discount_Amount) 
                                                 FROM Discounts 
                                                 WHERE Order_ID = NEW.Order_ID 
                                                 AND IsDeleted = 0), 0));
END;

CREATE TRIGGER update_khata_on_order_update
AFTER UPDATE ON Orders
FOR EACH ROW
BEGIN
    UPDATE Khata
    SET Total_Due = Total_Due 
        - (OLD.Total_Amount - COALESCE((SELECT SUM(Discount_Amount) 
                                        FROM Discounts 
                                        WHERE Order_ID = OLD.Order_ID 
                                        AND IsDeleted = 0), 0))
        + (NEW.Total_Amount - COALESCE((SELECT SUM(Discount_Amount) 
                                        FROM Discounts 
                                        WHERE Order_ID = NEW.Order_ID 
                                        AND IsDeleted = 0), 0))
    WHERE Shopkeeper_ID = NEW.Shopkeeper_ID
    AND Brand = (SELECT Brand FROM Shopkeepers WHERE ID = NEW.Shopkeeper_ID);
END;
CREATE TRIGGER update_khata_on_order_delete
AFTER UPDATE OF IsDeleted ON Orders
FOR EACH ROW
WHEN NEW.IsDeleted = 1 AND OLD.IsDeleted = 0
BEGIN
    UPDATE Khata
    SET Total_Due = Total_Due - 
        (OLD.Total_Amount - COALESCE((SELECT SUM(Discount_Amount) 
                                      FROM Discounts 
                                      WHERE Order_ID = OLD.Order_ID 
                                      AND IsDeleted = 0), 0))
    WHERE Shopkeeper_ID = OLD.Shopkeeper_ID
    AND Brand = (SELECT Brand FROM Shopkeepers WHERE ID = OLD.Shopkeeper_ID);
END;
