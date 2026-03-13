#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
OUT_DIR="${ROOT_DIR}/benchmarks/results"
DATE_TAG="$(date +%F)"
TEMPLATE_SET="${FRACDASH_AGDAS_TEMPLATE_SET:-wave1}"
OUT_JSON="${OUT_DIR}/${DATE_TAG}-agdas-template-${TEMPLATE_SET}-phase2.json"

mkdir -p "${OUT_DIR}"

CHAIN_BOUND="${FRACDASH_TOY_CHAIN_BOUND_TEMPLATE:-disable}"
CHAIN_ARGS=("--max-chain-scan" "128")
if [[ "${CHAIN_BOUND}" == "disable" ]]; then
  CHAIN_ARGS+=("--disable-chain-bound")
else
  CHAIN_ARGS+=("--max-chain-bound" "${CHAIN_BOUND}")
fi

python3 "${ROOT_DIR}/scripts/toy_dashi_transitions.py" \
  --json \
  --agdas-templates \
  --agdas-template-set "${TEMPLATE_SET}" \
  "${CHAIN_ARGS[@]}" \
  > "${OUT_JSON}"

echo "wrote ${OUT_JSON}"
