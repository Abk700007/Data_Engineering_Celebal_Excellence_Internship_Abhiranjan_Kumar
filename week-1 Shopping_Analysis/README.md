# Shopping Dataset Analysis using Python and Pandas

## Project Overview

This project focuses on performing data exploration, cleaning, feature engineering, and exploratory data analysis (EDA) on a shopping products dataset using Python and Pandas.

The objective of this analysis is to understand product pricing, customer ratings, discounts, category distribution, and product popularity while applying fundamental data analysis techniques used in real-world data engineering and analytics workflows.

---

## Dataset

Dataset Used: `combined_dataset.csv`

The dataset contains product-level information including:

* Product ID
* Product Title
* Product Description
* Ratings
* Ratings Count
* Initial Price
* Final Price
* Discounts
* Product Category
* Seller Information
* Product Specifications
* Customer Reviews
* Additional Product Metadata

---

## Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Jupyter Notebook

---

## Project Workflow

### 1. Data Loading

* Loaded the dataset into a Pandas DataFrame.
* Examined dataset dimensions and column structure.

### 2. Data Understanding

* Inspected data types.
* Analyzed missing values.
* Generated summary statistics using `.info()` and `.describe()`.

### 3. Data Cleaning

* Converted price-related columns into numeric format.
* Handled missing values using appropriate fill strategies.
* Checked and removed duplicate records.
* Saved the cleaned dataset for further analysis.

### 4. Feature Engineering

Created additional features to improve analysis:

#### Price Difference

Measures the difference between the initial product price and the final selling price.

```python
price_difference = initial_price - final_price
```

#### Popularity Score

Measures product popularity using customer ratings and rating count.

```python
popularity_score = rating * ratings_count
```

#### Total Amount

Created a derived column using price and quantity.

```python
total_amount = price * quantity
```

---

## Exploratory Data Analysis

### Univariate Analysis

Performed analysis on individual variables:

* Product Ratings
* Product Prices
* Discount Distribution

Visualizations:

* Histogram of Ratings
* Histogram of Initial Prices

### Bivariate Analysis

Analyzed relationships between variables:

* Rating vs Popularity Score
* Initial Price vs Rating

Visualizations:

* Scatter Plots

### Category-Level Analysis

Analyzed product distribution across categories.

Visualizations:

* Bar Chart of Top Product Categories

### Outlier Detection

Analyzed pricing outliers using:

* Boxplot of Initial Product Prices

---

# Key Insights

### Customer Ratings

* Most products have ratings between 3.5 and 4.5.
* The average product rating is approximately 3.62.
* Customer feedback is generally positive across the dataset.

### Product Pricing

* The average product price is approximately ₹2723.
* The median product price is ₹1999.
* Most products belong to the affordable to mid-range pricing segment.

### Discounts

* A large number of products are sold at discounted prices.
* The average discount amount is approximately ₹1017.
* Some products receive very high discounts, indicating aggressive promotional strategies.

### Product Categories

* Tops, Dresses, and Shirts are the most represented categories.
* Apparel-related products dominate the dataset.

### Popularity

* Higher-rated products generally show higher popularity scores.
* A small number of products account for a significant share of customer engagement.

### Outliers

* Several premium-priced products were identified as outliers.
* These products significantly extend the upper range of the pricing distribution.

---

# Business Implications

### Product Promotion

Products with consistently high ratings can be prioritized in recommendation systems and marketing campaigns to improve customer engagement.

### Category Strategy

Categories such as Tops, Dresses, and Shirts represent major inventory segments and may require focused marketing and inventory planning.

### Pricing Strategy

The presence of substantial discounts suggests that promotional pricing plays an important role in attracting customers and driving sales.

### Customer Satisfaction

Since higher prices do not necessarily result in higher ratings, businesses should focus on product quality, customer experience, and value delivery rather than pricing alone.

### Inventory Management

Popularity metrics can help identify high-performing products and support data-driven inventory and demand planning decisions.

---

## Repository Structure

```text
week-1 Shopping_Analysis/
│
├── data/
│   └── combined_dataset.csv
│
├── notebook/
│   └── analysis.ipynb
│
├── cleaned_dataset.csv
│
└── README.md
```

---

## Conclusion

This project demonstrates the use of Python, Pandas, and data visualization libraries to perform end-to-end data exploration, cleaning, feature engineering, and business-oriented analysis on a real-world shopping dataset. The insights generated from this analysis can support better decision-making in pricing, marketing, inventory planning, and customer engagement strategies.
