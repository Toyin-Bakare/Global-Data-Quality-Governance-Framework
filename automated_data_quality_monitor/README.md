# Automated Data Quality Monitor (Great Expectations + Airflow + Slack Alerts + Trend Dashboard)

A portfolio-ready **Automated Data Quality Monitor** that continuously validates datasets, detects regressions,
and notifies teams when data quality breaks.

This project demonstrates:
- **Great Expectations** checkpoints (nulls, ranges, schema checks)
- **Automated scheduling** via **Apache Airflow**
- **Slack alerting** via webhook with actionable failure summaries
- **Historical tracking** of validation results in Postgres
- A lightweight **FastAPI dashboard** to view recent runs and failures
- A **local Docker Compose stack** that runs everything reproducibly

---

## Problem Statement

Data quality issues commonly show up as:
- upstream schema changes that silently break pipelines
- stale ingestions / missing partitions
- null-rate creep in key columns
- values out of expected range
- uniqueness violations for join keys

If checks run manually, issues are detected too late.

**Goal:** Run checks on a schedule, persist results, and alert immediately with context.

---

## Architecture

Airflow DAG (scheduled)
1. Generate + load demo dataset into Postgres (simulates warehouse ingestion)
2. Run Great Expectations checkpoint
3. Persist validation result (run + per-expectation results) into Postgres
4. If failed: Send Slack alert with failures + dashboard link
5. Dashboard reads Postgres to show trends / failures

---

## Repository Structure (How each file solves the problem)

### `dq_monitor/` (core app)
- `config.py` — config for DB + Slack webhook
- `db.py` — Postgres connection + migrations for result tables
- `validator.py` — runs GE checkpoint programmatically
- `result_store.py` — parses GE validation result JSON into normalized tables
- `slack.py` — formats + sends Slack alerts
- `dashboard.py` — FastAPI dashboard endpoints: `/runs`, `/failures`

### `airflow/`
- `airflow/dags/dq_monitor_dag.py` — DAG wiring tasks in order
- `airflow/plugins/dq_tasks.py` — task implementations (generate/load, validate, store, alert)

### `great_expectations/`
- `great_expectations.yml` — GE project config
- `expectations/customer_orders_suite.json` — expectation suite
- `checkpoints/daily_checkpoint.yml` — checkpoint definition

### `data/`
- `generate_demo_data.py` — demo data generator (with failure injection flags)
- `load_to_postgres.py` — loads CSV into Postgres warehouse table

### `infra/`
- `docker-compose.yml` — Postgres + Airflow + Dashboard
- `Dockerfile.airflow` — Airflow image with GE + project code
- `Dockerfile.dashboard` — Dashboard image
- `airflow.env` — environment config (DB URL, checkpoint, Slack)
- `entrypoint.sh` — bootstraps GE datasource and Airflow admin user

### `tests/`
- `test_slack_format.py` — Slack payload formatting
- `test_result_store.py` — smoke test for JSON formatting logic

---

## Quickstart (Local)

```bash
docker compose -f infra/docker-compose.yml up --build
```

Airflow UI: http://localhost:8081 (admin/admin)  
Dashboard: http://localhost:8090

Enable the DAG: `dq_monitor_dag`

### Optional: Force a failure to see Slack alerts
Set in `infra/airflow.env`:
- `INJECT_FAILURE=true`
- `SLACK_WEBHOOK_URL=...`

---

## Resume-ready highlights
- Built an automated data quality monitoring system using Great Expectations + Airflow + Postgres
- Implemented actionable Slack alerts with failed expectations and dashboard deep-links
- Persisted validation results for historical trending and regression detection
- Shipped dockerized local stack and a lightweight dashboard for visibility into quality over time
