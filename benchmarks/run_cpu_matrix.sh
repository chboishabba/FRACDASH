#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_PATH="${1:-$ROOT/benchmarks/results/$(date +%F)-cpu-matrix.jsonl}"

mkdir -p "$(dirname "$OUT_PATH")"
: > "$OUT_PATH"

(cd "$ROOT/fractran" && ./build.sh >/dev/null)

declare -a scenarios=(
  "mult_smoke"
  "primegame_small"
  "primegame_medium"
  "primegame_large"
)

for scenario in "${scenarios[@]}"; do
  if [[ "$scenario" == "mult_smoke" ]]; then
    declare -a engines=("naive-fast" "reg" "frac-opt" "cycle" "compiled")
  else
    declare -a engines=("reg" "frac-opt" "cycle" "compiled")
  fi

  for engine in "${engines[@]}"; do
    checkpoint_policy="exact"
    if [[ "$engine" == "cycle" ]]; then
      checkpoint_policy="at-least"
    fi
    "$ROOT/fractran/fractran-bench" \
      --scenario "$scenario" \
      --engine "$engine" \
      --mode logical-steps \
      --checkpoint-policy "$checkpoint_policy" \
      --repeats 5 \
      --output "$OUT_PATH" \
      >/dev/null
  done
done

echo "$OUT_PATH"
