# Databricks notebook source
# MAGIC %md
# MAGIC # 03_Gold_Modeling
# MAGIC 
# MAGIC Ingests Silver tables, constructs the Star Schema (dimensions and fact), pre-computes analytical KPIs, registers tables in the Hive Metastore, and optimizes the fact table using Z-Ordering.

# COMMAND ----------

# DBTITLE 1,Define Widgets for Configuration
dbutils.widgets.text("storage_account_name", "satactivity", "ADLS Gen2 Storage Account Name")
dbutils.widgets.text("container_name", "sat-activity", "Container Name")
dbutils.widgets.text("storage_account_key", "", "ADLS Gen2 Access Key (Optional)")
dbutils.widgets.text("base_silver_path", "dbfs:/FileStore/food_delivery_analytics/silver", "Base Silver Delta Path")
dbutils.widgets.text("base_gold_path", "dbfs:/FileStore/food_delivery_analytics/gold", "Base Gold Delta Path")
dbutils.widgets.text("target_database", "default", "Target Database Name")

# COMMAND ----------

# DBTITLE 1,Initialize Configurations
storage_account_name = dbutils.widgets.get("storage_account_name")
container_name = dbutils.widgets.get("container_name")
storage_account_key = dbutils.widgets.get("storage_account_key")
base_silver_path = dbutils.widgets.get("base_silver_path")
base_gold_path = dbutils.widgets.get("base_gold_path")
target_database = dbutils.widgets.get("target_database")

# Configure ADLS Authentication if storage account key is provided
if storage_account_key.strip() != "":
    spark.conf.set(
        f"fs.azure.account.key.{storage_account_name}.dfs.core.windows.net",
        storage_account_key
    )
    if "dbfs:/FileStore" in base_silver_path:
        base_silver_path = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/silver"
    if "dbfs:/FileStore" in base_gold_path:
        base_gold_path = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/gold"
    print(f"Authenticated with ADLS Gen2. Silver Path: {base_silver_path}, Gold Path: {base_gold_path}")
else:
    print(f"No storage key provided. Using Paths: Silver Path = {base_silver_path}, Gold Path = {base_gold_path}")

# COMMAND ----------

# DBTITLE 1,Load Silver Tables
try:
    silver_users = spark.read.format("delta").load(f"{base_silver_path.rstrip('/')}/users")
    silver_restaurants = spark.read.format("delta").load(f"{base_silver_path.rstrip('/')}/restaurants")
    silver_orders = spark.read.format("delta").load(f"{base_silver_path.rstrip('/')}/orders")
    print("Successfully loaded all Silver tables.")
except Exception as e:
    print(f"❌ Failed to load Silver tables. Error: {str(e)}")
    raise e

# COMMAND ----------

# DBTITLE 1,Build Gold Dimension Tables
from pyspark.sql.functions import col

gold_dim_users_path = f"{base_gold_path.rstrip('/')}/dim_users"
gold_dim_restaurants_path = f"{base_gold_path.rstrip('/')}/dim_restaurants"

# Filter active records for dimensions to ensure uniqueness of keys
print("Building gold_dim_users...")
dim_users = (
    silver_users
    .filter(col("is_current").cast("boolean") == True)
    .select("user_id", "user_name", "city")
)

(dim_users.write
 .format("delta")
 .mode("overwrite")
 .save(gold_dim_users_path))

print("Building gold_dim_restaurants...")
dim_restaurants = (
    silver_restaurants
    .filter(col("is_current").cast("boolean") == True)
    .select("restaurant_id", "restaurant_name", "cuisine", "rating")
)

(dim_restaurants.write
 .format("delta")
 .mode("overwrite")
 .save(gold_dim_restaurants_path))

print("Gold dimension tables created successfully.")

# COMMAND ----------

# DBTITLE 1,Build Gold Fact Table (Denormalized)
gold_fact_orders_path = f"{base_gold_path.rstrip('/')}/fact_orders"

print("Building gold_fact_orders...")
# Join Silver orders with Gold dimensions via LEFT JOIN
# Denormalize city, restaurant_name, cuisine, and rating (Fixes limitation from project docs)
fact_orders = (
    silver_orders.alias("o")
    .join(dim_users.alias("u"), "user_id", "left")
    .join(dim_restaurants.alias("r"), "restaurant_id", "left")
    .select(
        col("o.order_id"),
        col("o.user_id"),
        col("o.restaurant_id"),
        col("o.order_timestamp"),
        col("o.total_amount"),
        col("o.status"),
        col("u.city").alias("city"),
        col("r.restaurant_name").alias("restaurant_name"),
        col("r.cuisine").alias("cuisine"),
        col("r.rating").alias("rating")
    )
)

(fact_orders.write
 .format("delta")
 .mode("overwrite")
 .save(gold_fact_orders_path))

print("Gold fact table created successfully.")

# COMMAND ----------

# DBTITLE 1,Pre-compute KPI Aggregates
from pyspark.sql.functions import sum as _sum, count, avg, date_trunc, desc

gold_kpi_revenue_by_city_path = f"{base_gold_path.rstrip('/')}/kpi_revenue_by_city"
gold_kpi_restaurant_performance_path = f"{base_gold_path.rstrip('/')}/kpi_restaurant_performance"
gold_kpi_daily_trends_path = f"{base_gold_path.rstrip('/')}/kpi_daily_trends"

# KPI 1: Revenue and order volume by city
print("Computing KPI: Revenue by City...")
kpi_revenue_by_city = (
    fact_orders
    .groupBy("city")
    .agg(
        _sum("total_amount").alias("total_revenue"),
        count("order_id").alias("total_orders")
    )
    .orderBy(desc("total_revenue"))
)

(kpi_revenue_by_city.write
 .format("delta")
 .mode("overwrite")
 .save(gold_kpi_revenue_by_city_path))

# KPI 2: Restaurant rankings, average rating, and order counts
print("Computing KPI: Restaurant Performance...")
kpi_restaurant_performance = (
    fact_orders
    .groupBy("restaurant_name", "cuisine")
    .agg(
        _sum("total_amount").alias("revenue"),
        avg("rating").alias("avg_rating"),
        count("order_id").alias("order_count")
    )
    .orderBy(desc("revenue"))
)

(kpi_restaurant_performance.write
 .format("delta")
 .mode("overwrite")
 .save(gold_kpi_restaurant_performance_path))

# KPI 3: Daily revenue and order count trends
print("Computing KPI: Daily Trends...")
kpi_daily_trends = (
    fact_orders
    .groupBy(date_trunc("day", col("order_timestamp")).cast("date").alias("order_date"))
    .agg(
        _sum("total_amount").alias("daily_revenue"),
        count("order_id").alias("daily_orders")
    )
    .orderBy("order_date")
)

(kpi_daily_trends.write
 .format("delta")
 .mode("overwrite")
 .save(gold_kpi_daily_trends_path))

print("Gold KPI tables pre-computed successfully.")

# COMMAND ----------

# DBTITLE 1,Register Tables in Unity Catalog Metastore
# Switch catalog to the workspace Unity Catalog
spark.sql("USE CATALOG food_delivery_dbw_east")

# Create target database if it doesn't exist in the catalog
spark.sql(f"CREATE DATABASE IF NOT EXISTS {target_database}")

tables_to_register = [
    ("gold_dim_users", gold_dim_users_path),
    ("gold_dim_restaurants", gold_dim_restaurants_path),
    ("gold_fact_orders", gold_fact_orders_path),
    ("gold_kpi_revenue_by_city", gold_kpi_revenue_by_city_path),
    ("gold_kpi_restaurant_performance", gold_kpi_restaurant_performance_path),
    ("gold_kpi_daily_trends", gold_kpi_daily_trends_path)
]

for table_name, physical_path in tables_to_register:
    full_table_name = f"{target_database}.{table_name}"
    print(f"Registering logical table {full_table_name}...")
    # Load conformed Delta data from ADLS Gen2
    df = spark.read.format("delta").load(physical_path)
    # Save as managed table in Unity Catalog default schema
    df.write.format("delta").mode("overwrite").saveAsTable(full_table_name)
    print(f"Logical table {full_table_name} registered successfully in Unity Catalog.")

