import sqlite3
import sys
from pathlib import Path
from datetime import datetime


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "ecommerce.db"
)


# ============================================================
# Test Helpers
# ============================================================

def create_test_database():

    connection = sqlite3.connect(":memory:")

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    connection.executescript("""
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT
        );

        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            cost_price REAL
        );

        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT,
            order_date TEXT NOT NULL,
            status TEXT,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        );

        CREATE TABLE order_items (
            item_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount_percent REAL NOT NULL,

            FOREIGN KEY (order_id)
                REFERENCES orders(order_id),

            FOREIGN KEY (product_id)
                REFERENCES products(product_id),

            CHECK (discount_percent >= 0),
            CHECK (discount_percent <= 100)
        );
    """)

    return connection


# ============================================================
# Test 1
# Zero Revenue Date
# ============================================================

def test_zero_revenue_date():

    connection = create_test_database()

    try:

        connection.execute("""
            INSERT INTO customers
            VALUES (
                'CUST_TEST_001',
                'Test Customer',
                'test@example.com'
            )
        """)

        connection.execute("""
            INSERT INTO products
            VALUES (
                'PROD_TEST_001',
                'Test Product',
                100
            )
        """)

        connection.execute("""
            INSERT INTO orders
            VALUES (
                'ORD_TEST_001',
                'CUST_TEST_001',
                '2026-01-01 10:00:00',
                'CANCELLED'
            )
        """)

        connection.commit()

        result = connection.execute("""
            SELECT
                COALESCE(
                    SUM(
                        oi.quantity
                        * oi.unit_price
                        * (
                            1 -
                            oi.discount_percent / 100.0
                        )
                    ),
                    0
                )
            FROM orders o

            LEFT JOIN order_items oi
                ON o.order_id = oi.order_id

            WHERE DATE(o.order_date)
                  = '2026-01-01'
        """).fetchone()[0]

        assert result == 0

        print(
            "PASS: Zero-revenue date handled correctly"
        )

    finally:

        connection.close()


# ============================================================
# Test 2
# Negative Quantity / Return
# ============================================================

def test_negative_quantity():

    connection = create_test_database()

    try:

        connection.execute("""
            INSERT INTO customers
            VALUES (
                'CUST_TEST_002',
                'Return Customer',
                'return@example.com'
            )
        """)

        connection.execute("""
            INSERT INTO products
            VALUES (
                'PROD_TEST_002',
                'Return Product',
                100
            )
        """)

        connection.execute("""
            INSERT INTO orders
            VALUES (
                'ORD_TEST_002',
                'CUST_TEST_002',
                '2026-01-02 10:00:00',
                'RETURNED'
            )
        """)

        connection.execute("""
            INSERT INTO order_items
            VALUES (
                'ITEM_TEST_002',
                'ORD_TEST_002',
                'PROD_TEST_002',
                -2,
                100,
                0
            )
        """)

        connection.commit()

        result = connection.execute("""
            SELECT quantity
            FROM order_items
            WHERE item_id = 'ITEM_TEST_002'
        """).fetchone()[0]

        assert result == -2

        print(
            "PASS: Negative quantity preserved as return"
        )

    finally:

        connection.close()


# ============================================================
# Test 3
# Invalid Customer Reference
# ============================================================

def test_invalid_customer_reference():

    connection = create_test_database()

    try:

        connection.execute("""
            INSERT INTO customers
            VALUES (
                'CUST_TEST_003',
                'Valid Customer',
                'valid@example.com'
            )
        """)

        connection.commit()

        try:

            connection.execute("""
                INSERT INTO orders
                VALUES (
                    'ORD_TEST_003',
                    'CUSTOMER_DOES_NOT_EXIST',
                    '2026-01-03 10:00:00',
                    'PENDING'
                )
            """)

            connection.commit()

            raise AssertionError(
                "Invalid customer reference was accepted"
            )

        except sqlite3.IntegrityError:

            print(
                "PASS: Invalid customer reference rejected"
            )

    finally:

        connection.close()


# ============================================================
# Test 4
# Duplicate Customer ID
# ============================================================

def test_duplicate_customer_id():

    connection = create_test_database()

    try:

        connection.execute("""
            INSERT INTO customers
            VALUES (
                'CUST_TEST_004',
                'First Customer',
                'first@example.com'
            )
        """)

        connection.commit()

        try:

            connection.execute("""
                INSERT INTO customers
                VALUES (
                    'CUST_TEST_004',
                    'Duplicate Customer',
                    'duplicate@example.com'
                )
            """)

            connection.commit()

            raise AssertionError(
                "Duplicate customer ID was accepted"
            )

        except sqlite3.IntegrityError:

            print(
                "PASS: Duplicate customer ID rejected"
            )

    finally:

        connection.close()


# ============================================================
# Test 5
# Duplicate Order ID
# ============================================================

def test_duplicate_order_id():

    connection = create_test_database()

    try:

        connection.execute("""
            INSERT INTO customers
            VALUES (
                'CUST_TEST_005',
                'Order Customer',
                'order@example.com'
            )
        """)

        connection.execute("""
            INSERT INTO orders
            VALUES (
                'ORD_TEST_005',
                'CUST_TEST_005',
                '2026-01-05 10:00:00',
                'PENDING'
            )
        """)

        connection.commit()

        try:

            connection.execute("""
                INSERT INTO orders
                VALUES (
                    'ORD_TEST_005',
                    'CUST_TEST_005',
                    '2026-01-06 10:00:00',
                    'DELIVERED'
                )
            """)

            connection.commit()

            raise AssertionError(
                "Duplicate order ID was accepted"
            )

        except sqlite3.IntegrityError:

            print(
                "PASS: Duplicate order ID rejected"
            )

    finally:

        connection.close()


# ============================================================
# Test 6
# Date Validation
# ============================================================

def test_invalid_date():

    invalid_date = "2026-99-99"

    try:

        datetime.strptime(
            invalid_date,
            "%Y-%m-%d"
        )

        raise AssertionError(
            "Invalid date was accepted"
        )

    except ValueError:

        print(
            "PASS: Invalid date rejected"
        )


# ============================================================
# Part 5 Specific Edge Cases
# ============================================================

def test_order_items_invalid_order_id():
    connection = create_test_database()
    try:
        connection.execute("""
            INSERT INTO products VALUES ('PROD_TEST_101', 'Test Product', 100)
        """)
        connection.commit()
        try:
            connection.execute("""
                INSERT INTO order_items
                VALUES ('ITEM_TEST_101', 'ORD_DOES_NOT_EXIST', 'PROD_TEST_101', 1, 100, 0)
            """)
            connection.commit()
            raise AssertionError("Foreign key violation for order_id not in orders was accepted")
        except sqlite3.IntegrityError:
            print("PASS: order_items with invalid order_id rejected via foreign key")
    finally:
        connection.close()


def test_discount_greater_than_100():
    connection = create_test_database()
    try:
        connection.execute("INSERT INTO customers VALUES ('CUST_TEST_102', 'Test Cust', 'a@b.com')")
        connection.execute("INSERT INTO products VALUES ('PROD_TEST_102', 'Test Prod', 100)")
        connection.execute("INSERT INTO orders VALUES ('ORD_TEST_102', 'CUST_TEST_102', '2026-01-01 10:00:00', 'PLACED')")
        connection.commit()
        try:
            connection.execute("""
                INSERT INTO order_items
                VALUES ('ITEM_TEST_102', 'ORD_TEST_102', 'PROD_TEST_102', 1, 100, 110.0)
            """)
            connection.commit()
            raise AssertionError("discount_percent > 100 was accepted")
        except sqlite3.IntegrityError:
            print("PASS: discount_percent > 100 rejected via CHECK constraint")
    finally:
        connection.close()


def test_quantity_is_zero():
    from scripts.clean_data import clean_order_items
    issues = []
    item = {
        "item_id": "ITEM_TEST_103",
        "order_id": "ORD_TEST_103",
        "product_id": "PROD_TEST_103",
        "quantity": "0",
        "unit_price": "100.0",
        "discount_percent": "0.0"
    }
    clean_order_items([item], issues)
    assert len(issues) > 0
    assert any("ZERO QUANTITY" in issue for issue in issues)
    print("PASS: quantity = 0 correctly flagged during cleaning")


def test_future_order_date():
    from scripts.clean_data import clean_orders
    issues = []
    order = {
        "order_id": "ORD_TEST_104",
        "customer_id": "CUST_TEST_104",
        "order_date": "2030-01-01 10:00:00",
        "status": "PLACED",
        "region_code": "NORTH"
    }
    clean_orders([order], issues)
    assert len(issues) > 0
    assert any("FUTURE ORDER DATE" in issue for issue in issues)
    print("PASS: future order_date correctly flagged during cleaning")


# ============================================================
# Run Tests
# ============================================================

def main():

    print("=" * 70)
    print("EDGE CASE TESTS")
    print("=" * 70)

    tests = [
        test_zero_revenue_date,
        test_negative_quantity,
        test_invalid_customer_reference,
        test_duplicate_customer_id,
        test_duplicate_order_id,
        test_invalid_date,
        test_order_items_invalid_order_id,
        test_discount_greater_than_100,
        test_quantity_is_zero,
        test_future_order_date
    ]

    passed = 0
    failed = 0

    for test in tests:

        try:

            test()
            passed += 1

        except Exception as error:

            failed += 1

            print(
                f"FAIL: {test.__name__}"
            )

            print(
                f"      {error}"
            )

    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    print(
        f"Passed : {passed}"
    )

    print(
        f"Failed : {failed}"
    )

    if failed > 0:

        sys.exit(1)

    print()
    print("All edge-case tests passed.")


if __name__ == "__main__":
    main()