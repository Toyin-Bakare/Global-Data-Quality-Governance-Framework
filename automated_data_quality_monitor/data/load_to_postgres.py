from __future__ import annotations
import argparse, csv, os
import psycopg2

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--table", default="customer_orders")
    p.add_argument("--db-url", default=os.getenv("DQ_DB_URL", "postgresql://dq:dq@localhost:5432/dq"))
    args = p.parse_args()

    ddl = f"""CREATE TABLE IF NOT EXISTS {args.table} (
      order_id TEXT PRIMARY KEY,
      customer_id TEXT,
      order_amount DOUBLE PRECISION,
      ingestion_ts TIMESTAMPTZ
    );
    TRUNCATE TABLE {args.table};
    """

    with psycopg2.connect(args.db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
            with open(args.csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [(r["order_id"], r["customer_id"] or None, float(r["order_amount"]), r["ingestion_ts"]) for r in reader]
            cur.executemany(
                f"INSERT INTO {args.table}(order_id, customer_id, order_amount, ingestion_ts) VALUES (%s,%s,%s,%s)",
                rows
            )
        conn.commit()

if __name__ == "__main__":
    main()
