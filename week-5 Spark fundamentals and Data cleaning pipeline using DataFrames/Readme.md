# Spark Basics and DataFrames - Week 5 Assignment

## Intern Details
* **Name:** Abhiranjan Kumar
* **Institution:** ITER (SOA University)
* **Organization:** Celebal Technologies (Celebal Excellence Internship)
* **Track:** Data Engineering
* **Topic:** Apache Spark & PySpark DataFrames

---

## Project Overview
For my Week 5 task in the Celebal Technologies Internship, I focused on learning the core fundamentals of Apache Spark. I built a data cleaning, transformation, and aggregation pipeline using PySpark DataFrames. The pipeline processes an intentionally messy sales dataset containing duplicates, invalid schema types, null values, and inconsistent text casing.

---

## 📂 Project Structure
Here is how I organized the files for my Week 5 project:

```text
week-5 Spark fundamentals and Data cleaning pipeline using DataFrames/
├── Data/
│   └── dataset.csv              -- Intentionally messy customer sales dataset (315 rows)
├── Notebook/
│   └── spark_basics.ipynb       -- My step-by-step PySpark pipeline walkthrough notebook
├── Output/
│   └── results.csv              -- The final aggregated output saved by my pipeline
├── week-5_assignment_answers.docx  -- Word document containing answers to the 15 questions
└── Readme.md                    -- This documentation
```

---

## 🎯 Objectives & What I Learned

1. **Understand Spark vs MapReduce:** 
   * Learned why Spark is significantly faster (10-100x) than MapReduce due to its **in-memory processing** and optimized **DAG execution plans** instead of constant disk write/read cycles.
2. **DataFrame Immutability:** 
   * Explored how Spark DataFrames are immutable and how transformations are lazily evaluated until an action is called.
3. **Data Cleaning:** 
   * Wrote logic to deduplicate data, handle missing values (drop vs. fill), and cleanse inconsistent inputs.
4. **Filtering and Schema Modification:** 
   * Applied conditional filters and type-casting (string to integer, renaming column headers).
5. **Aggregation & Grouping:** 
   * Used Spark SQL aggregation functions (`avg`, `sum`, `count`, `min`, `max`) and applied HAVING-style filtering on grouped records.
6. **Performance Optimization (Narrow vs. Wide Transformations):** 
   * Studied execution plans (`df.explain()`) to understand shuffles (data movement across partitions).

---

## ⚙️ How to Run My Notebook
To run my Spark pipeline:

1. **Prerequisites:** Ensure you have Python 3.9+ and Java (8, 11, 17, or 21) installed on your system.
2. **Install Libraries:** Run the following command in your terminal:
   ```bash
   pip install pyspark pandas
   ```
3. **Run Notebook:** Open [spark_basics.ipynb](file:///d:/Users/LENOVO/Desktop/Celebal/week-5%20Spark%20fundamentals%20and%20Data%20cleaning%20pipeline%20using%20DataFrames/Notebook/spark_basics.ipynb) using VS Code or Jupyter Notebook, select your Python kernel, and run all cells.
4. **Output Verification:** Running the notebook will automatically regenerate the cleaned and aggregated report in [results.csv](file:///d:/Users/LENOVO/Desktop/Celebal/week-5%20Spark%20fundamentals%20and%20Data%20cleaning%20pipeline%20using%20DataFrames/Output/results.csv).

---

## 🚀 Walkthrough of Steps I Implemented

### Step 1: MapReduce vs Spark (Theory)
I documented the theoretical advantages of Spark's RAM-centric computation and lazy evaluation model compared to Hadoop's disk-bound MapReduce.

### Step 2: Initialize Spark Session
I initialized a local `SparkSession` with an app name of `"SparkAssignment_Week5"` using:
```python
spark = SparkSession.builder.appName("SparkAssignment_Week5").master("local[*]").getOrCreate()
```

### Step 3: Load Data
I loaded the dataset [dataset.csv](file:///d:/Users/LENOVO/Desktop/Celebal/week-5%20Spark%20fundamentals%20and%20Data%20cleaning%20pipeline%20using%20DataFrames/Data/dataset.csv) using Spark's CSV reader, printed the column names, and checked the raw row count (315 rows).

### Step 4: Data Cleaning
I applied the following cleansing operations:
* **Deduplication:** Dropped 15 duplicate rows, reducing the count to 300 rows.
* **Schema Fix:** Standardized the `age` column by trimming whitespace, casting to a string, then double, and finally integer.
* **Casing Normalization:** Applied `F.initcap` to clean up mixed casing (e.g., converting `"ELECTRONICS"` and `"electronics"` to `"Electronics"`).
* **Out-of-Bounds Curation:** Set unrealistic ages (ages <= 0 or > 100) to `null`.
* **Null Handling:** Dropped rows where the critical `age` field was null, while filling missing `region` and `category` fields with `"Unknown"` to retain data for aggregation.

### Step 5: Filter Data
I demonstrated filtering datasets by age ranges (25–45), specific categories (`Electronics`), specific regions (`North`), and a combined conditional query.

### Step 6: Transform Schema
I renamed the `sales_amount` column to `total_sales` and cast sales figures to a rounded double type.

### Step 7: Aggregation
Calculated overall summary statistics across the whole dataset (min/max sales, average customer age, total sales).

### Step 8: Group Data
I performed a multi-level `groupBy` query on `region` and `category`, calculating average sales, total sales, and custom counts, and then filtered the groupings to only include rows where `num_customers > 5`.

### Step 9: Shuffling & Wide Transformations (Theory & Execution)
I used `df.explain()` on my grouped DataFrames to view the physical execution plan and highlighted how wide transformations (like `groupBy`) trigger an `Exchange` (shuffle boundary) which can affect performance at scale.

### Step 10: Complete Pipeline Function
I packaged all the loading, cleaning, transforming, and saving logic into a modular `run_pipeline(input_path)` function for reusability.

---

## 📊 My Sample Aggregation Results (`Output/results.csv`)

| region | category | num_customers | avg_sales | total_sales_sum | avg_age |
| :--- | :--- | :--- | :--- | :--- | :--- |
| South | Clothing | 19 | 309.73 | 5884.94 | 40.0 |
| Central | Furniture | 14 | 383.04 | 5362.60 | 47.6 |
| South | Toys | 15 | 254.05 | 3810.75 | 40.2 |
| East | Clothing | 14 | 219.34 | 3070.74 | 40.6 |
| Central | Electronics | 10 | 290.19 | 2901.87 | 34.1 |

---

## 💡 Key Insights & Observations
1. **Cleaning Yield:** Cleaning reduced the raw row count from 315 to 281. This highlights how real-world datasets require robust validation and sanitization before staging.
2. **Impact of Case Inconsistency:** If casing wasn't normalized (e.g. `"ELECTRONICS"` vs `"Electronics"`), Spark's `groupBy` would split them into separate entities, corrupting the aggregation results.
3. **Wide vs. Narrow Transformations:** Identifying shuffles (`Exchange` in Spark's plan) helps plan partition strategies to minimize network overhead during large scale operations.