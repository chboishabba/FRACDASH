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
- Current status: active exact-step CPU baseline for sampled `primegame_*`
  workloads, with further low-latency rule-selection and SIMD/layout work still
  open.
- Hot path: denominator divisibility is compiled to lane-wise valuation
  threshold checks (`state_lanes >= require_lanes`), followed by priority
  first-enabled rule selection and a delta update. Runtime rule guards should
  not use integer division or modulus.

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
- Current conservative routing heuristic: CPU for very small batches (`<= 4`);
  warm resident GPU is consistently preferred in the sampled
  `batch_size >= 32`, `steps >= 8` region; smaller scenario-specific wins need
  remeasurement before becoming gates
- Current dashiCORE baseline check: `scripts/check_dashicore_reuse.py` imports
  the reusable Vulkan helper modules by reference and passes the Carrier
  passthrough smoke, confirming the reuse boundary is live

## Current Execution Stack

1. CPU reference and benchmark harness remain the semantic oracle.
2. Compiled CPU execution uses prime-valuation vectors, denominator threshold
   vectors, and rule deltas.
3. GPU layout and Vulkan smokes mirror the same threshold/delta contract for
   independent batched states.
4. Resident GPU execution is a throughput path for batches or wide frontier
   scans, not the default low-latency path for one sequential trace.
5. General-purpose Vulkan helper improvements should be upstreamed to
   `../dashiCORE`; FRACTRAN state semantics stay local.

`../dashiCORE` should be read as a source of Vulkan handles, buffer plumbing,
shader/SPIR-V conventions, backend registration, timing/hash patterns, and
Carrier smoke kernels. It is not currently a FRACTRAN priority-frontier runtime.

## Next Runtime Optimization

1. Make the CPU guard/selection path smaller and more predictable:
   threshold compare, horizontal reduction, first-enabled priority projection,
   and delta update.
2. Maintain an enabled-rule frontier bitset where possible:
   - `chosen = first_set(enabled)` / `ctz`
   - apply the selected sparse/dense delta
   - refresh only rules depending on changed lanes via a lane-to-rules index
3. Explore SIMD/cache-resident layouts for rule scans before adding new GPU
   semantics.
4. Treat Zig as an optional implementation language for this native CPU engine,
   not as a replacement for Python/NumPy experiment code or SPIR-V batch
   kernels. The first Zig prototype must reproduce compiled-engine parity on
   small canonical workloads before growing bindings or GPU integration.
5. Use GPU only when many independent states or a wide frontier can amortize
   dispatch and transfer costs.
6. Keep FFT/wave approaches out of the exact FRACTRAN VM unless a genuine
   convolution or spectral workload is introduced.

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

## Bridge Correctness Layer

FRACDASH also has a cross-cutting architecture obligation beyond raw execution:
the bridge from upstream AGDA semantics into local executable carriers must be
stated as a semantics-preserving compilation problem.

That layer has three parts:

1. source semantics
   - canonical DASHI / AGDA state and step objects
2. target semantics
   - FRACDASH carrier/template or FRACTRAN/register execution objects
3. bridge obligations
   - compile map
   - decode/readout map
   - quotient assumptions
   - simulation/refinement condition
   - invariant/Lyapunov/contraction preservation
   - observable validity
   - robustness against implementation-preserving perturbations

The current repo has executable pieces of that story, but not yet a fully
formalized end-to-end bridge contract. See
[`BRIDGE_CORRECTNESS.md`](/home/c/Documents/code/FRACDASH/BRIDGE_CORRECTNESS.md).
