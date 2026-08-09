import sqlite3
from pathlib import Path


# Configuration

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "ecommerce.db"
)


# Query 10 - Multiple-Level CTE

QUERY_10 = """
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
    END

LIMIT 30;
"""


# Query 11 - NTILE Customer Segmentation

QUERY_11 = """
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
    total_value DESC

LIMIT 30;
"""


# Query 12 - Year-over-Year Comparison

QUERY_12 = """
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
"""


# Query 13 - First / Last Purchased Category

QUERY_13 = """
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
    customer_id

LIMIT 30;
"""


# Query 14 - Cumulative Revenue Distribution

QUERY_14 = """
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
    revenue DESC

LIMIT 30;
"""


# Query 15 - Cohort Analysis

QUERY_15 = """
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
    cc.month_number

LIMIT 30;
"""


# Query 16 - Frequently Bought Together

QUERY_16 = """
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
"""


# Generic Query Runner

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

        print(
            " | ".join(
                "NULL" if value is None else str(value)
                for value in row
            )
        )


# Main

def main():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    try:

        run_query(
            connection,
            QUERY_10,
            "QUERY 10 - MULTI-LEVEL CTE"
        )

        run_query(
            connection,
            QUERY_11,
            "QUERY 11 - NTILE CUSTOMER SEGMENTATION"
        )

        run_query(
            connection,
            QUERY_12,
            "QUERY 12 - YEAR-OVER-YEAR COMPARISON"
        )

        run_query(
            connection,
            QUERY_13,
            "QUERY 13 - FIRST / LAST CATEGORY ANALYSIS"
        )

        run_query(
            connection,
            QUERY_14,
            "QUERY 14 - CUMULATIVE REVENUE DISTRIBUTION"
        )

        run_query(
            connection,
            QUERY_15,
            "QUERY 15 - COHORT ANALYSIS"
        )

        run_query(
            connection,
            QUERY_16,
            "QUERY 16 - FREQUENTLY BOUGHT TOGETHER"
        )

    finally:

        connection.close()


if __name__ == "__main__":
    main()