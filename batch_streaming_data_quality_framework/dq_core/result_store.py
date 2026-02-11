from __future__ import annotations
import json
from typing import Any, Dict, List
import psycopg2
from psycopg2.extras import RealDictCursor
from dq_core.config import settings

DDL = [
"""CREATE TABLE IF NOT EXISTS dq_run (
  run_id TEXT PRIMARY KEY,
  run_type TEXT NOT NULL,
  contract_name TEXT NOT NULL,
  entity TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  success BOOLEAN NOT NULL,
  summary JSONB NOT NULL
);""",
"""CREATE TABLE IF NOT EXISTS dq_rule_result (
  id BIGSERIAL PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES dq_run(run_id) ON DELETE CASCADE,
  rule_id TEXT NOT NULL,
  rule_type TEXT NOT NULL,
  field TEXT,
  severity TEXT NOT NULL,
  success BOOLEAN NOT NULL,
  metric_value DOUBLE PRECISION,
  details JSONB NOT NULL
);""",
]

def get_conn(db_url: str | None = None):
    return psycopg2.connect(db_url or settings.db_url)

def migrate():
    with get_conn() as conn:
        with conn.cursor() as cur:
            for stmt in DDL:
                cur.execute(stmt)
        conn.commit()

def insert_run(run: Dict[str, Any]) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO dq_run(run_id, run_type, contract_name, entity, started_at, success, summary)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (run_id) DO UPDATE SET success=EXCLUDED.success, summary=EXCLUDED.summary""",
                (run["run_id"], run["run_type"], run["contract_name"], run["entity"], run["started_at"], run["success"], json.dumps(run["summary"]))
            )
        conn.commit()

def insert_rule_results(run_id: str, results: List[Dict[str, Any]]) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            for r in results:
                cur.execute(
                    """INSERT INTO dq_rule_result(run_id, rule_id, rule_type, field, severity, success, metric_value, details)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (run_id, r["rule_id"], r["rule_type"], r.get("field"), r["severity"], r["success"], r.get("metric_value"), json.dumps(r.get("details") or {}))
                )
        conn.commit()

def fetch_latest_runs(limit: int = 50):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM dq_run ORDER BY started_at DESC LIMIT %s", (limit,))
            return cur.fetchall()
