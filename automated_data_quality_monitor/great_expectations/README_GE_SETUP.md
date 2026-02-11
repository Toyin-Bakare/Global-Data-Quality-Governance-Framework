# Great Expectations Setup Notes

In the Airflow container we keep the GE project at `/opt/great_expectations`.
On container start, `infra/entrypoint.sh` configures a Postgres datasource named `pg_dq`
using `DQ_DB_URL`.
