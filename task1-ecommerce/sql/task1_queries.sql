-- =====================================================================
-- Task 1 - SQL analysis. Tables: customers, products, orders, order_items
-- (loaded from data/clean/*.csv). Written in standard SQL: runs unchanged on
-- PostgreSQL 12+, MySQL 8+ and SQLite 3.25+.
-- Revenue = order_items.revenue (already quantity*unit_price*(1-discount/100)),
-- counted only for orders with order_status = 'Delivered' unless stated.
-- =====================================================================

-- Q1. Monthly revenue and month-over-month growth % (LAG)
WITH monthly AS (
    SELECT o.order_month,
           SUM(oi.revenue) AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.order_month
)
SELECT order_month,
       ROUND(revenue, 2) AS revenue,
       ROUND(LAG(revenue) OVER (ORDER BY order_month), 2) AS prev_month_revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY order_month))
             / NULLIF(LAG(revenue) OVER (ORDER BY order_month), 0), 2) AS mom_growth_pct
FROM monthly
ORDER BY order_month;


-- Q2. Top 10 products by revenue, with category and rank within the category
WITH product_rev AS (
    SELECT p.product_id, p.product_name, p.category,
           SUM(oi.revenue) AS revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.order_status = 'Delivered'
    GROUP BY p.product_id, p.product_name, p.category
),
ranked AS (
    SELECT *,
           RANK()       OVER (ORDER BY revenue DESC)                      AS overall_rank,
           DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS rank_in_category
    FROM product_rev
)
SELECT overall_rank, product_id, product_name, category,
       ROUND(revenue, 2) AS revenue, rank_in_category
FROM ranked
WHERE overall_rank <= 10
ORDER BY overall_rank;



-- Q3. % of customers who placed more than one order
-- (denominator = customers with at least one order; all order statuses count as "placed")
WITH cust_orders AS (
    SELECT customer_id, COUNT(*) AS n_orders
    FROM orders
    GROUP BY customer_id
)
SELECT COUNT(*)                                                          AS customers_with_orders,
       SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END)                     AS repeat_customers,
       ROUND(100.0 * SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_customer_pct
FROM cust_orders;



-- Q4a. Average delivery days per category (Delivered orders; an order with items from
--      several categories counts once per category it contains)
SELECT p.category,
       COUNT(DISTINCT o.order_id)        AS orders,
       ROUND(AVG(o.delivery_days), 2)    AS avg_delivery_days
FROM orders o
JOIN (SELECT DISTINCT order_id, product_id FROM order_items) oi ON oi.order_id = o.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.order_status = 'Delivered'
GROUP BY p.category
ORDER BY avg_delivery_days DESC;



-- Q4b. Average delivery days per state, flagging the 3 slowest states
WITH state_days AS (
    SELECT c.state,
           COUNT(*)                       AS orders,
           ROUND(AVG(o.delivery_days), 2) AS avg_delivery_days
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'Delivered'
    GROUP BY c.state
)
SELECT state, orders, avg_delivery_days,
       RANK() OVER (ORDER BY avg_delivery_days DESC) AS slowness_rank,
       CASE WHEN RANK() OVER (ORDER BY avg_delivery_days DESC) <= 3
            THEN 'SLOWEST 3' ELSE '' END AS flag
FROM state_days
ORDER BY avg_delivery_days DESC;


-- Q5. Running total of spend per customer, ordered by order date
--     (order value = sum of item revenue; Delivered orders only)
WITH order_value AS (
    SELECT o.customer_id, o.order_id, o.order_date,
           SUM(oi.revenue) AS order_value
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.customer_id, o.order_id, o.order_date
)
SELECT customer_id, order_id, order_date,
       ROUND(order_value, 2) AS order_value,
       ROUND(SUM(order_value) OVER (PARTITION BY customer_id
                                    ORDER BY order_date, order_id
                                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total
FROM order_value
ORDER BY customer_id, order_date, order_id;


-- Q6. Customers in the top 10% by lifetime spend (NTILE(10) = decile 1 is the top)
WITH lifetime AS (
    SELECT o.customer_id, SUM(oi.revenue) AS lifetime_spend
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'Delivered'
    GROUP BY o.customer_id
),
deciles AS (
    SELECT customer_id, lifetime_spend,
           NTILE(10) OVER (ORDER BY lifetime_spend DESC) AS decile
    FROM lifetime
)
SELECT d.customer_id, c.customer_name, c.state,
       ROUND(d.lifetime_spend, 2) AS lifetime_spend
FROM deciles d
JOIN customers c ON c.customer_id = d.customer_id
WHERE d.decile = 1
ORDER BY d.lifetime_spend DESC;


-- Q7. Cancellation and return rate by payment method (all orders in the denominator)
SELECT payment_method,
       COUNT(*) AS total_orders,
       SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
       SUM(CASE WHEN order_status = 'Returned'  THEN 1 ELSE 0 END) AS returned,
       ROUND(100.0 * SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate_pct,
       ROUND(100.0 * SUM(CASE WHEN order_status = 'Returned'  THEN 1 ELSE 0 END) / COUNT(*), 2) AS return_rate_pct
FROM orders
GROUP BY payment_method
ORDER BY cancellation_rate_pct DESC;
