-- PostgreSQL schema + load. Run from the task1-ecommerce folder with psql:
--   createdb shop && psql -d shop -f sql/00_load_postgres.sql
-- (\copy reads files from your machine; paths are relative to where psql is started)
DROP TABLE IF EXISTS order_items, orders, products, customers CASCADE;

CREATE TABLE customers (customer_id VARCHAR(10) PRIMARY KEY, customer_name TEXT, city TEXT,
                        state VARCHAR(10), signup_date DATE);
CREATE TABLE products  (product_id VARCHAR(10) PRIMARY KEY, product_name TEXT, category TEXT, price NUMERIC(12,2));
CREATE TABLE orders    (order_id VARCHAR(10) PRIMARY KEY, customer_id VARCHAR(10) REFERENCES customers,
                        order_date DATE, delivery_date DATE, order_status TEXT, payment_method TEXT,
                        delivery_days INT, order_month CHAR(7));
CREATE TABLE order_items (order_item_id VARCHAR(10) PRIMARY KEY, order_id VARCHAR(10) REFERENCES orders,
                        product_id VARCHAR(10) REFERENCES products, quantity INT, unit_price NUMERIC(12,2),
                        discount_pct NUMERIC(5,2), discount_imputed INT, revenue NUMERIC(14,2));

\copy customers   FROM 'data/clean/customers.csv'   CSV HEADER
\copy products    FROM 'data/clean/products.csv'    CSV HEADER
\copy orders      FROM 'data/clean/orders.csv'      CSV HEADER
\copy order_items FROM 'data/clean/order_items.csv' CSV HEADER

CREATE INDEX ON orders(customer_id); CREATE INDEX ON order_items(order_id); CREATE INDEX ON order_items(product_id);
