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
10. Keep the Monster 10-walk lane on locked canonical semantics (`MONSTER10WALK_CANONICAL.md`) and run `scripts/freeze_monster10walk_canonical.py --strict-lock` as a regression gate whenever physics templates change.
11. Keep canonical edge semantics transition-witnessed by the required template set (`physics8|physics9`) instead of sequence policy alone.
12. Treat `monster/MonsterLean` theorem claims file-by-file by quarantine status; only `closed_for_local_claim_reuse` files may be cited as local proof support.
13. Prioritize closure tracking for `MonsterWalk.lean`, `MonsterWalkPrimes.lean`, `MonsterWalkRings.lean`, and `BottPeriodicity.lean` via the quarantine report queue.
14. Treat the physics lane as a discrete-law measurement problem first: keep exact gates for source-charge conservation, source-parity preservation, locality bounds, forward-cone bounds, and cycle-distance nonincrease, then layer statistical geometry surrogates (perturbation stability, geodesic-like flow, curvature-like concentration, defect attraction) on top of the same artifacts.
15. Continue the template lane only against the corrected cycle-reachable geometry surrogate, not the earlier `distance_to_cycle = -1` biased version.
16. Widen the analyzer with explicit observable surrogates so the next phase can talk about shell/interior occupancy, re-entry, and source-defect coupling directly rather than only through candidate-law scores.
17. Use `physics20` as the current exploratory recurrent-widening branch beyond `physics18/19`, but keep the hard lock anchored to `physics2..physics8` until a later branch is intentionally promoted.
18. Split the next physics round into two explicit branches:
   - `physics21` on the current 6-register carrier, targeting the first direct `boundary -> interior` re-entry without breaking the exact V1 laws.
   - `carrier8_physics1` on a new physics-local 8-register carrier that preserves the first 6 registers and adds `R7` boundary-return memory plus `R8` transport/debt memory.
19. Treat the 6-register `physics21` branch as the only near-term promotion candidate; keep the 8-register branch exploratory and excluded from the hard lock until it emits stable, branch-local observables.

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
   - `physics5` now restores recurrence with split cleared/latched shell rearm and keeps action-rank increases far below `physics3`, but it is still much sparser than the `physics3` lead.
   - `physics6` now improves the ordered hybrid further by adding narrow shell-refresh transitions; it recovers more structure than `physics5` without increasing action-rank jumps, and is the best controlled hybrid so far.
   - the built-in long-tail diagnosis now resolves the one apparent `physics6` timeout to a cycle under a higher cap, so the next pass should widen recurrence from the `physics6` baseline rather than chase tail uncertainty.
   - `physics7` now widens recurrence from `physics6` through preserve-only shell probes, increasing breadth while keeping the action-rank jump count flat.
   - `physics8` now adds staged shell release and improves both breadth and depth from `physics7` while keeping the jump count flat and timeout count at zero.
   - `physics9` now adds shell-stage mid probes and improves breadth from `physics8` (`228` vs `222` edges) while preserving timeout and action-jump bounds.
   - `physics10` now adds a constrained neutral-shell probe on top of `physics9`, improving cyclic coverage (`146` vs `132`) while preserving jump-count (`27`) and timeout (`0`) bounds.
   - `physics11` now adds boundary discharge before shell entry on top of `physics10`, improving breadth and cyclic coverage again (`256` edges, `161` cyclic starts) while keeping jump-count (`27`) and timeout (`0`) bounds flat.
   - `physics12` adds staged-shell boundary detours and improves breadth (`274` edges) while keeping constrained bounds flat, but does not increase depth (`longest_chain` stays `13`).
   - `physics13` adds a targeted mid-contract detour and increases depth to `14` while preserving constrained bounds (`increases=27`, `timeouts=0`).
   - `physics14` adds high-severity shell rearm and improves constrained recurrence strongly (`302` edges, `194` cyclic starts) while preserving depth `14` and constrained bounds (`increases=27`, `timeouts=0`).
   - `physics15` adds a narrow boundary crossfeed detour and pushes depth to `22` while preserving constrained bounds (`303` edges, `194` cyclic starts, `increases=27`, `timeouts=0`).
   - `physics16` adds high-severity boundary discharge and reduces terminal states to `502` while improving recurrence (`330` edges, `227` cyclic starts) under unchanged constrained bounds (`increases=27`, `timeouts=0`).
   - `physics17` adds a narrow boundary handoff and pushes depth to `29` under unchanged constrained bounds (`331` edges, `227` cyclic starts, `increases=27`, `timeouts=0`).
   - `physics18` adds mid-severity boundary discharge and reduces terminal states to `475` while improving recurrence (`358` edges, `254` cyclic starts) under unchanged constrained bounds (`longest_chain=29`, `increases=27`, `timeouts=0`).
  - `physics20` now widens the deterministic recurrent graph to `301` deterministic edges and improves the corrected geometry/defect suite, but it still has `boundary_to_interior = 0`; the next narrow pass should therefore target direct re-entry rather than breadth alone.
  - run `physics21` as a balanced re-entry attempt on the same carrier: preserve exact V1 laws, keep corrected geodesic-like flow `>= 0.90`, and only promote if the branch introduces a nonzero `boundary_to_interior` count alongside a richer deterministic recurrent graph than `physics20`.
  - in parallel, start a physics-local 8-register carrier with explicit return-memory/debt registers so later experiments can separate boundary-return type from transport load instead of overloading the 6-register grammar.

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
