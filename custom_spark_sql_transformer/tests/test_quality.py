from pyspark.sql import Row
from transformer.config import NotNullRule, UniqueRule, RowCountRule
from transformer.quality import run_quality_checks

def test_quality_rules(spark):
    df = spark.createDataFrame([Row(id=1, v="a"), Row(id=1, v="b"), Row(id=2, v=None)])
    df.createOrReplaceTempView("t")

    rules = [
        NotNullRule(view="t", columns=["v"]),
        UniqueRule(view="t", columns=["id"]),
        RowCountRule(view="t", min=1, max=10),
    ]
    report = run_quality_checks(spark, rules)
    assert report.ok is False
    assert any(not c["passed"] for c in report.checks)
