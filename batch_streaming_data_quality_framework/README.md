# Batch + Streaming Data Quality Framework 
(Great Expectations + Kafka + Spark + Airflow + Alerts)

A **data quality platform** that validates **batch** and **streaming** pipelines using a unified control plane:
- **Batch DQ**: scheduled validations (Airflow) against warehouse tables or files
- **Streaming DQ**: real-time checks on Kafka events (Spark Structured Streaming) with sliding-window metrics
- **Shared rule registry**: DQ rules stored as YAML “contracts”
- **Central result store**: Postgres schema for runs, expectations, and incidents
- **Alerting**: Slack webhook alerts with severity
- **Local-first**: Docker Compose runs Postgres + Kafka + Spark + Airflow + Dashboard API

---

## Quickstart

```bash
docker compose -f infra/docker-compose.yml up --build
```

- Airflow UI: http://localhost:8081 (admin/admin)
- Dashboard API: http://localhost:8091

Produce events:
```bash
docker exec -it dq_kafka bash -lc "python /opt/app/streaming/kafka_producer.py --seconds 30 --bad-rate 0.08"
```

Run batch DQ:
- Enable DAG `batch_dq_dag` in Airflow and trigger.

---

## Repo Map (How files solve the problem)

### Core library (`dq_core/`)
- `contracts.py` parses YAML contracts into executable rules
- `metrics.py` implements reusable DQ metrics (null rate, range, allowed values)
- `result_store.py` provides Postgres schema + persistence for DQ runs/results/incidents
- `alerting.py` formats and sends Slack alerts
- `config.py` centralizes env configuration

### Batch
- `batch/warehouse_loader.py` loads a demo “warehouse” table in Postgres
- `batch/ge_runner.py` runs Great Expectations validations from the same contract
- `airflow/dags/batch_dq_dag.py` schedules batch validations + alerts

### Streaming
- `streaming/kafka_producer.py` produces good/bad events to Kafka for demo
- `streaming/spark_streaming_dq.py` reads Kafka and computes windowed metrics with Spark

### Dashboard
- `dashboard/api.py` exposes REST endpoints to query runs/incidents

### Infra
- `infra/docker-compose.yml` runs the full stack locally
- `infra/Dockerfile.*` container images for Airflow/Spark/Dashboard

---

## Project highlights

- Built a unified **batch + streaming data quality framework** with contract-driven rules reused across ETL and Kafka pipelines
- Implemented **real-time DQ** using Spark Structured Streaming with sliding-window metrics and schema checks
- Persisted validation outcomes to Postgres and implemented alerting via Slack
- Delivered a dockerized local stack and an API for querying runs and incidents
