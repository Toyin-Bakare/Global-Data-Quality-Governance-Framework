from __future__ import annotations
import argparse, json, random, time
from datetime import datetime, timezone
from kafka import KafkaProducer

def make_event(i: int, bad: bool):
    now = datetime.now(timezone.utc).isoformat()
    currencies = ["USD","NGN","GBP"]
    e = {"order_id": f"o-{i:09d}", "customer_id": f"c-{random.randint(1,20000):06d}",
         "amount_cents": random.randint(100, 300000), "currency": random.choice(currencies), "event_ts": now}
    if bad:
        mode = random.choice(["null_customer","bad_currency","out_of_range"])
        if mode == "null_customer": e["customer_id"] = None
        if mode == "bad_currency": e["currency"] = "XXX"
        if mode == "out_of_range": e["amount_cents"] = 999999999
    return e

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bootstrap", default="localhost:9092")
    p.add_argument("--topic", default="events.orders")
    p.add_argument("--seconds", type=int, default=30)
    p.add_argument("--bad-rate", type=float, default=0.05)
    args = p.parse_args()

    producer = KafkaProducer(bootstrap_servers=args.bootstrap, value_serializer=lambda v: json.dumps(v).encode("utf-8"), acks="all")
    start = time.time()
    i = 0
    while time.time() - start < args.seconds:
        producer.send(args.topic, make_event(i, random.random() < args.bad_rate))
        i += 1
        time.sleep(0.02)
    producer.flush()
    print(f"sent {i} events")

if __name__ == "__main__":
    main()
