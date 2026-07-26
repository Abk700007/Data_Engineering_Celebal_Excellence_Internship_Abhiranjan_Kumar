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

### **Q7: How does Spark use the Lineage Graph (DAG) to provide fault tolerance if a worker node fails?**

Spark does not rely on expensive data replication across multiple machines for fault tolerance. Instead, it tracks the history of all transformations used to build a DataFrame inside a **Directed Acyclic Graph (DAG)** or **Lineage Graph**.

If a worker node fails and a partition of data is lost:
1.  Spark's Driver identifies which partition went missing.
2.  It traces back through the Lineage Graph to determine the exact sequence of transformations that created that lost partition.
3.  It schedules a new task on a healthy executor to recompute *only* that missing partition from the original source or the nearest cached/checkpointed stage.

This logical reconstruction makes Spark highly resilient with minimal storage overhead.

---

### **Q8: Write a query to filter a DataFrame df_orders for rows where the status is 'Completed' AND the amount is greater than 1000.**

```python
from pyspark.sql.functions import col

completed_high_value = df_orders.filter(
    (col("status") == "Completed") & (col("amount") > 1000)
)
```

> [!NOTE]
> In PySpark, when combining conditions using logical operators like `&` (AND) or `|` (OR), you **must** wrap each condition in parentheses to prevent operator precedence issues.

---

### **Q9: Explain the concept of Predicate Pushdown in Parquet and how it affects the amount of data loaded into memory.**

**Predicate Pushdown** is an optimization where filter conditions (predicates) are pushed down directly to the storage layer (the Parquet reader) during the file scan operation.

Parquet files divide data into row groups and store summary statistics (such as `min_value` and `max_value`) for each column inside the file footer.
1.  When Spark processes a query with a filter (e.g., `df.filter(col("price") > 1000)`), it pushes this filter down.
2.  The Parquet reader checks the `min`/`max` metadata of each row group before reading.
3.  If a row group's `max_value` for `price` is less than 1000, Spark skips reading, loading, and decompressing that row group entirely.

This prevents loading irrelevant blocks of data from disk into Spark's executor memory, drastically reducing network I/O, CPU cycles, and memory footprint.

---

### **Q10: Write a code snippet to add a new column final_price which is the base_price multiplied by 1.18 (18% tax).**

```python
from pyspark.sql.functions import col, round as spark_round

df_with_tax = df.withColumn(
    "final_price", 
    spark_round(col("base_price") * 1.18, 2)
)
```

Here, `withColumn()` is used to instantiate the new column, and `spark_round` ensures the calculated decimal values are rounded to 2 decimal places for financial reporting.

---

### **Q11: What is the difference between Transformations and Actions? Provide two examples of each.**

*   **Transformations:** Lazily evaluated operations that define how to build a new DataFrame from an existing one. They do not trigger computations immediately but compile a lineage graph.
    *   *Narrow Transformations:* Do not require data shuffling across partitions (e.g., `filter()`, `select()`, `withColumn()`).
    *   *Wide Transformations:* Require data to be shuffled across nodes (e.g., `groupBy()`, `join()`, `distinct()`).
*   **Actions:** Eagerly evaluated operations that trigger the execution of all recorded transformations (the DAG lineage) to produce a final value or output.
    *   *Examples:* `show()`, `count()`, `collect()`, `write()`.

---

### **Q12: Write the Spark command to load a Parquet file from "path/to/input", filter out any rows where user_id is null, and save the result as a CSV at "path/to/output".**

```python
from pyspark.sql.functions import col

# 1. Load Parquet file
df = spark.read.parquet("path/to/input")

# 2. Filter out null user_id rows
filtered_df = df.filter(col("user_id").isNotNull())

# 3. Save as CSV
filtered_df.write.mode("overwrite") \
                 .option("header", True) \
                 .csv("path/to/output")
```

---

### **Q13: In Spark Architecture, what is the difference between Client Mode and Cluster Mode?**

The difference depends on **where the Driver process runs**:

*   **Client Mode:**
    *   The Driver process runs locally on the host machine that submitted the job (e.g., your laptop, or an edge gateway node).
    *   Executors run on the worker nodes in the cluster.
    *   *Use Case:* Best for interactive environments, notebooks (Jupyter, Zepplin), and debugging where console outputs must be reviewed in real-time.
    *   *Risk:* If the host machine disconnects or powers down, the entire Spark job fails immediately.
*   **Cluster Mode:**
    *   The Driver process is scheduled and runs inside an application master container *directly on one of the worker nodes* in the cluster.
    *   Executors run on other worker nodes in the cluster.
    *   *Use Case:* Best for production workloads, cron scheduler jobs, and batch jobs.
    *   *Advantage:* Once submitted, the local submission terminal can disconnect, and the job will execute independently to completion.

---

### **Q14: Write a query to filter a dataset for rows where the region is 'North' OR the priority is 'High'.**

```python
from pyspark.sql.functions import col

filtered_df = df.filter(
    (col("region") == "North") | (col("priority") == "High")
)
```

---

### **Q15: When exploring a dataset, why is it safer to use .show(5) instead of .collect() on a multi-terabyte dataset?**

*   **`collect()` is dangerous:** It pulls *every single row* of the distributed DataFrame from all executors across the cluster and brings it back to the Driver process as a single in-memory collection. If the dataset is multi-terabyte, this will instantly exceed the driver’s memory limits, causing an **Out-Of-Memory (OOM) crash** and disrupting the application.
*   **`show(5)` is safe:** It only requests the first 5 records from Spark. Spark utilizes short-circuit execution: executors only process and send a small subset of partitions containing enough data to produce the first 5 rows. The Driver receives a negligible amount of data, keeping it safe and fast.
