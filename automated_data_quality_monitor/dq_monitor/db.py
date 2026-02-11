from __future__ import annotations
import psycopg2
from psycopg2.extras import RealDictCursor
from dq_monitor.config import settings

DDL = [
    """CREATE TABLE IF NOT EXISTS dq_run (
        run_id TEXT PRIMARY KEY,
        checkpoint_name TEXT NOT NULL,
        started_at TIMESTAMPTZ NOT NULL,
        success BOOLEAN NOT NULL,
        statistics JSONB NOT NULL
    );""",
    """CREATE TABLE IF NOT EXISTS dq_expectation_result (
        id BIGSERIAL PRIMARY KEY,
        run_id TEXT NOT NULL REFERENCES dq_run(run_id) ON DELETE CASCADE,
        expectation_type TEXT NOT NULL,
        column_name TEXT,
        success BOOLEAN NOT NULL,
        result JSONB NOT NULL
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

def fetch_all(sql: str, params=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()

def execute(sql: str, params=None):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
        conn.commit()
