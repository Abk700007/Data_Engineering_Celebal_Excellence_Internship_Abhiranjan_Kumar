-- Section D: Joins & Relationships

-- Q19: Inner join to show order along with customer first and last name
SELECT o.order_id, 
       o.order_date, 
       c.first_name, 
       c.last_name, 
       o.total_amount
FROM orders o
INNER JOIN customers c 
   ON o.customer_id = c.customer_id;

-- Q20: Left join to list all customers and their orders (including those with no orders)
SELECT c.customer_id, 
       c.first_name, 
       c.last_name, 
       c.city,
       o.order_id, 
       o.order_date, 
       o.status, 
       o.total_amount
FROM customers c
LEFT JOIN orders o 
   ON c.customer_id = o.customer_id;

-- Q21: Join across orders, order_items, and products
SELECT o.order_id, 
       p.product_name, 
       oi.quantity, 
       oi.unit_price, 
       oi.discount_pct
FROM orders o
INNER JOIN order_items oi 
   ON o.order_id = oi.order_id
INNER JOIN products p 
   ON oi.product_id = p.product_id;

/*
Q22: Difference between LEFT JOIN and RIGHT JOIN, and when to use FULL OUTER JOIN.

- LEFT JOIN: Returns all rows from the left table, and matched rows from the right table.
  Unmatched rows get NULLs. Example: `customers LEFT JOIN orders` shows all customers, even those who haven't ordered.
- RIGHT JOIN: Returns all rows from the right table, and matched rows from the left table.
  Example: `customers RIGHT JOIN orders` shows all orders. Since orders require a valid customer, this is like an INNER JOIN.
- FULL OUTER JOIN: Returns all rows when there is a match in either table. You would use it to combine two lists
  and keep unmatched rows from both sides (e.g. merging leads list and registered users list to find mismatches on both sides).
*/

/*
Q23: Foreign key relationships and inserting customer_id = 999.

- FK relations in schema:
  1. orders.customer_id -> customers.customer_id
  2. order_items.order_id -> orders.order_id
  3. order_items.product_id -> products.product_id

- Inserting order with customer_id = 999 fails with a Foreign Key Constraint violation error.
  The DB blocks it because 999 does not exist in the customers table, maintaining referential integrity.
*/
