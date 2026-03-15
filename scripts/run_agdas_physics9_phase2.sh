#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/benchmarks/results"
DATE_TAG="${DATE_TAG:-2026-03-15}"

mkdir -p "${OUT_DIR}"
OUT_JSON="${OUT_DIR}/${DATE_TAG}-agdas-physics9-phase2.json"

python3 "${ROOT_DIR}/scripts/agdas_physics_experiments.py" --template-set physics9 --json > "${OUT_JSON}"

echo "wrote ${OUT_JSON}"
