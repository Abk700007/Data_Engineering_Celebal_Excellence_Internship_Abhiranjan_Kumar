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

