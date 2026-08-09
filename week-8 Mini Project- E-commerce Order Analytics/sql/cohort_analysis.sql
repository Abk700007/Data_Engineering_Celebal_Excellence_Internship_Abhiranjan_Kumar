-- ============================================================
-- E-Commerce Order Analytics System
-- Advanced SQL - CTE, NTILE, YoY, First/Last,
-- Cumulative Distribution and Cohort Analysis
-- ============================================================


-- ============================================================
-- QUERY 10
-- CTE WITH MULTIPLE LEVELS
--
-- Step 1:
-- Calculate monthly revenue per customer.
--
-- Step 2:
-- Categorize customers:
-- High   > 10000
-- Medium 5000 - 10000
-- Low    < 5000
--
-- Step 3:
-- Count customers in each category per month.
-- ============================================================

WITH monthly_customer_revenue AS (

    SELECT

        o.customer_id,

        strftime(
            '%Y-%m',
            o.order_date
        ) AS order_month,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS monthly_revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.customer_id IS NOT NULL

    GROUP BY
        o.customer_id,
        order_month
),

customer_categories AS (

    SELECT

        customer_id,

        order_month,

        monthly_revenue,

        CASE

            WHEN monthly_revenue > 10000
                THEN 'High'

            WHEN monthly_revenue >= 5000
                THEN 'Medium'

            ELSE 'Low'

        END AS revenue_category

    FROM monthly_customer_revenue
)

SELECT

    order_month,

    revenue_category,

    COUNT(*) AS customer_count

FROM customer_categories

GROUP BY
    order_month,
    revenue_category

ORDER BY
    order_month,
    CASE revenue_category
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
    END;


-- ============================================================
-- QUERY 11
-- NTILE FOR CUSTOMER LIFETIME VALUE SEGMENTATION
--
-- Divide customers into 4 quartiles based on total lifetime
-- value.
--
-- 1 = Platinum
-- 2 = Gold
-- 3 = Silver
-- 4 = Bronze
-- ============================================================

WITH customer_lifetime_value AS (

    SELECT

        o.customer_id,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS total_value

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.customer_id IS NOT NULL

    GROUP BY
        o.customer_id
),

quartiles AS (

    SELECT

        customer_id,

        total_value,

        NTILE(4) OVER (
            ORDER BY total_value DESC
        ) AS quartile

    FROM customer_lifetime_value
)

SELECT

    customer_id,

    total_value,

    quartile,

    CASE quartile

        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        WHEN 4 THEN 'Bronze'

    END AS quartile_label

FROM quartiles

ORDER BY
    quartile,
    total_value DESC;


-- ============================================================
-- QUERY 12
-- YEAR-OVER-YEAR REVENUE COMPARISON
--
-- Compare each month's revenue with the same month
-- in the previous year.
-- ============================================================

WITH monthly_revenue AS (

    SELECT

        CAST(
            strftime('%Y', o.order_date)
            AS INTEGER
        ) AS year,

        CAST(
            strftime('%m', o.order_date)
            AS INTEGER
        ) AS month,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    GROUP BY
        year,
        month
)

SELECT

    curr.year,

    curr.month,

    ROUND(curr.revenue, 2) AS revenue,

    ROUND(prev.revenue, 2) AS prev_year_revenue,

    CASE

        WHEN prev.revenue IS NULL
            THEN NULL

        WHEN prev.revenue = 0
            THEN NULL

        ELSE ROUND(
            (
                (curr.revenue - prev.revenue)
                / prev.revenue
            ) * 100,
            2
        )

    END AS yoy_growth_percent

FROM monthly_revenue curr

LEFT JOIN monthly_revenue prev
    ON curr.year = prev.year + 1
   AND curr.month = prev.month

ORDER BY
    curr.year,
    curr.month;


-- ============================================================
-- QUERY 13
-- FIRST / LAST VALUE ANALYSIS
--
-- Find the first purchased category and the most recent
-- purchased category for each customer.
-- ============================================================

WITH customer_category_history AS (

    SELECT

        o.customer_id,

        p.category,

        o.order_date,

        o.order_id,

        FIRST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id
            ORDER BY
                o.order_date ASC,
                o.order_id ASC
            ROWS BETWEEN UNBOUNDED PRECEDING
                 AND UNBOUNDED FOLLOWING
        ) AS first_category,

        LAST_VALUE(p.category) OVER (
            PARTITION BY o.customer_id
            ORDER BY
                o.order_date ASC,
                o.order_id ASC
            ROWS BETWEEN UNBOUNDED PRECEDING
                 AND UNBOUNDED FOLLOWING
        ) AS most_recent_category

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    JOIN products p
        ON oi.product_id = p.product_id

    WHERE o.customer_id IS NOT NULL
)

SELECT DISTINCT

    customer_id,

    first_category,

    most_recent_category,

    CASE

        WHEN first_category != most_recent_category
            THEN 'Yes'

        ELSE 'No'

    END AS category_shift

FROM customer_category_history

ORDER BY
    customer_id;


-- ============================================================
-- QUERY 14
-- CUMULATIVE DISTRIBUTION
--
-- Calculate what percentage of total revenue comes from
-- customers as we move from highest-revenue customer
-- to lowest-revenue customer.
--
-- Output:
-- customer_id
-- revenue
-- cumulative_revenue
-- cumulative_percent
-- ============================================================

WITH customer_revenue AS (

    SELECT

        o.customer_id,

        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ) AS revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.customer_id IS NOT NULL

    GROUP BY
        o.customer_id
),

ranked_customers AS (

    SELECT

        customer_id,

        ROUND(
            revenue,
            2
        ) AS revenue,

        SUM(revenue) OVER (
            ORDER BY revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING
                 AND CURRENT ROW
        ) AS cumulative_revenue,

        SUM(revenue) OVER () AS total_revenue

    FROM customer_revenue
)

SELECT

    customer_id,

    revenue,

    ROUND(
        cumulative_revenue,
        2
    ) AS cumulative_revenue,

    ROUND(
        (
            cumulative_revenue
            / NULLIF(total_revenue, 0)
        ) * 100,
        2
    ) AS cumulative_percent

FROM ranked_customers

ORDER BY
    revenue DESC;


-- ============================================================
-- QUERY 15
-- COMPLEX CTE: COHORT ANALYSIS
--
-- Customers are grouped by registration month.
--
-- Month 0 = registration month
-- Month 1 = first month after registration
-- Month 2 = second month
-- Month 3 = third month
--
-- Calculate customer counts and retention rates.
-- ============================================================

WITH customer_cohorts AS (

    SELECT

        customer_id,

        strftime(
            '%Y-%m',
            registration_date
        ) AS cohort_month

    FROM customers
),

customer_orders AS (

    SELECT DISTINCT

        o.customer_id,

        strftime(
            '%Y-%m',
            o.order_date
        ) AS order_month

    FROM orders o

    WHERE o.customer_id IS NOT NULL
),

cohort_activity AS (

    SELECT

        c.customer_id,

        c.cohort_month,

        o.order_month,

        (
            (
                CAST(
                    strftime(
                        '%Y',
                        o.order_month || '-01'
                    )
                    AS INTEGER
                )
                -
                CAST(
                    strftime(
                        '%Y',
                        c.cohort_month || '-01'
                    )
                    AS INTEGER
                )
            ) * 12
            +
            (
                CAST(
                    strftime(
                        '%m',
                        o.order_month || '-01'
                    )
                    AS INTEGER
                )
                -
                CAST(
                    strftime(
                        '%m',
                        c.cohort_month || '-01'
                    )
                    AS INTEGER
                )
            )
        ) AS month_number

    FROM customer_cohorts c

    JOIN customer_orders o
        ON c.customer_id = o.customer_id

    WHERE o.order_month >= c.cohort_month
),

cohort_counts AS (

    SELECT

        cohort_month,

        month_number,

        COUNT(
            DISTINCT customer_id
        ) AS active_customers

    FROM cohort_activity

    WHERE month_number BETWEEN 0 AND 3

    GROUP BY
        cohort_month,
        month_number
),

cohort_size AS (

    SELECT

        cohort_month,

        COUNT(*) AS total_customers

    FROM customer_cohorts

    GROUP BY
        cohort_month
)

SELECT

    cc.cohort_month,

    cc.month_number,

    cc.active_customers,

    cs.total_customers,

    ROUND(
        (
            cc.active_customers
            * 100.0
            / NULLIF(
                cs.total_customers,
                0
            )
        ),
        2
    ) AS retention_rate

FROM cohort_counts cc

JOIN cohort_size cs
    ON cc.cohort_month = cs.cohort_month

ORDER BY
    cc.cohort_month,
    cc.month_number;


-- ============================================================
-- QUERY 16
-- SELF-JOIN WITH WINDOW FUNCTION
--
-- Find products frequently bought together.
--
-- A-B and B-A are treated as the same pair.
-- Same-product pairs are excluded.
-- ============================================================

WITH order_product_pairs AS (

    SELECT DISTINCT

        oi1.order_id,

        CASE

            WHEN oi1.product_id < oi2.product_id
                THEN oi1.product_id

            ELSE oi2.product_id

        END AS product_a,

        CASE

            WHEN oi1.product_id < oi2.product_id
                THEN oi2.product_id

            ELSE oi1.product_id

        END AS product_b

    FROM order_items oi1

    JOIN order_items oi2

        ON oi1.order_id = oi2.order_id

       AND oi1.product_id < oi2.product_id
),

pair_counts AS (

    SELECT

        product_a,

        product_b,

        COUNT(*) AS times_bought_together

    FROM order_product_pairs

    GROUP BY
        product_a,
        product_b
),

ranked_pairs AS (

    SELECT

        product_a,

        product_b,

        times_bought_together,

        DENSE_RANK() OVER (
            ORDER BY times_bought_together DESC
        ) AS pair_rank

    FROM pair_counts
)

SELECT

    pa.product_name AS product_a,

    pb.product_name AS product_b,

    rp.times_bought_together,

    rp.pair_rank

FROM ranked_pairs rp

JOIN products pa
    ON rp.product_a = pa.product_id

JOIN products pb
    ON rp.product_b = pb.product_id

ORDER BY
    rp.pair_rank,
    product_a,
    product_b

LIMIT 20;