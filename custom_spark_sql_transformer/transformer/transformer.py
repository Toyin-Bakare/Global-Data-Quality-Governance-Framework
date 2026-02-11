from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict

import yaml
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp

from transformer.config import JobSpec
from transformer.sql_renderer import load_and_render_sql
from transformer.udfs import register_udfs
from transformer.quality import enforce_quality

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class SparkSqlTransformer:
    def __init__(self, spark: SparkSession):
        self.spark = spark
        register_udfs(spark)

    @staticmethod
    def load_job_spec(path: str) -> JobSpec:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        return JobSpec.model_validate(raw)

    def _read_input(self, inp) -> None:
        if inp.format == "csv":
            df = self.spark.read.options(**({"header": "true", "inferSchema": "true"} | inp.options)).csv(inp.path)
        elif inp.format == "parquet":
            df = self.spark.read.options(**inp.options).parquet(inp.path)
        else:
            raise ValueError(f"Unsupported input format: {inp.format}")
        df.createOrReplaceTempView(inp.name)

    def _add_audit_columns(self, view: str, job_name: str, run_id: str) -> str:
        df = self.spark.table(view)
        audited = (
            df.withColumn("_job_name", lit(job_name))
              .withColumn("_run_id", lit(run_id))
              .withColumn("_ingested_at", current_timestamp())
        )
        out_view = f"{view}__audited"
        audited.createOrReplaceTempView(out_view)
        return out_view

    def run(self, spec: JobSpec, variables: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        for inp in spec.inputs:
            self._read_input(inp)

        for step in spec.sql_steps:
            sql = load_and_render_sql(step.sql_file, variables=variables)
            df = self.spark.sql(sql)
            if step.create_view:
                df.createOrReplaceTempView(step.create_view)

        enforce_quality(self.spark, spec.dq_rules)

        output_view = spec.output.view
        if spec.add_audit_columns:
            output_view = self._add_audit_columns(output_view, spec.job_name, run_id)

        out_df = self.spark.table(output_view)
        writer = out_df.write.mode(spec.output.mode)
        if spec.output.partition_by:
            writer = writer.partitionBy(*spec.output.partition_by)

        if spec.output.format == "parquet":
            writer.parquet(spec.output.path)
        else:
            raise ValueError(f"Unsupported output format: {spec.output.format}")

        return {
            "job_name": spec.job_name,
            "run_id": run_id,
            "output_view": output_view,
            "output_path": spec.output.path,
            "completed_at": _utc_now_iso(),
        }
