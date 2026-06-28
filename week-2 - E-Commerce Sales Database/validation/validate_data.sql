-- VALIDATE DATA sql script

-- Count records in each table to ensure complete data loading
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'products' AS table_name, COUNT(*) AS row_count FROM products
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM orders
UNION ALL
SELECT 'order_items' AS table_name, COUNT(*) AS row_count FROM order_items;

-- Check a sample from each table to verify structure and contents
SELECT 'customer_sample' AS sample_type, customer_id, first_name, last_name, email FROM customers LIMIT 2;
SELECT 'product_sample' AS sample_type, product_id, product_name, category, unit_price FROM products LIMIT 2;
SELECT 'order_sample' AS sample_type, order_id, customer_id, order_date, status, total_amount FROM orders LIMIT 2;
SELECT 'order_item_sample' AS sample_type, item_id, order_id, product_id, quantity, unit_price FROM order_items LIMIT 2;
