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

What does not exist yet:

- the canonical minimal DASHI transition vocabulary
- the signed FRACTRAN encoding for DASHI state
- the DASHI-to-FRACTRAN compiler or interpreter layer
- the executable 10-basin obstruction experiments

## Research Goals

The near-term questions are:

1. Can a small DASHI voxel transition system be compiled into FRACTRAN with a clear decode map?
2. Which invariants survive translation: locality, parity, reversibility, chamber structure, ultrametric behavior?
3. Do fixed prime sets impose the same kind of reachability obstruction discussed in the 10-basin analysis?
4. Can the basin graph be formalized well enough to verify the claimed maximum monotone-chain length `4`?
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
python3 benchmarks/summarize_cpu_matrix.py benchmarks/results/$(date +%F)-cpu-matrix.jsonl
```

The benchmark artifacts currently tracked in-repo include:

- [`benchmarks/results/2026-03-13-cpu-matrix.jsonl`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix.jsonl)
- [`benchmarks/results/2026-03-13-cpu-matrix-summary.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix-summary.json)

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

## Read First

Before making substantial changes, read:

1. [`COMPACTIFIED_CONTEXT.md`](/home/c/Documents/code/FRACDASH/COMPACTIFIED_CONTEXT.md)
2. [`AGENTS.md`](/home/c/Documents/code/FRACDASH/AGENTS.md)
3. [`TODO.md`](/home/c/Documents/code/FRACDASH/TODO.md)

That is the current source of truth for project intent, guardrails, and active priorities.
