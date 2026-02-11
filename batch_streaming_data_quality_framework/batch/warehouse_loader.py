from __future__ import annotations
import argparse, random
from datetime import datetime, timezone
import psycopg2

def ensure_table(cur):
    cur.execute(
        """CREATE TABLE IF NOT EXISTS wh_orders (
           order_id TEXT PRIMARY KEY,
           customer_id TEXT,
           amount_cents BIGINT,
           currency TEXT,
           event_ts TIMESTAMPTZ
        );"""
    )
    cur.execute("TRUNCATE TABLE wh_orders;")

def load_rows(cur, rows: int, bad_rate: float):
    now = datetime.now(timezone.utc)
    currencies = ["USD","NGN","GBP"]
    for i in range(rows):
        bad = random.random() < bad_rate
        order_id = f"o-{i:06d}"
        customer_id = None if (bad and i % 9 == 0) else f"c-{random.randint(1,500):05d}"
        amount = 999999999 if (bad and i % 17 == 0) else random.randint(100, 200000)
        currency = "XXX" if (bad and i % 23 == 0) else random.choice(currencies)
        cur.execute(
            "INSERT INTO wh_orders(order_id, customer_id, amount_cents, currency, event_ts) VALUES (%s,%s,%s,%s,%s)",
            (order_id, customer_id, amount, currency, now),
        )

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db-url", required=True)
    p.add_argument("--rows", type=int, default=500)
    p.add_argument("--bad-rate", type=float, default=0.05)
    args = p.parse_args()

    with psycopg2.connect(args.db_url) as conn:
        with conn.cursor() as cur:
            ensure_table(cur)
            load_rows(cur, args.rows, args.bad_rate)
        conn.commit()

if __name__ == "__main__":
    main()
