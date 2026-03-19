#!/usr/bin/env bash
# Reproduce the physics1 oracle artifact deterministically.

set -e

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")

echo "Regenerating physics1 oracle artifacts..."
python3 "$SCRIPT_DIR/export_physics1_deltas.py" --canonical

echo "Physics1 oracle reproduction complete."
echo "Canonical artifact: benchmarks/results/physics1_deltas_canonical.json"
