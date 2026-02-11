from __future__ import annotations
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.plugins.dq_tasks import (
    task_generate_and_load_demo_data,
    task_run_validation,
    task_store_results,
    task_slack_alert,
)

default_args = {"owner": "dq-monitor", "retries": 1, "retry_delay": timedelta(minutes=3)}

with DAG(
    dag_id="dq_monitor_dag",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["dq", "great_expectations"],
) as dag:

    t1 = PythonOperator(task_id="generate_and_load_demo_data", python_callable=task_generate_and_load_demo_data)
    t2 = PythonOperator(task_id="run_great_expectations_checkpoint", python_callable=task_run_validation)
    t3 = PythonOperator(task_id="store_validation_results", python_callable=task_store_results)
    t4 = PythonOperator(task_id="slack_alert_on_failure", python_callable=task_slack_alert, trigger_rule="all_done")

    t1 >> t2 >> t3 >> t4
