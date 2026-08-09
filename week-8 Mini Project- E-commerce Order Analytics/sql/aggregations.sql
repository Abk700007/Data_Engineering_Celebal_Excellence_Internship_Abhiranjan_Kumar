-- ============================================================
-- E-Commerce Order Analytics System
-- Basic & Intermediate SQL Analysis
-- ============================================================


-- ============================================================
-- QUERY 1
-- Total Revenue Per Category
--
-- Revenue formula:
--
-- quantity × unit_price ×
-- (1 - discount_percent / 100)
--
-- Negative quantities represent returns and therefore
-- reduce revenue.
-- ============================================================

SELECT
    p.category,

    ROUND(
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ),
        2
    ) AS total_revenue

FROM order_items oi

JOIN products p
    ON oi.product_id = p.product_id

GROUP BY
    p.category

ORDER BY
    total_revenue DESC;


-- ============================================================
-- QUERY 2
-- Top 10 Customers By Total Order Value
-- ============================================================

SELECT
    o.customer_id,

    c.customer_name,

    ROUND(
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ),
        2
    ) AS total_order_value

FROM orders o

JOIN customers c
    ON o.customer_id = c.customer_id

JOIN order_items oi
    ON o.order_id = oi.order_id

GROUP BY
    o.customer_id,
    c.customer_name

ORDER BY
    total_order_value DESC

LIMIT 10;


-- ============================================================
-- QUERY 3
-- Month-Wise Order Count
--
-- The assignment asks for the last 12 months.
-- SQLite date functions are used to group orders by month.
-- ============================================================

SELECT
    strftime(
        '%Y-%m',
        order_date
    ) AS order_month,

    COUNT(*) AS order_count

FROM orders

WHERE date(order_date) >= date(
    'now',
    '-12 months'
)

GROUP BY
    order_month

ORDER BY
    order_month;


-- ============================================================
-- QUERY 4
-- Customers Who Placed Orders But Never Had Any Item
-- Delivered
-- ============================================================

SELECT DISTINCT

    o.customer_id,

    c.customer_name

FROM orders o

JOIN customers c
    ON o.customer_id = c.customer_id

WHERE NOT EXISTS (

    SELECT 1

    FROM orders delivered_orders

    JOIN order_items oi
        ON delivered_orders.order_id = oi.order_id

    WHERE delivered_orders.customer_id = o.customer_id

      AND delivered_orders.status = 'DELIVERED'
);


-- ============================================================
-- QUERY 5
-- Products That Were Ordered But Had More Returns
-- Than Purchases
--
-- Positive quantity = purchase
-- Negative quantity = return
-- ============================================================

SELECT

    p.product_id,

    p.product_name,

    SUM(
        CASE
            WHEN oi.quantity > 0
            THEN oi.quantity
            ELSE 0
        END
    ) AS total_purchased,

    SUM(
        CASE
            WHEN oi.quantity < 0
            THEN ABS(oi.quantity)
            ELSE 0
        END
    ) AS total_returned

FROM products p

JOIN order_items oi
    ON p.product_id = oi.product_id

GROUP BY
    p.product_id,
    p.product_name

HAVING
    total_returned > total_purchased

ORDER BY
    total_returned DESC;


-- ============================================================
-- QUERY 6
-- Return Rate Per Category
--
-- return rate =
-- returned items / total items × 100
--
-- Negative quantities are treated as returned quantities.
-- ============================================================

SELECT

    p.category,

    SUM(
        CASE
            WHEN oi.quantity < 0
            THEN ABS(oi.quantity)
            ELSE 0
        END
    ) AS returned_items,

    SUM(
        ABS(oi.quantity)
    ) AS total_items,

    ROUND(
        100.0
        *
        SUM(
            CASE
                WHEN oi.quantity < 0
                THEN ABS(oi.quantity)
                ELSE 0
            END
        )
        /
        NULLIF(
            SUM(ABS(oi.quantity)),
            0
        ),
        2
    ) AS return_rate_percent

FROM products p

JOIN order_items oi
    ON p.product_id = oi.product_id

GROUP BY
    p.category

ORDER BY
    return_rate_percent DESC;