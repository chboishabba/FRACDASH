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
- The current `compiled` engine is the active exact-step CPU baseline for the sampled `primegame` workloads, but CPU low-latency guard/selection work remains open.
- The benchmark harness now summarizes `compiled` by tracking emitted integer values directly, avoiding repeated `unfExpVec` reconstruction during checksum generation.
- The current `lut` engine is limited to binary-threshold denominator programs where every denominator exponent is `<= 1`.
- The benchmark matrix is run via `benchmarks/run_cpu_matrix.sh`.
- The current summary/decision report is produced by `benchmarks/summarize_cpu_matrix.py`.
- The active canonical matrix currently tracks `reg`, `frac-opt`, `cycle`, and `compiled`; `lut` is parked and can still be benchmarked manually.
- Checkpoint semantics:
  - `reg`, `frac-opt`, `compiled`, `lut`: `exact`
  - `cycle`: `at-least`
- `mult_smoke` is a 2-step exact logical-step smoke scenario.
- Current decision: `compiled` is the exact-step baseline for the sampled matrix; GPU work is a resident batch-throughput path, while single-trace low-latency work remains CPU-first.

Initial snapshot date:

- `2026-03-13`

Files captured so far:

- `2026-03-13-primegame-reg.txt`
- `2026-03-13-primegame-frac-opt.txt`
- `2026-03-13-primegame-compiled.txt`
- `2026-03-13-cpu-matrix.jsonl`
- `2026-03-13-cpu-matrix-summary.json`
- `2026-03-13-gpu-benchmark-primegame-small.json`
- `2026-03-20-cpu-profile.json`
- `2026-03-20-gpu-profile.json`
- `2026-03-20-perf-profile-summary.{json,md}`

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

The extended matrix now includes `primegame_small`, `mult_smoke`, `paper_smoke`, and the new `hamming_smoke` program sampled across `batch_size = 4, 16, 32, 64, 128` and `steps = 4, 8, 16`. That coverage supports a host-local routing heuristic:

- default to CPU for tiny batches (`batch_size <= 4`)
- prefer GPU in the consistently sampled warm-resident region
  `batch_size >= 32` and `steps >= 8`
- scenario-specific GPU wins still appear (e.g., `paper_smoke` at `batch_size = 16`, `steps = 4` or `primegame_small` at `batch_size = 32`, `steps = 4`), but these remain measurement candidates until further tuning justifies per-scenario overrides

Additional paper smoke result:

- `paper_smoke` confirms the same shape: CPU for tiny batches, GPU preferred at `batch_size = 32` once `steps >= 8`, and a narrow middle band (`batch_size = 4`, `steps = 32`) that remains `measure-more`.

## Profiling milestone (2026-03-20)

- CPU profiling runner: `scripts/profile_fractran_cpu.py`
  - exact-step timing plus GHC `.prof` / RTS breakdowns
  - default engines: `compiled`, `frac-opt`, `reg` (`cycle` profiled separately as checkpoint-only)
  - artifact: `benchmarks/results/2026-03-20-cpu-profile.json`
- GPU profiling runner: `scripts/profile_fractran_gpu.py`
  - cold-start vs warm-resident timing breakdowns using the resident Vulkan path
  - artifact: `benchmarks/results/2026-03-20-gpu-profile.json`
- Combined decision summary: `scripts/summarize_fractran_perf_profiles.py`
  - artifacts: `benchmarks/results/2026-03-20-perf-profile-summary.{json,md}`
- Current read: no obvious large exact-step CPU win beyond the `compiled` baseline; warm-resident GPU wins are real in the measured batch region; next targets are routing refinement and GPU host/setup overhead reduction.

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

## Physics invariant target check

Use the physics gate after physics-template or invariant-analysis changes.

Run:

```bash
python3 scripts/check_physics_invariant_targets.py
```

Or emit machine-readable output:

```bash
python3 scripts/check_physics_invariant_targets.py --json
```

The check validates canonical relationship targets over the latest `physics2..physics8` artifacts:

- Lyapunov nonincrease (`nonincrease_ratio == 1.0`, no increase edges)
- controlled-hybrid progression (`physics5..physics8` edge/cycle growth with fixed jump-count cap)
- long-tail resolution (`still_timeout == 0` on `physics6..physics8`)
- expected `physics4` overconstraint signature

See `PHYSICS_INVARIANT_TARGETS.md` for the explicit target table and current baseline numbers.

Invariant artifacts also now include `observable_surrogates` for non-gated exploratory measurements:

- region occupancy across boundary/shell/interior
- action-phase occupancy
- shell and boundary re-entry flow
- source-latch alignment
- source-defect coupling

## Rank-4 Obstruction Reproduction

Rank-4 diagnostics are now artifact-backed and reproducible from scripts.

Run:

```bash
python3 scripts/derive_rank4_dataset.py
python3 scripts/run_rank4_diagnostics.py
python3 scripts/run_rank4_discriminators.py
python3 scripts/run_rank4_canonical_gpu_parity.py
python3 scripts/ablate_prime_triplets.py --template-set physics8
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
- `benchmarks/results/2026-03-15-prime-triplet-ablation.json`

Default mode is report-only. Identity-level `B4`/`D4`/`F4` claims remain unproven.

## Monster 10-Walk Canonical Lock

Run:

```bash
python3 scripts/freeze_monster10walk_canonical.py --strict-lock
python3 scripts/quarantine_monsterlean_claims.py
```

Default lock mode enforces transition-witness support from `physics8` and `physics9`.

Current lock artifacts:

- `benchmarks/results/2026-03-15-monster10walk-canonical.json`
- `benchmarks/results/2026-03-15-monsterlean-claim-status.json`
- `benchmarks/results/2026-03-15-monsterlean-claim-status.md`

## Experiment Entrypoint Index

This table is the current navigation surface for reproducible experiment lanes.
Claim status uses the repo vocabulary: `implemented`, `observed
experimentally`, or `conjectured`.

| Lane | Entrypoint | Canonical outputs / summaries | Claim status |
| :--- | :--- | :--- | :--- |
| CPU exact-step baseline | `benchmarks/run_cpu_matrix.sh`; `benchmarks/summarize_cpu_matrix.py` | `2026-03-13-cpu-matrix*.jsonl/json`; `2026-03-20-cpu-profile.json`; `2026-03-20-perf-profile-summary.{json,md}` | `implemented` |
| GPU threshold/delta contract | `scripts/check_fractran_gpu_layout.py`; `scripts/check_fractran_vulkan_step.py`; `scripts/benchmark_fractran_gpu.py`; `scripts/profile_fractran_gpu.py` | `2026-03-13-gpu-routing-matrix*.json`; `2026-03-20-gpu-profile.json` | `implemented` for parity smokes; `observed experimentally` for routing |
| Toy DASHI fixed-prime comparison | `scripts/toy_dashi_transitions.py`; `scripts/run_toy_dashi_phase2.sh` | `2026-03-13-toy-dashi-phase2.json` | `implemented` toy model |
| AGDAS physics phase-2 family | `scripts/agdas_physics_experiments.py`; `scripts/run_agdas_physics*_phase2.sh` | `2026-03-14/15/23-agdas-physics*-phase2.json`; invariant JSONs | `observed experimentally` |
| Carrier8 branch | `scripts/agdas_physics8_experiments.py --template-set carrier8_physicsN --json` | `2026-03-15/23-agdas-carrier8-physics*-phase2.json`; `2026-03-23-cross-carrier-baseline-summary.{json,md}` | `observed experimentally` |
| Bridge macro/invariant checks | `scripts/export_physics_family_deltas.py`; `scripts/check_physics_family_macro_soundness.py`; `scripts/check_physics_family_bridge_invariants.py`; `scripts/build_bridge_regime_summary.py` | `2026-03-19-physics*-{deltas,macro-soundness,bridge-*}.json`; `2026-03-19-bridge-regime-summary.{json,md}` | `implemented` for checked slices |
| Formalism intake | `scripts/check_dashi_agda_formalism.py`; `scripts/check_dashi_agda_wave_surface.py` | `2026-03-22-dashi-agda-formalism-check.{json,md}`; `2026-03-20-dashi-agda-wave-surface.{json,md}` | `implemented` intake checks |
| Rank-4 / 10-walk | `scripts/derive_rank4_dataset.py`; `scripts/run_rank4_diagnostics.py`; `scripts/run_rank4_discriminators.py`; `scripts/freeze_monster10walk_canonical.py --strict-lock` | rank4 dataset/diagnostics/discriminators; `2026-03-15-monster10walk-canonical.json` | `observed experimentally`; theorem identity `conjectured` |
| Prime dynamics | `scripts/toy_dashi_transitions.py`; `scripts/ablate_prime_triplets.py --template-set physics8` | `2026-03-15-prime-triplet-ablation*.json` | `observed experimentally` |
| Named-equation probe | `scripts/named_equation_probe.py` | `2026-03-20-equation-probe-{wave,heat}.json`; `2026-03-20-equation-probe-summary.md` | `observed experimentally` |
| Waveform / branch-density rendering | `scripts/render_trace_waveform.py`; `scripts/render_trace_graph.py`; `scripts/render_zkperf_waveform.py` | `*.trace-waveform.{json,html,png}`; `rank4-dataset-latest.branch-density-view.*` | `implemented` visualization |
| DA51 / zkperf compression | `scripts/compact_zkperf_trace.py`; `scripts/compact_dashi_perfhistory.py`; `scripts/compact_dashi_da51_shards.py`; `scripts/compact_dashi_da51_inner.py` | `2026-03-27-zkperf-*`; `2026-03-27-dashi-da51-*`; compare stats JSON | `implemented` codecs for frozen corpora |

## Artifact Retention Policy

- Track canonical JSON/Markdown summaries when they are named in
  `CHANGELOG.md`, `README.md`, `status.md`, or this benchmark index.
- Track selected `.html`, `.png`, `.cbor`, `.spv`, and `.agdai` artifacts only
  when they are reproducibility evidence for a named experiment or formal
  interface.
- Treat `__pycache__`, `.pytest_cache`, GHC scratch output, `.prof` files, and
  submodule-local build products as transient unless a document explicitly
  promotes a specific file as a canonical artifact.
