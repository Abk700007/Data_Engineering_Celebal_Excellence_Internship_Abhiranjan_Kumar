import csv
import sqlite3
from pathlib import Path


# Configuration

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "ecommerce.db"

SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

CLEANED_DIR = BASE_DIR / "data" / "cleaned"


# Database Connection

def get_connection():
    """Create and return a SQLite database connection."""

    connection = sqlite3.connect(DATABASE_PATH)

    # Enable foreign-key enforcement.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# Create Tables

def create_tables(connection):
    """Execute the SQL schema file."""

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        schema = file.read()

    connection.executescript(schema)

    connection.commit()

    print("Database schema created successfully.")


# CSV Loader

def load_csv(
    connection,
    filename,
    table_name,
    columns
):
    """Load a cleaned CSV file into a SQLite table."""

    filepath = CLEANED_DIR / filename

    with open(
        filepath,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        rows = []

        for row in reader:

            values = []

            for column in columns:

                value = row[column]

                # Convert empty strings to NULL.
                if value == "":
                    value = None

                values.append(value)

            rows.append(tuple(values))

    placeholders = ", ".join(
        ["?"] * len(columns)
    )

    column_names = ", ".join(columns)

    query = f"""
        INSERT INTO {table_name}
        ({column_names})
        VALUES ({placeholders})
    """

    connection.executemany(
        query,
        rows
    )

    connection.commit()

    print(
        f"Loaded {len(rows)} rows "
        f"into {table_name}."
    )


# Clear Existing Data

def clear_tables(connection):
    """Clear existing rows before reloading data."""

    connection.execute(
        "DELETE FROM order_items"
    )

    connection.execute(
        "DELETE FROM orders"
    )

    connection.execute(
        "DELETE FROM products"
    )

    connection.execute(
        "DELETE FROM customers"
    )

    connection.commit()

    print("Existing table data cleared.")


# Verify Row Counts

def verify_database(connection):

    tables = [
        "customers",
        "products",
        "orders",
        "order_items"
    ]

    print()
    print("=" * 50)
    print("DATABASE VERIFICATION")
    print("=" * 50)

    for table in tables:

        cursor = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        count = cursor.fetchone()[0]

        print(
            f"{table:<15}: {count}"
        )


# Main

def main():

    print("=" * 60)
    print("E-COMMERCE ORDER ANALYTICS SYSTEM")
    print("DATABASE SETUP")
    print("=" * 60)

    connection = get_connection()

    try:

        # Create database tables
        create_tables(connection)

        # Clear previous data if script is run again
        clear_tables(connection)

        # Load customers first because orders reference them
        load_csv(
            connection,
            "customers_clean.csv",
            "customers",
            [
                "customer_id",
                "customer_name",
                "email",
                "registration_date",
                "customer_type"
            ]
        )

        # Products must exist before order_items
        load_csv(
            connection,
            "products_clean.csv",
            "products",
            [
                "product_id",
                "product_name",
                "category",
                "subcategory",
                "cost_price"
            ]
        )

        # Orders reference customers
        load_csv(
            connection,
            "orders_clean.csv",
            "orders",
            [
                "order_id",
                "customer_id",
                "order_date",
                "status",
                "region_code"
            ]
        )

        # Order items reference both orders and products
        load_csv(
            connection,
            "order_items_clean.csv",
            "order_items",
            [
                "item_id",
                "order_id",
                "product_id",
                "quantity",
                "unit_price",
                "discount_percent"
            ]
        )

        # Verify everything
        verify_database(connection)

    except sqlite3.Error as error:

        print()
        print("SQLite error:")
        print(error)

    finally:

        connection.close()

        print()
        print("Database connection closed.")


if __name__ == "__main__":
    main()