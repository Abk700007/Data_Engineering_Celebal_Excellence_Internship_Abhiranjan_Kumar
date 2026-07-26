# Execution Results — Week 6 Spark Data Processing

This file contains the actual captured console output from running `notebook/spark_data_processing.ipynb` end to end on the sample dataset `data/source.csv` using PySpark (local mode).

### 1. Spark Session Created
```
Spark Version : 4.2.0
Application Name : Week6_Spark_Data_Processing
Master : local[*]
Default Parallelism : 1

```

### 2. Dataset Loaded
```
Row count: 20
Column count: 8
Columns: ['product_id', 'product_name', 'category', 'price', 'quantity', 'region', 'priority', 'status']
```

### 3. Schema (Explicit Schema Load)
```
root
 |-- product_id: integer (nullable = true)
 |-- product_name: string (nullable = true)
 |-- category: string (nullable = true)
 |-- price: double (nullable = true)
 |-- quantity: integer (nullable = true)
 |-- region: string (nullable = true)
 |-- priority: string (nullable = true)
 |-- status: string (nullable = true)


```

### 3b. Schema (inferSchema=True Load)
```
root
 |-- product_id: integer (nullable = true)
 |-- product_name: string (nullable = true)
 |-- category: string (nullable = true)
 |-- price: double (nullable = true)
 |-- quantity: integer (nullable = true)
 |-- region: string (nullable = true)
 |-- priority: string (nullable = true)
 |-- status: string (nullable = true)


```

### 4. Null Value Audit (before cleaning)
```
Null count in 'price': 2
Null count in 'quantity': 3
```

### 4b. After Cleaning
```
Row count after dropping null price & filling null quantity: 18
```

### 5. Filter: category == 'Electronics'
```
+----------+-----------------+-----------+-------+--------+------+--------+---------+
|product_id|product_name     |category   |price  |quantity|region|priority|status   |
+----------+-----------------+-----------+-------+--------+------+--------+---------+
|101       |Wireless Mouse   |Electronics|799.5  |120     |North |Low     |Completed|
|102       |Bluetooth Speaker|Electronics|1999.0 |45      |South |Medium  |Completed|
|105       |LED Monitor      |Electronics|8999.0 |25      |North |Medium  |Completed|
|108       |Smartphone       |Electronics|15999.0|60      |West  |High    |Completed|
|109       |Gaming Keyboard  |Electronics|2499.0 |0       |North |Medium  |Pending  |
|112       |Laptop Stand     |Electronics|899.0  |80      |West  |Medium  |Completed|
|114       |Desk Lamp        |Electronics|650.0  |90      |South |Low     |Completed|
|116       |Tablet           |Electronics|12999.0|35      |North |High    |Completed|
|119       |Router           |Electronics|1799.0 |0       |West  |Medium  |Completed|
+----------+-----------------+-----------+-------+--------+------+--------+---------+


```

### 6. Select product_id, price (Electronics only)
```
+----------+-------+
|product_id|price  |
+----------+-------+
|101       |799.5  |
|102       |1999.0 |
|105       |8999.0 |
|108       |15999.0|
|109       |2499.0 |
|112       |899.0  |
|114       |650.0  |
|116       |12999.0|
|119       |1799.0 |
+----------+-------+


```

### 7. Rename Columns
```
Renamed 'product_name' -> 'item_name', 'price' -> 'unit_price'
New columns: ['product_id', 'item_name', 'category', 'unit_price', 'quantity', 'region', 'priority', 'status']
```

### 8. Data Type Casting
```
Cast 'unit_price' -> Double, 'product_id' -> String (demonstration)
```

### 9. Add Columns: final_price (18% tax), category_upper
```
+----------+-----------------+-----------+----------+--------+------+--------+---------+-----------+--------------+
|product_id|item_name        |category   |unit_price|quantity|region|priority|status   |final_price|category_upper|
+----------+-----------------+-----------+----------+--------+------+--------+---------+-----------+--------------+
|101       |Wireless Mouse   |Electronics|799.5     |120     |North |Low     |Completed|943.41     |ELECTRONICS   |
|102       |Bluetooth Speaker|Electronics|1999.0    |45      |South |Medium  |Completed|2358.82    |ELECTRONICS   |
|103       |Office Chair     |Furniture  |4500.0    |15      |East  |High    |Pending  |5310.0     |FURNITURE     |
|104       |Notebook Set     |Stationery |150.0     |300     |West  |Low     |Completed|177.0      |STATIONERY    |
|105       |LED Monitor      |Electronics|8999.0    |25      |North |Medium  |Completed|10618.82   |ELECTRONICS   |
|106       |Study Table      |Furniture  |3200.0    |10      |South |Low     |Cancelled|3776.0     |FURNITURE     |
|108       |Smartphone       |Electronics|15999.0   |60      |West  |High    |Completed|18878.82   |ELECTRONICS   |
|109       |Gaming Keyboard  |Electronics|2499.0    |0       |North |Medium  |Pending  |2948.82    |ELECTRONICS   |
|110       |Bookshelf        |Furniture  |2750.0    |18      |South |Low     |Completed|3245.0     |FURNITURE     |
|111       |Sketch Pens      |Stationery |120.0     |220     |East  |Low     |Completed|141.6      |STATIONERY    |
|112       |Laptop Stand     |Electronics|899.0     |80      |West  |Medium  |Completed|1060.82    |ELECTRONICS   |
|114       |Desk Lamp        |Electronics|650.0     |90      |South |Low     |Completed|767.0      |ELECTRONICS   |
|115       |Whiteboard       |Stationery |1100.0    |0       |East  |Medium  |Pending  |1298.0     |STATIONERY    |
|116       |Tablet           |Electronics|12999.0   |35      |North |High    |Completed|15338.82   |ELECTRONICS   |
|117       |Filing Cabinet   |Furniture  |3999.0    |12      |South |Low     |Cancelled|4718.82    |FURNITURE     |
|118       |Marker Set       |Stationery |199.0     |150     |East  |High    |Completed|234.82     |STATIONERY    |
|119       |Router           |Electronics|1799.0    |0       |West  |Medium  |Completed|2122.82    |ELECTRONICS   |
|120       |Wall Clock       |Furniture  |499.0     |60      |North |Low     |Completed|588.82     |FURNITURE     |
+----------+-----------------+-----------+----------+--------+------+--------+---------+-----------+--------------+


```

### 10. Null Handling (final)
```
Filled remaining nulls in 'quantity' with 0 before writing output.
```

### 11. Wide Transformation: groupBy(category).agg(...)  [causes shuffle]
```
+-----------+--------------+------------------+
|category   |total_quantity|avg_final_price   |
+-----------+--------------+------------------+
|Electronics|455           |6115.349999999999 |
|Furniture  |115           |3527.728          |
|Stationery |670           |462.85499999999996|
+-----------+--------------+------------------+


```

### 12. Action Examples
```
df.count() -> 18
(count/show are actions; select/filter/groupBy above were transformations)
```

### 12b. Filter: status == 'Completed' AND final_price > 1000
```
+----------+-----------------+-----------+----------+--------+------+--------+---------+-----------+--------------+
|product_id|item_name        |category   |unit_price|quantity|region|priority|status   |final_price|category_upper|
+----------+-----------------+-----------+----------+--------+------+--------+---------+-----------+--------------+
|102       |Bluetooth Speaker|Electronics|1999.0    |45      |South |Medium  |Completed|2358.82    |ELECTRONICS   |
|105       |LED Monitor      |Electronics|8999.0    |25      |North |Medium  |Completed|10618.82   |ELECTRONICS   |
|108       |Smartphone       |Electronics|15999.0   |60      |West  |High    |Completed|18878.82   |ELECTRONICS   |
|110       |Bookshelf        |Furniture  |2750.0    |18      |South |Low     |Completed|3245.0     |FURNITURE     |
|112       |Laptop Stand     |Electronics|899.0     |80      |West  |Medium  |Completed|1060.82    |ELECTRONICS   |
|116       |Tablet           |Electronics|12999.0   |35      |North |High    |Completed|15338.82   |ELECTRONICS   |
|119       |Router           |Electronics|1799.0    |0       |West  |Medium  |Completed|2122.82    |ELECTRONICS   |
+----------+-----------------+-----------+----------+--------+------+--------+---------+-----------+--------------+


```

### 12c. Filter: region == 'North' OR priority == 'High'
```
+----------+---------------+-----------+----------+--------+------+--------+---------+-----------+--------------+
|product_id|item_name      |category   |unit_price|quantity|region|priority|status   |final_price|category_upper|
+----------+---------------+-----------+----------+--------+------+--------+---------+-----------+--------------+
|101       |Wireless Mouse |Electronics|799.5     |120     |North |Low     |Completed|943.41     |ELECTRONICS   |
|103       |Office Chair   |Furniture  |4500.0    |15      |East  |High    |Pending  |5310.0     |FURNITURE     |
|105       |LED Monitor    |Electronics|8999.0    |25      |North |Medium  |Completed|10618.82   |ELECTRONICS   |
|108       |Smartphone     |Electronics|15999.0   |60      |West  |High    |Completed|18878.82   |ELECTRONICS   |
|109       |Gaming Keyboard|Electronics|2499.0    |0       |North |Medium  |Pending  |2948.82    |ELECTRONICS   |
|116       |Tablet         |Electronics|12999.0   |35      |North |High    |Completed|15338.82   |ELECTRONICS   |
|118       |Marker Set     |Stationery |199.0     |150     |East  |High    |Completed|234.82     |STATIONERY    |
|120       |Wall Clock     |Furniture  |499.0     |60      |North |Low     |Completed|588.82     |FURNITURE     |
+----------+---------------+-----------+----------+--------+------+--------+---------+-----------+--------------+


```

### Performance Note (Wide Transformation Timing)
```
groupBy/agg (wide transformation) wall time: 1.1201 seconds
```

### 13. Write CSV
```
Written to output/processed_csv/ (coalesced to 1 partition for a single readable file)
```

### 14. Write Parquet
```
Written to output/processed_parquet/ (columnar, snappy-compressed by default)
```

### 15. Performance Explanation
```
CSV output size (bytes)     : 1499
Parquet output size (bytes) : 3830

Physical Plan for a filtered read on Parquet (demonstrates Predicate Pushdown):

```

### 15b. Explain Plan (Predicate Pushdown on Parquet read)
```
== Parsed Logical Plan ==
'Filter '`>`('final_price, 1000)
+- Relation [product_id#329,item_name#330,category#331,unit_price#332,quantity#333,region#334,priority#335,status#336,final_price#337,category_upper#338] parquet

== Analyzed Logical Plan ==
product_id: int, item_name: string, category: string, unit_price: double, quantity: int, region: string, priority: string, status: string, final_price: double, category_upper: string
Filter (final_price#337 > cast(1000 as double))
+- Relation [product_id#329,item_name#330,category#331,unit_price#332,quantity#333,region#334,priority#335,status#336,final_price#337,category_upper#338] parquet

== Optimized Logical Plan ==
Filter (isnotnull(final_price#337) AND (final_price#337 > 1000.0))
+- Relation [product_id#329,item_name#330,category#331,unit_price#332,quantity#333,region#334,priority#335,status#336,final_price#337,category_upper#338] parquet

== Physical Plan ==
*(1) Filter (isnotnull(final_price#337) AND (final_price#337 > 1000.0))
+- *(1) ColumnarToRow
   +- FileScan parquet [product_id#329,item_name#330,category#331,unit_price#332,quantity#333,region#334,priority#335,status#336,final_price#337,category_upper#338] Batched: true, DataFilters: [isnotnull(final_price#337), (final_price#337 > 1000.0)], Format: Parquet, Location: InMemoryFileIndex(1 paths)[file:/home/claude/week6-spark-assignment/output/processed_parquet], PartitionFilters: [], PushedFilters: [IsNotNull(final_price), GreaterThan(final_price,1000.0)], ReadSchema: struct<product_id:int,item_name:string,category:string,unit_price:double,quantity:int,region:stri...


```
