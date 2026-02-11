from __future__ import annotations
import argparse, json, os
from pyspark.sql import SparkSession
from transformer.transformer import SparkSqlTransformer

def main():
    p = argparse.ArgumentParser(description="Custom Spark SQL Transformer")
    p.add_argument("--config", required=True)
    p.add_argument("--vars", default="{}")
    p.add_argument("--run-id", default=None)
    args = p.parse_args()

    variables = json.loads(args.vars or "{}")
    run_id = args.run_id or variables.get("run_id") or f"run_{os.getpid()}"

    spark = SparkSession.builder.appName("custom-spark-sql-transformer").getOrCreate()
    engine = SparkSqlTransformer(spark)

    spec = engine.load_job_spec(args.config)
    result = engine.run(spec, variables=variables, run_id=run_id)
    print(json.dumps(result, indent=2))

    spark.stop()

if __name__ == "__main__":
    main()
