from __future__ import annotations
import os, json, subprocess
from dq_monitor.validator import run_checkpoint, new_run_id
from dq_monitor.result_store import store_validation_result
from dq_monitor.slack import build_slack_payload, send_slack
from dq_monitor.db import migrate

def task_generate_and_load_demo_data(**_kwargs):
    migrate()
    out_csv = "/tmp/customer_orders.csv"
    inject_failure = os.getenv("INJECT_FAILURE", "false").lower() == "true"
    cmd = ["python", "-m", "data.generate_demo_data", "--out", out_csv, "--rows", "200"]
    if inject_failure:
        cmd += ["--inject-null-customer"]
    subprocess.check_call(cmd)
    subprocess.check_call(["python", "-m", "data.load_to_postgres", "--csv", out_csv, "--table", "customer_orders"])

def task_run_validation(ti, **_kwargs):
    run_id = new_run_id()
    ti.xcom_push(key="run_id", value=run_id)
    checkpoint_name = os.getenv("GE_CHECKPOINT", "daily_checkpoint")
    result = run_checkpoint(checkpoint_name=checkpoint_name)
    ti.xcom_push(key="checkpoint_name", value=checkpoint_name)
    ti.xcom_push(key="validation_json", value=json.dumps(result, default=str))

def _first_validation(validation: dict) -> dict:
    run_results = validation.get("run_results") or {}
    first_key = next(iter(run_results.keys()))
    first = run_results[first_key]
    return first.get("validation_result") or {}

def task_store_results(ti, **_kwargs):
    migrate()
    run_id = ti.xcom_pull(key="run_id")
    checkpoint_name = ti.xcom_pull(key="checkpoint_name")
    validation = json.loads(ti.xcom_pull(key="validation_json"))
    vres = _first_validation(validation)
    store_validation_result(run_id=run_id, checkpoint_name=checkpoint_name, validation=vres)

def task_slack_alert(ti, **_kwargs):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        print("SLACK_WEBHOOK_URL not set; skipping Slack alert.")
        return
    run_id = ti.xcom_pull(key="run_id")
    checkpoint_name = ti.xcom_pull(key="checkpoint_name")
    validation = json.loads(ti.xcom_pull(key="validation_json"))
    vres = _first_validation(validation)

    if bool(vres.get("success", False)):
        print("DQ passed; no Slack alert.")
        return

    dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8090")
    payload = build_slack_payload(run_id, checkpoint_name, vres, dashboard_url=dashboard_url)
    send_slack(webhook, payload)
