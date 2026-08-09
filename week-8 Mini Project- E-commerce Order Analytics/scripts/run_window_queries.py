import sqlite3
from pathlib import Path


# Configuration

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "ecommerce.db"
)


# Query 7 - Running Total

QUERY_7 = """
WITH daily_revenue AS (

    SELECT
        o.region_code,
        DATE(o.order_date) AS order_date,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS daily_revenue

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    GROUP BY
        o.region_code,
        DATE(o.order_date)
)

SELECT
    region_code,
    order_date,
    daily_revenue,

    ROUND(
        SUM(daily_revenue) OVER (
            PARTITION BY region_code
            ORDER BY order_date
            ROWS BETWEEN UNBOUNDED PRECEDING
                 AND CURRENT ROW
        ),
        2
    ) AS running_total

FROM daily_revenue

ORDER BY
    region_code,
    order_date

LIMIT 20;
"""


# Query 8 - DENSE_RANK

QUERY_8 = """
WITH product_revenue AS (

    SELECT
        p.category,
        p.product_id,
        p.product_name,

        ROUND(
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount_percent / 100.0)
            ),
            2
        ) AS total_revenue

    FROM products p

    JOIN order_items oi
        ON p.product_id = oi.product_id

    GROUP BY
        p.category,
        p.product_id,
        p.product_name
)

SELECT
    category,
    product_name,
    total_revenue,

    DENSE_RANK() OVER (
        PARTITION BY category
        ORDER BY total_revenue DESC
    ) AS rank_in_category

FROM product_revenue

ORDER BY
    category,
    rank_in_category,
    product_name

LIMIT 30;
"""


# Query 9 - LAG / Days Gap

QUERY_9 = """
WITH customer_orders AS (

    SELECT
        o.customer_id,
        DATE(o.order_date) AS order_date,

        LAG(
            DATE(o.order_date)
        ) OVER (
            PARTITION BY o.customer_id
            ORDER BY DATE(o.order_date)
        ) AS previous_order_date

    FROM orders o

    WHERE o.customer_id IS NOT NULL
)

SELECT

    customer_id,

    order_date,

    previous_order_date,

    CASE

        WHEN previous_order_date IS NULL
        THEN NULL

        ELSE CAST(
            julianday(order_date)
            - julianday(previous_order_date)
            AS INTEGER
        )

    END AS days_gap

FROM customer_orders

ORDER BY
    customer_id,
    order_date

LIMIT 30;
"""


# Query 9B - At Risk Customers

QUERY_9B = """
WITH customer_orders AS (

    SELECT
        o.customer_id,
        DATE(o.order_date) AS order_date,

        LAG(
            DATE(o.order_date)
        ) OVER (
            PARTITION BY o.customer_id
            ORDER BY DATE(o.order_date)
        ) AS previous_order_date

    FROM orders o

    WHERE o.customer_id IS NOT NULL
),

customer_gaps AS (

    SELECT
        customer_id,

        CAST(
            julianday(order_date)
            - julianday(previous_order_date)
            AS INTEGER
        ) AS days_gap

    FROM customer_orders

    WHERE previous_order_date IS NOT NULL
),

average_gaps AS (

    SELECT
        customer_id,

        ROUND(
            AVG(days_gap),
            2
        ) AS average_gap_days

    FROM customer_gaps

    GROUP BY
        customer_id
)

SELECT

    customer_id,

    average_gap_days,

    CASE

        WHEN average_gap_days > 30
        THEN 'At Risk'

        ELSE 'Active'

    END AS customer_status

FROM average_gaps

ORDER BY
    average_gap_days DESC

LIMIT 30;
"""


# Runner

def run_query(connection, query, title):

    print()
    print("=" * 100)
    print(title)
    print("=" * 100)

    cursor = connection.execute(query)

    rows = cursor.fetchall()

    if not rows:
        print("No results found.")
        return

    columns = [
        description[0]
        for description in cursor.description
    ]

    print(" | ".join(columns))
    print("-" * 100)

    for row in rows:
        print(" | ".join(
            "NULL" if value is None else str(value)
            for value in row
        ))


# Main

def main():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        run_query(
            connection,
            QUERY_7,
            "QUERY 7 - RUNNING TOTAL BY REGION"
        )

        run_query(
            connection,
            QUERY_8,
            "QUERY 8 - PRODUCT RANKING WITH DENSE_RANK"
        )

        run_query(
            connection,
            QUERY_9,
            "QUERY 9 - CUSTOMER ORDER GAPS WITH LAG"
        )

        run_query(
            connection,
            QUERY_9B,
            "QUERY 9B - AT RISK CUSTOMERS"
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()