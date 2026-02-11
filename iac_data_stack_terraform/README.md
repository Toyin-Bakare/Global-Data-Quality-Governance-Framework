# Infrastructure-as-Code (IaC) 
Data Stack (Terraform) — AWS Reference Architecture

This repo is a **Terraform implementation** of a modern “data stack” baseline on AWS.

It provisions:
- **Networking:** VPC, public/private subnets, NAT, route tables, security groups
- **Storage:** S3 “data lake” buckets (raw / curated / logs) with encryption + lifecycle
- **Compute:** ECS Fargate cluster baseline (cluster, task roles, log groups)
- **Database:** RDS Postgres (private) for metadata/config
- **Observability:** CloudWatch log groups + example alarm
- **IAM:** least-privilege task execution + task roles
- **Env separation:** `envs/dev` and `envs/prod` using `modules/*`

---

## Problem Statement

Teams often bootstrap data platforms using console-created resources that:
- drift between environments,
- lack consistent encryption/access controls,
- are hard to reproduce and review.

**Goal:** A repeatable, secure Terraform baseline for a data platform that supports dev/prod and clean module reuse.

---

## High-Level Architecture

```
VPC
 ├─ Public subnets (IGW/NAT)
 └─ Private subnets (ECS tasks, RDS)

S3 Data Lake (raw/curated/logs)
RDS Postgres (private)
ECS Fargate cluster (baseline roles/logs)
CloudWatch (logs + baseline alarm)
```

---

## Repo Structure (How the code solves the problem)

### Root
- `versions.tf` — pins Terraform/providers
- `providers.tf` — AWS provider config
- `backend.tf.example` — remote state example (S3 + DynamoDB lock)
- `scripts/tf.sh` — convenience wrapper for init/plan/apply

### Environments
- `envs/dev` / `envs/prod`
  - `main.tf` wires modules
  - `variables.tf` inputs
  - `outputs.tf` exports
  - `terraform.tfvars.example` starter values

### Modules
- `modules/network` — VPC + subnets + NAT + routing
- `modules/s3_datalake` — secure buckets + lifecycle
- `modules/rds_postgres` — private RDS + subnet group + SG
- `modules/ecs_cluster` — ECS cluster + roles + log groups
- `modules/observability` — CloudWatch baseline

---

## Quickstart (Dev)

```bash
cp envs/dev/terraform.tfvars.example envs/dev/terraform.tfvars
cd envs/dev
terraform init
terraform plan
terraform apply
```

---

## Project highlights

- Built reusable Terraform modules for an AWS data platform baseline (VPC, S3, ECS, RDS)
- Enforced secure defaults: private RDS, blocked public S3 access, encryption at rest, lifecycle policies
- Implemented environment separation (dev/prod) with consistent networking and IAM roles
