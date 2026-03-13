# FRACDASH Plan

## Current Phase

Phase 2: Core experiments (detailed toy DASHI dynamics)

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
- `DASHI_STATE.md` records the minimal signed ternary registers and their FRACTRAN mapping
- `gpu_shaders/fractran_step.comp` and `gpu/vulkan_fractran_step.py` now implement the first real one-step Vulkan path
- `scripts/check_fractran_vulkan_step.py` now proves one-step GPU parity against the dense CPU contract on `mult_smoke` and `primegame_small`
- the Vulkan step path now also supports batched state buffers and matches dense CPU parity across every tested batch slot
- the Vulkan runner now keeps batched buffers resident across repeated exact steps and matches dense CPU parity on the final resident state
- the Vulkan runner now records the resident multi-step path into one command buffer submission with ping-pong descriptor sets, preserving parity while reducing host dispatch overhead
- the first routing benchmark now shows the resident GPU path ahead of the dense CPU contract on `primegame_small` at batch sizes `32`, `128`, and `512` for `32` exact steps
- the broader routing matrix now supports a first conservative rule: CPU for `batch_size <= 4`, GPU for `batch_size >= 128`, with a measured middle region that already favors GPU for `primegame_small` at `batch_size = 32`, `steps >= 8`
- the `paper_smoke` matrix matches the same threshold pattern (GPU at `batch_size = 32`, `steps >= 8`) with a narrow `measure-more` band

## Immediate Next Actions

1. Keep the `compiled` engine as the stable exact-step CPU baseline while monitoring parity/artifacts.
2. Record the deterministic GPU routing rule derived from `benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json` and use it as the gating condition for future host/GPU work.
3. Once the routing policy is locked, upstream any reusable helper/adapter plumbing back into `../dashiCORE` while keeping the FRACTRAN-specific state layout and parity logic local to FRACDASH.
4. Continue referencing the `../dashiCORE` Vulkan helpers via `gpu/dashicore_bridge.py` and the adapter passthrough smoke path.
5. Preserve the exact vs. at-least checkpoint semantics and keep the `cycle` engine pegged as the at-least sentinel.
6. Implement the full AGDAS-to-FRACTRAN physics bridge from the AGDA semantics in `../dashi_agda` into a typed transition IR before broader CORE integration work. The primary route is now FRACDASH-side mapping/templates, not edits to the `.agda` sources: `scripts/agdas_bridge.py` emits the wave-1 templates, and `scripts/toy_dashi_transitions.py` can execute them via `--agdas-templates`.
7. Resume Phase 2 CORE experiments with that bridge and keep the toy transition set as the deterministic safety gate. The parser remains available in `scripts/agdas_bridge.py` for optional source-coupled extraction, but the main execution path no longer depends on marker availability in the `.agda` tree.
8. Prioritize the physics-facing bridge over deeper Monster compression unless the Monster path starts producing equally strong structure. `physics1` and `physics2` now provide the most relevant James-facing signal.
9. Run timing regression checks between matrix runs with `scripts/check_timing_regression.py` after material CPU changes.

## Phase 2 Experiment Work

1. Use `scripts/toy_dashi_transitions.py` to enumerate the FRACTRAN fractions for the toy signed-ternary state space, detail the prime-level invariants, and verify that the decoder round-trips each encoded state.
2. Build the basin graph starting from the canonical start state, capture the sequence of transitions, and measure the longest monotone chain within the explored subset.
3. Expand the exploration to the full `3^4=81` encoded state space, compare fixed-prime vs explicit prime dynamics, and collect the deterministic basin partition data.
4. Feed these reproducible outputs back into the CORE experiment log so these results can drive the next CORE-facing experiment pass.
5. Build the first AGDAS parser/extractor and interpreter surface in `scripts/toy_dashi_transitions.py` or a companion module so full transition programs can be emitted as FRACTRAN fractions.
   Current state: parser exists in `scripts/agdas_bridge.py`; verifier execution is connected via `scripts/toy_dashi_transitions.py --agdas-path`; the active bridge path is the FRACDASH-side template/mapping route exercised via `--agdas-templates`, with the `.agda` tree used as semantic reference rather than a required annotated input.
6. Continue widening the physics-facing bridge:
   - `physics1` on the 4-register carrier is already recurrent and informative.
   - `physics2` now runs on a dedicated 6-register carrier and produces a denser recurrent graph than `physics1`.
   - `physics3` now adds cone-shell refinement and action monotonicity reporting on the same 6-register carrier, and currently leads the bridge path.
   - `physics4` tightened shell/interior rearm guards on the same carrier and cut action-rank increases sharply, but it overconstrained the dynamics and eliminated recurrence.
   - the next pass should therefore be a `physics5` hybrid: keep the stronger rearm discipline where it matters, but selectively restore recurrence from the `physics3` loop instead of adding more scan variants first.

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

## Latest Phase 2 Output

- `scripts/toy_dashi_transitions.py --json` now emits:
  - fixed-prime walk summaries over all 81 states,
  - deterministic basin partition summaries,
  - fixed-prime vs explicit-semantics comparison for all states,
  - deterministic fixed-prime chain-bound verification, with canonical JSON artifacts defaulting to `--max-chain-bound 2`.
