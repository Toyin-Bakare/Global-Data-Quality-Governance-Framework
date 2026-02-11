from __future__ import annotations
import argparse
from pyspark.sql import SparkSession

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--path", required=True)
    p.add_argument("--limit", type=int, default=50)
    args = p.parse_args()

    spark = SparkSession.builder.appName("inspect-parquet").getOrCreate()
    df = spark.read.parquet(args.path)
    df.show(args.limit, truncate=False)
    spark.stop()

if __name__ == "__main__":
    main()
