-- Ingest and normalize raw Superstore data

-- 1. Import Superstore Dataset into superstore_raw
-- For SQLite:
-- .mode csv
-- .import 'data/Sample - Superstore.csv' superstore_raw

-- For MySQL:
-- LOAD DATA INFILE '../data/Sample - Superstore.csv' INTO TABLE superstore_raw FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;

-- For PostgreSQL:
-- \copy superstore_raw FROM '../data/Sample - Superstore.csv' WITH (FORMAT csv, HEADER true);

-- 2. Populate customers table
INSERT INTO customers (customer_id, customer_name, segment)
SELECT DISTINCT customer_id, customer_name, segment
FROM superstore_raw;

-- 3. Populate products table (deduplicated)
INSERT INTO products (product_id, category, sub_category, product_name)
SELECT product_id, category, sub_category, product_name
FROM (
    SELECT DISTINCT product_id, category, sub_category, product_name,
           ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY row_id DESC) as rn
    FROM superstore_raw
) t
WHERE rn = 1;

-- 4. Populate orders table
INSERT INTO orders (
    order_id, customer_id, product_id, order_date, ship_date, ship_mode, sales, quantity, discount, profit
)
SELECT DISTINCT 
    order_id, customer_id, product_id, order_date, ship_date, ship_mode, sales, quantity, discount, profit
FROM superstore_raw;

-- 5. Validation queries
SELECT 'superstore_raw' AS table_name, COUNT(*) AS row_count FROM superstore_raw
UNION ALL
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products' AS table_name, COUNT(*) AS row_count FROM products
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM orders;

SELECT COUNT(*) AS orphan_orders 
FROM orders 
WHERE customer_id IS NULL OR product_id IS NULL;
