from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def assert_no_nulls(df: DataFrame, cols: list[str], name: str):
    exprs = [F.sum(F.col(c).isNull().cast("int")).alias(c) for c in cols]
    row = df.select(*exprs).collect()[0].asDict()
    bad = {k: v for k, v in row.items() if v and v > 0}
    if bad:
        raise ValueError(f"[{name}] Null check failed: {bad}")

def assert_unique(df: DataFrame, cols: list[str], name: str):
    total = df.count()
    distinct = df.select(*cols).distinct().count()
    if total != distinct:
        raise ValueError(f"[{name}] Uniqueness check failed for {cols}: total={total}, distinct={distinct}")
