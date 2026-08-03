# Delta Lake Integration & Slowly Changing Dimensions (SCD) — Week 7 Assignment

## Intern Details
* **Name:** Abhiranjan Kumar
* **Institution:** ITER (SOA University)
* **Organization:** Celebal Technologies (Celebal Excellence Internship)
* **Track:** Data Engineering
* **Topic:** Delta Lake Architecture, PySpark Integration & Slowly Changing Dimensions (SCD Type 1 & Type 2)

---

## Project Overview
For the Week 7 Delta Lake Assessment in the Celebal Technologies Internship, I focused on building and documenting a modern Data Lakehouse pipeline. This pipeline leverages the robust transaction layer of **Delta Lake** to handle data consistency and record state management. 

Specifically, this project demonstrates how to implement **Slowly Changing Dimensions (SCD) Type 1 and Type 2** using PySpark and Delta Table APIs. These patterns are essential for maintaining accurate dimensions in analytical data warehouses, enabling teams to choose between overwriting data (Type 1) and tracking historical changes over time (Type 2).

---

## 📂 Project Structure
The folder is organized as follows:

```text
week-7 delta-lake-assignment/
├── notebooks/
│   └── delta_lake_scd.ipynb          -- PySpark Jupyter Notebook implementing SCD Type 1 & Type 2
├── report/
│   └── delta_lake_report.md          -- Summary report answering conceptual questions and pipeline details
├── data/
│   └── delta/
│       └── customer_table/           -- Delta table storage location on disk
│           └── _delta_log/           -- ACID transaction logs (.json commit files)
└── screenshots/                      -- Step-by-step execution checkpoints
    ├── data_loading/                 -- Initial ingestion of raw customer records into Delta format
    ├── data_cleaning/                -- Cleaned DataFrames, schema casting, and null handling
    ├── scd1/                         -- Results and physical/logical execution of SCD Type 1 upserts
    ├── scd2/                         -- History tracking, active/inactive flags, and SCD Type 2 results
    ├── validation/                   -- Schema validation, history queries, and time travel checks
    └── final_output/                 -- Query outputs from the final customer dimension table
```

---

## 🎯 Objectives & What I Learned

1. **Delta Lake Core Architecture:** Explored how Delta Lake brings **ACID Transactions**, **Schema Enforcement & Evolution**, **Unified Batch & Streaming**, and **Time Travel** to standard Apache Spark data lakes.
2. **Under-the-Hood Logging:** Analyzed the `_delta_log` directory to see how JSON transaction logs maintain the single source of truth for table state.
3. **Slowly Changing Dimensions (SCD) Theory:**
   * **SCD Type 1 (No History):** Overwrites existing record attributes when updates occur. It is used when historical tracking is unnecessary (e.g., fixing spelling mistakes, correcting minor errors).
   * **SCD Type 2 (Full History):** Maintains historical tracking by end-dating the older record (marking it inactive) and inserting a new active record with a new start date.
4. **PySpark Delta Table API:** Applied the programmatic `DeltaTable.merge()` API in PySpark to express complex conditional upsert logic.
5. **Time Travel Operations:** Queried historical snapshots of the Delta table using versioning (`versionAsOf`) and timestamping (`timestampAsOf`).

---

## 🚀 Walkthrough of Steps & Implementations

### Step 1: Initializing Spark Session with Delta Lake support
To enable Delta Lake APIs and catalogs, the local Spark session is configured with Delta packages and Spark SQL catalog extensions.
```python
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = SparkSession.builder \
    .appName("Week7_Delta_Lake_SCD") \
    .master("local[*]") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

spark = configure_spark_with_delta_pip(builder).getOrCreate()
```

### Step 2: Initial Ingestion & Data Cleaning
* Loaded the raw customer dataset.
* Performed standard transformations: cast customer identifiers, trimmed whitespace, and filled null fields with default values.
* Saved the base table to disk in Delta format.
```python
# Write as Delta Table
df_clean.write.format("delta").mode("overwrite").save("data/delta/customer_table")
```

### Step 3: Implementing SCD Type 1 (Overwrite updates)
In SCD Type 1, when a record's attributes change, we overwrite the existing values.
* **Match Condition:** `target.customer_id == source.customer_id`
* **Action:** Update all columns in target with source values.
* **Non-Match Action:** Insert the new record.

```python
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "data/delta/customer_table")

# Perform SCD Type 1 Upsert
deltaTable.alias("target") \
    .merge(
        source_df.alias("source"),
        "target.customer_id = source.customer_id"
    ) \
    .whenMatchedUpdate(set={
        "customer_name": "source.customer_name",
        "email": "source.email",
        "phone": "source.phone",
        "city": "source.city",
        "last_updated": "current_timestamp()"
    }) \
    .whenNotMatchedInsert(values={
        "customer_id": "source.customer_id",
        "customer_name": "source.customer_name",
        "email": "source.email",
        "phone": "source.phone",
        "city": "source.city",
        "last_updated": "current_timestamp()"
    }) \
    .execute()
```

### Step 4: Implementing SCD Type 2 (History Tracking)
SCD Type 2 keeps all historical iterations of a record. It requires tracking columns like `is_current`, `start_date`, and `end_date`.
When a change occurs:
1. **End-date** the current active record in the target (set `is_current = False`, `end_date = current_date`).
2. **Insert** the new record with `is_current = True`, `start_date = current_date`, and `end_date = Null`.

This is implemented using a **one-pass merge** by joining the source DataFrame with a subquery of the target, or by doing a merge that handles multiple actions.

#### PySpark One-Pass Merge Pattern:
```python
# 1. Identify modified rows that need to be updated/inserted
# 2. Join source and target to create a merge source DataFrame
# 3. Perform merge with insert and update statements

# Prepare updates dataframe with null keys for the insert records
updates_df = source_df.join(target_df.filter("is_current = true"), "customer_id", "inner") \
    .filter("source.city != target.city OR source.email != target.email")

# Combine source and updates (marked with null keys to force insert)
staged_df = source_df.unionByName(
    updates_df.withColumn("customer_id", lit(None))
)

# Merge operation
deltaTable.alias("target") \
    .merge(
        staged_df.alias("source"),
        "target.customer_id = source.customer_id AND target.is_current = true"
    ) \
    .whenMatchedUpdate(
        condition="target.city != source.city OR target.email != source.email",
        set={
            "is_current": "false",
            "end_date": "current_date()"
        }
    ) \
    .whenNotMatchedInsert(values={
        "customer_id": "source.customer_id",
        "customer_name": "source.customer_name",
        "email": "source.email",
        "phone": "source.phone",
        "city": "source.city",
        "start_date": "current_date()",
        "end_date": "lit(None)",
        "is_current": "true"
    }) \
    .execute()
```

### Step 5: History Audit & Time Travel
Delta Lake's built-in transaction log enables querying older snapshots of tables:
```python
# Check version history
history_df = deltaTable.history()
history_df.select("version", "timestamp", "operation", "operationParameters").show(truncate=False)

# Time travel: read version 1
df_v1 = spark.read.format("delta").option("versionAsOf", 1).load("data/delta/customer_table")
df_v1.show()
```

---

## 📊 Key Insights & Verification

### 1. ACID Transaction Logs (`_delta_log`)
Each transaction (write, update, merge) creates a commit file in `_delta_log/` (e.g., `00000000000000000000.json`). These files list the exact files added or removed during that transaction, ensuring atomicity and consistency.

### 2. Performance & Maintenance
Delta Lake provides specific SQL utilities for long-term health:
* **OPTIMIZE:** Compacates small files into larger files to speed up reader performance.
* **VACUUM:** Safely deletes old data files that are no longer referenced in the latest transaction logs (by default, older than 7 days).

---

## ⚙️ How to Setup and Run
1. **Prerequisites:**
   * Python 3.8+
   * Java (JDK 8 or 11) configured under `JAVA_HOME`.
   * Apache Spark 3.x configured locally.
2. **Install Delta Spark library:**
   ```bash
   pip install pyspark delta-spark jupyter
   ```
3. **Execute Pipeline:**
   Launch Jupyter Notebook:
   ```bash
   jupyter notebook notebooks/delta_lake_scd.ipynb
   ```
   Run all cells sequentially to ingest the raw files, perform the SCD Type 1 & Type 2 transformations, and inspect the resulting transaction logs and history.
