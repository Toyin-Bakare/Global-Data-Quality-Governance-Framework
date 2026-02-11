from dataclasses import dataclass
from typing import Any, Dict, List
import yaml

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

@dataclass
class MetricDef:
    name: str
    type: str
    window_hours: int
    description: str | None = None
    event_type: str | None = None
    value_col: str | None = None
    any_event: bool = False

def load_metrics(path: str) -> List[MetricDef]:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    out = []
    for m in raw.get("metrics", []):
        out.append(MetricDef(
            name=m["name"],
            type=m["type"],
            window_hours=int(m["window_hours"]),
            description=m.get("description"),
            event_type=m.get("event_type"),
            value_col=m.get("value_col"),
            any_event=bool(m.get("any_event", False)),
        ))
    return out

def compute_user_level_metrics(exposures: DataFrame, outcomes: DataFrame, metrics: List[MetricDef]) -> DataFrame:
    """
    Returns one row per (experiment_id, user_id, variant) with metric columns.
    exposures: experiment_id, user_id, variant, exposure_ts
    outcomes: user_id, event_ts, event_type, value
    """
    base = exposures.select("experiment_id", "user_id", "variant", "exposure_ts")

    # Join outcomes within each metric's window (point-in-time safe)
    # Strategy: For each metric, filter outcomes by type, window, then aggregate per user.
    result = base

    for m in metrics:
        w_end = F.expr(f"exposure_ts + interval {m.window_hours} hours")

        o = outcomes
        if m.type in ("count_events", "sum_values") and m.event_type:
            o = o.filter(F.col("event_type") == F.lit(m.event_type))
        if m.type == "user_binary_active" and not m.any_event and m.event_type:
            o = o.filter(F.col("event_type") == F.lit(m.event_type))

        joined = (
            base.join(
                o,
                on=(base.user_id == o.user_id) &
                   (o.event_ts >= base.exposure_ts) &
                   (o.event_ts < w_end),
                how="left"
            )
        )

        if m.type == "count_events":
            agg = joined.groupBy("experiment_id", "user_id", "variant").agg(
                F.count(F.col("event_ts")).alias(m.name)
            )
        elif m.type == "sum_values":
            value_col = m.value_col or "value"
            agg = joined.groupBy("experiment_id", "user_id", "variant").agg(
                F.coalesce(F.sum(F.col(value_col)), F.lit(0.0)).alias(m.name)
            )
        elif m.type == "user_binary_active":
            agg = joined.groupBy("experiment_id", "user_id", "variant").agg(
                (F.max(F.col("event_ts").isNotNull().cast("int"))).alias(m.name)
            )
        else:
            raise ValueError(f"Unsupported metric type: {m.type}")

        result = result.join(agg, on=["experiment_id", "user_id", "variant"], how="left")

        # fill nulls after each metric
        result = result.withColumn(m.name, F.coalesce(F.col(m.name), F.lit(0)))

    return result
