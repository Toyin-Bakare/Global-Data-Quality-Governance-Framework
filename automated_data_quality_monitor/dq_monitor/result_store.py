from __future__ import annotations
from typing import Any, Dict
from datetime import datetime, timezone
from dq_monitor.db import execute

def json_dumps(obj: Any) -> str:
    import json
    return json.dumps(obj, default=str)

def _now():
    return datetime.now(timezone.utc)

def store_validation_result(run_id: str, checkpoint_name: str, validation: Dict[str, Any]) -> None:
    success = bool(validation.get("success", False))
    stats = validation.get("statistics") or {}

    execute(
        """INSERT INTO dq_run(run_id, checkpoint_name, started_at, success, statistics)
           VALUES (%s, %s, %s, %s, %s)
           ON CONFLICT (run_id) DO UPDATE SET
             checkpoint_name=EXCLUDED.checkpoint_name,
             started_at=EXCLUDED.started_at,
             success=EXCLUDED.success,
             statistics=EXCLUDED.statistics""",
        (run_id, checkpoint_name, _now(), success, json_dumps(stats)),
    )

    for r in (validation.get("results") or []):
        exp = (r.get("expectation_config") or {})
        exp_type = exp.get("expectation_type")
        kwargs = exp.get("kwargs") or {}
        col = kwargs.get("column")
        res = r.get("result") or {}
        exp_success = bool(r.get("success", False))

        execute(
            """INSERT INTO dq_expectation_result(run_id, expectation_type, column_name, success, result)
               VALUES (%s, %s, %s, %s, %s)""",
            (run_id, exp_type, col, exp_success, json_dumps(res)),
        )
