import os
from transformer.transformer import SparkSqlTransformer

def test_end_to_end(spark, tmp_path):
    root = tmp_path / "examples"
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "sql").mkdir(parents=True, exist_ok=True)
    (root / "output").mkdir(parents=True, exist_ok=True)

    (root / "data" / "customers.csv").write_text("customer_id,email,name,country\nc-001,Ada@Example.com,Ada Okafor,NG\nc-002,bola@example.com,Bola Adeyemi,NG\n")
    (root / "data" / "orders.csv").write_text("order_id,customer_id,amount\no-100,c-001,199.0\no-101,c-001,49.0\no-200,c-002,20.0\n")

    (root / "sql" / "01_customers_clean.sql").write_text("""SELECT
CAST(customer_id AS STRING) AS customer_id,
LOWER(TRIM(email)) AS email,
TRIM(name) AS name,
UPPER(TRIM(country)) AS country,
email_domain(LOWER(TRIM(email))) AS email_domain
FROM customers_raw
""")
    (root / "sql" / "02_customer_revenue.sql").write_text("""WITH orders_agg AS (
SELECT CAST(customer_id AS STRING) AS customer_id, SUM(CAST(amount AS DOUBLE)) AS total_revenue
FROM orders_raw GROUP BY CAST(customer_id AS STRING)
)
SELECT c.customer_id, c.email, c.country, COALESCE(o.total_revenue,0.0) AS total_revenue
FROM customers_clean c LEFT JOIN orders_agg o ON c.customer_id=o.customer_id
""")

    cfg = f"""job_name: test_job
inputs:
  - name: customers_raw
    path: {str(root / 'data' / 'customers.csv')}
    format: csv
    options: {{ header: "true", inferSchema: "true" }}
  - name: orders_raw
    path: {str(root / 'data' / 'orders.csv')}
    format: csv
    options: {{ header: "true", inferSchema: "true" }}
sql_steps:
  - name: clean_customers
    sql_file: {str(root / 'sql' / '01_customers_clean.sql')}
    create_view: customers_clean
  - name: customer_revenue
    sql_file: {str(root / 'sql' / '02_customer_revenue.sql')}
    create_view: customer_revenue
output:
  view: customer_revenue
  path: {str(root / 'output' / 'customer_revenue')}
  format: parquet
  mode: overwrite
  partition_by: []
dq_rules:
  - type: not_null
    view: customers_clean
    columns: ["customer_id","email"]
  - type: unique
    view: customers_clean
    columns: ["customer_id"]
add_audit_columns: true
"""
    cfg_path = root / "job.yml"
    cfg_path.write_text(cfg)

    engine = SparkSqlTransformer(spark)
    spec = engine.load_job_spec(str(cfg_path))
    engine.run(spec, variables={"env":"test","run_date":"2026-02-09"}, run_id="r1")

    out_path = str(root / "output" / "customer_revenue")
    assert os.path.exists(out_path)

    df = spark.read.parquet(out_path)
    assert df.count() == 2
    assert "_run_id" in df.columns
