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

