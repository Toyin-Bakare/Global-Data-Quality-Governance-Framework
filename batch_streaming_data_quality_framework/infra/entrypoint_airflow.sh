#!/usr/bin/env bash
set -e

python - <<'PY'
import os
from great_expectations.data_context import FileDataContext

root = os.getenv("GE_ROOT_DIR", "/opt/great_expectations")
db_url = os.getenv("DQ_DB_URL")
ctx = FileDataContext(context_root_dir=root)

names = [ds["name"] for ds in ctx.list_datasources()]
if "pg_dq" not in names:
    ctx.add_datasource(
        name="pg_dq",
        class_name="Datasource",
        execution_engine={"class_name":"SqlAlchemyExecutionEngine","connection_string": db_url},
        data_connectors={
            "default_runtime_data_connector_name": {
                "class_name":"RuntimeDataConnector",
                "batch_identifiers":["default_identifier_name"]
            }
        }
    )
PY

airflow db init
airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@example.com --password admin || true
airflow scheduler & exec airflow webserver
