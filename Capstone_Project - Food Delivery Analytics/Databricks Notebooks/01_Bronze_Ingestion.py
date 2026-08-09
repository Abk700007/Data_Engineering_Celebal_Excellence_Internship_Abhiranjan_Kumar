# Databricks notebook source
# MAGIC %md
# MAGIC # 01_Bronze_Ingestion
# MAGIC 
# MAGIC Ingests raw CSV data sources from storage into the Bronze layer as Delta Lake tables.
# MAGIC 
# MAGIC **Source CSVs:**
# MAGIC - `orders.csv`
# MAGIC - `orders_cdc.csv`
# MAGIC - `users_scd.csv`
# MAGIC - `restaurants_scd.csv`
# MAGIC 
# MAGIC **Target Bronze Tables:**
# MAGIC - `bronze/orders`
# MAGIC - `bronze/orders_cdc`
# MAGIC - `bronze/users`
# MAGIC - `bronze/restaurants`

# COMMAND ----------

# DBTITLE 1,Define Widgets for Configuration
dbutils.widgets.text("storage_account_name", "satactivity", "ADLS Gen2 Storage Account Name")
dbutils.widgets.text("container_name", "sat-activity", "Container Name")
dbutils.widgets.text("storage_account_key", "", "ADLS Gen2 Access Key (Optional)")
dbutils.widgets.text("base_raw_path", "dbfs:/FileStore/food_delivery_analytics/raw", "Base Raw Files Path (ADLS or DBFS)")
dbutils.widgets.text("base_bronze_path", "dbfs:/FileStore/food_delivery_analytics/bronze", "Base Bronze Delta Path")

# COMMAND ----------

# DBTITLE 1,Initialize Configurations
storage_account_name = dbutils.widgets.get("storage_account_name")
container_name = dbutils.widgets.get("container_name")
storage_account_key = dbutils.widgets.get("storage_account_key")
base_raw_path = dbutils.widgets.get("base_raw_path")
base_bronze_path = dbutils.widgets.get("base_bronze_path")

# Configure ADLS Authentication if storage account key is provided
if storage_account_key.strip() != "":
    spark.conf.set(
        f"fs.azure.account.key.{storage_account_name}.dfs.core.windows.net",
        storage_account_key
    )
    # Automatically update raw and bronze paths to use Azure storage if they are default dbfs values
    if "dbfs:/FileStore" in base_raw_path:
        base_raw_path = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/raw"
    if "dbfs:/FileStore" in base_bronze_path:
        base_bronze_path = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/bronze"
    print(f"Authenticated with ADLS Gen2. Raw Path: {base_raw_path}, Bronze Path: {base_bronze_path}")
else:
    print(f"No storage key provided. Using Paths: Raw Path = {base_raw_path}, Bronze Path = {base_bronze_path}")

# COMMAND ----------

# DBTITLE 1,Cleanup existing bronze directory for Idempotent Reruns
try:
    print(f"Cleaning up existing bronze directory at {base_bronze_path}...")
    dbutils.fs.rm(base_bronze_path, True)
    print("Cleanup successful.")
except Exception as e:
    print(f"Cleanup info (directory might not exist yet): {str(e)}")

# COMMAND ----------

# DBTITLE 1,Define Ingestion Helper Function
from pyspark.sql.functions import current_timestamp, col

def ingest_to_bronze(source_csv_name, target_folder_name):
    source_path = f"{base_raw_path.rstrip('/')}/{source_csv_name}"
    target_path = f"{base_bronze_path.rstrip('/')}/{target_folder_name}"
    
    print(f"Starting Ingestion: {source_path} -> {target_path}...")
    
    # Read CSV with headers and inferred schema
    df = (spark.read
          .format("csv")
          .option("header", "true")
          .option("inferSchema", "true")
          .load(source_path))
    
    # Add lineage metadata columns
    df_with_metadata = (df
                        .withColumn("_ingestion_timestamp", current_timestamp())
                        .withColumn("_source_file_name", col("_metadata.file_path")))
    
    # Save to Delta format with overwrite mode
    (df_with_metadata.write
     .format("delta")
     .mode("overwrite")
     .save(target_path))
    
    print(f"Successfully Ingested: {source_csv_name} -> {target_folder_name}")

# COMMAND ----------

# DBTITLE 1,Ingestion Loop with Isolation
sources = [
    ("orders.csv", "orders"),
    ("orders_cdc.csv", "orders_cdc"),
    ("users_scd.csv", "users"),
    ("restaurants_scd.csv", "restaurants")
]

for csv_name, folder_name in sources:
    try:
        ingest_to_bronze(csv_name, folder_name)
    except Exception as e:
        print(f"❌ Failed: Ingesting {csv_name} failed. Error: {str(e)}")
        print("Continuing with next sources...")

# COMMAND ----------

# DBTITLE 1,Verification
try:
    print("Listing bronze folders to confirm successful ingestion:")
    files = dbutils.fs.ls(base_bronze_path)
    for f in files:
        print(f.path)
except Exception as e:
    print(f"❌ Verification failed to list directories: {str(e)}")
