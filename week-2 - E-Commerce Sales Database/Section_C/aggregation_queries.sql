-- Section C: Aggregation Queries

-- Q13: Count total orders
SELECT COUNT(*) AS total_orders FROM orders;

-- Q14: Find total revenue from 'Delivered' orders
SELECT SUM(total_amount) AS total_delivered_revenue 
FROM orders 
WHERE status = 'Delivered';

-- Q15: Calculate average unit_price of products in each category
SELECT category, AVG(unit_price) AS average_price 
FROM products 
GROUP BY category;

-- Q16: Count of orders and total revenue for each status, sorted by revenue descending
SELECT status, 
       COUNT(*) AS order_count, 
       SUM(total_amount) AS total_revenue
FROM orders 
GROUP BY status 
ORDER BY total_revenue DESC;

-- Q17: Find most expensive and cheapest product in each category
SELECT category, 
       MAX(unit_price) AS max_price, 
       MIN(unit_price) AS min_price
FROM products 
GROUP BY category;

-- Q18: Product categories where average unit_price > 2000
SELECT category, AVG(unit_price) AS average_price
FROM products 
GROUP BY category 
HAVING AVG(unit_price) > 2000;
