from __future__ import annotations
from datetime import datetime, timedelta
import json, os, uuid
import psycopg2

from airflow import DAG
from airflow.operators.python import PythonOperator

from dq_core.contracts import load_contract
from dq_core.result_store import migrate, insert_run, insert_rule_results
from dq_core.alerting import build_slack_payload, send_slack
from dq_core.config import settings
from batch.ge_runner import run_contract_against_postgres
from batch.warehouse_loader import ensure_table, load_rows

DEFAULT_ARGS = {"owner": "dq", "retries": 1, "retry_delay": timedelta(minutes=2)}
CONTRACT_PATH = "/opt/app/contracts/orders.yaml"

def load_demo():
    db_url = os.getenv("DQ_DB_URL")
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            ensure_table(cur)
            load_rows(cur, rows=500, bad_rate=float(os.getenv("BATCH_BAD_RATE", "0.05")))
        conn.commit()

def run_batch(ti):
    migrate()
    contract = load_contract(CONTRACT_PATH)
    run_id = str(uuid.uuid4())
    started = datetime.utcnow().isoformat()

    ge = run_contract_against_postgres(contract, query="SELECT * FROM wh_orders")
    ge_results = ge.get("results") or []

    results = []
    for idx, rule in enumerate(contract.rules):
        r = ge_results[idx] if idx < len(ge_results) else {}
        ok = bool(r.get("success", False))
        results.append({
            "rule_id": rule.id,
            "rule_type": rule.type,
            "field": rule.field,
            "severity": rule.severity,
            "success": ok,
            "metric_value": None,
            "details": {"ge_result": r.get("result") or {}},
        })

    success = all(x["success"] for x in results)
    summary = {"evaluated": len(results), "failed": sum(1 for x in results if not x["success"])}

    insert_run({
        "run_id": run_id,
        "run_type": "batch",
        "contract_name": contract.name,
        "entity": contract.entity,
        "started_at": started,
        "success": success,
        "summary": summary,
    })
    insert_rule_results(run_id, results)

    ti.xcom_push(key="run_id", value=run_id)
    ti.xcom_push(key="success", value=success)
    ti.xcom_push(key="failed_rules", value=json.dumps([r for r in results if not r["success"]]))

def alert(ti):
    if not settings.slack_webhook_url:
        return
    if ti.xcom_pull(key="success"):
        return
    run_id = ti.xcom_pull(key="run_id")
    failed = json.loads(ti.xcom_pull(key="failed_rules") or "[]")
    payload = build_slack_payload("Batch DQ Failed", "high", f"{settings.dashboard_url}/runs?run_id={run_id}", failed)
    send_slack(settings.slack_webhook_url, payload)

with DAG(
    dag_id="batch_dq_dag",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["dq","batch"],
) as dag:
    t0 = PythonOperator(task_id="load_demo_warehouse_table", python_callable=load_demo)
    t1 = PythonOperator(task_id="run_batch_dq", python_callable=run_batch)
    t2 = PythonOperator(task_id="slack_alert_on_failure", python_callable=alert, trigger_rule="all_done")
    t0 >> t1 >> t2
