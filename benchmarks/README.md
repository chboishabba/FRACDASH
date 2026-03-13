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
- `2026-03-13-gpu-benchmark-primegame-small.json`

## Initial GPU Routing Result

The first host-GPU routing benchmark is captured in:

- `benchmarks/results/2026-03-13-gpu-benchmark-primegame-small.json`

Current measured result on the RX 580 / RADV host:

- workload: `primegame_small`
- exact steps per state: `32`
- tested batch sizes: `32`, `128`, `512`
- parity held between the dense CPU contract and the resident Vulkan path
- the resident GPU path was already preferred on every tested batch size

Current routing hint:

- prefer GPU for `primegame_small`-like resident workloads once the batch is at least `32` states and the run length is at least `32` exact steps
- keep CPU as the default for tiny or unmeasured workloads until the matrix is expanded

Broader routing matrix artifact:

- `benchmarks/results/2026-03-13-gpu-routing-matrix.json`
- `benchmarks/results/2026-03-13-gpu-routing-paper.json`

Current conservative routing rule from the broader matrix:

- default to CPU when `batch_size <= 4`
- prefer GPU when `batch_size >= 128`
- for `primegame_small`-like resident workloads, prefer GPU already at `batch_size = 32` once `steps >= 8`
- keep the remaining middle region as `measure-more`, especially when `batch_size = 32` with very short runs

Additional paper smoke result:

- `paper_smoke` confirms the same shape: CPU for tiny batches, GPU preferred at `batch_size = 32` once `steps >= 8`, and a narrow middle band (`batch_size = 4`, `steps = 32`) that remains `measure-more`.
