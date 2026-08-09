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
