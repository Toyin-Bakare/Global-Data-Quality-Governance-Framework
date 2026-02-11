# Automated Data Governance & Quality Engineering

An end-to-end framework for enforcing Data Quality (DQ) gates across hybrid batch/streaming environments. Shifting data management from reactive fixing to proactive, IaC-driven governance


### 1. Experimentation Metrics Framework
**Tech:** Spark, SQL, Python  
Reusable metrics pipeline for A/B testing with standardized exposure/outcome modeling and metric definitions.


📁 [`experimentation-metrics-framework`](https://github.com/Toyin-Bakare/Global-Data-Quality-Governance-Framework/tree/main/Experimentation%20Metrics%20Framework)

---

### 2. Batch + Streaming Data Quality Framework
**Tech:** Great Expectations / custom checks, Spark, SQL  
Automated data audits, anomaly detection, and freshness checks for large-scale datasets.

📁 [`data-quality-framework`]()

---


### 3. Custom Spark SQL Transformer 
**Tech:** Spark & Scala/Java  
A custom Spark library that performs a complex, non-standard data transformation (like PII masking or advanced currency conversion with historical lookups).

Focus: Optimize the Spark DAG and minimize data shuffling.

Use Case: Contribution to Databricks/Spark infrastructure at a platform level.

📁 [`Custom Spark SQL Transformer`](https://github.com/Toyin-Bakare/Global-Data-Quality-Governance-Framework/tree/main/custom_spark_sql_transformer)

---
### 4. Automated Data Quality Monitor 
**Tech:** Python & Snowflake/SQL  
Tool that runs scheduled "sanity checks" on a dataset (e.g., checking for nulls, outliers, or schema drift) and sends alerts to Slack/PagerDuty.

Focus: Use Great Expectations or a similar framework to define "data contracts."

Use Case: For Data Science and Risk teams who rely on clean, reliable data.

📁 [`Automated Data Quality Monitor`](https://github.com/Toyin-Bakare/Global-Data-Quality-Governance-Framework/tree/main/automated_data_quality_monitor)

---

### 5. Infrastructure-as-Code (IaC) for a Data Stack (Terraform) 
A repository that spins up an entire "Block-like" stack: a VPC, a Kafka cluster (via Confluent or Managed), and a Kubernetes cluster.

Focus: Focus on security (IAM roles, VPC peering, and encryption at rest).

Use Case: In the event you need to deploy your own project end-to-end including Infrasctructure deployment.

📁 [`Infrastructure-as-Code (IaC)`](https://github.com/Toyin-Bakare/Global-Data-Quality-Governance-Framework/tree/main/iac_data_stack_terraform)



=============
## Notes
- All projects are built as portfolio examples and do not include proprietary code.
- Where applicable, projects include local Docker setups for reproducibility.

---

## Contact
- LinkedIn: https://www.linkedin.com/in/toyinobakare
- Email: tonyobaker@gmail.com
