-- ============================================================
-- E-Commerce Order Analytics System
-- SQLite Database Schema
-- ============================================================


-- ============================================================
-- Customers
-- ============================================================

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT,
    registration_date TEXT,
    customer_type TEXT
        CHECK (
            customer_type IN (
                'REGULAR',
                'PREMIUM',
                'VIP'
            )
        )
);


-- ============================================================
-- Products
-- ============================================================

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    cost_price REAL NOT NULL
);


-- ============================================================
-- Orders
-- ============================================================

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    region_code TEXT,

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);


-- ============================================================
-- Order Items
-- ============================================================

CREATE TABLE IF NOT EXISTS order_items (
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


-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_orders_customer
ON orders(customer_id);


CREATE INDEX IF NOT EXISTS idx_orders_date
ON orders(order_date);


CREATE INDEX IF NOT EXISTS idx_order_items_order
ON order_items(order_id);


CREATE INDEX IF NOT EXISTS idx_order_items_product
ON order_items(product_id);


CREATE INDEX IF NOT EXISTS idx_customers_registration
ON customers(registration_date);