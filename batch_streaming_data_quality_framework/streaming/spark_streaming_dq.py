from __future__ import annotations
import os, uuid
from datetime import datetime

from pyspark.sql import SparkSession, functions as F, types as T
from dq_core.config import settings
from dq_core.result_store import migrate, insert_run, insert_rule_results
from dq_core.contracts import load_contract
from dq_core.alerting import build_slack_payload, send_slack

CONTRACT_PATH = os.getenv("DQ_CONTRACT_PATH", "/opt/app/contracts/orders.yaml")

schema = T.StructType([
    T.StructField("order_id", T.StringType(), True),
    T.StructField("customer_id", T.StringType(), True),
    T.StructField("amount_cents", T.LongType(), True),
    T.StructField("currency", T.StringType(), True),
    T.StructField("event_ts", T.StringType(), True),
])

def main():
    migrate()
    contract = load_contract(CONTRACT_PATH)

    spark = SparkSession.builder.appName("streaming-dq").getOrCreate()

    df = (spark.readStream.format("kafka")
          .option("kafka.bootstrap.servers", settings.kafka_bootstrap)
          .option("subscribe", settings.topic_orders)
          .option("startingOffsets", "latest")
          .load())

    parsed = (df.select(F.from_json(F.col("value").cast("string"), schema).alias("e"))
                .select("e.*")
                .withColumn("event_ts_ts", F.to_timestamp("event_ts")))

    windowed = (parsed.withWatermark("event_ts_ts", "2 minutes")
                .groupBy(F.window("event_ts_ts", "1 minute").alias("w"))
                .agg(
                    F.count("*").alias("n"),
                    F.sum(F.when(F.col("customer_id").isNull(), 1).otherwise(0)).alias("null_customer"),
                    F.sum(F.when(~F.col("currency").isin(["USD","NGN","GBP"]), 1).otherwise(0)).alias("bad_currency"),
                    F.sum(F.when((F.col("amount_cents") < 0) | (F.col("amount_cents") > 500000), 1).otherwise(0)).alias("bad_amount"),
                ))

    def handle(batch_df, batch_id: int):
        rows = batch_df.collect()
        for r in rows:
            run_id = str(uuid.uuid4())
            started = datetime.utcnow().isoformat()
            n = int(r["n"])
            null_rate = (int(r["null_customer"]) / n) if n else 0.0
            bad_currency_rate = (int(r["bad_currency"]) / n) if n else 0.0
            bad_amount_rate = (int(r["bad_amount"]) / n) if n else 0.0

            results = []
            failing = []
            severities = []

            for rule in contract.rules:
                ok = True
                metric = None
                if rule.id == "customer_id_not_null":
                    metric = null_rate
                    ok = metric <= 0.01
                elif rule.id == "currency_allowed":
                    metric = bad_currency_rate
                    ok = metric <= 0.01
                elif rule.id == "amount_in_range":
                    metric = bad_amount_rate
                    ok = metric <= 0.01
                elif rule.id == "order_id_not_null":
                    metric = 0.0
                    ok = True

                res = {"rule_id": rule.id, "rule_type": rule.type, "field": rule.field, "severity": rule.severity,
                       "success": bool(ok), "metric_value": float(metric) if metric is not None else None,
                       "details": {"window": str(r["w"]), "n": n}}
                results.append(res)
                if not ok:
                    failing.append(res)
                    severities.append(rule.severity)

            success = all(x["success"] for x in results)
            insert_run({"run_id": run_id, "run_type": "stream", "contract_name": contract.name, "entity": contract.entity,
                        "started_at": started, "success": success, "summary": {"window": str(r["w"]), "n": n, "failed": len(failing)}})
            insert_rule_results(run_id, results)

            if (not success) and settings.slack_webhook_url:
                severity = "high" if "high" in severities else ("medium" if "medium" in severities else "low")
                payload = build_slack_payload("Streaming DQ Failed", severity, f"{settings.dashboard_url}/runs?run_id={run_id}", failing)
                send_slack(settings.slack_webhook_url, payload)

    q = (windowed.writeStream.foreachBatch(handle)
         .outputMode("update")
         .option("checkpointLocation", "/tmp/spark-checkpoints/streaming-dq")
         .start())
    q.awaitTermination()

if __name__ == "__main__":
    main()
