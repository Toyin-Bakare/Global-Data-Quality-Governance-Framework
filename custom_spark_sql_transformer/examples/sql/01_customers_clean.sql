SELECT
  CAST(customer_id AS STRING) AS customer_id,
  LOWER(TRIM(email)) AS email,
  TRIM(name) AS name,
  UPPER(TRIM(country)) AS country,
  email_domain(LOWER(TRIM(email))) AS email_domain,
  '{{ env }}' AS env_tag,
  '{{ run_date }}' AS run_date
FROM customers_raw
WHERE customer_id IS NOT NULL
