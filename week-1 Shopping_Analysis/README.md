# Shopping Dataset Analysis

This repository contains the analysis and cleaning of a shopping products dataset using Python and Pandas.

## Analysis Workflow

The analysis is documented in the [analysis.ipynb](file:///d:/Users/LENOVO/Desktop/Jupyter%20notebook%20programs/week-1%20Shopping_Analysis/notebook/analysis.ipynb) notebook and covers the following stages:

### 1. Data Loading & Initial Exploration
* Loaded the raw dataset (`combined_dataset.csv`) containing 1,000 products and 24 attributes.
* Checked dataset dimensions, columns, data types, and initial summary statistics.

### 2. Data Cleaning
* **Currency/Numeric Conversion**: Stripped currency symbols (`₹`), commas, and quotes from the `final_price` column and converted it to float.
* **Missing Value Imputation**:
  * Imputed missing numeric values (e.g., `discount`) using their column mean.
  * Imputed missing categorical values (e.g., `seller_name`, `what_customers_said`) with `"Unknown"`.
* **Deduplication**: Checked and removed duplicate records.
* **Output**: Saved the resulting cleaned dataset as `cleaned_dataset.csv` in the root folder.

### 3. Feature Engineering
Created new columns to enhance the analysis:
* `quantity`: Since quantity was not provided in the original dataset, a default quantity of `10` was assumed for the calculations.
* `total_amount`: Total value of the initial inventory (`initial_price * quantity`).
* `price_difference`: Absolute discount value in currency (`initial_price - final_price`).
* `popularity_score`: A composite metric of customer engagement (`rating * ratings_count`).

### 4. Exploratory Data Analysis (EDA)
* **Univariate Analysis**:
  * Plotted the distribution of product ratings (mean: ~3.62, median: 4.1).
  * Analyzed the distribution of initial prices (mean: ~₹2723, median: ₹1999).
* **Bivariate Analysis**:
  * Plotted the relationship between customer rating and popularity score.
  * Investigated the relationship between initial price and rating (showing no strong correlation).
* **Category-Level Analysis**:
  * Identified the top product categories, dominated by `tops` (122), `dresses` (100), and `shirts` (97).
* **Outlier Detection**:
  * Used a boxplot on `initial_price` to identify high-priced premium outlier products (prices extending up to ₹22,199).

---

## Brief Summary

In this project, a shopping dataset of 1,000 items was cleaned by formatting price columns, handling missing values, and deduplicating rows. Four engineered features (`quantity`, `total_amount`, `price_difference`, and `popularity_score`) were created to analyze pricing and popularity. Since quantity was not originally provided, a value of 10 was assumed for each product. Exploratory data analysis revealed that apparel categories (Tops, Dresses, Shirts) dominate the dataset, customer ratings are generally positive (averaging 3.62), and product price does not correlate strongly with customer rating.
