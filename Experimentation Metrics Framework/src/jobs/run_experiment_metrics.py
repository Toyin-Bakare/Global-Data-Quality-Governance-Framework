import argparse
from pyspark.sql import functions as F

from framework.config import JobConfig
from framework.io import spark_session, read_parquet, write_parquet
from framework.metrics import load_metrics, compute_user_level_metrics
from framework.experiment import select_exposures, aggregate_variant, add_lift
from framework.checks import assert_no_nulls
from framework.cuped import compute_covariate, apply_cuped

def main(job_conf_path: str):
    cfg = JobConfig.load(job_conf_path)

    app_name = cfg.get("spark", "app_name", default="experiment-metrics")
    master = cfg.get("spark", "master", default="local[*]")
    spark = spark_session(app_name, master)

    exposures_path = cfg.get("inputs", "exposures_path")
    outcomes_path = cfg.get("inputs", "outcomes_path")

    exp_id = cfg.get("experiment", "experiment_id")
    attribution = cfg.get("experiment", "attribution", default="first_exposure")

    out_dir = cfg.get("outputs", "out_dir")
    out_mode = cfg.get("outputs", "mode", default="overwrite")

    metrics_file = cfg.get("metrics_file")
    metrics = load_metrics(metrics_file)

    exposures = read_parquet(spark, exposures_path)
    outcomes = read_parquet(spark, outcomes_path)

    # basic checks
    assert_no_nulls(exposures, ["experiment_id", "user_id", "variant", "exposure_ts"], "exposures")
    assert_no_nulls(outcomes, ["user_id", "event_ts", "event_type"], "outcomes")

    exp_exposures = select_exposures(exposures, exp_id, attribution).cache()

    user_metrics = compute_user_level_metrics(exp_exposures, outcomes, metrics).cache()

    # optional CUPED
    cuped_enabled = bool(cfg.get("cuped", "enabled", default=False))
    if cuped_enabled:
        pre_hours = int(cfg.get("cuped", "pre_period_hours", default=168))
        cov_event = cfg.get("cuped", "metric_for_covariate", default="play")
        cov = compute_covariate(exp_exposures, outcomes, cov_event, pre_hours)

        metric_cols = [m.name for m in metrics if m.type in ("count_events", "sum_values", "user_binary_active")]
        user_metrics = apply_cuped(user_metrics, cov, metric_cols)

    # aggregate by variant
    variant_agg = aggregate_variant(user_metrics)
    variant_lift = add_lift(variant_agg, control_variant="control")

    # write outputs
    write_parquet(user_metrics, f"{out_dir}/user_level_metrics.parquet", mode=out_mode)
    write_parquet(variant_lift, f"{out_dir}/variant_summary.parquet", mode=out_mode)

    print("Wrote outputs to:", out_dir)
    variant_lift.show(50, truncate=False)

    spark.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_conf", required=True)
    args = parser.parse_args()
    main(args.job_conf)
