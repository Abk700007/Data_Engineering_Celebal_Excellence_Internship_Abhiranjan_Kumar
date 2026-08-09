# Power BI Business Intelligence Dashboard

This directory contains the final visualization and reporting layer of the Food Delivery Analytics platform. 

The dashboard file **`CEI_Food_Delivery_Analytics_Dashboard.pbix`** is connected directly to the Azure Databricks Unity Catalog serving metastore via **DirectQuery**, enabling live analytical slicing and dicing without data duplication.

---

## 1. Dashboard Structure & Pages

The dashboard is structured into **4 dedicated pages** designed to serve different business stakeholders. Screenshots of each page are located in the `Power BI/screenshots/` folder:

### Page 1: Executive Summary (`01_dashboard_page1_executive_summary.png`)
*   **Target Audience**: Business Executives & Regional Managers.
*   **Key Visuals**:
    *   *Geographic Sales Map*: A Map visual mapping bubble sizes to total revenues across major cities in India (Delhi, Mumbai, Jaipur, Bangalore).
    *   *City Revenue Split*: A horizontal clustered bar chart comparing the total sales generated in each city.
    *   *Total Corporate Revenue Card*: A metric card highlighting the overall sales of **`9M`** (`$9,028,576`).
*   **Primary Data Source**: `gold_kpi_revenue_by_city` (pre-aggregated to maximize dashboard load speeds).

### Page 2: Restaurant Leaderboard (`02_dashboard_page2_restaurant_leaderboard.png`)
*   **Target Audience**: Restaurant Partnership Teams & Operations Managers.
*   **Key Visuals**:
    *   *Leaderboard Table*: A grid listing restaurant names, cuisines, total orders handled, total revenues generated, and average user ratings.
    *   *Cuisine Share Chart*: A pie chart illustrating the revenue contribution of each cuisine (Italian, Indian, Fast Food, Chinese) to overall sales.
*   **Primary Data Source**: `gold_kpi_restaurant_performance`

### Page 3: Daily Operations (`03_dashboard_page3_daily_operations.png`)
*   **Target Audience**: Daily Operations Control Room.
*   **Key Visuals**:
    *   *Daily Revenue Trend*: A time-series line chart tracking daily revenue peaks.
    *   *Daily Order Volume*: A column chart tracking the absolute volume of order requests processed daily.
*   **Primary Data Source**: `gold_kpi_daily_trends` (since sample records occur on April 17, 2026, it shows a single-day peak).

### Page 4: Order Drillthrough (`04_dashboard_page4_order_drillthrough.png`)
*   **Target Audience**: Customer Support & Transaction Analysts.
*   **Key Visuals**:
    *   *Transaction Browser Table*: A granular, detailed list displaying raw order metadata (`order_id`, `order_timestamp`, `city`, `restaurant_name`, `cuisine`, `status`, `total_amount`).
    *   *Interactive Search Slicers*: Checkbox filters allowing the user to filter the raw transaction records dynamically by City, Order Status, and Restaurant.
*   **Primary Data Source**: `gold_fact_orders` conformed transactional fact table.

---

## 2. Reconnecting to your Databricks Cluster

If your Databricks cluster is restarted or rebuilt, you will need to update the data source connection settings in Power BI Desktop:

1.  Open `CEI_Food_Delivery_Analytics_Dashboard.pbix` in Power BI Desktop.
2.  Go to **Home** → **Transform Data** → **Data source settings**.
3.  Select the **Azure Databricks** connection and click **Change Source**.
4.  Enter your cluster parameters:
    *   **Server Hostname**: `adb-7405616248700702.2.azuredatabricks.net`
    *   **HTTP Path**: `/sql/protocolv1/o/7405616248700702/0809-015309-8dmi5vhe`
5.  If prompted for credentials, select **Token** authentication and paste your new **Personal Access Token (PAT)** from Databricks User Settings.
6.  Save and apply changes to update the live charts.
