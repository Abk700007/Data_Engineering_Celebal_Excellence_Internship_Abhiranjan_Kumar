-- Section A: SQL Basics

-- Q1: Display all columns and rows from customers table
SELECT * FROM customers;

-- Q2: Retrieve first_name, last_name, and city of all customers
SELECT first_name, last_name, city FROM customers;

-- Q3: List all unique categories available in the products table
SELECT DISTINCT category FROM products;

-- Q4: Primary Key of each table and explanation
-- customers: customer_id
-- products: product_id
-- orders: order_id
-- order_items: item_id
-- Explanation: A Primary Key must be unique to uniquely identify each row in a table.
-- It cannot be NULL because a missing value cannot serve as a valid identifier.

-- Q5: Constraints on email column in customers
-- Constraints: UNIQUE and NOT NULL.
-- If we insert a duplicate email, it will violate the UNIQUE constraint, causing the RDBMS to reject the insert.

-- Q6: Try inserting a product with unit_price = -50
-- INSERT INTO products (product_id, product_name, category, brand, unit_price, stock_qty)
-- VALUES (209, 'Test Product', 'Electronics', 'Brand', -50.00, 100);

-- Explanation: This insert fails because of the constraint `CHECK (unit_price > 0)`.
-- It triggers a check constraint violation error.
