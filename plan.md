# FRACDASH Plan

## Current Phase

Phase 1: CPU-side seam extraction and exponent-vector validation

## Milestones

### Milestone A: Baseline harness

Status: completed

- non-interactive benchmark CLI exists
- baseline artifacts are stored
- local build works on this machine

### Milestone B: Compiled seam prototype

Status: completed

- explicit compiled representation exists
- parity checks across the current matrix succeeded for `reg`, `frac-opt`, and `compiled`
- matrix results are now available for the next routing decision

### Milestone C: CPU optimization loop

Status: completed

- compare `compiled`, `reg`, `frac-opt`, and `cycle` over a wider benchmark set
- save benchmark artifacts and summary
- choose the next CPU optimization target by rule

Decision:
- proceed with LUT/divisibility-mask CPU work next
- keep `compiled` as a reusable baseline, but do not make further compiled-path tuning the immediate priority
- treat `cycle` as an `at-least` checkpoint engine, not an exact-step peer
- keep `mult_smoke` fixed at its real exact logical-step target of `2`

### Milestone D: LUT CPU path

Status: completed

- define the divisibility mask shape used by the current benchmark programs
- prototype `mask -> rule` lookup on CPU
- benchmark LUT path against `frac-opt`, `compiled`, and `cycle`

Result:
- v1 LUT path is limited to programs whose denominator thresholds are all `<= 1`
- LUT parity holds on `mult_smoke` and the current `primegame_*` scenarios
- LUT cleanly rejects `hamming`, which requires a threshold-aware generalization
- `frac-opt` remains faster than `lut` on `primegame_medium` and `primegame_large`, so LUT is not promoted to the active CPU baseline

### Milestone E: Compiled-path tuning

Status: completed

- park LUT as a completed side experiment, not the current optimization path
- target the compiled exact-step path directly against `frac-opt`
- start by importing `frac-opt`-style rule-order narrowing into the compiled seam
- rerun the existing benchmark matrix after each narrow optimization round

Current result:
- the first tuning round ports rule-order narrowing into the compiled evaluator
- compiled parity still holds against `reg` and `frac-opt`
- compiled now beats `frac-opt` on `primegame_small` and `primegame_large`, and is close but slightly slower on `primegame_medium`
- the current summary rule therefore routes to `continue compiled-path tuning`
- a later tuning round keeps compiled runs in exponent-vector form until summary time, removing benchmark-side `IntMap` decoding overhead
- the current canonical matrix now has `compiled` ahead of `frac-opt` on `primegame_small`, `primegame_medium`, and `primegame_large`
- `fractran/build.sh --profile` now works on this host by using static profiling instead of incompatible dynamic profiling
- GHC cost-centre profiling on `primegame_medium` and `primegame_large` shows `unfExpVec` and checksum work dominating compiled runs, `applyRule` as the largest engine-side hotspot, and rule matching materially smaller
- an `applyRule` rewrite from indexed array updates to element-wise zipping landed cleanly and improved the exact-step compiled path
- the compiled benchmark path now tracks current integer values directly, removing the dominant `unfExpVec` reconstruction cost from checksum generation
- after these two extra profiling-backed rounds, `compiled` is now the leading exact-step CPU path on the sampled `primegame_*` workloads

### Milestone F: GPU reuse adapter

Status: active

- define how FRACDASH references `../dashiCORE`
- prove one trivial dispatch path
- keep state movement and semantics isolated

Current direction:
- reuse `../dashiCORE` Vulkan helper modules by import/reference, not by copying files
- keep FRACTRAN state packing, parity checking, and step semantics in FRACDASH
- upstream only generic helpers or kernels back into `dashiCORE`
- `gpu/dashicore_bridge.py` is now the FRACDASH-local reference/import seam
- `scripts/check_dashicore_reuse.py` is now the minimal smoke path for by-reference imports and adapter passthrough
- `gpu/fractran_layout.py` now defines the first FRACTRAN-specific dense GPU contract
- `scripts/check_fractran_gpu_layout.py` now proves that contract against the compiled CPU baseline on `mult_smoke` and `primegame_small`
- `gpu_shaders/fractran_step.comp` and `gpu/vulkan_fractran_step.py` now implement the first real one-step Vulkan path
- `scripts/check_fractran_vulkan_step.py` now proves one-step GPU parity against the dense CPU contract on `mult_smoke` and `primegame_small`
- the Vulkan step path now also supports batched state buffers and matches dense CPU parity across every tested batch slot
- the Vulkan runner now keeps batched buffers resident across repeated exact steps and matches dense CPU parity on the final resident state
- the Vulkan runner now records the resident multi-step path into one command buffer submission with ping-pong descriptor sets, preserving parity while reducing host dispatch overhead
- the first routing benchmark now shows the resident GPU path ahead of the dense CPU contract on `primegame_small` at batch sizes `32`, `128`, and `512` for `32` exact steps
- the broader routing matrix now supports a first conservative rule: CPU for `batch_size <= 4`, GPU for `batch_size >= 128`, with a measured middle region that already favors GPU for `primegame_small` at `batch_size = 32`, `steps >= 8`
- the `paper_smoke` matrix matches the same threshold pattern (GPU at `batch_size = 32`, `steps >= 8`) with a narrow `measure-more` band

## Immediate Next Actions

1. Treat `compiled` as the active exact-step CPU baseline for future work.
2. Pivot to minimal GPU implementation planning against the current compiled semantics and benchmark contract.
3. Use `../dashiCORE` host-side Vulkan helpers as the first reuse seam instead of cloning GPU code into FRACDASH.
4. Expand the routing benchmark to at least one more program beyond `paper_smoke`, focusing on the `batch_size = 4..32`, `steps = 4..16` middle region.
5. Preserve the current exact-vs-at-least checkpoint semantics in all future benchmark extensions.
6. Keep LUT parked unless it becomes specifically useful as a GPU-side representation.

## CPU To GPU Handoff Criteria

1. The CPU execution model is stable enough that there is one intended fast path, not several unfinished experiments.
2. Another focused CPU optimization round fails to produce a clear win over the current baseline.
3. The intended workload is many independent trajectories or another batch-friendly shape, not just one scalar trajectory.
4. The GPU design keeps state resident across many steps rather than bouncing host/device state every step.
5. The current benchmark contract and CPU correctness oracle remain unchanged so GPU comparisons are meaningful.

## Risks

- Benchmarks may be too noisy or too narrow to guide optimization well.
- Binary-threshold LUTs may be too narrow to matter unless generalized beyond presence-only masks.
- GPU reuse may become messy if the boundary to `../dashiCORE` is not explicit.
