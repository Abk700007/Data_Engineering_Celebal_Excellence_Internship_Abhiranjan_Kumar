# Food Delivery Analytics: End-to-End Data Engineering & BI on Azure Databricks

This repository contains my capstone project for implementing a production-grade, end-to-end data engineering pipeline and interactive business intelligence dashboard. 

The project is built on **Microsoft Azure** using **Azure Databricks (LTS 17.3, Photon Engine)** and **Azure Data Lake Storage Gen2 (ADLS)**. It implements a three-tier **Medallion Architecture (Bronze → Silver → Gold)** using **Delta Lake**, leading to a clean, conformed **Star Schema** data model consumed in **Power BI** via **DirectQuery**.

---

## 1. Project Architecture Flow

```mermaid
graph LR
    subgraph ADLS Gen2 Storage Container
        Raw[Raw Landing CSVs] -->|01_Bronze_Ingestion| Bronze[Bronze Delta Tables]
        Bronze -->|02_Silver_Transformation| Silver[Silver Conformed Delta]
        Silver -->|03_Gold_Modeling| Gold[Gold Star Schema & KPIs]
    end
    subgraph Azure Databricks Compute
        UC[(Unity Catalog Metastore)] <-->|External Tables Registration| Gold
    end
    subgraph Serving Layer
        PowerBI[Power BI Desktop Dashboard] <-->|DirectQuery live connection| UC
    end
```

