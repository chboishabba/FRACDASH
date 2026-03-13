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
- Current status: parity-oriented prototype, not yet a tuned performance engine.

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

## Key Invariants

- CPU reference behavior remains the semantic anchor.
- Signed-state behavior must be explicit, never implied.
- Experimental outputs must be reproducible and stored.
- GPU code stays behind a clear adapter boundary.
