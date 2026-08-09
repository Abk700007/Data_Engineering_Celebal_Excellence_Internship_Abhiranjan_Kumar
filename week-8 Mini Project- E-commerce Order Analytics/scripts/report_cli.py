import sqlite3
from pathlib import Path
from datetime import datetime, timedelta


# Configuration

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "ecommerce.db"
)


# Database

def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# Input Validation

def get_report_type():

    print()
    print("Select report type:")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")

    while True:

        choice = input(
            "\nEnter choice (1-3): "
        ).strip()

        if choice == "1":
            return "daily"

        if choice == "2":
            return "weekly"

        if choice == "3":
            return "monthly"

        print(
            "Invalid choice. "
            "Please enter 1, 2, or 3."
        )


def get_date(prompt):

    while True:

        value = input(
            prompt
        ).strip()

        try:

            return datetime.strptime(
                value,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            print(
                "Invalid date format. "
                "Use YYYY-MM-DD."
            )


def get_date_range():

    while True:

        start_date = get_date(
            "Enter start date (YYYY-MM-DD): "
        )

        end_date = get_date(
            "Enter end date (YYYY-MM-DD): "
        )

        if end_date < start_date:

            print(
                "End date cannot be before "
                "start date."
            )

            continue

        return start_date, end_date


# Report SQL

REVENUE_SQL = """
SELECT
    COALESCE(
        SUM(
            oi.quantity
            * oi.unit_price
            * (1 - oi.discount_percent / 100.0)
        ),
        0
    ) AS revenue

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE DATE(o.order_date)
      BETWEEN DATE(?) AND DATE(?)
"""


ORDERS_SQL = """
SELECT
    COUNT(DISTINCT o.order_id) AS order_count

FROM orders o

WHERE DATE(o.order_date)
      BETWEEN DATE(?) AND DATE(?)
"""


CUSTOMERS_SQL = """
SELECT
    COUNT(DISTINCT o.customer_id)
    AS unique_customers

FROM orders o

WHERE DATE(o.order_date)
      BETWEEN DATE(?) AND DATE(?)

AND o.customer_id IS NOT NULL
"""


TOP_PRODUCTS_SQL = """
SELECT

    p.product_name,

    SUM(
        oi.quantity
        * oi.unit_price
        * (1 - oi.discount_percent / 100.0)
    ) AS revenue

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

JOIN products p
    ON oi.product_id = p.product_id

WHERE DATE(o.order_date)
      BETWEEN DATE(?) AND DATE(?)

GROUP BY
    p.product_id,
    p.product_name

ORDER BY
    revenue DESC

LIMIT 3
"""


RETURN_RATE_SQL = """
SELECT

    COALESCE(
        SUM(
            CASE
                WHEN oi.quantity < 0
                THEN ABS(oi.quantity)
                ELSE 0
            END
        ),
        0
    ) AS returned_items,

    COALESCE(
        SUM(
            ABS(oi.quantity)
        ),
        0
    ) AS total_items

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE DATE(o.order_date)
      BETWEEN DATE(?) AND DATE(?)
"""


# Query Helpers

def get_revenue(
    connection,
    start_date,
    end_date
):

    row = connection.execute(
        REVENUE_SQL,
        (
            start_date.isoformat(),
            end_date.isoformat()
        )
    ).fetchone()

    return float(
        row["revenue"]
    )


def get_order_count(
    connection,
    start_date,
    end_date
):

    row = connection.execute(
        ORDERS_SQL,
        (
            start_date.isoformat(),
            end_date.isoformat()
        )
    ).fetchone()

    return int(
        row["order_count"]
    )


def get_unique_customers(
    connection,
    start_date,
    end_date
):

    row = connection.execute(
        CUSTOMERS_SQL,
        (
            start_date.isoformat(),
            end_date.isoformat()
        )
    ).fetchone()

    return int(
        row["unique_customers"]
    )


def get_top_products(
    connection,
    start_date,
    end_date
):

    return connection.execute(
        TOP_PRODUCTS_SQL,
        (
            start_date.isoformat(),
            end_date.isoformat()
        )
    ).fetchall()


def get_return_rate(
    connection,
    start_date,
    end_date
):

    row = connection.execute(
        RETURN_RATE_SQL,
        (
            start_date.isoformat(),
            end_date.isoformat()
        )
    ).fetchone()

    returned_items = float(
        row["returned_items"]
    )

    total_items = float(
        row["total_items"]
    )

    if total_items == 0:
        return 0.0

    return (
        returned_items
        / total_items
        * 100
    )


# Report Generation

def calculate_percent_change(current, previous):
    if previous == 0:
        if current == 0:
            return "0.00%"
        return "+100.00%"
    change = ((current - previous) / previous) * 100
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:,.2f}%"


def generate_report(
    report_type,
    start_date,
    end_date
):

    days_delta = (end_date - start_date).days + 1
    prev_start_date = start_date - timedelta(days=days_delta)
    prev_end_date = start_date - timedelta(days=1)

    connection = get_connection()

    try:

        # Current period metrics
        revenue = get_revenue(
            connection,
            start_date,
            end_date
        )

        order_count = get_order_count(
            connection,
            start_date,
            end_date
        )

        unique_customers = (
            get_unique_customers(
                connection,
                start_date,
                end_date
            )
        )

        top_products = get_top_products(
            connection,
            start_date,
            end_date
        )

        return_rate = get_return_rate(
            connection,
            start_date,
            end_date
        )

        # Previous period metrics
        prev_revenue = get_revenue(
            connection,
            prev_start_date,
            prev_end_date
        )

        prev_order_count = get_order_count(
            connection,
            prev_start_date,
            prev_end_date
        )

        prev_unique_customers = (
            get_unique_customers(
                connection,
                prev_start_date,
                prev_end_date
            )
        )

    finally:

        connection.close()

    # Percentage changes
    revenue_change = calculate_percent_change(revenue, prev_revenue)
    orders_change = calculate_percent_change(order_count, prev_order_count)
    customers_change = calculate_percent_change(unique_customers, prev_unique_customers)

    # Average Order Value

    if order_count == 0:

        average_order_value = 0.0

    else:

        average_order_value = (
            revenue
            / order_count
        )

    # Print Report

    print()
    print("=" * 70)
    print("E-COMMERCE ORDER ANALYTICS REPORT")
    print("=" * 70)

    print(
        f"Report Type : {report_type.title()}"
    )

    print(
        f"Start Date  : {start_date}"
    )

    print(
        f"End Date    : {end_date}"
    )

    print(
        f"Prev Period : {prev_start_date} to {prev_end_date}"
    )

    print("-" * 70)

    print(
        f"Revenue             : "
        f"{revenue:,.2f} ({revenue_change} vs prev period)"
    )

    print(
        f"Orders              : "
        f"{order_count:,} ({orders_change} vs prev period)"
    )

    print(
        f"Unique Customers    : "
        f"{unique_customers:,} ({customers_change} vs prev period)"
    )

    print(
        f"Average Order Value : "
        f"{average_order_value:,.2f}"
    )

    print(
        f"Return Rate         : "
        f"{return_rate:.2f}%"
    )

    print()
    print("Top 3 Products")
    print("-" * 70)

    if not top_products:

        print(
            "No products found for "
            "this date range."
        )

    else:

        for index, product in enumerate(
            top_products,
            start=1
        ):

            product_revenue = float(
                product["revenue"]
            )

            print(
                f"{index}. "
                f"{product['product_name']}"
                f" — "
                f"{product_revenue:,.2f}"
            )

    print("=" * 70)


# Main

def main():

    print("=" * 70)
    print("E-COMMERCE ORDER ANALYTICS SYSTEM")
    print("=" * 70)

    report_type = get_report_type()

    start_date, end_date = (
        get_date_range()
    )

    generate_report(
        report_type,
        start_date,
        end_date
    )


if __name__ == "__main__":
    main()