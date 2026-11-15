"""Load the cleaned CSVs into MySQL without LOAD DATA (no server settings needed).
    python src/load_mysql.py            # asks for host/user/password
Env vars MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT are used if set."""
import os
from getpass import getpass
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

CLEAN = Path(__file__).resolve().parents[1] / "data/clean"
host = os.getenv("MYSQL_HOST", "localhost")
port = os.getenv("MYSQL_PORT", "3306")
user = os.getenv("MYSQL_USER") or input("MySQL user [root]: ") or "root"
pwd = os.getenv("MYSQL_PASSWORD") or getpass("MySQL password: ")

DDL = [
    "CREATE DATABASE IF NOT EXISTS shop",
    "USE shop",
    "DROP TABLE IF EXISTS order_items", "DROP TABLE IF EXISTS orders",
    "DROP TABLE IF EXISTS products", "DROP TABLE IF EXISTS customers",
    """CREATE TABLE customers (customer_id VARCHAR(10) PRIMARY KEY, customer_name VARCHAR(100), city VARCHAR(60),
        state VARCHAR(10), signup_date DATE)""",
    """CREATE TABLE products (product_id VARCHAR(10) PRIMARY KEY, product_name VARCHAR(100), category VARCHAR(50),
        price DECIMAL(12,2))""",
    """CREATE TABLE orders (order_id VARCHAR(10) PRIMARY KEY, customer_id VARCHAR(10), order_date DATE,
        delivery_date DATE NULL, order_status VARCHAR(20), payment_method VARCHAR(30), delivery_days INT NULL,
        order_month CHAR(7), FOREIGN KEY (customer_id) REFERENCES customers(customer_id))""",
    """CREATE TABLE order_items (order_item_id VARCHAR(10) PRIMARY KEY, order_id VARCHAR(10), product_id VARCHAR(10),
        quantity INT, unit_price DECIMAL(12,2), discount_pct DECIMAL(5,2), discount_imputed INT, revenue DECIMAL(14,2),
        FOREIGN KEY (order_id) REFERENCES orders(order_id), FOREIGN KEY (product_id) REFERENCES products(product_id))""",
]

server = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}:{port}/")
with server.begin() as con:
    for stmt in DDL:
        con.execute(text(stmt))

db = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}:{port}/shop")
for name, dates in [("customers", ["signup_date"]), ("products", []),
                    ("orders", ["order_date", "delivery_date"]), ("order_items", [])]:   # parents before children
    df = pd.read_csv(CLEAN / f"{name}.csv", parse_dates=dates)
    df = df.astype(object).where(df.notna(), None)          # NaN/NaT -> NULL
    df.to_sql(name, db, if_exists="append", index=False, chunksize=2000)
    print(f"{name}: {len(df):,} rows loaded")

with db.begin() as con:
    for stmt in ["CREATE INDEX idx_orders_cust ON orders(customer_id)",
                 "CREATE INDEX idx_items_order ON order_items(order_id)",
                 "CREATE INDEX idx_items_prod ON order_items(product_id)"]:
        con.execute(text(stmt))
    print("orders in DB:", con.execute(text("SELECT COUNT(*) FROM orders")).scalar(), "(expect 15000)")
