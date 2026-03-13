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
- FRACDASH bridge: `gpu/dashicore_bridge.py`
- FRACTRAN GPU contract: `GPU_CONTRACT.md`
- Candidate shared components:
  - `gpu_common_methods.py`
  - `gpu_vulkan_adapter.py`
  - `gpu_vulkan_dispatcher.py`
  - `gpu_vulkan_backend.py`
  - `gpu_vulkan_gemv.py`
- Constraint: FRACDASH should import, adapt, or link these, not vendor-copy them.
- Current interpretation: reuse the Vulkan host/device plumbing and shader asset conventions, but keep FRACTRAN state semantics and step logic local to FRACDASH.
- Current smoke path: `scripts/check_dashicore_reuse.py`
- Current exact-step contract: dense exponent vectors plus per-rule thresholds/deltas in `gpu/fractran_layout.py`, validated by `scripts/check_fractran_gpu_layout.py`
- Current Vulkan kernel proof: `gpu_shaders/fractran_step.comp` plus `gpu/vulkan_fractran_step.py`, validated by `scripts/check_fractran_vulkan_step.py`
- Current batching shape: flattened `state_count x prime_count` exponent buffers plus one `(selected_rule, halted)` pair per state
- Current resident-execution shape: one upload of rule/state buffers, repeated exact-step dispatches, one final readback
- Current low-overhead execution shape: one recorded multi-dispatch command buffer using ping-pong descriptor sets and a single queue submission
- Current routing evidence: the low-overhead resident GPU path already beats the dense CPU contract on the tested `primegame_small` batch benchmark for batch sizes `32+` at `32` exact steps
- Current conservative routing rule: CPU for very small batches (`<= 4`), GPU for clearly large batches (`>= 128`), and a scenario-sensitive middle region that already favors GPU for `primegame_small` at `batch_size = 32`, `steps >= 8`

## Intended Near-Term Evolution

1. Stabilize CPU benchmark coverage.
2. Improve compiled path data layout and compatibility testing.
3. Add LUT-oriented CPU experiments.
4. Define a thin adapter to `../dashiCORE` GPU infrastructure without copying helper code.
5. Prove one minimal FRACDASH-side import/passthrough path through that adapter before FRACTRAN-specific kernel work.
6. Fix the FRACTRAN-specific device contract around dense exponent vectors and per-rule thresholds/deltas.
7. Add the first minimal Vulkan kernel over that dense contract and validate it against the CPU step semantics.
8. Widen that kernel from single-state dispatch to batched state buffers while preserving exact-step parity.
9. Keep those batched buffers resident across repeated exact steps and validate the final state against CPU parity.
10. Upstream any general-purpose kernel/dispatch helper back into `dashiCORE` once it proves reusable beyond FRACTRAN.

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
