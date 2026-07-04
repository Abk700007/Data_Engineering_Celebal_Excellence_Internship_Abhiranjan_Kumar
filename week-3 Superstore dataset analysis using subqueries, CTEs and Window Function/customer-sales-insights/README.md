# Customer Sales Insights - Week 3 SQL Assignment

## Project Overview
This repository contains the database schema, staging environment, data ingestion pipeline outline, and advanced analytics templates for the Week 3 Data Engineering SQL assignment. The primary goal of this project is to analyze customer purchasing behavior, order details, and product dimensions using advanced SQL queries to derive actionable business insights from the Superstore dataset.

---

## Dataset
The project analyzes the **Superstore Dataset** (`Superstore.csv`), which contains comprehensive details on:
- **Customers**: Demographics, identifiers, customer names, and segments.
- **Orders**: Sales value, transaction quantities, discounts, profit metrics, and order timelines.
- **Products**: Product catalog information, category, sub-category, and names.

---

## Objectives
1. **Data Ingestion and Schema Normalization**:
   - Establish a staging table (`superstore_raw`) to import the raw transactional CSV records.
   - Design and build clean, normalized relational tables: `customers`, `orders`, and `products` using integrity-preserving SQL mappings.
2. **Advanced Analytics and Question Resolution**:
   - Utilize subqueries to identify outstanding sales orders and filtering limits.
   - Implement Common Table Expressions (CTEs) for multi-tiered customer sales summaries.
   - Leverage Window Functions to perform ranking, cumulative sequencing, and customer segmentation.
3. **Mini Project - Customer Sales Insights**:
   - Aggregate sales across dimensions to answer executive business questions like identifying top/bottom performers, single-order customers, and highest order values.

---

## Key Business Insights
The resolved database queries yield the following executive findings on customer purchasing patterns:
- **Revenue Driver**: **Sean Miller** is the highest-value customer by a large margin, with a total spending of **$25,043.05**, including a single peak transaction of **$23,661.23**.
- **Customer Tiers**: The average customer lifetime value across the dataset is **$2,897.43**. High-spending customers like **Tamara Chand ($19,052.22)** and **Raymond Buch ($15,117.34)** stand out as core targets for loyalty campaigns.
- **Transactional Behavior**: A segment of users (such as **Anthony O'Donnell** and **Carl Jackson**) are single-order customers, presenting direct opportunities for secondary marketing engagement to prompt repeat purchases.
- **Top Individual Deals**: Individual transaction analysis shows that highest-value orders are driven by furniture and technology categories, led by Sean Miller's purchase of Cisco TelePresence units.

---

## SQL Concepts Used
- **Database Schema Definition**: Data Definition Language (DDL) for establishing clean primary and foreign key constraints.
- **Data Insertion and Deduping**: Utilizing `SELECT DISTINCT` to transform flat raw transactional data into normalized dimensional tables.
- **Subqueries**: Both correlated and uncorrelated subqueries for advanced filtering against calculated statistical values (e.g., average sales).
- **Common Table Expressions (CTEs)**: Restructuring queries for modular readability, isolation of intermediate aggregation logic, and code maintenance.
- **Window Functions**: Performing mathematical and statistical rankings using functions such as `ROW_NUMBER()`, `RANK()`, and `DENSE_RANK()` alongside custom partitioning schemes (`PARTITION BY`).
- **Complex JOIN Operations**: Integrating fact and dimension tables across CTE steps and window operations to build final unified reporting datasets.

---

## Folder Structure
```text
customer-sales-insights/
├── data/
│   ├── Sample - Superstore.csv   # Raw dataset
│   ├── superstore.db             # Generated SQLite database
│   └── verify_db.py              # Python automation pipeline script
├── sql/
│   ├── create_tables.sql         # Resolved DDL schemas for database and tables
│   ├── insert_data.sql           # Resolved DML operations for ingestion & validation
│   └── advanced_queries.sql      # Resolved Advanced SQL queries, CTEs, and window functions
├── mini project/
│   └── mini_project.sql          # Executed query outputs and insights for Mini Project
├── results/
│   └── result.sql                # Executed query outputs and insights for main assignment
└── README.md                     # Project documentation
```

---

## Getting Started
1. **Automated Pipeline Execution**:
   - Run the python verification pipeline:
     ```bash
     python "data/verify_db.py"
     ```
   - This script will automatically create `data/superstore.db`, load the `Sample - Superstore.csv` dataset, apply all DDL/DML transformations, and output the executed query results to `results/result.sql` and `mini project/mini_project.sql`.
2. **DDL Schemas**: Run [create_tables.sql](file:///d:/Users/LENOVO/Desktop/Celebal/week%203-%20superstore%20data%20analysis%20using%20subqueries,CTE%20and%20window%20functions/customer-sales-insights/sql/create_tables.sql) to define schemas manually.
3. **Data Populating**: Run [insert_data.sql](file:///d:/Users/LENOVO/Desktop/Celebal/week%203-%20superstore%20data%20analysis%20using%20subqueries,CTE%20and%20window%20functions/customer-sales-insights/sql/insert_data.sql) to clean and insert row-records into destination tables.
4. **Assignment Queries**: Open [advanced_queries.sql](file:///d:/Users/LENOVO/Desktop/Celebal/week%203-%20superstore%20data%20analysis%20using%20subqueries,CTE%20and%20window%20functions/customer-sales-insights/sql/advanced_queries.sql) to review and execute the analytical queries.
5. **Results & Insights**: Review the parsed outputs inside [result.sql](file:///d:/Users/LENOVO/Desktop/Celebal/week%203-%20superstore%20data%20analysis%20using%20subqueries,CTE%20and%20window%20functions/customer-sales-insights/results/result.sql) and [mini_project.sql](file:///d:/Users/LENOVO/Desktop/Celebal/week%203-%20superstore%20data%20analysis%20using%20subqueries,CTE%20and%20window%20functions/customer-sales-insights/mini%20project/mini_project.sql).
