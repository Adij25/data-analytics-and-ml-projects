-- MySQL 8.0+ schema + load (Option B). Run from the task1-ecommerce folder:
--   mysql --local-infile=1 -u root -p < sql/00_load_mysql.sql
-- Needs local_infile enabled on the server:  SET GLOBAL local_infile = 1;  (run once as root)
-- If that is blocked, use the Python loader instead (src/load_mysql.py) - it needs no special settings.
CREATE DATABASE IF NOT EXISTS shop;
USE shop;
DROP TABLE IF EXISTS order_items; DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;    DROP TABLE IF EXISTS customers;

CREATE TABLE customers (customer_id VARCHAR(10) PRIMARY KEY, customer_name VARCHAR(100), city VARCHAR(60),
                        state VARCHAR(10), signup_date DATE);
CREATE TABLE products  (product_id VARCHAR(10) PRIMARY KEY, product_name VARCHAR(100), category VARCHAR(50),
                        price DECIMAL(12,2));
CREATE TABLE orders    (order_id VARCHAR(10) PRIMARY KEY, customer_id VARCHAR(10), order_date DATE,
                        delivery_date DATE NULL, order_status VARCHAR(20), payment_method VARCHAR(30),
                        delivery_days INT NULL, order_month CHAR(7),
                        FOREIGN KEY (customer_id) REFERENCES customers(customer_id));
CREATE TABLE order_items (order_item_id VARCHAR(10) PRIMARY KEY, order_id VARCHAR(10), product_id VARCHAR(10),
                        quantity INT, unit_price DECIMAL(12,2), discount_pct DECIMAL(5,2), discount_imputed INT,
                        revenue DECIMAL(14,2),
                        FOREIGN KEY (order_id) REFERENCES orders(order_id),
                        FOREIGN KEY (product_id) REFERENCES products(product_id));

LOAD DATA LOCAL INFILE 'data/clean/customers.csv' INTO TABLE customers
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE 'data/clean/products.csv' INTO TABLE products
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
-- empty delivery_date / delivery_days (cancelled & shipped orders) must become NULL, not ''
LOAD DATA LOCAL INFILE 'data/clean/orders.csv' INTO TABLE orders
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES
  (order_id, customer_id, order_date, @dd, order_status, payment_method, @days, order_month)
  SET delivery_date = NULLIF(@dd, ''), delivery_days = NULLIF(@days, '');
LOAD DATA LOCAL INFILE 'data/clean/order_items.csv' INTO TABLE order_items
  FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;

CREATE INDEX idx_orders_cust ON orders(customer_id);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_items_prod  ON order_items(product_id);
