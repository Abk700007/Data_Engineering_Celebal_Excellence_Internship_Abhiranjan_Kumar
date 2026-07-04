-- ==========================================
-- Customer Sales Insights Mini Project
-- Description: Resolved queries and outputs for the mini project.
-- ==========================================

-- ------------------------------------------
-- Mini Project: Q1. Who are the top 5 customers?
-- ------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, cs.total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales DESC
LIMIT 5;

-- QUERY RESULTS (showing top 5 of 5 total rows):
-- +---------------+-------------+
-- | customer_name | total_sales |
-- +---------------+-------------+
-- | Sean Miller   |    25043.05 |
-- | Tamara Chand  |    19052.22 |
-- | Raymond Buch  |    15117.34 |
-- | Tom Ashbrook  |    14595.62 |
-- | Adrian Barton |    14473.57 |
-- +---------------+-------------+

-- ------------------------------------------
-- Mini Project: Q2. Who are the bottom 5 customers?
-- ------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, cs.total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales ASC
LIMIT 5;

-- QUERY RESULTS (showing top 5 of 5 total rows):
-- +-----------------+-------------+
-- | customer_name   | total_sales |
-- +-----------------+-------------+
-- | Thais Sissman   |        4.83 |
-- | Lela Donovan    |        5.30 |
-- | Carl Jackson    |       16.52 |
-- | Mitch Gastineau |       16.74 |
-- | Roy Skaria      |       22.33 |
-- +-----------------+-------------+

-- ------------------------------------------
-- Mini Project: Q3. Which customers made only one order?
-- ------------------------------------------
WITH customer_order_counts AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS num_orders
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, coc.num_orders
FROM customer_order_counts coc
JOIN customers c ON coc.customer_id = c.customer_id
WHERE coc.num_orders = 1
ORDER BY c.customer_name;

-- QUERY RESULTS (showing top 5 of 12 total rows):
-- +-------------------+------------+
-- | customer_name     | num_orders |
-- +-------------------+------------+
-- | Anemone Ratner    |          1 |
-- | Anthony O'Donnell |          1 |
-- | Carl Jackson      |          1 |
-- | Jenna Caffey      |          1 |
-- | Jocasta Rupert    |          1 |
-- +-------------------+------------+

-- ------------------------------------------
-- Mini Project: Q4. Which customers have above-average sales?
-- ------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
),
average_sales AS (
    SELECT AVG(total_sales) AS avg_sales
    FROM customer_sales
)
SELECT c.customer_name, cs.total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
CROSS JOIN average_sales
WHERE cs.total_sales > average_sales.avg_sales
ORDER BY cs.total_sales DESC;

-- QUERY RESULTS (showing top 5 of 294 total rows):
-- +---------------+-------------+
-- | customer_name | total_sales |
-- +---------------+-------------+
-- | Sean Miller   |    25043.05 |
-- | Tamara Chand  |    19052.22 |
-- | Raymond Buch  |    15117.34 |
-- | Tom Ashbrook  |    14595.62 |
-- | Adrian Barton |    14473.57 |
-- +---------------+-------------+

-- ------------------------------------------
-- Mini Project: Q5. What is the highest order value per customer?
-- ------------------------------------------
WITH order_sales AS (
    SELECT customer_id, order_id, SUM(sales) AS order_total
    FROM orders
    GROUP BY customer_id, order_id
)
SELECT c.customer_name, MAX(os.order_total) AS max_order_value
FROM order_sales os
JOIN customers c ON os.customer_id = c.customer_id
GROUP BY os.customer_id, c.customer_name
ORDER BY max_order_value DESC;

-- QUERY RESULTS (showing top 5 of 793 total rows):
-- +---------------+-----------------+
-- | customer_name | max_order_value |
-- +---------------+-----------------+
-- | Sean Miller   |        23661.23 |
-- | Tamara Chand  |        18336.74 |
-- | Raymond Buch  |        14052.48 |
-- | Tom Ashbrook  |        13716.46 |
-- | Becky Martin  |        10539.90 |
-- +---------------+-----------------+

