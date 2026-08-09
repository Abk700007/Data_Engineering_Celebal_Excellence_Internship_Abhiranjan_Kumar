import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


# Configuration

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)

NUM_CUSTOMERS = 600
NUM_PRODUCTS = 600
NUM_ORDERS = 1500
NUM_ORDER_ITEMS = 3000

# Controlled Data Quality Issues

INVALID_EMAIL_COUNT = 12          # 2% of 600
INCONSISTENT_DATE_COUNT = 75      # 5% of 1500
NEGATIVE_QUANTITY_COUNT = 90      # 3% of 3000
MISSING_CUSTOMER_COUNT = 75       # 5% of 1500


# Sample Data

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rahul",
    "Rohan", "Karan", "Yash", "Amit", "Akash",
    "Neha", "Priya", "Ananya", "Isha", "Sneha",
    "Pooja", "Riya", "Kavya", "Aditi", "Meera"
]

LAST_NAMES = [
    "Sharma", "Patel", "Sawant", "Joshi", "Deshmukh",
    "Kulkarni", "Pawar", "Jadhav", "More", "Shinde",
    "Verma", "Gupta", "Singh", "Khan", "Mehta"
]

CATEGORIES = {
    "Electronics": [
        "Laptop",
        "Smartphone",
        "Tablet",
        "Headphones",
        "Keyboard",
        "Mouse",
        "Monitor",
        "Smartwatch"
    ],
    "Clothing": [
        "T-Shirt",
        "Jeans",
        "Jacket",
        "Hoodie",
        "Sneakers",
        "Shirt",
        "Dress"
    ],
    "Home": [
        "Chair",
        "Table",
        "Lamp",
        "Cushion",
        "Bedsheet",
        "Curtains",
        "Storage Box"
    ],
    "Books": [
        "Novel",
        "Programming Book",
        "Data Science Book",
        "Biography",
        "History Book",
        "Science Book"
    ]
}

SUBCATEGORIES = {
    "Electronics": "Consumer Electronics",
    "Clothing": "Apparel",
    "Home": "Home & Living",
    "Books": "Books & Education"
}

STATUSES = [
    "PLACED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "RETURNED"
]

REGIONS = [
    "NORTH",
    "SOUTH",
    "EAST",
    "WEST",
    "CENTRAL"
]

CUSTOMER_TYPES = [
    "REGULAR",
    "PREMIUM",
    "VIP"
]


# Utility Functions

def random_date(start_date, end_date):
    """Generate a random datetime between two dates."""
    time_difference = end_date - start_date
    random_seconds = random.randint(0, int(time_difference.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def write_csv(filename, rows, fieldnames):
    """Write rows to a CSV file."""
    filepath = RAW_DIR / filename

    with open(filepath, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created: {filepath}")


# Generate Customers

def generate_customers():
    customers = []

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 8, 1)

    # Exactly 12 customers will receive invalid emails.
    invalid_email_indices = set(
        range(INVALID_EMAIL_COUNT)
    )

    for i in range(1, NUM_CUSTOMERS + 1):

        customer_id = f"CUST{i:04d}"
        customer_name = random_name()

        # Controlled invalid emails

        if (i - 1) in invalid_email_indices:

            invalid_emails = [
                f"user{i}example.com",
                f"user{i}@",
                f"user{i}",
                f"@example.com"
            ]

            email = random.choice(
                invalid_emails
            )

        else:

            first_name = (
                customer_name
                .split()[0]
                .lower()
            )

            last_name = (
                customer_name
                .split()[1]
                .lower()
            )

            email = (
                f"{first_name}."
                f"{last_name}"
                f"{i}@example.com"
            )

        registration_date = random_date(
            start_date,
            end_date
        ).strftime("%Y-%m-%d")

        customer_type = random.choice(
            CUSTOMER_TYPES
        )

        customers.append({
            "customer_id": customer_id,
            "customer_name": customer_name,
            "email": email,
            "registration_date": registration_date,
            "customer_type": customer_type
        })

    write_csv(
        "customers.csv",
        customers,
        [
            "customer_id",
            "customer_name",
            "email",
            "registration_date",
            "customer_type"
        ]
    )

    return customers

# Generate Products

def generate_products():
    products = []

    product_id = 1

    for category, product_names in CATEGORIES.items():

        for base_name in product_names:

            for variation in range(1, 25):

                name = f"{base_name} {variation}"

                # Intentional product-name issues
                issue = random.random()

                if issue < 0.05:
                    name = f"  {name}  "

                elif issue < 0.10:
                    name = name.upper()

                elif issue < 0.15:
                    name = name.lower()

                cost_price = round(
                    random.uniform(100, 50000),
                    2
                )

                products.append({
                    "product_id": f"PROD{product_id:04d}",
                    "product_name": name,
                    "category": category,
                    "subcategory": SUBCATEGORIES[category],
                    "cost_price": cost_price
                })

                product_id += 1

                if len(products) >= NUM_PRODUCTS:
                    break

            if len(products) >= NUM_PRODUCTS:
                break

        if len(products) >= NUM_PRODUCTS:
            break

    write_csv(
        "products.csv",
        products,
        [
            "product_id",
            "product_name",
            "category",
            "subcategory",
            "cost_price"
        ]
    )

    return products


# Generate Orders

def generate_orders(customers):
    orders = []

    customer_ids = [
        customer["customer_id"]
        for customer in customers
    ]

    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 8, 1)

    # Controlled data-quality issues

    # Exactly 75 orders will have inconsistent date format.
    inconsistent_date_indices = set(
        range(INCONSISTENT_DATE_COUNT)
    )

    # Exactly 75 orders will have missing customer IDs.
    missing_customer_indices = set(
        range(MISSING_CUSTOMER_COUNT)
    )

    for i in range(1, NUM_ORDERS + 1):

        order_id = f"ORD{i:05d}"

        # Missing customer IDs

        if (i - 1) in missing_customer_indices:

            customer_id = ""

        else:

            customer_id = random.choice(
                customer_ids
            )

        # Generate order date

        order_datetime = random_date(
            start_date,
            end_date
        )

        # Controlled inconsistent date format

        if (i - 1) in inconsistent_date_indices:

            order_date = order_datetime.strftime(
                "%d-%m-%Y %H:%M:%S"
            )

        else:

            order_date = order_datetime.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        status = random.choice(
            STATUSES
        )

        region_code = random.choice(
            REGIONS
        )

        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "status": status,
            "region_code": region_code
        })

    write_csv(
        "orders.csv",
        orders,
        [
            "order_id",
            "customer_id",
            "order_date",
            "status",
            "region_code"
        ]
    )

    return orders


# Generate Order Items

def generate_order_items(orders, products):
    order_items = []

    order_ids = [
        order["order_id"]
        for order in orders
    ]

    product_ids = [
        product["product_id"]
        for product in products
    ]

    product_prices = {
        product["product_id"]: product["cost_price"]
        for product in products
    }

    # Exactly 90 negative quantities (3% of 3000)

    negative_quantity_indices = set(
        range(NEGATIVE_QUANTITY_COUNT)
    )

    for i in range(1, NUM_ORDER_ITEMS + 1):

        item_id = f"ITEM{i:06d}"

        # Always use an existing order_id.
        order_id = random.choice(
            order_ids
        )

        product_id = random.choice(
            product_ids
        )

        # Normal quantity
        quantity = random.randint(
            1,
            5
        )

        # Controlled returns

        if (i - 1) in negative_quantity_indices:

            quantity = -quantity

        base_price = product_prices[
            product_id
        ]

        # Selling price can differ from cost price
        unit_price = round(
            base_price
            * random.uniform(1.1, 2.0),
            2
        )

        discount_percent = round(
            random.uniform(0, 50),
            2
        )

        order_items.append({
            "item_id": item_id,
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_percent": discount_percent
        })

    write_csv(
        "order_items.csv",
        order_items,
        [
            "item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount_percent"
        ]
    )

    return order_items


# Main

def main():
    print("=" * 60)
    print("E-Commerce Order Analytics System")
    print("Generating raw datasets...")
    print("=" * 60)

    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(customers)
    generate_order_items(orders, products)

    print()
    print("=" * 60)
    print("DATA GENERATION COMPLETE")
    print("=" * 60)

    print(f"Customers   : {len(customers)}")
    print(f"Products    : {len(products)}")
    print(f"Orders      : {len(orders)}")
    print(f"Order Items : {NUM_ORDER_ITEMS}")

    print()
    print(f"Raw files created in: {RAW_DIR}")


if __name__ == "__main__":
    main()