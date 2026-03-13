# FRACDASH Architecture

## Current Architecture

### 1. Baseline evaluator

- Source: `fractran/`
- Purpose: trusted CPU reference implementation
- Current binaries:
  - `fractran`
  - `fractran-bench`

### 2. Execution seam

- Source: `fractran/src/Fractran.hs`
- Observation: `fracOpt` and `cycles` already compile rationals into exponent maps before stepping.
- Role: insertion point for alternate compiled/dense execution paths.

### 3. Compiled prototype

- Source: `fractran/src/Compiled.hs`
- Purpose: explicit compiled program representation and dense exponent-vector stepping path.
- Current status: exact-step prototype now entering a tuning phase against `frac-opt`.

### 4. Benchmark layer

- Source: `fractran/src/Bench.hs`
- Artifact root: `benchmarks/results/`
- Purpose: deterministic CLI runs and artifact capture for engine comparison.

### 5. External GPU reuse boundary

- Source of truth: `../dashiCORE`
- Candidate shared components:
  - `gpu_common_methods.py`
  - `gpu_vulkan_dispatcher.py`
  - `gpu_vulkan_backend.py`
  - `gpu_vulkan_gemv.py`
- Constraint: FRACDASH should import, adapt, or link these, not vendor-copy them.

## Intended Near-Term Evolution

1. Stabilize CPU benchmark coverage.
2. Improve compiled path data layout and compatibility testing.
3. Add LUT-oriented CPU experiments.
4. Only then define a thin adapter to `../dashiCORE` GPU infrastructure.

## CPU To GPU Handoff

FRACDASH should not move into `../dashiCORE` integration just because a GPU path exists. The handoff only happens once:

1. the intended CPU fast path is settled,
2. one more focused CPU tuning round fails to beat the baseline clearly,
3. the next workload is batch-friendly enough to amortize dispatch and transfer costs,
4. state can remain device-resident across many FRACTRAN steps,
5. the current benchmark contract stays usable as the correctness oracle.

## Key Invariants

- CPU reference behavior remains the semantic anchor.
- Signed-state behavior must be explicit, never implied.
- Experimental outputs must be reproducible and stored.
- GPU code stays behind a clear adapter boundary.
