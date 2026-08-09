import csv
import re
from pathlib import Path
from datetime import datetime


# Configuration

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "output"

CLEANED_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# File Helpers

def read_csv(filename):
    """Read a CSV file from the raw data directory."""
    filepath = RAW_DIR / filename

    with open(filepath, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def write_csv(filename, rows, fieldnames):
    """Write cleaned data to the cleaned directory."""
    filepath = CLEANED_DIR / filename

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {filepath}")


# Date Cleaning

def normalize_order_date(date_value):
    """Convert supported order date formats to YYYY-MM-DD HH:MM:SS."""

    if not date_value or not date_value.strip():
        return None

    date_value = date_value.strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S"
    ]

    for date_format in formats:
        try:
            parsed_date = datetime.strptime(
                date_value,
                date_format
            )

            return parsed_date.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:
            continue

    return None


# Part 2.1 - clean_orders()

def clean_orders(orders, issues):
    """Fix date formats and handle NULL customer_ids."""

    cleaned_orders = []

    for order in orders:

        original_date = order["order_date"]

        normalized_date = normalize_order_date(
            original_date
        )

        # Handle order date

        if normalized_date is None:

            issues.append(
                f"INVALID ORDER DATE | "
                f"order_id={order['order_id']} | "
                f"value={original_date}"
            )

        elif normalized_date != original_date:

            issues.append(
                f"DATE FORMAT FIXED | "
                f"order_id={order['order_id']} | "
                f"old={original_date} | "
                f"new={normalized_date}"
            )

        # Check for future date
        if normalized_date:
            try:
                order_dt = datetime.strptime(normalized_date, "%Y-%m-%d %H:%M:%S")
                if order_dt > datetime.now():
                    issues.append(
                        f"FUTURE ORDER DATE | "
                        f"order_id={order['order_id']} | "
                        f"value={normalized_date}"
                    )
            except ValueError:
                pass

        # Handle NULL customer_id

        customer_id = order["customer_id"].strip()

        if customer_id == "":
            customer_id = None

            issues.append(
                f"MISSING CUSTOMER ID | "
                f"order_id={order['order_id']}"
            )

        cleaned_orders.append({
            "order_id": order["order_id"].strip(),
            "customer_id": customer_id or "",
            "order_date": normalized_date or "",
            "status": order["status"].strip().upper(),
            "region_code": order["region_code"].strip().upper()
        })

    return cleaned_orders


# Part 2.2 - clean_products()

def clean_products(products, issues):
    """Normalize product names (trim spaces, title case)."""

    cleaned_products = []

    for product in products:

        original_name = product["product_name"]

        cleaned_name = " ".join(
            original_name.strip().split()
        ).title()

        if cleaned_name != original_name:

            issues.append(
                f"PRODUCT NAME NORMALIZED | "
                f"product_id={product['product_id']} | "
                f"old={original_name} | "
                f"new={cleaned_name}"
            )

        cleaned_products.append({
            "product_id": product["product_id"].strip(),
            "product_name": cleaned_name,
            "category": product["category"].strip(),
            "subcategory": product["subcategory"].strip(),
            "cost_price": product["cost_price"].strip()
        })

    return cleaned_products


# Part 2.3 - validate_emails()

def validate_emails(customers, issues):
    """Return list of customer_ids with invalid emails."""

    invalid_customer_ids = []

    email_pattern = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    for customer in customers:

        email = customer["email"].strip()

        if not email_pattern.match(email):

            customer_id = customer["customer_id"]

            invalid_customer_ids.append(
                customer_id
            )

            issues.append(
                f"INVALID EMAIL | "
                f"customer_id={customer_id} | "
                f"email={email}"
            )

    return invalid_customer_ids


# Clean Customers

def clean_customers(customers, issues):
    """Clean customer data while preserving invalid emails."""

    cleaned_customers = []

    for customer in customers:

        cleaned_customers.append({
            "customer_id": customer["customer_id"].strip(),
            "customer_name": " ".join(
                customer["customer_name"].strip().split()
            ),
            "email": customer["email"].strip(),
            "registration_date": customer[
                "registration_date"
            ].strip(),
            "customer_type": customer[
                "customer_type"
            ].strip().upper()
        })

    return cleaned_customers


# Part 2.4 - check_referential_integrity()

def check_referential_integrity(
    orders,
    order_items,
    issues
):
    """Find order_items referencing non-existent orders."""

    order_ids = {
        order["order_id"]
        for order in orders
    }

    invalid_items = []

    for item in order_items:

        order_id = item["order_id"].strip()

        if order_id not in order_ids:

            invalid_items.append(
                item["item_id"]
            )

            issues.append(
                f"INVALID ORDER REFERENCE | "
                f"item_id={item['item_id']} | "
                f"order_id={order_id}"
            )

    return invalid_items


# Clean Order Items

def clean_order_items(order_items, issues):
    """Clean formatting of order item fields."""

    cleaned_items = []

    for item in order_items:

        quantity = int(item["quantity"])

        if quantity < 0:

            issues.append(
                f"RETURN ITEM | "
                f"item_id={item['item_id']} | "
                f"quantity={quantity}"
            )

        elif quantity == 0:

            issues.append(
                f"ZERO QUANTITY | "
                f"item_id={item['item_id']}"
            )

        discount = float(item["discount_percent"])

        if discount < 0 or discount > 100:

            issues.append(
                f"INVALID DISCOUNT | "
                f"item_id={item['item_id']} | "
                f"discount_percent={discount}"
            )

        cleaned_items.append({
            "item_id": item["item_id"].strip(),
            "order_id": item["order_id"].strip(),
            "product_id": item["product_id"].strip(),
            "quantity": str(quantity),
            "unit_price": item["unit_price"].strip(),
            "discount_percent": item[
                "discount_percent"
            ].strip()
        })

    return cleaned_items


# Report Generator

def write_quality_report(issues):
    """Write all detected data-quality issues to a report."""

    report_path = OUTPUT_DIR / "data_quality_report.txt"

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "E-COMMERCE ORDER ANALYTICS SYSTEM\n"
        )

        file.write(
            "DATA QUALITY REPORT\n"
        )

        file.write("=" * 70 + "\n\n")

        file.write(
            f"Total issues found: {len(issues)}\n\n"
        )

        if not issues:

            file.write(
                "No data-quality issues were found.\n"
            )

        else:

            for number, issue in enumerate(
                issues,
                start=1
            ):

                file.write(
                    f"{number}. {issue}\n"
                )

    print(f"Created: {report_path}")


# Main

def main():

    print("=" * 70)
    print("E-COMMERCE ORDER ANALYTICS SYSTEM")
    print("DATA CLEANING")
    print("=" * 70)

    issues = []

    # Read raw data

    customers = read_csv(
        "customers.csv"
    )

    products = read_csv(
        "products.csv"
    )

    orders = read_csv(
        "orders.csv"
    )

    order_items = read_csv(
        "order_items.csv"
    )

    print()
    print("Raw data loaded:")
    print(f"Customers   : {len(customers)}")
    print(f"Products    : {len(products)}")
    print(f"Orders      : {len(orders)}")
    print(f"Order Items : {len(order_items)}")

    # Clean data

    cleaned_customers = clean_customers(
        customers,
        issues
    )

    cleaned_products = clean_products(
        products,
        issues
    )

    cleaned_orders = clean_orders(
        orders,
        issues
    )

    cleaned_order_items = clean_order_items(
        order_items,
        issues
    )

    # Validation

    invalid_emails = validate_emails(
        cleaned_customers,
        issues
    )

    invalid_order_items = check_referential_integrity(
        cleaned_orders,
        cleaned_order_items,
        issues
    )

    # Write cleaned CSV files

    write_csv(
        "customers_clean.csv",
        cleaned_customers,
        [
            "customer_id",
            "customer_name",
            "email",
            "registration_date",
            "customer_type"
        ]
    )

    write_csv(
        "products_clean.csv",
        cleaned_products,
        [
            "product_id",
            "product_name",
            "category",
            "subcategory",
            "cost_price"
        ]
    )

    write_csv(
        "orders_clean.csv",
        cleaned_orders,
        [
            "order_id",
            "customer_id",
            "order_date",
            "status",
            "region_code"
        ]
    )

    write_csv(
        "order_items_clean.csv",
        cleaned_order_items,
        [
            "item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount_percent"
        ]
    )

    # Write report

    write_quality_report(
        issues
    )

    # Summary

    print()
    print("=" * 70)
    print("DATA CLEANING COMPLETE")
    print("=" * 70)

    print(f"Invalid emails           : {len(invalid_emails)}")
    print(
        f"Invalid order references : "
        f"{len(invalid_order_items)}"
    )
    print(
        f"Total issues reported    : "
        f"{len(issues)}"
    )

    print()
    print(
        f"Cleaned files: {CLEANED_DIR}"
    )

    print(
        f"Quality report: "
        f"{OUTPUT_DIR / 'data_quality_report.txt'}"
    )


if __name__ == "__main__":
    main()