--🛎️ Service Area Table
CREATE TABLE IF NOT EXISTS Service_Area (
    service_area_id INTEGER PRIMARY KEY, 
    description TEXT,
    status INTEGER DEFAULT 0,
    timestamp DATETIME 
);

-- 🗂️ Category Table
CREATE TABLE IF NOT EXISTS Category (
    category_id INTEGER PRIMARY KEY,
    description TEXT NOT NULL
);

-- 📦 Product Modifier Table
CREATE TABLE IF NOT EXISTS Product_Modifier (
    product_id INTEGER,
    modifier TEXT NOT NULL, 
    FOREIGN KEY (product_id) REFERENCES  
Product(product_id)
);

-- 🥪 Product Item Table
CREATE TABLE IF NOT EXISTS Product (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    category_id INTEGER,
    price INTEGER NOT NULL,
    tax INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

-- 👤 Customer Table
CREATE TABLE IF NOT EXISTS Customer (
    customer_id INTEGER PRIMARY KEY, -- phone number as unique int
    description TEXT, -- name, initial or anything a customer wishes to be 
    point INTEGER DEFAULT 0
);

-- 📜 Customer History Table
CREATE TABLE IF NOT EXISTS  Customer_History (
    customer_id INTEGER,
    point INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
); 

CREATE TRIGGER IF NOT EXISTS log_customer_insert
AFTER INSERT ON Customer
FOR EACH ROW
BEGIN
    INSERT INTO Customer_History (customer_id, point, timestamp)
    VALUES (NEW.customer_id, NEW.point, CURRENT_TIMESTAMP);
END;


CREATE TRIGGER IF NOT EXISTS log_customer_update
AFTER UPDATE ON Customer
FOR EACH ROW
BEGIN
    INSERT INTO Customer_History (customer_id, point, timestamp)
    VALUES (NEW.customer_id, NEW.point, CURRENT_TIMESTAMP);
END;

-- 🧾 Order_Cart Table
CREATE TABLE IF NOT EXISTS Order_Cart (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_status INTEGER NOT NULL DEFAULT 0,
    service_area_id INTEGER NOT NULL,
    customer_id INTEGER,
    subtotal INTEGER NOT NULL DEFAULT 0,
    charged INTEGER NOT NULL DEFAULT 0,
    special_request TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_area_id) REFERENCES Service_Area(service_area_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- 📜 Order History Table
CREATE TABLE IF NOT EXISTS  Order_History (
    order_id INTEGER,
    order_status INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
); 


CREATE TRIGGER IF NOT EXISTS log_order_insert
AFTER INSERT ON Order_Cart
FOR EACH ROW
BEGIN
    INSERT INTO Order_History (order_id, order_status, timestamp)
    VALUES (NEW.order_id, NEW.order_status, CURRENT_TIMESTAMP);
END;


CREATE TRIGGER IF NOT EXISTS log_order_update
AFTER UPDATE ON Order_Cart
FOR EACH ROW
BEGIN
    INSERT INTO Order_History (order_id, order_status, timestamp)
    VALUES (NEW.order_id, NEW.order_status, CURRENT_TIMESTAMP);
END;


CREATE INDEX IF NOT EXISTS idx_order_history_timestamp
ON Order_History(timestamp);


-- 🧃 Order Product Table
CREATE TABLE IF NOT EXISTS Order_Product (
    order_id INTEGER,
    product_id INTEGER,
    service_area_id INTEGER,
    Modifier TEXT,
    product_quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES Order_Cart(order_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

-- 👤 Role Table
CREATE TABLE IF NOT EXISTS Role(
    role_id INTEGER PRIMARY KEY, 
    description TEXT	
);

-- 👤 User Table
CREATE TABLE IF NOT EXISTS User(
    user_id INTEGER PRIMARY KEY, 
    description TEXT,
    status INTEGER	
);

-- 👤 User Role Table
CREATE TABLE IF NOT EXISTS User_Role (
    user_id INTEGER,
    role_id INTEGER,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (role_id) REFERENCES Role(role_id)
);

-- 📜 User History Table
CREATE TABLE IF NOT EXISTS  User_History (
    user_id INTEGER,
    role_id INTEGER,
    status INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
); 


CREATE TRIGGER IF NOT EXISTS log_user_insert
AFTER INSERT ON User
FOR EACH ROW
BEGIN
    INSERT INTO User_History (user_id, role_id, status, timestamp)
    VALUES (NEW.user_id, NEW.role_id, NEW.status, CURRENT_TIMESTAMP);
END;


CREATE TRIGGER IF NOT EXISTS log_order_update
AFTER UPDATE ON Order_Cart
FOR EACH ROW
BEGIN
    INSERT INTO Order_History (order_id, order_status, timestamp)
    VALUES (NEW.order_id, NEW.order_status, CURRENT_TIMESTAMP);
END;


INSERT INTO Service_Area (service_area_id, description) VALUES
(1, 'buffet tables for eight'),
(2, 'square table for two'),
(3, 'rectangular table for four'),
(4, 'round table for six'),
(5, 'VIP booth'),
(6, 'outdoor patio table'),
(7, 'bar counter seat'),
(8, 'window-side table for two');


-- 👤 Role 
INSERT INTO role (role_id, description) VALUES (1, 'Cashier');
INSERT INTO role (role_id, description) VALUES (2, 'Server');
INSERT INTO role (role_id, description) VALUES (3, 'Cook');
INSERT INTO role (role_id, description) VALUES (4, 'Delivery Driver');
INSERT INTO role (role_id, description) VALUES (5, 'Manager');
INSERT INTO role (role_id, description) VALUES (6, 'Administrator');
INSERT INTO role (role_id, description) VALUES (7, 'Self Service');


-- 🗂️ Category  
INSERT INTO Category (category_id, description)
VALUES
(1, 'Burgers and Sandwiches'),  -- 🍔
(2, 'Fried Chicken'),           -- 🍗
(3, 'Salads and Wraps'),        -- 🥗
(4, 'Sides');                   -- 🍟

-- 🍔 Burgers and Sandwiches (Category ID: 1)
INSERT INTO Product (product_id, description, category_id, price, tax) VALUES
(1, 'Classic Cheeseburger', 1, 599, 0.60),
(2,  'Grilled Chicken Club', 1, 799, 0.80),
(3, 'Veggie Burger', 1, 699, 0.70);

-- 🍗 Fried Chicken (Category ID: 2)
INSERT INTO Product (product_id, description, category_id, price, tax) VALUES
(5, 'Crispy Chicken Tenders (6 pcs)', 2, 699, 0.70),
(6, 'Chicken Bucket (8 pcs)', 2, 1299, 1.30),
(7, 'Spicy Fried Chicken Sandwich', 2, 679, 0.68);

-- 🥗 Salads and Wraps (Category ID: 3)
INSERT INTO Product (product_id, description, category_id, price, tax) VALUES
(8, 'Grilled Chicken Caesar Salad', 3, 749, 0.75),
(9, 'Southwest Chicken Wrap', 3, 699, 0.70),
(10, 'Garden Salad', 3, 599, 0.60);

-- 🍟 Sides (Category ID: 4)
INSERT INTO Product (product_id, description, category_id, price, tax) VALUES
(11, 'French Fries (Small)', 4, 249, 0.25),
(12, 'French Fries (Large)', 4, 349, 0.35);


INSERT INTO Product_Modifier (product_id, modifier) VALUES
(1,'Sweet'),
(1,'Spicy'),
(2,'Sweet'),
(2,'Spicy'),
(3,'Sweet'),
(3,'Spicy'),
(4,'No onion'),
(4,'No lettuce'),
(4,'No cheese'),
(4,'No tomato'); 



