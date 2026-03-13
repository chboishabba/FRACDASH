#!/usr/bin/env bash
set -euo pipefail

## Default behavior is deterministic regression behavior:
## - chain bound is fixed (default 2) to lock down the fixed-prime full-space claim by failing the run if any run exceeds it,
## - output filename is date-stamped for artifact history.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT_DIR="benchmarks/results"
mkdir -p "$OUT_DIR"
TIMESTAMP="$(date +%Y-%m-%d)"
OUT_FILE="${OUT_DIR}/${TIMESTAMP}-toy-dashi-phase2.json"
CHAIN_BOUND="${FRACDASH_TOY_CHAIN_BOUND:-2}"
CHAIN_ARGS=("--max-chain-scan" "128")

if [[ "$CHAIN_BOUND" == "disable" ]]; then
  CHAIN_ARGS+=("--disable-chain-bound")
else
  CHAIN_ARGS+=("--max-chain-bound" "$CHAIN_BOUND")
fi

python3 scripts/toy_dashi_transitions.py \
  --json \
  "${CHAIN_ARGS[@]}" \
  > "$OUT_FILE"

echo "Wrote $OUT_FILE"
