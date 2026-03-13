# FRACDASH

FRACDASH is a research repo for translating a minimal, explicit subset of DASHI-style dynamics into FRACTRAN and testing what survives that translation.

The current project stance is strict:

- treat DASHI to FRACTRAN as an executable modeling problem, not a metaphor
- preserve signed balanced-ternary behavior with an explicit encoding
- keep claims about basin structure, geometry, and degeneracy at the level the repo can actually support
- prefer CPU-first measurement and reproducible artifacts before any GPU work

## Current Status

The repo already contains a checked-out FRACTRAN baseline in [`fractran/`](/home/c/Documents/code/FRACDASH/fractran) plus a benchmark harness and recorded CPU matrix artifacts under [`benchmarks/results/`](/home/c/Documents/code/FRACDASH/benchmarks/results).

What exists now:

- a trusted local CPU reference implementation in [`fractran/`](/home/c/Documents/code/FRACDASH/fractran)
- a deterministic benchmark CLI via `fractran-bench`
- a compiled exponent-vector execution path for comparison against the baseline
- benchmark summaries showing the current optimization focus is still CPU work, specifically compiled-path tuning
- an expanded GPU routing matrix that now includes `primegame_small`, `mult_smoke`, `paper_smoke`, and the new `hamming_smoke` headless program across the batch_size `16..64` / steps `4..16` band

What does not exist yet:

- the DASHI-to-FRACTRAN compiler or interpreter layer
- the executable 10-basin obstruction experiments
- the canonical Phase 2 AGDAS bridge path from `all_dashi_agdas.txt` into executable FRACTRAN physics

## Research Goals

The near-term questions are:

1. Can a small DASHI voxel transition system be compiled into FRACTRAN with a clear decode map?
2. Which invariants survive translation: locality, parity, reversibility, chamber structure, ultrametric behavior?
3. Do fixed prime sets impose the same kind of reachability obstruction discussed in the 10-basin analysis?
4. Can the basin graph be formalized well enough to verify a deterministic monotone-chain bound over the full `3^4` signed space?
5. Is the reported total degeneracy `113` structural or just coincidence?

## Repo Structure

- [`COMPACTIFIED_CONTEXT.md`](/home/c/Documents/code/FRACDASH/COMPACTIFIED_CONTEXT.md): durable project context and resolved conversation metadata
- [`AGENTS.md`](/home/c/Documents/code/FRACDASH/AGENTS.md): repo-specific working rules and deliverable standards
- [`spec.md`](/home/c/Documents/code/FRACDASH/spec.md): project objective, scope, and success criteria
- [`architecture.md`](/home/c/Documents/code/FRACDASH/architecture.md): current execution architecture and CPU-to-GPU boundary
- [`ROADMAP.md`](/home/c/Documents/code/FRACDASH/ROADMAP.md): phased implementation path
- [`TODO.md`](/home/c/Documents/code/FRACDASH/TODO.md): active task queue and open decisions
- [`CHANGELOG.md`](/home/c/Documents/code/FRACDASH/CHANGELOG.md): material repo changes
- [`benchmarks/`](/home/c/Documents/code/FRACDASH/benchmarks): benchmark runners, summaries, and result artifacts
- [`fractran/`](/home/c/Documents/code/FRACDASH/fractran): local FRACTRAN baseline interpreter and benchmark binary

## Getting Started

### Prerequisites

- `ghc`
- standard shell tooling for the benchmark scripts

### Build The FRACTRAN Binaries

```sh
cd fractran
./build.sh
```

This produces:

- `./fractran`
- `./fractran-bench`

### Run A Quick Benchmark

```sh
cd fractran
./fractran-bench --scenario primegame_small --engine compiled --mode logical-steps --checkpoint-policy exact
```

Available benchmark engines currently include:

- `naive-fast`
- `reg`
- `frac-opt`
- `cycle`
- `compiled`
- `lut`

Notes:

- `cycle` is treated as an `at-least` checkpoint engine because fast-forwarding can overshoot a target logical step.
- The active benchmark matrix currently compares `reg`, `frac-opt`, `cycle`, and `compiled`.
- The `lut` path remains available for manual experiments but is not part of the active canonical matrix.

### Run The Canonical CPU Matrix

```sh
./benchmarks/run_cpu_matrix.sh
python3 benchmarks/summarize_cpu_matrix.py benchmarks/results/2026-03-13-cpu-matrix.jsonl
```

The benchmark artifacts currently tracked in-repo include:

- [`benchmarks/results/2026-03-13-cpu-matrix.jsonl`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix.jsonl)
- [`benchmarks/results/2026-03-13-cpu-matrix-summary.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix-summary.json)
- [`benchmarks/results/2026-03-13-toy-dashi-phase2.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-toy-dashi-phase2.json)

### Timing Regression Check

Use the timing regression gate to ensure new CPU work does not materially regress wall-clock:

```sh
scripts/run_cpu_regression.sh \
  benchmarks/results/2026-03-13-cpu-matrix.jsonl \
  benchmarks/results/2026-03-13-cpu-matrix-regression-<timestamp>.jsonl \
  0.50
```

Or invoke the checker directly:

```sh
python3 scripts/check_timing_regression.py \
  --baseline benchmarks/results/2026-03-13-cpu-matrix.jsonl \
  --current benchmarks/results/2026-03-13-cpu-matrix-regression-*.jsonl \
  --engine compiled \
  --engine frac-opt \
  --engine reg \
  --min-baseline-seconds 0.0001 \
  --tolerance 0.20
```

It compares median `cpu_seconds` across the tracked `(scenario, engine)` pairs and exits non-zero if slowdowns exceed tolerance.

## Working Principles

- Docs before code. Update intent and experiment notes before changing implementations.
- No theorem inflation. Root-system, lattice, and moonshine language stays conjectural unless the repo contains an actual derivation.
- Signed behavior must be encoded explicitly. Do not hand-wave balanced ternary into unsigned FRACTRAN.
- Reproducibility is mandatory. Experiments need an entrypoint, summary, and saved artifacts.
- GPU work is downstream. The current baseline assumption is that algorithmic CPU wins matter more than naive early parallelism.

## External Reuse Boundary

FRACDASH should reuse GPU infrastructure from [`../dashiCORE`](/home/c/Documents/code/dashiCORE) by reference, adapter, or documented linkage when that becomes necessary. It should not copy those helper modules into this repo without a specific justification.

The first candidate files to reuse later are:

- [`../dashiCORE/gpu_common_methods.py`](/home/c/Documents/code/dashiCORE/gpu_common_methods.py)
- [`../dashiCORE/gpu_vulkan_dispatcher.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_dispatcher.py)
- [`../dashiCORE/gpu_vulkan_backend.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_backend.py)
- [`../dashiCORE/spv/`](/home/c/Documents/code/dashiCORE/spv)

The concrete FRACDASH bridge for that boundary now lives in:

- [`gpu/dashicore_bridge.py`](/home/c/Documents/code/FRACDASH/gpu/dashicore_bridge.py)
- [`scripts/check_dashicore_reuse.py`](/home/c/Documents/code/FRACDASH/scripts/check_dashicore_reuse.py)

Run the reuse smoke test with:

```sh
python3 scripts/check_dashicore_reuse.py
```

Override the default `../dashiCORE` location by setting `FRACDASH_DASHICORE_ROOT` if needed.

The current exact-step FRACTRAN GPU contract is documented in:

- [`GPU_CONTRACT.md`](/home/c/Documents/code/FRACDASH/GPU_CONTRACT.md)
- [`gpu/fractran_layout.py`](/home/c/Documents/code/FRACDASH/gpu/fractran_layout.py)
- [`scripts/check_fractran_gpu_layout.py`](/home/c/Documents/code/FRACDASH/scripts/check_fractran_gpu_layout.py)

Run the contract parity smoke with:

```sh
python3 scripts/check_fractran_gpu_layout.py
```

The first real Vulkan step smoke now lives in:

- [`gpu_shaders/fractran_step.comp`](/home/c/Documents/code/FRACDASH/gpu_shaders/fractran_step.comp)
- [`gpu/vulkan_fractran_step.py`](/home/c/Documents/code/FRACDASH/gpu/vulkan_fractran_step.py)
- [`scripts/check_fractran_vulkan_step.py`](/home/c/Documents/code/FRACDASH/scripts/check_fractran_vulkan_step.py)

Run it on the host with Vulkan access:

```sh
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json python3 scripts/check_fractran_vulkan_step.py --batch-size 4 --multi-steps 3
```

That entrypoint now validates single-state, batched one-step, and batched multi-step resident dispatch.

The first routing benchmark artifact now lives in:

- [`benchmarks/results/2026-03-13-gpu-benchmark-primegame-small.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-gpu-benchmark-primegame-small.json)
- [`benchmarks/results/2026-03-13-gpu-routing-matrix.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-gpu-routing-matrix.json)
- [`benchmarks/results/2026-03-13-gpu-routing-paper.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-gpu-routing-paper.json)
- [`benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json)

Current measured hint on this host:

- for `primegame_small`-like resident workloads at `32` exact steps, GPU already wins at batch sizes `32`, `128`, and `512`
- in the broader matrix, CPU remains the safe default for `batch_size <= 4`, GPU is already preferred for `batch_size >= 128`, and `primegame_small` reaches the GPU-preferred region at `batch_size = 32`, `steps >= 8`
- `paper_smoke` shows the same threshold behavior, with GPU preferred at `batch_size = 32`, `steps >= 8`

## Deterministic GPU Routing Rule

The new extended matrix (`benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json`) now samples the `16..64` batch / `4..16` step band for `primegame_small`, `mult_smoke`, `paper_smoke`, and the new `hamming_smoke` program. The measured shape lets us commit to a deterministic CPU/GPU rule on this host:

- Route to CPU when `batch_size <= 4` or when `batch_size = 16` and `steps < 16`.
- Route to GPU when `batch_size >= 32` and `steps >= 8`, or when the run has at least `16` exact steps regardless of batch size.
- The measurement still notes scenario-specific wins at `batch_size = 16`, `steps = 8` (particularly `hamming_smoke`) and at `batch_size = 32`, `steps = 4` for non-`primegame_small` workloads, but the deterministic rule above keeps the routing policy stable until we intentionally tune further.

This deterministic routing rule now feeds the GPU handoff plan: once the rule stabilizes, FRACDASH will upstream reusable dispatch helpers while keeping FRACTRAN semantics local.

## GPU Upstream Plan

The deterministic routing rule also serves as the gatekeeper for elevating reusable GPU helpers into `../dashiCORE`. See [`GPU_UPSTREAM.md`](/home/c/Documents/code/FRACDASH/GPU_UPSTREAM.md) for the checklist: it reiterates the rule, requires rerunning the extended matrix after any CPU change to keep `compiled` stable, and then stages the actual upstream work module by module.

## Phase 2: Toy DASHI transitions

A new experimental entrypoint, [`scripts/toy_dashi_transitions.py`](/home/c/Documents/code/FRACDASH/scripts/toy_dashi_transitions.py), defines a minimal FRACTRAN program for a signed 4-register ternary state space (`3^4 = 81` encodings). Each register state is encoded by one of three dedicated primes, and the script prints the FRACTRAN fractions plus a reference encoding and decoder. This gives us a concrete starting point for the Phase 2 CORE experiments (toy transitions, decoder, basin traversal) before we bring GPU scheduling into the mix. The script also explores the basin graph from a selected start value, reports monotone-chain statistics, compares fixed-prime and explicit-prime stepping across all states, and can emit a deterministic JSON artifact for reproducible basin and walk data.

[`scripts/agdas_bridge.py`](/home/c/Documents/code/FRACDASH/scripts/agdas_bridge.py) is now the first executable AGDAS bridge stage. The AGDA code in `../dashi_agda` is treated as the semantic reference, but the active executable bridge is maintained in FRACDASH via `AGDAS_BRIDGE_MAPPING.md` and a wave-1 template transition set. The parser for source-coupled transition markers still exists, but it is now optional rather than the main path.
The current primary bridge baseline is the template transition set exposed by `scripts/agdas_bridge.py --emit-templates --template-set wave1`, and the Phase 2 runner can exercise template sets with `scripts/run_agdas_template_phase2.sh`. The template runner defaults to disabling the chain bound (set `FRACDASH_TOY_CHAIN_BOUND_TEMPLATE=2` to re-enable it) and selects the template set via `FRACDASH_AGDAS_TEMPLATE_SET=wave1|wave2|all`.
The wave-2 `MonsterState` / `Monster.Step` probe now runs as `FRACDASH_AGDAS_TEMPLATE_SET=wave2`, but its artifact is mostly terminal under the current 4-register encoding, which is evidence that richer Monster-style dynamics likely need a larger encoded state model.
That larger carrier prototype now exists in `scripts/agdas_wave3_state.py`: it expands the bridge carrier from `3^4 = 81` to `3^6 = 729` states so mask summary, candidate/admissibility, and a 2-trit window can live on distinct registers before we attempt the next Monster-facing experiment pass.
The first wave-3 execution path now exists in `scripts/agdas_wave3_experiments.py` and writes `benchmarks/results/2026-03-14-agdas-template-wave3-phase2.json`. It confirms the larger carrier is wired, but it also shows the next missing piece clearly: the current Monster-facing wave-3 templates still model only a single step because no rule reintroduces pending choice/admissibility state after a transition.
For a more physics-facing path, FRACDASH now also has a local formal sketch in `formalism/PhysicsBridgeRefreshSketch.agda` and a recurrent `physics1` template set covering severity join, contraction-style relaxation, and boundary reset. Its artifact is `benchmarks/results/2026-03-14-agdas-physics1-phase2.json`, and it already shows nontrivial recurrent behavior on the existing 4-register carrier, making it the higher-signal bridge direction for now.
The intended next physics layer is a 6-register `physics2` carrier with separate source severities, effective joined severity, region flag, signature latch, and action/energy phase. That widening is meant to preserve the same local story while giving the bridge enough state to model scan/materialize/relax/reset explicitly instead of overloading the 4-register toy carrier.
That widened physics layer is now implemented. The dedicated carrier lives in `scripts/agdas_physics2_state.py`, the runner in `scripts/agdas_physics_experiments.py`, and the canonical artifact in `benchmarks/results/2026-03-14-agdas-physics2-phase2.json`. On this first pass it produces a substantially denser recurrent structure than `physics1`, with `657` edges over `729` states, longest chain `12`, and a canonical 4-step scan -> join -> contract -> rearm cycle.

[`scripts/toy_dashi_transitions.py`](/home/c/Documents/code/FRACDASH/scripts/toy_dashi_transitions.py) is now wired to consume AGDAS candidates either from optional parsed source markers via `--agdas-path` or from the primary FRACDASH-side bridge templates via `--agdas-templates --agdas-template-set wave1|wave2|all`. This keeps the verifier and basin tooling usable without editing upstream AGDA sources.

The canonical artifact generation is now pinned to a monotone-chain bound of `2` for the full `3^4` fixed-prime walk space.
That pinning is a regression gate for this artifact stream: the command exits non-zero if any fixed-prime trajectory in the captured space exceeds the bound. It is not a claim of a global theorem unless we later pass additional evidence.

```sh
scripts/run_toy_dashi_phase2.sh
```

That script writes `benchmarks/results/YYYY-MM-DD-toy-dashi-phase2.json` and enforces the fixed-prime chain check by default (`2`), unless `--disable-chain-bound` is supplied (or `FRACDASH_TOY_CHAIN_BOUND=disable` is set).

You can keep the check interactive by adding `--disable-chain-bound` or using custom values with `--max-chain-bound`.

## Read First

# Minimal DASHI state space

- `DASHI_STATE.md` describes the smallest signed ternary registers and the FRACTRAN encoding we target.

Before making substantial changes, read:

1. [`COMPACTIFIED_CONTEXT.md`](/home/c/Documents/code/FRACDASH/COMPACTIFIED_CONTEXT.md)
2. [`AGENTS.md`](/home/c/Documents/code/FRACDASH/AGENTS.md)
3. [`TODO.md`](/home/c/Documents/code/FRACDASH/TODO.md)
4. [`AGDAS_BRIDGE_NOTES.md`](/home/c/Documents/code/FRACDASH/AGDAS_BRIDGE_NOTES.md)
5. [`AGDAS_BRIDGE_MAPPING.md`](/home/c/Documents/code/FRACDASH/AGDAS_BRIDGE_MAPPING.md)

That is the current source of truth for project intent, guardrails, and active priorities.
