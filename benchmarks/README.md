# Benchmarks

Initial FRACDASH benchmark artifacts live in `benchmarks/results/`.

Current baseline notes:

- The local `fractran/` checkout is the CPU reference implementation.
- `fractran-bench` exposes these engines for comparison:
  - `reg`
  - `frac-opt`
  - `cycle`
  - `compiled`
  - `lut`
- The current `compiled` engine is now the active exact-step CPU baseline for the sampled `primegame` workloads.
- The benchmark harness now summarizes `compiled` by tracking emitted integer values directly, avoiding repeated `unfExpVec` reconstruction during checksum generation.
- The current `lut` engine is limited to binary-threshold denominator programs where every denominator exponent is `<= 1`.
- The benchmark matrix is run via `benchmarks/run_cpu_matrix.sh`.
- The current summary/decision report is produced by `benchmarks/summarize_cpu_matrix.py`.
- The active canonical matrix currently tracks `reg`, `frac-opt`, `cycle`, and `compiled`; `lut` is parked and can still be benchmarked manually.
- Checkpoint semantics:
  - `reg`, `frac-opt`, `compiled`, `lut`: `exact`
  - `cycle`: `at-least`
- `mult_smoke` is a 2-step exact logical-step smoke scenario.
- Current decision: CPU tuning has reached a good checkpoint; `compiled` is the exact-step baseline and the next milestone is the minimal GPU path.

Initial snapshot date:

- `2026-03-13`

Files captured so far:

- `2026-03-13-primegame-reg.txt`
- `2026-03-13-primegame-frac-opt.txt`
- `2026-03-13-primegame-compiled.txt`
- `2026-03-13-cpu-matrix.jsonl`
- `2026-03-13-cpu-matrix-summary.json`
