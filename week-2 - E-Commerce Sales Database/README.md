# My E-Commerce Sales Database Project (ShopEase)

For my Week 2 task in the Celebal Technologies Internship, I worked on setting up a relational sales database for an e-commerce platform called ShopEase. I designed the database schema, defined tables with proper primary keys and foreign keys, wrote custom check constraints, created index structures to optimize search speeds, and solved a wide range of SQL queries from basic selects to advanced transactions.

---

## 📂 My Project Structure

Here is how I organized my files for this project:

```text
week-2 - E-Commerce Sales Database/
├── database/
│   ├── create_database.sql   -- Where I create the ecommerce_sales database
│   ├── create_tables.sql     -- Where I define all my tables and their constraints
│   ├── create_indexes.sql    -- Where I create my indexes to speed up lookups
│   └── insert_data.sql       -- Where I load my sample dataset
├── validation/
│   └── validate_data.sql     -- My verification scripts to count rows and check my tables
├── Section_A/
│   └── basic_queries.sql     -- My answers to the basic SQL questions (Q1 - Q6)
├── Section_B/
│   └── filtering_queries.sql -- My filtering and optimization solutions (Q7 - Q12)
├── Section_C/
│   └── aggregation_queries.sql -- My group by and aggregate query answers (Q13 - Q18)
├── Section_D/
│   └── joins_queries.sql     -- My multi-table join and constraint queries (Q19 - Q23)
├── Section_E/
│   └── advanced_queries.sql  -- My conditional logic, ACID theory, and transaction blocks (Q24 - Q27)
├── results/                  -- The directory where I stored all query result tables
│   ├── Section_A_results.txt
│   ├── Section_B_results.txt
│   ├── Section_C_results.txt
│   ├── Section_D_results.txt
│   └── Section_E_results.txt
└── README.md                 -- This README document
```

---

## 🛠️ My Database Schema & Table Constraints

I created 4 relational tables inside my database:

### 1. `customers`
Stores all my customer profile information, their city/state locations, and premium membership status.
* **Primary Key:** `customer_id`
* **Unique Key:** `email`
* **My Indexes:** `idx_customers_city` (city-based filters), `idx_customers_state` (state-based filters)

### 2. `products`
Holds the catalog details for the products.
* **Primary Key:** `product_id`
* **My Check Constraints:** I made sure `unit_price > 0` and `stock_qty >= 0` so no negative numbers get in.
* **My Indexes:** `idx_products_category` (category-based filters)

### 3. `orders`
Contains my high-level order transactions.
* **Primary Key:** `order_id`
* **Foreign Key:** `customer_id` referencing `customers`
* **My Check Constraints:** I restricted `status` to only ('Pending','Shipped','Delivered','Cancelled') and verified `total_amount >= 0`.
* **My Indexes:** `idx_orders_date` (date-based sorting), `idx_orders_status` (status filters)

### 4. `order_items`
Tracks the individual item rows linked to orders.
* **Primary Key:** `item_id`
* **Foreign Keys:** `order_id` (pointing to orders), `product_id` (pointing to products)
* **My Check Constraints:** I ensured `quantity > 0`, `unit_price > 0`, and `discount_pct` is between 0 and 100.

---

## 🔗 Entity Relationships

```text
 customers ──(1:N)──▶ orders
 orders ──(1:N)──▶ order_items
 products ──(1:N)──▶ order_items
```

---

## 🚀 How I Set Up and Ran My SQL Scripts

All my queries are written in clean, standard SQL. You can execute them on PostgreSQL, MySQL, or SQLite.

### My Recommended Steps:

1. **Create the Database:** Run `database/create_database.sql` to initialize the database schema.
2. **Create the Tables:** Run `database/create_tables.sql` to define the tables and constraints.
3. **Build the Indexes:** Run `database/create_indexes.sql` to speed up operations.
4. **Load my Sample Data:** Run `database/insert_data.sql` to fill all tables.
5. **Verify data:** Run `validation/validate_data.sql` to ensure the correct number of rows were created.

---

## 📝 Key Concepts I Explained in this Task

* **Indexing & SARGability:** I explained how B-Tree indexes speed up lookups. I also demonstrated why using functions on indexed columns (like `YEAR(join_date) = 2024`) blocks index use and rewrote the query to be SARGable.
* **LEFT JOIN vs. RIGHT JOIN:** I detailed how left joins retain all records from the left side and match on the right, whereas right joins do the opposite.
* **ACID Transactions:** I broke down what Atomicity, Consistency, Isolation, and Durability mean in real-world terms (using a bank transfer example) and wrote a transaction block to handle safe inventory updates and order inserts atomically.
