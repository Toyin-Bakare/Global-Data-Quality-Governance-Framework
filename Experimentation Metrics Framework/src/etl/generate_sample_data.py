import os
import random
from datetime import datetime, timedelta, timezone

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DoubleType

BASE = "/opt/app/data/input"
os.makedirs(BASE, exist_ok=True)

def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def main():
    spark = (
        SparkSession.builder
        .appName("generate-sample-experiment-data")
        .master("local[*]")
        .getOrCreate()
    )

    random.seed(7)

    experiment_id = "exp_123"
    start = dt("2026-01-01T00:00:00Z")
    end = dt("2026-01-15T00:00:00Z")

    # Create exposures
    users = [f"u_{i:05d}" for i in range(1, 5001)]
    variants = ["control", "treatment"]

    exposures = []
    for u in users:
        exposure_time = start + timedelta(hours=random.randint(0, int((end-start).total_seconds()//3600)))
        variant = random.choices(variants, weights=[0.5, 0.5])[0]
        exposures.append((experiment_id, u, variant, exposure_time))

    exposure_schema = StructType([
        StructField("experiment_id", StringType(), False),
        StructField("user_id", StringType(), False),
        StructField("variant", StringType(), False),
        StructField("exposure_ts", TimestampType(), False),
    ])

    df_exp = spark.createDataFrame(exposures, schema=exposure_schema)

    # Create outcomes: play/search/purchase events around exposure
    outcome_schema = StructType([
        StructField("user_id", StringType(), False),
        StructField("event_ts", TimestampType(), False),
        StructField("event_type", StringType(), False),
        StructField("value", DoubleType(), True),
    ])

    outcomes = []
    for row in df_exp.select("user_id", "variant", "exposure_ts").collect():
        u, v, t0 = row["user_id"], row["variant"], row["exposure_ts"]

        # Pre-period activity (for CUPED covariate)
        pre_plays = random.randint(0, 6)
        for _ in range(pre_plays):
            ts = t0 - timedelta(hours=random.randint(1, 24*7))
            outcomes.append((u, ts, "play", None))

        # Post exposure behavior (treatment slightly higher)
        lift = 1.15 if v == "treatment" else 1.0

        post_plays = int(random.randint(0, 10) * lift)
        post_searches = int(random.randint(0, 6) * lift)

        for _ in range(post_plays):
            ts = t0 + timedelta(hours=random.randint(0, 24*7))
            outcomes.append((u, ts, "play", None))

        for _ in range(post_searches):
            ts = t0 + timedelta(hours=random.randint(0, 24*3))
            outcomes.append((u, ts, "search", None))

        # Purchases rarer; treatment slightly higher
        if random.random() < 0.06 * lift:
            ts = t0 + timedelta(hours=random.randint(0, 24*7))
            value = round(random.uniform(4.99, 19.99), 2)
            outcomes.append((u, ts, "purchase", value))

    df_out = spark.createDataFrame(outcomes, schema=outcome_schema)

    # Write parquet
    df_exp.write.mode("overwrite").parquet(f"{BASE}/exposures.parquet")
    df_out.write.mode("overwrite").parquet(f"{BASE}/outcomes.parquet")

    print("Wrote:")
    print(f" - {BASE}/exposures.parquet")
    print(f" - {BASE}/outcomes.parquet")

    spark.stop()

if __name__ == "__main__":
    main()
