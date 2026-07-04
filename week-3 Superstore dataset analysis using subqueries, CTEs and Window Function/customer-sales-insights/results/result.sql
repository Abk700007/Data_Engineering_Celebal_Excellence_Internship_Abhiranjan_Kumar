-- ==========================================
-- Week 3 Assignment - SQL Query Results
-- Description: Executed queries and their outputs from Sample - Superstore.csv.
-- ==========================================

-- Database Ingestion Stats:
-- - superstore_raw records loaded: 9994
-- - customers records: 793
-- - products records: 1862
-- - orders records: 9986

-- ------------------------------------------

-- ------------------------------------------
-- Section 1: Subqueries: Q1. Find all orders where sales are greater than the average sales
-- ------------------------------------------
SELECT o.order_id, c.customer_name, p.product_name, o.sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
WHERE o.sales > (SELECT AVG(sales) FROM orders)
ORDER BY o.sales DESC;

-- QUERY RESULTS (showing top 5 of 2356 total rows):
-- +----------------+---------------+-------------------------------------------------------+----------+
-- | order_id       | customer_name | product_name                                          | sales    |
-- +----------------+---------------+-------------------------------------------------------+----------+
-- | CA-2014-145317 | Sean Miller   | Cisco TelePresence System EX90 Videoconferencing Unit | 22638.48 |
-- | CA-2016-118689 | Tamara Chand  | Canon imageCLASS 2200 Advanced Copier                 | 17499.95 |
-- | CA-2017-140151 | Raymond Buch  | Canon imageCLASS 2200 Advanced Copier                 | 13999.96 |
-- | CA-2017-127180 | Tom Ashbrook  | Canon imageCLASS 2200 Advanced Copier                 | 11199.97 |
-- | CA-2017-166709 | Hunter Lopez  | Canon imageCLASS 2200 Advanced Copier                 | 10499.97 |
-- +----------------+---------------+-------------------------------------------------------+----------+

-- ------------------------------------------
-- Section 1: Subqueries: Q2. Find the highest sales order for each customer
-- ------------------------------------------
SELECT o.customer_id, c.customer_name, o.order_id, o.sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.sales = (
    SELECT MAX(o_sub.sales)
    FROM orders o_sub
    WHERE o_sub.customer_id = o.customer_id
)
ORDER BY o.sales DESC;

-- QUERY RESULTS (showing top 5 of 795 total rows):
-- +-------------+---------------+----------------+----------+
-- | customer_id | customer_name | order_id       | sales    |
-- +-------------+---------------+----------------+----------+
-- | SM-20320    | Sean Miller   | CA-2014-145317 | 22638.48 |
-- | TC-20980    | Tamara Chand  | CA-2016-118689 | 17499.95 |
-- | RB-19360    | Raymond Buch  | CA-2017-140151 | 13999.96 |
-- | TA-21385    | Tom Ashbrook  | CA-2017-127180 | 11199.97 |
-- | HL-15040    | Hunter Lopez  | CA-2017-166709 | 10499.97 |
-- +-------------+---------------+----------------+----------+

-- ------------------------------------------
-- Section 2: CTEs: Q3. Calculate total sales for each customer
-- ------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT cs.customer_id, c.customer_name, cs.total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales DESC;

-- QUERY RESULTS (showing top 5 of 793 total rows):
-- +-------------+---------------+-------------+
-- | customer_id | customer_name | total_sales |
-- +-------------+---------------+-------------+
-- | SM-20320    | Sean Miller   |    25043.05 |
-- | TC-20980    | Tamara Chand  |    19052.22 |
-- | RB-19360    | Raymond Buch  |    15117.34 |
-- | TA-21385    | Tom Ashbrook  |    14595.62 |
-- | AB-10105    | Adrian Barton |    14473.57 |
-- +-------------+---------------+-------------+

-- ------------------------------------------
-- Section 2: CTEs: Q4. Find customers whose total sales are above average
-- ------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT cs.customer_id, c.customer_name, cs.total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_sales > (
    SELECT AVG(total_sales)
    FROM (
        SELECT SUM(sales) AS total_sales
        FROM orders
        GROUP BY customer_id
    ) t
)
ORDER BY cs.total_sales DESC;

-- QUERY RESULTS (showing top 5 of 294 total rows):
-- +-------------+---------------+-------------+
-- | customer_id | customer_name | total_sales |
-- +-------------+---------------+-------------+
-- | SM-20320    | Sean Miller   |    25043.05 |
-- | TC-20980    | Tamara Chand  |    19052.22 |
-- | RB-19360    | Raymond Buch  |    15117.34 |
-- | TA-21385    | Tom Ashbrook  |    14595.62 |
-- | AB-10105    | Adrian Barton |    14473.57 |
-- +-------------+---------------+-------------+

-- ------------------------------------------
-- Section 3: Window Functions: Q5. Rank all customers based on total sales
-- ------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT cs.customer_id, c.customer_name, cs.total_sales,
       RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id;

-- QUERY RESULTS (showing top 5 of 793 total rows):
-- +-------------+---------------+-------------+------------+
-- | customer_id | customer_name | total_sales | sales_rank |
-- +-------------+---------------+-------------+------------+
-- | SM-20320    | Sean Miller   |    25043.05 |          1 |
-- | TC-20980    | Tamara Chand  |    19052.22 |          2 |
-- | RB-19360    | Raymond Buch  |    15117.34 |          3 |
-- | TA-21385    | Tom Ashbrook  |    14595.62 |          4 |
-- | AB-10105    | Adrian Barton |    14473.57 |          5 |
-- +-------------+---------------+-------------+------------+

-- ------------------------------------------
-- Section 3: Window Functions: Q6. Assign row numbers to each order within a customer
-- ------------------------------------------
WITH distinct_orders AS (
    SELECT DISTINCT customer_id, order_id, order_date
    FROM orders
)
SELECT d.customer_id, c.customer_name, d.order_id, d.order_date,
       ROW_NUMBER() OVER (PARTITION BY d.customer_id ORDER BY d.order_date, d.order_id) AS order_seq
FROM distinct_orders d
JOIN customers c ON d.customer_id = c.customer_id;

-- QUERY RESULTS (showing top 10 of 5009 total rows):
-- +-------------+---------------+----------------+------------+-----------+
-- | customer_id | customer_name | order_id       | order_date | order_seq |
-- +-------------+---------------+----------------+------------+-----------+
-- | AA-10315    | Alex Avila    | CA-2014-128055 | 2014-03-31 |         1 |
-- | AA-10315    | Alex Avila    | CA-2014-138100 | 2014-09-15 |         2 |
-- | AA-10315    | Alex Avila    | CA-2015-121391 | 2015-10-04 |         3 |
-- | AA-10315    | Alex Avila    | CA-2016-103982 | 2016-03-03 |         4 |
-- | AA-10315    | Alex Avila    | CA-2017-147039 | 2017-06-29 |         5 |
-- | AA-10375    | Allen Armold  | CA-2014-158064 | 2014-04-21 |         1 |
-- | AA-10375    | Allen Armold  | CA-2014-130729 | 2014-10-24 |         2 |
-- | AA-10375    | Allen Armold  | CA-2015-140921 | 2015-02-03 |         3 |
-- | AA-10375    | Allen Armold  | CA-2015-109939 | 2015-05-08 |         4 |
-- | AA-10375    | Allen Armold  | CA-2015-114503 | 2015-11-13 |         5 |
-- +-------------+---------------+----------------+------------+-----------+

-- ------------------------------------------
-- Section 3: Window Functions: Q7. Display top 3 customers based on total sales
-- ------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
),
ranked_customers AS (
    SELECT cs.customer_id, c.customer_name, cs.total_sales,
           DENSE_RANK() OVER (ORDER BY cs.total_sales DESC) AS rnk
    FROM customer_sales cs
    JOIN customers c ON cs.customer_id = c.customer_id
)
SELECT customer_id, customer_name, total_sales, rnk
FROM ranked_customers
WHERE rnk <= 3;

-- QUERY RESULTS (showing top 3 of 3 total rows):
-- +-------------+---------------+-------------+-----+
-- | customer_id | customer_name | total_sales | rnk |
-- +-------------+---------------+-------------+-----+
-- | SM-20320    | Sean Miller   |    25043.05 |   1 |
-- | TC-20980    | Tamara Chand  |    19052.22 |   2 |
-- | RB-19360    | Raymond Buch  |    15117.34 |   3 |
-- +-------------+---------------+-------------+-----+

-- ------------------------------------------
-- Section 4: Final Combined Query: Q8. Customer Name, Total Sales, and Rank using JOIN + CTE + Window Function together
-- ------------------------------------------
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT c.customer_name, cs.total_sales,
       DENSE_RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY sales_rank ASC;

-- QUERY RESULTS (showing top 10 of 793 total rows):
-- +--------------------+-------------+------------+
-- | customer_name      | total_sales | sales_rank |
-- +--------------------+-------------+------------+
-- | Sean Miller        |    25043.05 |          1 |
-- | Tamara Chand       |    19052.22 |          2 |
-- | Raymond Buch       |    15117.34 |          3 |
-- | Tom Ashbrook       |    14595.62 |          4 |
-- | Adrian Barton      |    14473.57 |          5 |
-- | Ken Lonsdale       |    14175.23 |          6 |
-- | Sanjit Chand       |    14142.33 |          7 |
-- | Hunter Lopez       |    12873.30 |          8 |
-- | Sanjit Engle       |    12209.44 |          9 |
-- | Christopher Conant |    12129.07 |         10 |
-- +--------------------+-------------+------------+

