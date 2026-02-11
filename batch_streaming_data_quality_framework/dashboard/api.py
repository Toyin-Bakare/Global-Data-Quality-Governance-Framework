from __future__ import annotations
from fastapi import FastAPI
from dq_core.result_store import migrate, fetch_latest_runs

app = FastAPI(title="DQ Framework Dashboard API", version="1.0.0")

@app.on_event("startup")
def _startup():
    migrate()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/runs")
def runs(limit: int = 50):
    return {"runs": fetch_latest_runs(limit=limit)}
