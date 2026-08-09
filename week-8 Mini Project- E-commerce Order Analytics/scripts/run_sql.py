import sqlite3
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "ecommerce.db"
)


# ============================================================
# Query 1
# Total Revenue Per Category
# ============================================================

QUERY_1 = """
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
"""


# ============================================================
# Query 2
# Top 10 Customers By Total Order Value
# ============================================================

QUERY_2 = """
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
"""


# ============================================================
# Query 3
# Month-Wise Order Count
# ============================================================

QUERY_3 = """
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
"""


# ============================================================
# Query 4
# Customers Who Placed Orders But Never Had
# Any Item Delivered
# ============================================================

QUERY_4 = """
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
)

ORDER BY
    o.customer_id;
"""


# ============================================================
# Query 5
# Products With More Returns Than Purchases
# ============================================================

QUERY_5 = """
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
"""


# ============================================================
# Query 6
# Return Rate Per Category
# ============================================================

QUERY_6 = """
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
"""


# ============================================================
# Query Runner
# ============================================================

def run_query(connection, query, title):

    print()
    print("=" * 90)
    print(title)
    print("=" * 90)

    cursor = connection.execute(query)

    rows = cursor.fetchall()

    if not rows:
        print("No results found.")
        return

    column_names = [
        description[0]
        for description in cursor.description
    ]

    print(" | ".join(column_names))
    print("-" * 90)

    for row in rows:
        print(" | ".join(str(value) for value in row))


# ============================================================
# Main
# ============================================================

def main():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        run_query(
            connection,
            QUERY_1,
            "QUERY 1 - TOTAL REVENUE PER CATEGORY"
        )

        run_query(
            connection,
            QUERY_2,
            "QUERY 2 - TOP 10 CUSTOMERS"
        )

        run_query(
            connection,
            QUERY_3,
            "QUERY 3 - MONTH-WISE ORDER COUNT"
        )

        run_query(
            connection,
            QUERY_4,
            "QUERY 4 - CUSTOMERS WITHOUT DELIVERED ITEMS"
        )

        run_query(
            connection,
            QUERY_5,
            "QUERY 5 - PRODUCTS WITH MORE RETURNS THAN PURCHASES"
        )

        run_query(
            connection,
            QUERY_6,
            "QUERY 6 - RETURN RATE PER CATEGORY"
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()