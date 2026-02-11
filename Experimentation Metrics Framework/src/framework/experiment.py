from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

def select_exposures(exposures: DataFrame, experiment_id: str, attribution: str) -> DataFrame:
    """
    attribution: first_exposure | last_exposure
    """
    df = exposures.filter(F.col("experiment_id") == F.lit(experiment_id))

    w = Window.partitionBy("experiment_id", "user_id").orderBy(F.col("exposure_ts").asc())
    if attribution == "last_exposure":
        w = Window.partitionBy("experiment_id", "user_id").orderBy(F.col("exposure_ts").desc())

    df = df.withColumn("rn", F.row_number().over(w)).filter(F.col("rn") == 1).drop("rn")
    return df

def aggregate_variant(user_metrics: DataFrame) -> DataFrame:
    """
    Computes:
    - n_users
    - mean of each metric per user
    """
    metric_cols = [c for c in user_metrics.columns if c not in ("experiment_id", "user_id", "variant", "exposure_ts")]

    agg_exprs = [F.countDistinct("user_id").alias("n_users")]
    for c in metric_cols:
        agg_exprs.append(F.avg(F.col(c)).alias(f"mean_{c}"))

    out = user_metrics.groupBy("experiment_id", "variant").agg(*agg_exprs)
    return out

def add_lift(variant_agg: DataFrame, control_variant: str = "control") -> DataFrame:
    """
    Adds lift vs control for mean_* columns.
    """
    means = [c for c in variant_agg.columns if c.startswith("mean_")]

    ctrl = (
        variant_agg.filter(F.col("variant") == F.lit(control_variant))
        .select("experiment_id", *[F.col(c).alias(f"ctrl_{c}") for c in means])
    )

    joined = variant_agg.join(ctrl, on="experiment_id", how="left")

    for c in means:
        joined = joined.withColumn(f"lift_{c[5:]}", (F.col(c) - F.col(f"ctrl_{c}")) / F.when(F.col(f"ctrl_{c}") == 0, F.lit(None)).otherwise(F.col(f"ctrl_{c}")))

    return joined
