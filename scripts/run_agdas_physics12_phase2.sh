#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/benchmarks/results"
DATE_TAG="$(date +%F)"

mkdir -p "${OUT_DIR}"

OUT_JSON="${OUT_DIR}/${DATE_TAG}-agdas-physics12-phase2.json"

python3 "${ROOT_DIR}/scripts/agdas_physics_experiments.py" --template-set physics12 --json > "${OUT_JSON}"

echo "wrote ${OUT_JSON}"
