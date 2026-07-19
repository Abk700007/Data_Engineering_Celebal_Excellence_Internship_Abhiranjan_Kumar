# Data Engineering - Celebal Excellence Internship

Welcome to My repository for the Data Engineering track of the **Celebal Excellence Internship**. This repository serves as a portfolio of assessments, projects, and tasks completed during the 8-week internship program.

---

## Program Structure

The internship is structured around weekly assessments covering different facets of Data Engineering, including Data Exploration, Data Cleaning, ETL pipelines, Data Modeling, and Analysis.

| Week | Assessment / Topic | Status | Description |
|---|---|---|---|
| **Week 1** | [Week 1 - Shopping Analysis](./week-1%20Shopping_Analysis/) | Completed | Exploratory Data Analysis, Data Cleaning, and Feature Engineering on a shopping products dataset. |
| **Week 2** | [Week 2 - E-Commerce Sales Database](./week-2%20-%20E-Commerce%20Sales%20Database/) | Completed | Relational Database setup, custom CHECK constraints, performance indexing, SQL queries (A-E), and transactional consistency checks. |
| **Week 3** | [Week 3 - Superstore dataset analysis](./week-3%20Superstore%20dataset%20analysis%20using%20subqueries,%20CTEs%20and%20Window%20Function/customer-sales-insights/) | Completed | Database normalization, Advanced Queries, Subqueries, CTEs, Window Functions, and Customer Sales Insights Mini-Project. |
| **Week 4** | [Week 4 - Azure Cloud and ADF Pipeline](./week-4%20Azure%20cloud%20concepts%20and%20Data%20Pipeline%20implementation%20using%20ADF/) | Completed | Azure cloud fundamentals, Storage accounts, Blob containers, ADF Pipelines, Linked Services, Datasets, activities (Get Metadata, Copy Data), Fault Tolerance, and RBAC Managed Identity configuration. |
| **Week 5** | [Week 5 - Spark fundamentals and Data cleaning pipeline](./week-5%20Spark%20fundamentals%20and%20Data%20cleaning%20pipeline%20using%20DataFrames/) | Completed | PySpark pipeline for data cleaning, transformation, and aggregation on customer sales data. |
| **Week 6** | *To be updated* | Upcoming | Week 6 assessment task. |
| **Week 7** | *To be updated* | Upcoming | Week 7 assessment task. |
| **Week 8** | *To be updated* | Upcoming | Week 8 assessment task. |

---

## Repository Directory Structure

The files and weekly assessment directories are structured as follows:

```text
.
├── week-1 Shopping_Analysis/
│   ├── data/
│   │   └── combined_dataset.csv
│   ├── notebook/
│   │   └── analysis.ipynb
│   ├── cleaned_dataset.csv
│   └── README.md
│
├── week-2 - E-Commerce Sales Database/
│   ├── database/
│   │   ├── create_database.sql
│   │   ├── create_tables.sql
│   │   ├── create_indexes.sql
│   │   └── insert_data.sql
│   ├── validation/
│   │   └── validate_data.sql
│   ├── Section_A/ to Section_E/
│   │   └── basic_queries.sql, filtering_queries.sql, etc.
│   ├── results/
│   │   └── Section_A_results.txt to Section_E_results.txt
│   └── README.md
│
├── week-3 Superstore dataset analysis using subqueries, CTEs and Window Function/
│   └── customer-sales-insights/
│       ├── data/
│       │   ├── Sample - Superstore.csv
│       │   └── superstore.db
│       │   
│       ├── sql/
│       │   ├── create_tables.sql
│       │   ├── insert_data.sql
│       │   └── advanced_queries.sql
│       ├── mini project/
│       │   └── mini_project.sql
│       ├── results/
│       │   └── result.sql
│       └── README.md
│
├── week-4 Azure cloud concepts and Data Pipeline implementation using ADF/
│   ├── Task_1_Resource_Group/
│   │   └── resource_group.png
│   ├── Task_2_Storage_Setup/
│   │   ├── storage_account.png
│   │   └── blob_container with CSV file.png
│   ├── Task_3_ADF_Basics/
│   │   ├── ADF_Overview.png
│   │   ├── Linked_Service.png
│   │   ├── Source_Dataset.png
│   │   ├── Destination_Dataset.png
│   │   └── Get_Metadata.png
│   ├── Task_4_Pipeline_Development/
│   │   ├── Pipeline_Design.png
│   │   ├── Source.png
│   │   ├── Sink.png
│   │   └── Mappings.png
│   ├── Task_5_Pipeline_Execution/
│   │   └── Pipeline_Execution_Success.png
│   ├── Task_6_IAM_Roles/
│   │   ├── IAM_Roles_assigned.png
│   │   ├── Reader.png
│   │   └── Contributor.png
│   ├── Mini_Project/
│   │   ├── Source_Blob_storage.png
│   │   ├── Get_Metadata_Activity.png
│   │   ├── Pipeline_Execution_Success.png
│   │   └── Destination_output.png
│   └── README.md
│
├── week-5 Spark fundamentals and Data cleaning pipeline using DataFrames/
│   ├── Data/
│   │   └── dataset.csv
│   ├── Notebook/
│   │   └── spark_basics.ipynb
│   ├── Output/
│   │   └── results.csv
│   ├── week-5_assignment_answers.docx
│   └── Readme.md
│
└── README.md (Root)
```

*Note: New folders for subsequent weeks will be created under the root directory as the internship progresses.*

---

## Getting Started

### Prerequisites
To run the notebooks and scripts locally, ensure you have the following installed:
* Python 3.8+
* Jupyter Notebook / JupyterLab
* Pandas
* NumPy
* Matplotlib
* Seaborn

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Abk700007/Data_Engineering_Celebal_Excellence_Internship_Abhiranjan_Kumar.git
   ```
2. Navigate to the weekly assessment of interest (e.g., `week-1 Shopping_Analysis`) and explore the notebooks/data.

---

## License & Internship Info
* **Intern**: Abhiranjan Kumar
* **Institution**:ITER(SOA University)
* **Organization**: Celebal Technologies (Celebal Excellence Internship)
* **Track**: Data Engineering
