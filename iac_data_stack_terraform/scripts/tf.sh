#!/usr/bin/env bash
set -euo pipefail
ENV_DIR="${1:-envs/dev}"
CMD="${2:-plan}"

cd "$ENV_DIR"
terraform fmt -recursive
terraform init -upgrade
terraform "$CMD" "${@:3}"
