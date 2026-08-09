# Databricks notebook source
# MAGIC %md
# MAGIC # 02_Silver_Transformation
# MAGIC 
# MAGIC Applies data quality rules, CDC merge logic, and dimension standardization to produce clean, conformed Silver tables.

# COMMAND ----------

# DBTITLE 1,Define Widgets for Configuration
dbutils.widgets.text("storage_account_name", "satactivity", "ADLS Gen2 Storage Account Name")
dbutils.widgets.text("container_name", "sat-activity", "Container Name")
dbutils.widgets.text("storage_account_key", "", "ADLS Gen2 Access Key (Optional)")
dbutils.widgets.text("base_bronze_path", "dbfs:/FileStore/food_delivery_analytics/bronze", "Base Bronze Delta Path")
dbutils.widgets.text("base_silver_path", "dbfs:/FileStore/food_delivery_analytics/silver", "Base Silver Delta Path")

# COMMAND ----------

# DBTITLE 1,Initialize Configurations
storage_account_name = dbutils.widgets.get("storage_account_name")
container_name = dbutils.widgets.get("container_name")
storage_account_key = dbutils.widgets.get("storage_account_key")
base_bronze_path = dbutils.widgets.get("base_bronze_path")
base_silver_path = dbutils.widgets.get("base_silver_path")

# Configure ADLS Authentication if storage account key is provided
if storage_account_key.strip() != "":
    spark.conf.set(
        f"fs.azure.account.key.{storage_account_name}.dfs.core.windows.net",
        storage_account_key
    )
    if "dbfs:/FileStore" in base_bronze_path:
        base_bronze_path = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/bronze"
    if "dbfs:/FileStore" in base_silver_path:
        base_silver_path = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/silver"
    print(f"Authenticated with ADLS Gen2. Bronze Path: {base_bronze_path}, Silver Path: {base_silver_path}")
else:
    print(f"No storage key provided. Using Paths: Bronze Path = {base_bronze_path}, Silver Path = {base_silver_path}")

# COMMAND ----------

# DBTITLE 1,Define Reusable Data Cleaning Function
from pyspark.sql.functions import col, trim, initcap
from pyspark.sql.types import StringType

def clean_dataframe(df):
    """
    Standardizes all string columns by trimming trailing/leading spaces
    and converting casing to initial capital letters (initcap).
    """
    for field in df.schema.fields:
        if isinstance(field.dataType, StringType):
            df = df.withColumn(field.name, initcap(trim(col(field.name))))
    return df

# COMMAND ----------

# DBTITLE 1,Process Orders CDC Merge
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, desc, coalesce, lit, current_timestamp
from delta.tables import DeltaTable

silver_orders_path = f"{base_silver_path.rstrip('/')}/orders"
bronze_orders_path = f"{base_bronze_path.rstrip('/')}/orders"
bronze_orders_cdc_path = f"{base_bronze_path.rstrip('/')}/orders_cdc"

print(f"Processing Orders CDC Merge: Target = {silver_orders_path}")

# 1. Load Bronze datasets
try:
    orders_df = spark.read.format("delta").load(bronze_orders_path)
    orders_cdc_df = spark.read.format("delta").load(bronze_orders_cdc_path)
except Exception as e:
    print(f"❌ Failed to load Bronze datasets: {str(e)}")
    raise e

# 2. Deduplicate CDC records to keep only the latest update per order
window_spec = Window.partitionBy("order_id").orderBy(desc("updated_at"))
deduped_cdc = (
    orders_cdc_df
    .withColumn("row_num", row_number().over(window_spec))
    .filter("row_num = 1")
    .drop("row_num")
)

# 3. Join base orders with CDC records to build unified states
# Fallback status to 'Ordered' and _last_updated to order_timestamp
orders_conformed = (
    orders_df.alias("o")
    .join(deduped_cdc.alias("c"), "order_id", "left")
    .select(
        col("o.order_id"),
        col("o.user_id"),
        col("o.restaurant_id"),
        col("o.order_timestamp"),
        col("o.total_amount"),
        coalesce(col("c.status"), lit("Ordered")).alias("status"),
        coalesce(col("c.updated_at"), col("o.order_timestamp")).alias("_last_updated")
    )
)

# 4. Standardize strings in combined dataset
orders_cleaned = clean_dataframe(orders_conformed)

# 5. Merge into Silver Orders delta folder using try/except
try:
    # Attempt to load the table as DeltaTable
    silver_table = DeltaTable.forPath(spark, silver_orders_path)
    
    print("Existing Silver Orders table found. Executing incremental CDC merge...")
    (silver_table.alias("target")
     .merge(
         orders_cleaned.alias("source"),
         "target.order_id = source.order_id"
     )
     .whenMatchedUpdate(set={
         "status": "source.status",
         "_last_updated": "source._last_updated"
     })
     .whenNotMatchedInsertAll()
     .execute())
    print("CDC merge completed successfully.")
except Exception as e:
    print(f"Silver orders table not found or cannot be loaded: {str(e)}")
    print("Initializing Silver orders table with overwrite...")
    (orders_cleaned.write
     .format("delta")
     .mode("overwrite")
     .option("mergeSchema", "true")
     .save(silver_orders_path))
    print("Silver orders table initialized successfully.")

# COMMAND ----------

# DBTITLE 1,Define Reusable Dimension Processing Function
def process_dimension(source_folder_name, target_folder_name):
    source_path = f"{base_bronze_path.rstrip('/')}/{source_folder_name}"
    target_path = f"{base_silver_path.rstrip('/')}/{target_folder_name}"
    
    print(f"Processing Dimension: {source_path} -> {target_path}...")
    
    # 1. Read Bronze dimension table
    df = spark.read.format("delta").load(source_path)
    
    # 2. Standardize string fields
    df_cleaned = clean_dataframe(df)
    
    # 3. Add audit processed timestamp
    df_with_audit = df_cleaned.withColumn("_processed_at", current_timestamp())
    
    # 4. Save to Silver in overwrite mode
    (df_with_audit.write
     .format("delta")
     .mode("overwrite")
     .save(target_path))
    
    print(f"Successfully processed and saved dimension to {target_folder_name}")

# COMMAND ----------

# DBTITLE 1,Standardize Dimensions
dimensions = [
    ("users", "users"),
    ("restaurants", "restaurants")
]

for src_folder, tgt_folder in dimensions:
    try:
        process_dimension(src_folder, tgt_folder)
    except Exception as e:
        print(f"❌ Failed: Dimension {src_folder} processing failed. Error: {str(e)}")
        raise e
