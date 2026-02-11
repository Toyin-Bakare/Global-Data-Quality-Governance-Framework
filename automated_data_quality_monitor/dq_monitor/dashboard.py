from __future__ import annotations
from fastapi import FastAPI
from dq_monitor.db import fetch_all, migrate

app = FastAPI(title="DQ Monitor Dashboard", version="1.0.0")

@app.on_event("startup")
def _startup():
    migrate()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/runs")
def runs(limit: int = 50):
    rows = fetch_all(
        """SELECT run_id, checkpoint_name, started_at, success, statistics
           FROM dq_run
           ORDER BY started_at DESC
           LIMIT %s""",
        (limit,),
    )
    return {"runs": rows}

@app.get("/failures")
def failures(limit: int = 200):
    rows = fetch_all(
        """SELECT e.run_id, r.started_at, r.checkpoint_name,
                  e.expectation_type, e.column_name, e.success, e.result
           FROM dq_expectation_result e
           JOIN dq_run r ON r.run_id = e.run_id
           WHERE e.success = false
           ORDER BY r.started_at DESC
           LIMIT %s""",
        (limit,),
    )
    return {"failures": rows}

if __name__ == "__main__":
    import os, uvicorn
    port = int(os.getenv("DASHBOARD_PORT", "8090"))
    uvicorn.run("dq_monitor.dashboard:app", host="0.0.0.0", port=port, reload=False)
