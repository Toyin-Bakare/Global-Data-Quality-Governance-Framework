# Experimentation Metrics Framework (Spark + YAML Metrics)

A reusable experimentation metrics pipeline that standardizes:
- exposure/assignment modeling
- outcome extraction (events, revenue, engagement)
- metric definitions (YAML)
- per-variant reporting + lift
- optional CUPED-style adjustment using pre-period behavior

## Why this exists
Experiment analysis breaks down when teams build one-off pipelines and inconsistent metrics.
This framework provides a platform-style foundation to scale experimentation reporting.

## Local quickstart
1) Start Spark
```bash
docker compose up -d

2) Generate sample data
docker exec -it spark-master python /opt/app/src/etl/generate_sample_data.py

3) Run metrics job
docker exec -it spark-master spark-submit /opt/app/src/jobs/run_experiment_metrics.py --job_conf /opt/app/conf/job.yaml

Outputs land in: data/output/

Key Concepts

Exposure table: experiment_id, user_id, variant, exposure_ts

Outcomes table: user_id, event_ts, event_type, value

Metrics: defined in YAML (count, sum, rate, avg per user), with windows relative to exposure

Spark UI: http://localhost:8080