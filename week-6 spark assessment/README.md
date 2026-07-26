# Spark Data Processing & Optimization — Week 6 Assignment

## Intern Details
* **Name:** Abhiranjan Kumar
* **Institution:** ITER (SOA University)
* **Organization:** Celebal Technologies (Celebal Excellence Internship)
* **Track:** Data Engineering
* **Topic:** Apache Spark Architecture, PySpark DataFrames & Performance Optimization

---

## Project Overview
For the Week 6 Spark Assessment in the Celebal Technologies Internship, I worked on implementing an end-to-end PySpark data engineering pipeline that showcases Spark's key architectural concepts, transformations, lazy evaluation model, and storage format efficiencies. The project processes a sample retail/e-commerce dataset to demonstrate schema enforcement, missing data curation, complex conditional filtering, custom calculations, and aggregation. 

Additionally, it provides deep analysis and validation of advanced Spark optimization features, including **Narrow vs. Wide Transformations (Shuffles)** and **Predicate Pushdown on Columnar Parquet Storage**.

---

## 📂 Project Structure
The folder is organized as follows:

```text
week-6 spark assessment/
├── Questions_and_Answers/
│   ├── Spark_Concepts_QA.pdf       -- Formal PDF answering the 15 LMS conceptual questions
│   └── Spark_Concepts_QA.md        -- Markdown edition of the 15 Q&As for direct Git reading
├── notebook/
│   └── spark_data_processing.ipynb -- Python Jupyter Notebook containing the full executed PySpark pipeline
├── data/
│   └── source.csv                  -- Messy input retail/e-commerce CSV dataset (20 rows, including null values)
├── output/
│   ├── processed_csv/              -- Final cleaned and transformed dataset saved in CSV format (coalesced)
│   └── processed_parquet/          -- Final cleaned and transformed dataset saved in Snappy-compressed Parquet format
├── results/
│   ├── execution_results.md        -- Detailed log of printed outputs from every stage of execution
│   └── screenshots/                -- Proof of execution outputs (Spark UI session, DataFrames, schema, plans)
│       ├── spark_session.png
│       ├── schema_output.png
│       ├── dataframe_show.png
│       ├── transformation_results.png
│       ├── csv_output.png
│       └── parquet_output.png
└── insights/
    └── performance_insights.md     -- Conceptual deep-dives into Spark performance, shuffles, and storage formats
```

---

## 🎯 Objectives & What I Learned

1. **Spark Architecture Foundations:** Deepened my understanding of the relationship between the **Driver** (coordinator and plan generator), the **Cluster Manager** (resource allocator), and the **Executors** (distributed execution workers), and contrasted **Client Mode** vs. **Cluster Mode** deployments.
2. **Lazy Evaluation & DAG Lineage:** Learned how Spark defers executing operations until an **Action** is invoked, building a **Directed Acyclic Graph (DAG)** that provides implicit fault tolerance (recomputing lost partitions) and query optimization.
3. **Robust Schema Enforcement:** Applied both `inferSchema` and explicit `StructType` schema validation, explaining why explicit schemas are a production best practice.
4. **Data Cleansing Pipelines:** Built robust null-handling rules (filtering out rows missing core identifiers and filling secondary attributes with defaults).
5. **Data Manipulation & Querying:** renaming columns, type casting, filtering with logical operations (`AND`/`OR`), and adding tax-derived calculations.
6. **Narrow vs. Wide Transformations:** Identified shuffle boundaries caused by wide transformations (`groupBy().agg()`) and analyzed the wall-clock times.
7. **Storage Format Efficiency:** Compared row-based (CSV) and columnar (Parquet) storage layouts, demonstrating Parquet's superior compression and **Predicate Pushdown** filter optimizations.

---

## 🚀 Walkthrough of Steps Implemented

The PySpark pipeline inside [spark_data_processing.ipynb](file:///d:/Users/LENOVO/Desktop/Celebal/week-6%20spark%20assessment/notebook/spark_data_processing.ipynb) executes the following operations:

### Step 1: Initializing Spark Session
A local `SparkSession` is initialized, setting a master configuration of `local[*]` to utilize all available CPU cores. Default shuffle partitions are tuned to `4` (since it's a small dataset, avoiding the default `200` partition overhead).
```python
spark = SparkSession.builder \
    .appName("Week6_Spark_Data_Processing") \
    .master("local[*]") \
    .config("spark.sql.shuffle.partitions", "4") \
    .getOrCreate()
```

### Step 2: Data Loading & Schema Handling
*   **Inferring Schema:** Read `source.csv` with `inferSchema=True` to observe Spark's automatic type deduction.
*   **Explicit Schema:** Defined and enforced a strict `StructType` schema. This avoids the secondary file scan that schema inference requires and ensures metadata safety.
```python
explicit_schema = StructType([
    StructField("product_id", IntegerType(), True),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("region", StringType(), True),
    StructField("priority", StringType(), True),
    StructField("status", StringType(), True),
])
df = spark.read.csv("../data/source.csv", header=True, schema=explicit_schema)
```

### Step 3: Missing Value Audit & Cleaning
*   Identified null occurrences: `price` had 2 nulls, and `quantity` had 3 nulls.
*   **Cleaning Logic:** Dropped records missing the critical `price` field (a business requirement) and filled missing `quantity` values with `0`. The row count adjusted from 20 to 18 rows.
```python
df_clean = df.dropna(subset=["price"]).fillna({"quantity": 0})
```

### Step 4: Row Filtering & Column Selection
*   Filtered the dataset for the `'Electronics'` category.
*   Selected only the `product_id` and `price` fields to illustrate column selection.
```python
electronics_df = df_clean.filter(col("category") == "Electronics")
selected_df = electronics_df.select("product_id", "price")
```

### Step 5: Column Renaming & Type Casting
*   Renamed `product_name` to `item_name` and `price` to `unit_price`.
*   Cast `unit_price` to `DoubleType` and `product_id` to `StringType` to satisfy the schema adjustment requirements.
```python
renamed_df = df_clean.withColumnRenamed("product_name", "item_name") \
                      .withColumnRenamed("price", "unit_price")
casted_df = renamed_df.withColumn("unit_price", col("unit_price").cast(DoubleType())) \
                       .withColumn("product_id", col("product_id").cast(StringType()))
```

### Step 6: Column Additions (Derived Fields)
*   Added `final_price` computed as `unit_price * 1.18` (18% tax) and rounded to 2 decimal points.
*   Added `category_upper` to normalize product categories to uppercase.
```python
final_df = renamed_df.withColumn("final_price", spark_round(col("unit_price") * 1.18, 2)) \
                      .withColumn("category_upper", upper(col("category")))
```

### Step 7: Multi-Condition Filtering (AND / OR)
*   **AND Filtering:** Filtered for orders where status is `'Completed'` **AND** final price is greater than `1000`.
*   **OR Filtering:** Filtered for records where region is `'North'` **OR** priority is `'High'`.
```python
high_value_completed = final_df.filter((col("status") == "Completed") & (col("final_price") > 1000))
priority_or_region = final_df.filter((col("region") == "North") | (col("priority") == "High"))
```

### Step 8: Wide Transformation & Grouped Aggregations
*   Grouped the cleaned records by `category` and calculated the total quantity sold and average final price.
*   This triggers a **shuffle stage** (wide transformation) because rows representing categories must be gathered across partitions.
```python
agg_df = final_df.groupBy("category") \
                  .agg({"final_price": "avg", "quantity": "sum"}) \
                  .withColumnRenamed("avg(final_price)", "avg_final_price") \
                  .withColumnRenamed("sum(quantity)", "total_quantity")
```

### Step 9: Writing Output in Optimized Formats
*   **CSV Writing:** Coalesced to a single partition (`coalesce(1)`) to output a single, readable CSV file (for demo convenience).
*   **Parquet Writing:** Saved the output in snappy-compressed columnar Parquet format.
```python
final_df.coalesce(1).write.mode("overwrite").option("header", True).csv("../output/processed_csv")
final_df.write.mode("overwrite").parquet("../output/processed_parquet")
```

---

## 📊 Key Execution Results & Optimization Insights

### 1. CSV vs. Parquet Size Comparison
At small scale (18 rows), the metadata and column-chunk header overhead makes Parquet larger on disk than CSV:
*   **CSV Size:** `1,499 bytes`
*   **Parquet Size:** `3,830 bytes`

> [!NOTE]
> On a real production dataset (millions of rows), Parquet's per-column compression algorithms (Snappy) amortize the footer metadata, resulting in massive storage savings (often up to 90% compared to raw CSV) and much faster query execution.

### 2. Verification of Predicate Pushdown
Reading back the written Parquet directory with a filter condition and calling `explain(True)` produces the following physical plan output:
```text
== Physical Plan ==
*(1) Filter (isnotnull(final_price#339) AND (final_price#339 > 1000.0))
+- *(1) ColumnarToRow
   +- FileScan parquet ... DataFilters: [isnotnull(final_price#339), (final_price#339 > 1000.0)], PushedFilters: [IsNotNull(final_price), GreaterThan(final_price,1000.0)], ReadSchema: struct<product_id:int,item_name:string,category:string,unit_price:double,quantity:int,region:stri...
```
The presence of **`PushedFilters: [IsNotNull(final_price), GreaterThan(final_price,1000.0)]`** in the `FileScan` operator verifies that Spark did not load all rows into memory to filter them. Instead, it instructed the Parquet file reader to inspect the metadata and skip entire row groups that failed the condition at disk level.

---

## ⚙️ How to Run the Pipeline

1.  **Prerequisites:** 
    *   Ensure Python 3.8+ is installed.
    *   Ensure Java (JDK 8, 11, or 17) is installed and the `JAVA_HOME` environment variable is configured correctly.
2.  **Install Required Packages:**
    ```bash
    pip install pyspark jupyter
    ```
3.  **Run the Notebook:**
    Navigate to the project folder and launch Jupyter:
    ```bash
    jupyter notebook notebook/spark_data_processing.ipynb
    ```
    Select a Python kernel and run all cells sequentially from top to bottom. The notebook will automatically pull the source file from `data/source.csv` and write output files into the `output/` directory.

---

## 📝 Answers to Concept Questions
To read the complete answers to the 15 assignment questions regarding Spark architecture, lazy evaluation, execution modes, narrow/wide transformations, and memory usage:
*   Open the Markdown version directly: [Spark_Concepts_QA.md](file:///d:/Users/LENOVO/Desktop/Celebal/week-6%20spark%20assessment/Questions_and_Answers/Spark_Concepts_QA.md)
*   Or download and view the PDF layout: [Spark_Concepts_QA.pdf](file:///d:/Users/LENOVO/Desktop/Celebal/week-6%20spark%20assessment/Questions_and_Answers/Spark_Concepts_QA.pdf)
