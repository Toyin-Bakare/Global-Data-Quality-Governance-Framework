from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

from transformer.config import DQRule, NotNullRule, UniqueRule, RowCountRule

@dataclass
class DQResult:
    ok: bool
    checks: List[Dict[str, Any]]

class DataQualityError(RuntimeError):
    def __init__(self, message: str, report: DQResult):
        super().__init__(message)
        self.report = report

def run_quality_checks(spark: SparkSession, rules: List[DQRule]) -> DQResult:
    checks: List[Dict[str, Any]] = []
    ok = True

    for rule in rules:
        if isinstance(rule, NotNullRule):
            df = spark.table(rule.view)
            for c in rule.columns:
                nulls = df.where(col(c).isNull()).count()
                passed = nulls == 0
                ok = ok and passed
                checks.append({"type": "not_null", "view": rule.view, "column": c, "null_count": nulls, "passed": passed})

        elif isinstance(rule, UniqueRule):
            df = spark.table(rule.view)
            dup = (
                df.groupBy(*[col(c) for c in rule.columns])
                  .count()
                  .where(col("count") > 1)
                  .count()
            )
            passed = dup == 0
            ok = ok and passed
            checks.append({"type": "unique", "view": rule.view, "columns": rule.columns, "duplicate_groups": dup, "passed": passed})

        elif isinstance(rule, RowCountRule):
            df = spark.table(rule.view)
            cnt = df.count()
            passed_min = (rule.min is None) or (cnt >= rule.min)
            passed_max = (rule.max is None) or (cnt <= rule.max)
            passed = passed_min and passed_max
            ok = ok and passed
            checks.append({"type": "row_count", "view": rule.view, "count": cnt, "min": rule.min, "max": rule.max, "passed": passed})
        else:
            ok = False
            checks.append({"type": "unknown", "passed": False, "rule": str(rule)})

    return DQResult(ok=ok, checks=checks)

def enforce_quality(spark: SparkSession, rules: List[DQRule]) -> None:
    report = run_quality_checks(spark, rules)
    if not report.ok:
        raise DataQualityError("Data quality checks failed", report)
