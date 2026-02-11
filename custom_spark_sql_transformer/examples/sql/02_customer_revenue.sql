WITH orders_agg AS (
  SELECT
    CAST(customer_id AS STRING) AS customer_id,
    SUM(CAST(amount AS DOUBLE)) AS total_revenue,
    COUNT(1) AS order_count
  FROM orders_raw
  GROUP BY CAST(customer_id AS STRING)
)
SELECT
  c.customer_id,
  c.email,
  c.name,
  c.country,
  c.email_domain,
  COALESCE(o.total_revenue, 0.0) AS total_revenue,
  COALESCE(o.order_count, 0) AS order_count
FROM customers_clean c
LEFT JOIN orders_agg o
  ON c.customer_id = o.customer_id
