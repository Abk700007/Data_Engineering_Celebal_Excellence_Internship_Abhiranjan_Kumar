# Spark Concepts — Questions & Answers
**Week 6 Data Engineering Assessment — Celebal Technologies**

This document contains detailed answers to the 15 concept and code-based questions assigned for the Week 6 Spark Assessment.

---

### **Q1: Explain the roles of the Driver, Cluster Manager, and Executor in a Spark application.**

Think of a Spark application like a construction project:

*   **Driver (The Site Manager):** The process that runs the `main()` function of your application. It creates the `SparkSession`, builds the execution plan (the DAG/Lineage Graph), and coordinates work distribution. It does not perform the heavy computational tasks itself; rather, it breaks the job into smaller tasks and schedules them.
*   **Cluster Manager (The Staffing Agency):** Responsible for allocating physical cluster resources (CPU cores and memory) to the Spark application. Spark can run on several cluster managers:
    *   *Standalone:* Spark's built-in simple cluster manager.
    *   *Hadoop YARN:* The resource manager for Hadoop clusters.
    *   *Apache Mesos:* A general cluster manager.
    *   *Kubernetes:* A container orchestration platform.
*   **Executors (The Construction Workers):** Worker processes running on cluster nodes. They are responsible for executing the individual tasks assigned by the Driver, storing computed data in memory or on disk (caching), and reporting status/results back to the Driver.

---

### **Q2: How does Spark’s Lazy Evaluation strategy improve performance when chain-processing large datasets?**

When you call transformations (like `filter()`, `select()`, `withColumn()`, or `join()`), Spark does not execute them immediately. Instead, it records them as logical instructions in a **Lineage Graph (DAG)**. Execution is deferred until a concrete **Action** (like `show()`, `count()`, or `write()`) is called.

**Why this improves performance:**
1.  **Catalyst Optimizer Planning:** Since Spark has the complete sequence of instructions beforehand, its Catalyst Optimizer can inspect and optimize the entire query plan globally rather than executing each step sequentially.
2.  **Filter/Predicate Pushdown:** Spark can push filters down to the data source so that only relevant records are read from disk.
3.  **Column Pruning:** Spark skips loading columns that are not used downstream.
4.  **Task Merging (Pipelining):** Spark can group multiple narrow transformations into a single execution stage, eliminating the need to write intermediate results to disk or transfer them over the network.

---

### **Q3: Write a Spark command to read a CSV file located at "data/source.csv", ensuring the first row is treated as a header and inferSchema is enabled.**

```python
df = spark.read.csv(
    "data/source.csv", 
    header=True, 
    inferSchema=True
)
```

*   `header=True` instructs Spark to treat the first row of the CSV file as the column headers.
*   `inferSchema=True` forces Spark to scan the CSV once to automatically detect and assign the data type (Integer, Double, Boolean, etc.) of each column, rather than loading everything as String types.

---

### **Q4: What is the difference between CSV and Parquet in terms of storage (row-based vs. columnar) and why does it matter for performance?**

| Feature | CSV (Comma-Separated Values) | Apache Parquet |
| :--- | :--- | :--- |
| **Storage Model** | **Row-based:** Records are stored line-by-line. To read a single column, all columns in the row must be scanned. | **Columnar:** Values from the same column are stored together in contiguous blocks. |
| **Schema Support** | Plain text; schema is not preserved. Must be inferred or provided on read. | Self-describing; schema and data types are saved directly in file metadata. |
| **Compression** | Poor (plain text); compression can only be applied to the whole file. | Excellent; per-column compression (e.g., Snappy, Gzip) utilizing value-similarity. |
| **Column Pruning** | No; full rows must always be read into memory. | Yes; only columns requested in `select()` are read from disk. |
| **Predicate Pushdown**| No; all records must be parsed before filtering. | Yes; skips reading blocks using min/max stats stored in metadata. |

**Why it matters for performance:** Parquet reduces disk I/O, minimizes memory footprints, compresses data up to 10x better than CSV, and speeds up analytical queries by orders of magnitude on large datasets.

---

### **Q5: Given a DataFrame df, write a query to select the columns product_id and price where the category is 'Electronics'.**

```python
from pyspark.sql.functions import col

# Recommended Approach (Using functions.col)
electronics_df = df.filter(col("category") == "Electronics") \
                   .select("product_id", "price")

# Alternative syntax using DataFrame references
# electronics_df = df.filter(df.category == "Electronics").select("product_id", "price")

electronics_df.show()
```

---

### **Q6: Write the code to "revise" a DataFrame by renaming the column old_name to new_name and casting the price column from a String to a Double.**

```python
from pyspark.sql.functions import col
from pyspark.sql.types import DoubleType

revised_df = df.withColumnRenamed("old_name", "new_name") \
               .withColumn("price", col("price").cast(DoubleType()))

# Alternatively, using string shortcut for casting:
# revised_df = df.withColumnRenamed("old_name", "new_name").withColumn("price", col("price").cast("double"))
```

---

