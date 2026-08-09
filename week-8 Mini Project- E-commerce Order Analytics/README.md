# Week 8 Mini Project: E-Commerce Order Analytics System

A comprehensive, end-to-end Python & SQL analytical system that generates mock e-commerce datasets with realistic data quality issues, cleans them using `pandas` and standard Python logic, imports them into a SQLite database with strict integrity constraints, and performs basic, intermediate, and advanced database analytics (window functions, cohort analysis, cumulative distributions, and Year-over-Year tracking).

---

## Project Architecture & Directory Structure

```text
week-8 Mini Project- E-commerce Order Analytics/
├── data/
│   ├── raw/                      # Messy, generated CSV datasets
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   └── cleaned/                  # Cleaned, standardized CSV datasets
│       ├── customers_clean.csv
│       ├── products_clean.csv
│       ├── orders_clean.csv
│       └── order_items_clean.csv
│
├── database/
│   └── ecommerce.db              # SQLite Database file
│
├── sql/
│   ├── schema.sql                # Table definitions & constraints
│   ├── aggregations.sql          # Basic & Intermediate queries (Q1-Q6)
│   ├── window_functions.sql      # Window function queries (Q7-Q9B)
│   └── cohort_analysis.sql       # Complex CTEs & Cohort queries (Q10-Q16)
│
├── scripts/
│   ├── generate_data.py          # Python mock data generator
│   ├── clean_data.py             # Data quality checks & cleaning
│   ├── database.py               # Schema setup and database loader
│   ├── report_cli.py             # CLI reporting tool with YoY metrics
│   ├── run_sql.py                # Runner for Basic/Intermediate queries
│   ├── run_window_queries.py     # Runner for Window function queries
│   └── run_advanced_queries.py   # Runner for CTEs & Cohorts
│
└── tests/
    └── test_edge_cases.py        # Test suite for Part 5 constraints
```

---

## Data Schema & Integrity Constraints

The system uses a relational model with foreign key enforcement (`PRAGMA foreign_keys = ON`) and SQLite check constraints:

* **`customers`**: Unique `customer_id` (PK), name, email, registration date, and `customer_type` checked to be either `REGULAR`, `PREMIUM`, or `VIP`.
* **`products`**: Unique `product_id` (PK), name, category, subcategory, and cost price.
* **`orders`**: Unique `order_id` (PK), referencing `customer_id` (FK), order date, status, and region code.
* **`order_items`**: Unique `item_id` (PK), referencing `order_id` (FK) and `product_id` (FK), quantity (negative represents returns), unit price, and a check constraint enforcing `discount_percent` to be between `0` and `100`.

---

## How to Run the Pipeline

Follow these steps sequentially to run the entire data pipeline:

### 1. Generate Raw Data
Generates 600 customers, 600 products, 1500 orders, and 3000 order items with simulated issues (3% negative quantities, 2% bad emails, 5% missing customer IDs, incorrect dates):
```bash
python scripts/generate_data.py
```

### 2. Clean and Standardize Data
Trims extra spaces, converts product names to Title Case, validates emails, checks referential integrity, flags future dates and zero quantities, and writes a detailed report to `output/data_quality_report.txt`:
```bash
python scripts/clean_data.py
```

### 3. Load Database Schema and Import Data
Creates database tables with constraint checks and loads the cleaned datasets:
```bash
python scripts/database.py
```

### 4. Run SQL Queries
You can run the script files to execute the SQL analysis and print the outputs directly:
```bash
# Run Basic & Intermediate Queries (Q1-Q6)
python scripts/run_sql.py

# Run Window Function Queries (Q7-Q9B)
python scripts/run_window_queries.py

# Run Advanced CTE & Cohort Queries (Q10-Q16)
python scripts/run_advanced_queries.py
```

### 5. Run the Interactive CLI Report Tool
Generates reports with metrics compared directly to the previous equivalent duration:
```bash
python scripts/report_cli.py
```

### 6. Run the Test Suite
Executes the edge-case validation tests (e.g., verifying foreign key violations, discount constraint bounds, zero quantities, and future dates):
```bash
python tests/test_edge_cases.py
```
