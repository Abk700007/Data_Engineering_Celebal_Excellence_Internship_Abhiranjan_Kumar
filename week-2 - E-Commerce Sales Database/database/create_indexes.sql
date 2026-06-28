-- CREATE INDEXES sql script

-- Index for filtering customers by city or state
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_customers_state ON customers(state);

-- Index for filtering products by category
CREATE INDEX idx_products_category ON products(category);

-- Index for date-based filtering and sorting, and status filtering on orders
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);
