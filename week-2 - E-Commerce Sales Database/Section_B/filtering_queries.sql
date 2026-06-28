-- Section B: Filtering & Optimization

-- Q7: Retrieve all orders with status = 'Delivered'
SELECT * FROM orders 
WHERE status = 'Delivered';

-- Q8: Find products in 'Electronics' with unit_price > 2000
SELECT * FROM products 
WHERE category = 'Electronics' 
  AND unit_price > 2000;

-- Q9: List customers who joined in 2024 and live in 'Maharashtra'
SELECT * FROM customers 
WHERE join_date >= '2024-01-01' 
  AND join_date <= '2024-12-31' 
  AND state = 'Maharashtra';

-- Q10: Find orders between '2024-08-10' and '2024-08-25' that are not cancelled
SELECT * FROM orders 
WHERE order_date BETWEEN '2024-08-10' AND '2024-08-25' 
  AND status <> 'Cancelled';

/*
Q11: What does idx_orders_date do? How does it improve query performance? Write a sample query.

- The index stores order_date in a sorted structure along with pointers to the actual table rows.
- Instead of scanning the whole table (O(N)), the database can quickly locate the rows using binary search (O(log N)).
- Sample query:
*/
SELECT * FROM orders WHERE order_date = '2024-08-15';

/*
Q12: Will the index on join_date be used for the query:
SELECT * FROM customers WHERE YEAR(join_date) = 2024;

- No. Wrapping the column in the YEAR() function prevents the database from using the index. 
  It has to run the function for every single row (Full Table Scan), making the query non-SARGable.
- SARGable rewritten query:
*/
SELECT * FROM customers 
WHERE join_date >= '2024-01-01' 
  AND join_date < '2025-01-01';
