#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASELINE="${1:-$ROOT/benchmarks/results/2026-03-13-cpu-matrix.jsonl}"
TIMESTAMP="$(date +%F_%H%M%S)"
CURRENT_OUT="${2:-$ROOT/benchmarks/results/$(date +%F)-cpu-matrix-regression-$TIMESTAMP.jsonl}"
TOLERANCE="${3:-0.50}"

mkdir -p "$(dirname "$CURRENT_OUT")"

"$ROOT/benchmarks/run_cpu_matrix.sh" "$CURRENT_OUT"

python3 "$ROOT/scripts/check_timing_regression.py" \
  --baseline "$BASELINE" \
  --current "$CURRENT_OUT" \
  --engine compiled \
  --engine frac-opt \
  --tolerance "$TOLERANCE"

echo "Current CPU matrix: $CURRENT_OUT"
