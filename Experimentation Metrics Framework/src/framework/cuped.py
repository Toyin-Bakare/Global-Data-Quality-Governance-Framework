from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def compute_covariate(exposures: DataFrame, outcomes: DataFrame, event_type: str, pre_period_hours: int) -> DataFrame:
    """
    Covariate = count of pre-period event_type in [exposure_ts - pre_period_hours, exposure_ts)
    Returns: (experiment_id, user_id, variant, covariate)
    """
    base = exposures.select("experiment_id", "user_id", "variant", "exposure_ts")
    start = F.expr(f"exposure_ts - interval {pre_period_hours} hours")

    pre = outcomes.filter(F.col("event_type") == F.lit(event_type))

    joined = base.join(
        pre,
        on=(base.user_id == pre.user_id) &
           (pre.event_ts >= start) &
           (pre.event_ts < base.exposure_ts),
        how="left"
    )

    cov = joined.groupBy("experiment_id", "user_id", "variant").agg(
        F.count(F.col("event_ts")).alias("covariate")
    )
    return cov

def apply_cuped(user_metrics: DataFrame, covariate_df: DataFrame, metric_cols: list[str]) -> DataFrame:
    """
    CUPED adjusted metric: y_adj = y - theta*(x - mean_x)
    where theta = cov(y, x)/var(x) computed over all users.
    """
    df = user_metrics.join(covariate_df, on=["experiment_id", "user_id", "variant"], how="left") \
                     .withColumn("covariate", F.coalesce(F.col("covariate"), F.lit(0.0)))

    mean_x = df.agg(F.avg("covariate").alias("mean_x")).collect()[0]["mean_x"]
    var_x = df.agg(F.var_samp("covariate").alias("var_x")).collect()[0]["var_x"]

    # If var is 0, skip
    if var_x is None or var_x == 0:
        return df

    for m in metric_cols:
        cov_yx = df.agg(F.covar_samp(F.col(m).cast("double"), F.col("covariate").cast("double")).alias("cov")).collect()[0]["cov"]
        theta = (cov_yx / var_x) if cov_yx is not None else 0.0

        df = df.withColumn(
            f"{m}_cuped",
            F.col(m).cast("double") - F.lit(theta) * (F.col("covariate") - F.lit(mean_x))
        )

    return df
