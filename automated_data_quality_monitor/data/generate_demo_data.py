from __future__ import annotations
import argparse, csv, random
from datetime import datetime, timedelta, timezone

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--rows", type=int, default=200)
    p.add_argument("--inject-null-customer", action="store_true")
    p.add_argument("--inject-out-of-range", action="store_true")
    args = p.parse_args()

    now = datetime.now(timezone.utc)
    ingested_at = now - timedelta(minutes=5)

    customers = [f"c-{i:04d}" for i in range(1, 51)]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["order_id","customer_id","order_amount","ingestion_ts"])
        w.writeheader()
        for i in range(args.rows):
            cust = random.choice(customers)
            if args.inject_null_customer and i % 50 == 0:
                cust = ""
            amt = round(random.random() * 500 + 10, 2)
            if args.inject_out_of_range and i % 60 == 0:
                amt = 99999.0
            w.writerow({
                "order_id": f"o-{i:06d}",
                "customer_id": cust,
                "order_amount": amt,
                "ingestion_ts": ingested_at.isoformat(),
            })

if __name__ == "__main__":
    main()
