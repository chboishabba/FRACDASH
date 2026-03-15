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
- `benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json`

The extended matrix now includes `primegame_small`, `mult_smoke`, `paper_smoke`, and the new `hamming_smoke` program sampled across `batch_size = 4, 16, 32, 64, 128` and `steps = 4, 8, 16`. That coverage lets us fix the previous `measure-more` band into a deterministic routing rule:

- default to CPU when `batch_size <= 4` or when `batch_size = 16` and `steps < 16`
- prefer GPU when `batch_size >= 32` and `steps >= 8`, or when the run lasts at least `16` exact steps regardless of batch size
- scenario-specific GPU wins still appear (e.g., `paper_smoke` at `batch_size = 16`, `steps = 4` or `primegame_small` at `batch_size = 32`, `steps = 4`), but the deterministic rule above stays stable until further tuning requires per-scenario overrides

Additional paper smoke result:

- `paper_smoke` confirms the same shape: CPU for tiny batches, GPU preferred at `batch_size = 32` once `steps >= 8`, and a narrow middle band (`batch_size = 4`, `steps = 32`) that remains `measure-more`.

## Timing regression check

Use the regression gate after CPU tuning changes.

Run:

```bash
scripts/run_cpu_regression.sh \
  [base-jsonl] \
  [current-jsonl] \
  [tolerance]
```

Or run the checker directly when you need custom options:

```bash
python3 scripts/check_timing_regression.py \
  --baseline benchmarks/results/2026-03-13-cpu-matrix.jsonl \
  --current benchmarks/results/2026-03-13-cpu-matrix-regression-*.jsonl \
  --engine compiled \
  --engine frac-opt \
  --engine reg \
  --min-baseline-seconds 0.0001 \
  --tolerance 0.20
```

The check compares median `cpu_seconds` for each tracked `(scenario, engine)` pair and fails when slowdown exceeds the configured tolerance. Use `--json` for CI-friendly output.

## Rank-4 Obstruction Reproduction

Rank-4 diagnostics are now artifact-backed and reproducible from scripts.

Run:

```bash
python3 scripts/derive_rank4_dataset.py
python3 scripts/run_rank4_diagnostics.py
python3 scripts/run_rank4_discriminators.py
python3 scripts/run_rank4_canonical_gpu_parity.py
```

Strict checks:

```bash
python3 scripts/run_rank4_diagnostics.py --strict-stable
python3 scripts/run_rank4_diagnostics.py --strict-lock
```

Current artifacts:

- `benchmarks/results/2026-03-15-rank4-dataset.json`
- `benchmarks/results/rank4-dataset-latest.json`
- `benchmarks/results/2026-03-15-rank4-diagnostics.json`
- `benchmarks/results/2026-03-15-rank4-discriminators.json`
- `benchmarks/results/2026-03-15-rank4-discriminators.md`
- `benchmarks/results/2026-03-15-rank4-canonical-gpu-parity.json`

Default mode is report-only. Identity-level `B4`/`D4`/`F4` claims remain unproven.
