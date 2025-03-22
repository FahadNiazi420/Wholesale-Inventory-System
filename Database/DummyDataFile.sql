INSERT INTO Salesmen (Name, Contact_Info, Total_Sales, Total_Collections, IsDeleted) 
VALUES 
('Ali Khan', '03211234567', 0, 0, 0),
('Usman Raza', '03009876543', 0, 0, 0),
('Ahmed Sheikh', '03125552222', 0, 0, 0);

INSERT INTO Products (Brand, Product_Name, Size, Price, Stock_Quantity, IsDeleted) 
VALUES 
('Bonapapa', 'Pampers S', 'S', 500, 100, 0),
('Bonapapa', 'Pampers M', 'M', 600, 120, 0),
('Bonapapa', 'Pampers L', 'L', 700, 150, 0),
('Bonapapa', 'Pampers XL', 'XL', 800, 80, 0),
('Bonapapa', 'Pampers XXL', 'XXL', 900, 60, 0),
('Candyland', 'Chocolato', 'Nil', 50, 200, 0),
('Candyland', 'Bisconni', 'Nil', 40, 250, 0),
('Candyland', 'Wafers', 'Nil', 30, 300, 0);

INSERT INTO Shopkeepers (Name, Contact_Info, Brand, IsDeleted) 
VALUES 
('Hamza Traders', '03234567890', 'Bonapapa', 0),
('Hassan General Store', '03001234567', 'Bonapapa', 0),
('Rashid Mart', '03124567890', 'Candyland', 0),
('Al Madina Store', '03451234567', 'Candyland', 0);
