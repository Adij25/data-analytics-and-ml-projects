"""Part A - cleaning. Run: python src/clean.py
Writes data/clean/*.csv and a local SQLite db (data/shop.db) used only to test the SQL."""
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

np.random.seed(42)
ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN = ROOT / "data/raw", ROOT / "data/clean"


def load_raw():
    return {n: pd.read_csv(RAW / f"task1_{n}.csv") for n in ["customers", "products", "orders", "order_items"]}


def clean(t, verbose=True):
    log = []
    cust, prod, orders, items = (t[k].copy() for k in ["customers", "products", "orders", "order_items"])

    # 1. duplicate orders (exact duplicate rows; order_id becomes unique afterwards)
    n0 = len(orders)
    orders = orders.drop_duplicates().reset_index(drop=True)
    assert orders.order_id.is_unique
    log.append(f"orders: removed {n0 - len(orders)} duplicate rows ({n0} -> {len(orders)})")

    # 2. state: strip/upper-case, then fill nulls from the customer's city (most common state of that city)
    cust["state"] = cust["state"].str.strip().str.upper()
    city_state = cust.dropna(subset=["state"]).groupby("city")["state"].agg(lambda s: s.mode().iat[0])
    n_null = int(cust["state"].isna().sum())
    cust["state"] = cust["state"].fillna(cust["city"].map(city_state)).fillna("UNKNOWN")
    log.append(f"customers.state: upper-cased; {n_null} nulls filled from city mode "
               f"({int((cust.state == 'UNKNOWN').sum())} left as UNKNOWN)")

    # 3. text dates -> datetime
    orders["order_date"] = pd.to_datetime(orders["order_date"], format="%d-%m-%Y")
    orders["delivery_date"] = pd.to_datetime(orders["delivery_date"], format="%d-%m-%Y")
    cust["signup_date"] = pd.to_datetime(cust["signup_date"])

    # 4. discount_pct is a discrete scheme {0,5,10,15,20}; 0 is both the mode and the median (~43% of rows).
    #    Fill with 0 = "no discount recorded": it never invents a discount, so revenue is not understated.
    #    A flag column keeps the imputation auditable.
    items["discount_imputed"] = items["discount_pct"].isna().astype(int)
    log.append(f"order_items.discount_pct: {int(items.discount_imputed.sum())} nulls filled with 0 (mode & median)")
    items["discount_pct"] = items["discount_pct"].fillna(0)

    # 5. missing delivery_date is legitimate for Cancelled/Shipped orders -> keep NaT, never impute
    miss = orders[orders.delivery_date.isna()].order_status.value_counts().to_dict()
    log.append(f"orders.delivery_date missing only for {miss} -> left null")

    # 6. derived columns
    items["revenue"] = (items["quantity"] * items["unit_price"] * (1 - items["discount_pct"] / 100)).round(2)
    orders["delivery_days"] = (orders["delivery_date"] - orders["order_date"]).dt.days
    orders["order_month"] = orders["order_date"].dt.strftime("%Y-%m")  # portable across Postgres/MySQL/SQLite

    # referential integrity
    assert items.order_id.isin(orders.order_id).all() and orders.customer_id.isin(cust.customer_id).all()
    assert items.product_id.isin(prod.product_id).all()
    if verbose:
        print("\n".join(log))
    return dict(customers=cust, products=prod, orders=orders, order_items=items), log


def export(c):
    CLEAN.mkdir(parents=True, exist_ok=True)
    for n, df in c.items():
        df.to_csv(CLEAN / f"{n}.csv", index=False, date_format="%Y-%m-%d")
    con = sqlite3.connect(ROOT / "data/shop.db")
    for n, df in c.items():
        d = df.copy()
        for col in d.select_dtypes("datetime").columns:
            d[col] = d[col].dt.strftime("%Y-%m-%d")
        d.to_sql(n, con, if_exists="replace", index=False)
    con.close()


if __name__ == "__main__":
    raw = load_raw()
    for n, df in raw.items():
        print(f"\n== {n} {df.shape}\n{df.dtypes.to_string()}\nnulls: {df.isna().sum()[df.isna().sum() > 0].to_dict()}")
    cleaned, _ = clean(raw)
    export(cleaned)
    print("\nexported ->", CLEAN)
