-- Section E: Advanced Concepts

-- Q24: Classify products into price tiers (Budget, Mid-Range, Premium)
SELECT product_name, 
       unit_price,
       CASE 
           WHEN unit_price < 1000 THEN 'Budget'
           WHEN unit_price BETWEEN 1000 AND 3000 THEN 'Mid-Range'
           ELSE 'Premium'
       END AS price_tier
FROM products;

-- Q25: Count 'Delivered' vs 'Not Delivered' orders in a single row
SELECT 
    SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS Delivered,
    SUM(CASE WHEN status <> 'Delivered' THEN 1 ELSE 0 END) AS Not_Delivered
FROM orders;

/*
Q26: Explain ACID properties with a bank transfer example.

- Atomicity (All or Nothing): Either the entire transfer succeeds, or nothing changes. If the system crashes mid-transfer, any partial changes are rolled back.
- Consistency (State Validity): The database must follow all rules. Total money in the bank must stay balanced, and account balances cannot go below zero.
- Isolation (Independence): Concurrent transfers do not interfere. A query checking balances while a transfer is running sees either the pre-transfer or post-transfer state, not a half-done state.
- Durability (Permanence): Once a transfer is committed, the changes are saved to disk permanently and will survive power failures.
*/

-- Q27: SQL transaction to place an order, insert items, and update stock atomically
BEGIN TRANSACTION;

-- 1. Insert order
INSERT INTO orders (order_id, customer_id, order_date, status, total_amount)
VALUES (1011, 102, CURRENT_DATE, 'Pending', 1598.00);

-- 2. Insert order items
INSERT INTO order_items (item_id, order_id, product_id, quantity, unit_price, discount_pct)
VALUES (5016, 1011, 207, 1, 899.00, 0.00),
       (5017, 1011, 202, 1, 799.00, 12.52);

-- 3. Update product stock
UPDATE products
SET stock_qty = stock_qty - 1
WHERE product_id = 207;

UPDATE products
SET stock_qty = stock_qty - 1
WHERE product_id = 202;

COMMIT;
