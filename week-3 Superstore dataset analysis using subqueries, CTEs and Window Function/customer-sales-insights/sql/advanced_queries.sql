-- Advanced Queries (Subqueries, CTEs, Window Functions)

-- ==========================================
-- Subqueries
-- ==========================================

-- Q1. Find all orders where sales are greater than the average sales
SELECT o.order_id, c.customer_name, p.product_name, o.sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
WHERE o.sales > (SELECT AVG(sales) FROM orders)
ORDER BY o.sales DESC;

-- Q2. Find the highest sales order for each customer
SELECT o.customer_id, c.customer_name, o.order_id, o.sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.sales = (
    SELECT MAX(o_sub.sales)
    FROM orders o_sub
    WHERE o_sub.customer_id = o.customer_id
)
ORDER BY o.sales DESC;

-- ==========================================
-- CTEs
-- ==========================================

-- Q3. Calculate total sales for each customer
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT cs.customer_id, c.customer_name, cs.total_sales
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales DESC;

-- Q4. Find customers whose total sales are above average
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

-- ==========================================
-- Window Functions
-- ==========================================

-- Q5. Rank all customers based on total sales
WITH customer_sales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT cs.customer_id, c.customer_name, cs.total_sales,
       RANK() OVER (ORDER BY cs.total_sales DESC) AS sales_rank
FROM customer_sales cs
JOIN customers c ON cs.customer_id = c.customer_id;

-- Q6. Assign row numbers to each order within a customer
WITH distinct_orders AS (
    SELECT DISTINCT customer_id, order_id, order_date
    FROM orders
)
SELECT d.customer_id, c.customer_name, d.order_id, d.order_date,
       ROW_NUMBER() OVER (PARTITION BY d.customer_id ORDER BY d.order_date, d.order_id) AS order_seq
FROM distinct_orders d
JOIN customers c ON d.customer_id = c.customer_id;

-- Q7. Display top 3 customers based on total sales
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

-- ==========================================
-- Final Combined Query
-- ==========================================

-- Q8. Customer Name, Total Sales, and Rank using JOIN + CTE + Window Function together
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


