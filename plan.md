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

### Milestone G: Bridge correctness formalization

Status: active

- state the AGDAS -> FRACDASH bridge as a source/target semantics problem
- define compile / decode / abstraction maps explicitly
- record the simulation/refinement obligation actually being claimed
- record quotient assumptions for reduced carriers and template families
- separate bridge-correctness obligations from downstream physics interpretation

Current direction:

- treat the remaining math as structured compiler-correctness math, not as
  moonshine/QFT interpretation work
- keep prime-exponent reachability, Lyapunov descent, contraction preservation,
  decoder validity, and robustness in the core bridge package
- keep root-system / curvature / QFT language downstream until the bridge
  package is tighter

### Milestone H: Physics1 Numeric Macro Realization

Status: active

- complete the first real `X -> Z -> Y` bridge slice on `physics1`
- keep the signed exponent-vector IR as the semantic surface
- turn the symbolic paired-prime macro layer into a concrete numeric FRACTRAN program
- state and check the first real signed-IR -> FRACTRAN soundness law

Current direction:

- treat `physics1` as the gold slice for hard bridge work before widening to later template families
- keep the exact `StepDelta` proof fixed and build the numeric realization beneath it
- preserve macro-step execution as the soundness target; do not collapse back to single-fraction semantics
- use the saved Python oracle artifact as regression input, but keep Agda / bridge semantics as the certification surface
- defer `physics3`, `physics15`, `physics19`, `physics20`, `physics21`, and `physics22` bridge-proof expansion until `physics1` has a checked numeric realization

### Milestone I: Physics3 Formal Closure

Status: complete

- close `physics3` as the second full bridge slice
- keep Python limited to delta export, macro checks, and regression fixtures
- prove the bridge generalizes beyond `physics1` before widening further

Current direction:

- `physics3` now has exact delta export, numeric macro soundness, bridge-local invariants, and a compiled formal `StepDelta` / explicit `X -> Z -> Y` package
- the bridge has now been closed on two concrete slices, which is enough to move the hard path into generic macro realization work rather than more slice-local proving first
- the next success condition is a reusable macro FRACTRAN contract shared cleanly by both `physics1` and `physics3`

### Milestone J: Generic Macro FRACTRAN Layer

Status: complete

- promote macro realization from slice-local code into bridge-generic machinery
- add a reusable Agda execution contract above the now-shared Python macro layer
- fix the reusable execution contract for `UnitDelta`, normalization, exclusivity, and `realizeUnit`
- benchmark the FRACTRAN-side cost surface once the generic path is stable

## Immediate Next Actions

### Hard Track

1. Keep Python frozen at oracle/export/regression scope unless a change directly reduces uncertainty in `X -> Z` or `Z -> Y`.
2. Treat the widened Batch C bridge family as the current stable local claim:
   - `physics15..physics22` remain `regime-valid`
   - the transmuting subregime is stable rather than a one-off
   - the canonical summary artifact is `benchmarks/results/2026-03-19-bridge-regime-summary.{json,md}`
3. Keep `formalism/BridgeInstances.agda` as the stronger numeric theorem layer for now, but preserve the partial generic lift already landed in `formalism/GenericMacroBridge.agda`:
   - class-indexed contraction/transmutation witness types stay generic
   - class-indexed numeric bound extractors now also stay generic
   - slice-relative residual theorems stay at the master layer unless another family proves they are truly generic
4. Promote the stable bridge claim consistently across repo summaries and downstream notes:
   - exact paired-prime macro realization
   - well-formedness preservation
   - strict contraction
   - bounded transmutation on widened slices
5. Shift the main engineering line toward proof-carrying consolidation:
   - source/target semantics packaging
   - named refinement obligations
   - decoder-validity / robustness statements
   - bridge-family theorem wording suitable for reuse
6. Keep the bridge-core validator package fixed as the shared observational layer:
   - conservation where applicable
   - L1 / Lyapunov descent
   - reversibility / irreversibility classification
   - terminal-basin and contraction-profile summaries
7. Treat the solver lane as decision-complete for now:
   - `wave` is structurally mismatched
   - `heat` is the least-bad fallback and only `qualitative_only`
   - do not spend more main-line effort on solver-speed claims unless a later matched-grid heat comparison is explicitly resumed
8. Use interpretation work downstream of the stable bridge claim rather than as a replacement for it.
9. Do one explicit CPU/GPU profiling pass before any further performance tuning:
   - CPU exact-step profiling should compare `compiled`, `frac-opt`, and `reg`
     using both wall-clock timing and GHC `.prof` / RTS summaries
   - GPU profiling should separate cold-start and warm-resident timings so host
     overhead is not mistaken for device cost
   - the profiling milestone should end with a decision artifact, not with a
     speculative optimization branch

### Delegated Support Track

1. Add normalization and macro metadata to the saved `physics1` oracle artifact so macro length and unit-step ordering are reproducible.
2. Keep the `compiled` engine as the stable exact-step CPU baseline while monitoring parity/artifacts.
3. Record the deterministic GPU routing rule derived from `benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json` and use it as the gating condition for future host/GPU work.
4. Once the routing policy is locked, upstream any reusable helper/adapter plumbing back into `../dashiCORE` while keeping the FRACTRAN-specific state layout and parity logic local to FRACDASH.
5. Continue referencing the `../dashiCORE` Vulkan helpers via `gpu/dashicore_bridge.py` and the adapter passthrough smoke path.
6. Preserve the exact vs. at-least checkpoint semantics and keep the `cycle` engine pegged as the at-least sentinel.
7. Keep bridge-oriented summaries, artifact tables, solver-probe notes, and status docs synchronized while the hard track lands.

### Bridge Expansion Order

1. `physics1`
2. `physics3`
3. Batch A: `physics4..physics8`
4. Batch B: `physics9..physics13`
5. Batch C: `physics15`, `physics19`, `physics20`, `physics21`, `physics22`
6. Batch D: `carrier8_physics1`, `carrier8_physics2`

Hard-track rule:
- do not widen beyond the current item until the previous family or batch has exact `StepDelta`, numeric macro realization, and checked invariant coverage

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
