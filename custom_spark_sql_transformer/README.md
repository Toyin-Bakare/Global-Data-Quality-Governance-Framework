# Custom Spark SQL Transformer 
(Config-Driven ETL with Templated SQL + UDFs + Data Quality Checks)

A project that implements a **config-driven Spark SQL transformation engine**.
It lets teams ship transformations as **SQL files + a YAML job spec**, without writing new Spark code per pipeline.

It supports:
- **Templated SQL** (Jinja-style variables/macros) for reusability across environments
- **Multiple inputs** (CSV/Parquet) registered as temporary views
- **UDF registration** (example: email domain extraction)
- **Data quality rules** (NOT NULL, uniqueness, row-count checks)
- **Operational metadata** (job_name, run_id, ingested_at columns)
- **Deterministic outputs** (Parquet) + optional partitioning

---

## Problem Statement

Analytics platforms often end up with lots of Spark jobs that are mostly:
- read input datasets
- run SQL transformations
- write outputs
- enforce some data quality checks
- add audit columns

When each pipeline is implemented as one-off code, you get:
- duplicated boilerplate
- inconsistent DQ gates and conventions
- harder-to-review changes
- slow iteration

**Goal:** Provide a reusable engine where:
- the **engine** (Spark, IO, DQ, UDFs) is stable
- the **pipeline logic** (SQL + YAML) changes quickly and is easy to review

---

## How It Works

1. Load YAML job spec
2. Read inputs and register temp views
3. Render SQL templates with variables/macros
4. Execute SQL steps to create output views
5. Enforce DQ rules
6. Add audit columns
7. Write output tables

---

## Repo Structure (How each file solves the problem)

### Engine (`transformer/`)
- `config.py` — typed config models (inputs, SQL steps, output, DQ rules)
- `sql_renderer.py` — Jinja2 rendering for templated SQL
- `udfs.py` — registers reusable UDFs into Spark SQL
- `quality.py` — implements DQ rules and produces a structured report
- `transformer.py` — orchestration engine
- `cli.py` — spark-submit friendly CLI entrypoint

### Example pipeline (`examples/`)
- `job_config.yml` — example job spec
- `sql/*.sql` — SQL steps
- `data/*.csv` — sample inputs
- `output/` — generated Parquet output directory (gitignored)

### Tools
- `tools/inspect_parquet.py` — prints a Parquet folder using Spark

### Tests (`tests/`)
- `conftest.py` — local SparkSession fixture
- `test_sql_renderer.py` — verifies templating
- `test_quality.py` — verifies DQ rules
- `test_transformer_end_to_end.py` — end-to-end run using tmp paths

---

## Quickstart

### 1) Install deps
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Run with spark-submit
```bash
spark-submit \
  --master local[2] \
  transformer/cli.py \
  --config examples/job_config.yml \
  --vars '{"run_date":"2026-02-09","env":"local"}' \
  --run-id demo_run_001
```

### 3) Inspect output
```bash
python tools/inspect_parquet.py --path examples/output/customer_revenue
```

---

## Project highlights
- Built a **config-driven Spark SQL transformation engine** (YAML + SQL) to eliminate per-pipeline boilerplate
- Added **templated SQL** with macros/variables for portability across environments
- Implemented **data quality gates** (null checks, uniqueness, row-count thresholds) with structured reports
- Added **UDF library + audit metadata columns** to standardize transformations across pipelines
- Shipped unit + end-to-end tests with local SparkSession
