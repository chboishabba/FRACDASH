# TODO

## Current Bridge Checkpoint

- [x] close `physics1` as the first exact local `X -> Z -> Y` bridge slice
- [x] close `physics3` as the second exact local `X -> Z -> Y` bridge slice
- [x] promote the macro FRACTRAN layer from slice-local to bridge-generic on both the Python and Agda sides
- [x] strengthen structural `WellFormedY` into a substantive paired-prime exclusivity invariant on the closed slices
- [x] add bridge-core validators plus terminal-basin and contraction-cost summaries for the closed slices
- [x] widen the Python-side bridge pipeline to `physics15`
- [x] classify the `physics15_boundary_crossfeed_neutral` conservation break as intended widened semantics (`transmuting_contracting`), not a bridge regression
- [x] widen the next bridge slice batch (`physics19`, `physics20`, `physics21`, `physics22`)
- [x] freeze the theorem split for this phase:
  - `formalism/GenericMacroBridge.agda` stays structural / class-indexed
  - `formalism/BridgeInstances.agda` stays the stronger numeric theorem layer for the closed family
- [x] write the short current formal result note for the closed bridge family
- [x] re-anchor the physics-facing interpretation layer so conservation is scoped to the `conservative_contracting` subregime and widened Batch C slices are described through bounded transmutation

## Current Performance Checkpoint

- [x] add a CPU profiling runner that combines exact-step timing with GHC `.prof` / RTS breakdowns for `compiled`, `frac-opt`, and `reg`
- [x] add a GPU profiling runner that separates cold-start, warm-resident, and per-phase timing on the Vulkan path
- [x] capture one profiling artifact set and a short "obvious gain / no obvious gain" decision summary before any further CPU or GPU optimization work
- [x] keep `cycle` outside the exact-step winner comparison and profile it only as an `at-least` checkpoint engine

## Phase 1: Minimal Model

- [x] Define the smallest DASHI state space that still preserves balanced ternary structure.
- [x] Specify one signed-register FRACTRAN encoding and its invariants.
- [x] Evaluate CPU-first FRACTRAN baselines, especially cycle-detecting or fast-forwarding interpreters.
- [x] Inspect `fractran/src/Fractran.hs` and identify the seam where a benchmark harness or alternative state representation can be introduced with minimal disruption.
- [x] Extend the new `fractran-bench` harness with representative workloads, result capture, and stable output files.
- [x] Compare the new compiled exponent-vector path against `reg`, `frac-opt`, and `cycle` on the same workloads.
- [x] Define the LUT/divisibility-mask representation to test next.
- [x] Implement a CPU LUT path and benchmark it against the current matrix baseline.
- [x] Keep `cycle` on `at-least` checkpoint semantics in future matrices; do not regress to exact-step comparison.
- [x] Decide whether to pursue a threshold-aware generalized LUT or return to compiled-path tuning.
- [x] Port `frac-opt`-style rule-order narrowing into the compiled evaluator.
- [x] Reduce benchmark-side compiled-path decoding overhead and rerun the matrix.
- [x] Reduce compiled-path allocation overhead inside `Compiled.hs` and rerun the matrix.
- [x] Decide whether `compiled` is now the practical CPU baseline for subsequent work.
- [x] Decide the initial deliverable:
  - a direct interpreter for the signed encoding
  - a compiler from DASHI transitions to vanilla FRACTRAN fractions
  - a benchmark harness around an existing fast CPU interpreter
    The current deliverable is the deterministic benchmark harness (with compiled parity checks) that exercises the signed encoding.

## Phase 2: Core Experiments

- [x] Implement a toy DASHI-to-FRACTRAN transition set for a signed 4-register `3^4` state space.
- [x] Build a decoder that maps prime exponent vectors back to DASHI states.
- [x] Compare fixed-prime dynamics against dynamics that explicitly reintroduce primes.
- [x] Encode and test the 10-basin walk as data (captured as deterministic basin partition statistics).
- [x] Verify the fixed-prime monotone-chain bound across all `3^4` states by executable search (`--max-chain-bound`) in
  [`scripts/toy_dashi_transitions.py`](/home/c/Documents/code/FRACDASH/scripts/toy_dashi_transitions.py). Current artifact reports `max_observed_chain=2`, so the bound holds for `2`.
- [ ] Implement the full AGDAS physics bridge from the AGDA semantics in `../dashi_agda`:
  - [x] add typed extraction/parsing into transition primitives (`scripts/agdas_bridge.py`)
  - [x] map parsed transition rules into FRACTRAN candidates with provenance
  - [x] wire that output into the Phase 2 verifier path and preserve round-trip checks (`scripts/toy_dashi_transitions.py --agdas-path`)
  - [x] define a FRACDASH-side wave-1 mapping in `AGDAS_BRIDGE_MAPPING.md`
  - [x] implement FRACDASH-side wave-1 template transitions in `scripts/agdas_bridge.py`)
  - [x] run the wave-1 template transitions through the Phase 2 verifier path (`--agdas-templates`)
  - [x] add a compressed wave-2 `MonsterState` / `Monster.Step` template set
  - [x] run the wave-2 template set through the Phase 2 verifier path and capture the artifact
  - [x] decide to enlarge the encoded state model before widening beyond the compressed Monster seam
  - [x] add a prototype wave-3 enlarged state carrier in `scripts/agdas_wave3_state.py`
  - [x] thread the wave-3 carrier into executable bridge experiments
  - [x] add a wave-3 Monster-facing template set in `scripts/agdas_bridge.py`
  - [x] compare the wave-3 bridge graph against the wave-2 artifact
  - [ ] add recurrent/refresh transitions so wave-3 is not just a one-shot step surface
  - [x] add a first physics-facing recurrent bridge seam (`physics1`) based on severity propagation and contraction
  - [x] capture the first physics-facing artifact (`benchmarks/results/2026-03-14-agdas-physics1-phase2.json`)
  - [x] implement the widened `physics2` layer on a dedicated 6-register carrier
  - [x] capture the first `physics2` artifact and compare it to `physics1`
  - [x] decide that the next physics pass should add cone-interior refinement first and report action monotonicity
  - [x] implement `physics3` on the same 6-register carrier
  - [x] capture the first `physics3` artifact and compare it to `physics2`
  - [x] decide that the next physics pass should tighten action-monotonicity constraints before adding more scan variants
  - [x] implement `physics4` on the same 6-register carrier with stricter shell/interior rearm guards
  - [x] capture the first `physics4` artifact and compare it to `physics3`
  - [x] design a `physics5` hybrid that restores recurrence while keeping most of the `physics4` monotonicity gain
  - [x] implement `physics5` on the same 6-register carrier with split shell-to-interior rearm
  - [x] capture the first `physics5` artifact and compare it to `physics3` and `physics4`
  - [x] design a `physics6` refinement that keeps the `physics5` hybrid but recovers more recurrent structure
  - [x] implement `physics6` with narrow shell-refresh transitions on top of `physics5`
  - [x] capture the first `physics6` artifact and compare it to `physics5`
  - [x] diagnose the remaining `physics6` timeout tail by rerunning with a higher walk cap and classifying the long-path states
  - [x] design a `physics7` refinement that widens recurrence from the `physics6` baseline without increasing the action-rank jump count
  - [x] implement `physics7` with preserve-only shell probe transitions on top of `physics6`
  - [x] capture the first `physics7` artifact and compare it to `physics6`
  - [x] design a `physics8` refinement that increases chain depth from the `physics7` baseline without increasing the action-rank jump count
  - [x] implement `physics8` with shell-stage release transitions on top of `physics7`
  - [x] capture the first `physics8` artifact and compare it to `physics7`
  - [x] design a `physics9` refinement that improves richness from `physics8` without increasing action-rank jump count or timeout count
  - [x] implement `physics9` with shell-stage mid probes on top of `physics8`
  - [x] capture the first `physics9` artifact and compare it to `physics8`
  - [x] design a `physics10` refinement that increases cyclic starts beyond `physics9` while keeping action-rank jump count and timeout count flat
  - [x] implement `physics10` with a constrained neutral-shell probe on top of `physics9`
  - [x] capture the first `physics10` artifact and compare it to `physics9`
  - [x] design a `physics11` refinement that widens recurrence from `physics10` while keeping action-rank jump count and timeout count flat
  - [x] implement `physics11` with boundary discharge before shell entry on top of `physics10`
  - [x] capture the first `physics11` artifact and compare it to `physics10`
  - [x] design a `physics12` refinement that increases chain depth beyond `13` while preserving `increases=27` and `timeouts=0`
  - [x] implement `physics12` as staged-shell boundary detours on top of `physics11`
  - [x] capture the first `physics12` artifact and compare it to `physics11`
  - [x] implement `physics13` targeted mid-contract detour on top of `physics12` and capture first artifact
  - [x] verify `physics13` reaches chain depth `14` while preserving `increases=27` and `timeouts=0`
  - [x] design a `physics14` refinement that improves cyclic starts beyond `161` while preserving chain depth `14`, `increases=27`, and `timeouts=0`
  - [x] implement `physics14` with high-severity shell rearm on top of `physics13`
  - [x] capture the first `physics14` artifact and verify constrained gains
  - [x] design a `physics15` refinement that keeps cyclic starts at or above `194` while attempting depth `15` without raising `increases` or `timeouts`
  - [x] implement `physics15` with narrow boundary crossfeed detour on top of `physics14`
  - [x] capture the first `physics15` artifact and verify constrained gains
  - [x] design a `physics16` refinement that reduces terminal states below `535` while preserving `cycle>=194`, `longest_chain>=22`, `increases=27`, and `timeouts=0`
  - [x] implement `physics16` with high-severity boundary discharge on top of `physics15`
  - [x] capture the first `physics16` artifact and verify constrained gains
  - [x] implement `physics17` narrow boundary handoff on top of `physics16` and capture first artifact
  - [x] verify `physics17` raises depth while preserving constrained bounds
  - [x] design a `physics18` refinement that reduces terminal states below `500` while preserving `cycle>=227`, `longest_chain>=29`, `increases=27`, and `timeouts=0`
  - [x] implement `physics18` with mid-severity boundary discharge on top of `physics17`
  - [x] capture the first `physics18` artifact and verify constrained gains
  - [x] design a `physics19` refinement that keeps terminal states at or below `475` while attempting depth `>=30` without raising `increases` or `timeouts`
  - [x] design and implement a `physics20` refinement that widens the deterministic recurrent graph beyond `274` edges while preserving the exact V1 laws and measuring the result against the corrected cycle-reachable geometry surrogate
  - [x] design and implement a `physics21` refinement on the same 6-register carrier that produces the first direct `boundary -> interior` re-entry while preserving the exact V1 laws and keeping corrected geodesic-like flow at or above `0.90`
  - [x] add a physics-local 8-register carrier branch with explicit boundary-return memory and transport/debt memory, then capture the first `carrier8_physics1` artifact with branch-local observable summaries
  - [x] add an authoritative AGDA closure intake/check artifact against `../dashi_agda`:
    - [x] verify the canonical closure/audit modules exist and are readable
    - [x] record their local FRACDASH executable counterparts or current gaps
    - [x] treat that artifact as the source-of-truth bridge status for future physics work
  - [x] document upstream Stage C / minimal-credible / seam / observable surfaces and their FRACDASH wiring map in `AGDAS_FORMALISM_INTAKE.md`
  - [x] extend the formalism checker to cover Stage C, MDL/Fejér/seam, observable, and known-limits QFT bridge modules
  - [x] refresh the formalism intake for the upstream execution-admissibility / family-classification witness expansion in `MinimalCrediblePhysicsClosure`, `PhysicsClosureCoreWitness`, and `PhysicsClosureFullInstance`
  - [x] add a first explicit FRACDASH-side executable witness/status layer (ExecutionWitnessSketch + per-slice status in BridgeInstances) for upstream execution admissibility beyond the regime-surrogate bridge theorems; reporters now emit `execution_status`
  - [x] add per-slice regime-class usage summary to execution status (conservative-only vs mixed transmuting)
  - [x] thread regime-class family tags/usage into invariant reports so failures can be scoped by class
  - [x] bulk-wire upstream surfaces into FRACDASH execution and reporting:
    - [x] add Stage C / minimal-credible targets to the invariant/observable reporters
    - [x] surface MDL/Fejér and seam certificate checks (or TODO stubs) in the physics target suite
    - [x] emit lift/scan/Monster provenance on generated templates for debugging and regression
- [ ] Introduce a prime-exponent-vector engine for batched runs and compare it against the bigint/cycle-detecting baseline.
- [ ] Prototype LUT or divisibility-mask rule selection on CPU before any GPU port.

## Phase 3: Interpretation

- [ ] Measure which invariants survive translation: locality, parity, reversibility, contraction, chamber structure.
- [x] Define a canonical physics-invariant target table (numbers + relationships) for `physics2..physics8`.
- [x] Add a physics-invariant regression checker that validates new artifacts against the canonical target table.
- [x] Upgrade the physics target table to a V1 mixed exact/statistical suite with direct physics-facing surrogate laws.
- [x] Extend invariant artifacts to emit `source_charge`, parity, locality, forward-cone, perturbation-stability, geodesic-like, curvature-like, and defect-attraction measurements.
- [x] Add a first observable-surrogate block beyond the V1 law table so artifacts also report shell/interior occupancy, source-defect alignment, and re-entry flow statistics.
- [x] Extend observable surrogates with branch-aware re-entry and 8-register memory profiles:
  - [x] `boundary_return_profile` for return-memory-tagged 8-register states
  - [x] `transport_debt_profile` for transport/debt occupancy splits on the 8-register branch
- [x] Promote `physics22` as the active exploratory 6-register baseline for future invariant work.
- [x] Build a widened-family comparison artifact for `physics15`, `physics19`, `physics20`, `physics21`, and `physics22` that aligns `execution_status` / regime usage with recurrent-core and geometry-surrogate outcomes.
- [x] Build a `physics21 -> physics22` baseline-delta artifact so future 6-register refinements are judged against the actual handoff gain shape, not just the widened-family endpoint table.
- [ ] Design the next 6-register refinement against the `physics22` baseline-delta target:
  - preserve the current fixed-walk cycle/terminal split
  - preserve `distance_to_cycle` as best candidate and keep geometry surrogates at least flat
  - improve the deterministic recurrent core beyond the current `physics22` delta profile
- [x] Decide whether the first `physics23` trial (`476 -> 503` deterministic edges, other main axes flat) is enough to replace `physics22` as the active 6-register baseline or should remain a successor candidate only.
- [x] Keep `physics23` as a genuine successor candidate, but not the active baseline yet: it improves the deterministic recurrent core without yet beating `physics22` on terminal mass or direct re-entry.
- [x] Build a cross-carrier comparison artifact that lines up the active 6-register baseline (`physics22`) against the exploratory 8-register branches on comparable recurrent-core / geometry / branch-local-observable axes.
- [x] Decide whether to treat `carrier8_physics2` as the active parallel 8-register experiment track, distinct from but not replacing the `physics22` 6-register baseline.
- [x] Treat `carrier8_physics2` as the active parallel 8-register track for now; `carrier8_physics3` did not move the shared comparison surface enough to dislodge it.
- [x] Design the next 8-register refinement beyond `carrier8_physics2/3`; target the actual weak point from `carrier8_physics3` by inserting an earlier boundary-return re-entry hook that can compete with the broad return-memory damping rules.
- [x] Design the next 8-register refinement beyond `carrier8_physics4`; the first early re-entry insertion still leaves the shared cross-carrier summary flat, so the next branch should target a deeper carrier8 basin/selection change rather than another placement-only tweak.
- [x] Decide whether `carrier8_physics5` is enough to replace `carrier8_physics2` as the active parallel 8-register baseline or should remain a successor candidate only; it is the first branch with nonzero sampled `boundary_to_interior`, but it gives back some curvature spread.
- [x] Promote `carrier8_physics6` as the provisional 8-register baseline: keeps `boundary_to_interior=6`, restores curvature (`~0.97`), small geodesic dip (`~0.989`), best-candidate strict decrease back to baseline (`~0.515`).
- [ ] Ingest a real source/attractor basis (ERDFA/CFT eigenvectors or PCA) and rerun physics6 with `--cone-basis` to get selective Δ-cone rejection; current placeholder bases reject 0 edges.
- [ ] Design the next 8-register refinement beyond `carrier8_physics6` informed by the rejection pattern from a source-aligned cone; target geodesic/strict recovery without losing boundary/curvature.
- [x] Add a deterministic-walk waveform renderer for saved phase-2 artifacts:
  - `scripts/render_trace_waveform.py`
  - emits standalone HTML + PNG from `deterministic_walk.path`
  - auto-enriches from matching invariant artifacts when available
- [ ] Decide whether the `113` total degeneracy has structural support or should be discarded as coincidence.
- [ ] Write and maintain the short result note distinguishing observations from conjectures for the active `physics22` exploratory baseline.
- [ ] Intake `monster/MonsterLean` references into FRACDASH with proof-completeness filtering:
  - [x] generate a machine-readable inventory for candidate modules (`MonsterWalk*`, `ComplexityLattice`) with `sorry`/`axiom` flags
  - [x] extract only reusable definitions/constants into FRACDASH-side notes
  - [x] reject or quarantine theorem claims that depend on `sorry`/`axiom` until reproduced experimentally in FRACDASH
  - [x] add a first constants-only 10-walk extractor from `BottPeriodicity.lean` and capture a diagnostic artifact
  - [x] freeze and lock canonical 10-walk semantics with strict-mode artifact gate
  - [x] re-derive the same 10-node walk topology from FRACDASH transition data and verify derivation match
  - [x] expand strict lock to required template set support (`physics8|physics9`) and transition-witnessed canonical edge semantics
  - [x] use lock script defaults as a regression gate (`scripts/freeze_monster10walk_canonical.py --strict-lock`)
  - [x] generate file-by-file Lean claim status (closed vs quarantined) for `monster/MonsterLean/*.lean`
  - [x] add prioritized closure queue reporting for `MonsterWalk.lean`, `MonsterWalkPrimes.lean`, `MonsterWalkRings.lean`, and `BottPeriodicity.lean`
  - [x] close prioritized Lean files by replacing `axiom`/`sorry` with narrowed, artifact-backed executable statements
- [ ] Reproduce the rank-4 obstruction diagnostics locally as artifacts:
  - [x] PCA effective-dimension measurement on the basin-prime matrix
  - [x] independent monotone-chain height measurement
- [ ] Run rank-4 discriminator experiments from `RANK4_OBSTRUCTION_NOTE.md`:
  - [x] root-length test (`D4` vs `F4`)
  - [x] reflection-closure test
  - [x] orbit-multiplicity test
  - [x] Clifford reflection test
  - [x] stability-gradient chamber test
- [x] Add a prime-triplet q-map ablation (`{47,59,71}` vs controls) to check whether obstruction diagnostics are specific or generic.

## Phase 4: GPU Reuse Path

- [x] Confirm which `../dashiCORE` modules are stable enough to reference directly for Vulkan dispatch, shader compilation, and GEMV-style kernels.
- [x] Add a thin FRACDASH-local adapter that imports `../dashiCORE` Vulkan helpers by reference.
- [x] Design a thin FRACDASH adapter layer that imports or shells out to `../dashiCORE` GPU infrastructure without copying files.
- [x] Add a smoke script that proves by-reference import and adapter passthrough without copying CORE code.
- [x] Define the first FRACTRAN-specific GPU buffer layout on top of the new bridge.
- [x] Prove the dense FRACTRAN GPU contract against the compiled CPU baseline on `mult_smoke` and `primegame_small`.
- [x] Turn the dense FRACTRAN contract into the first real Vulkan kernel interface.
- [x] Prove one-step GPU parity on `mult_smoke` and `primegame_small`.
- [x] Expand the Vulkan path from single-state stepping to batched state buffers.
- [x] Keep GPU state resident across many FRACTRAN steps; avoid per-step host/device roundtrips.
- [x] Extend the batched Vulkan path from one-step dispatch to multi-step device-resident execution.
- [x] Reduce submit and command-buffer overhead on the now-correct resident multi-step path.
- [x] Benchmark the single-submit resident GPU path against the dense compiled-equivalent CPU contract on larger batches.
- [x] Expand the routing benchmark beyond `primegame_small` and beyond the current `batch_size >= 32`, `steps = 32` regime.
- [x] Promote the current conservative routing rule into a deterministic CPU/GPU routing rule after more middle-region measurements and one additional program beyond `paper_smoke`.
- [x] Define the rule for when a FRACDASH GPU helper/kernel should be upstreamed back into `../dashiCORE`.

## Open Decisions

- [ ] Which DASHI operations count as the canonical subset for reimplementation?
- [ ] Which signed encoding is simplest while remaining faithful?
- [ ] Should experiments start from a hand-written FRACTRAN kernel, a higher-level compiler, or a wrapper around an existing fast CPU evaluator?
- [ ] What measured hotspot, if any, would justify GPU work later?
- [ ] After compiled-path tuning, is the next CPU experiment a generalized LUT keyed by threshold buckets or a batched/vectorized path?
- [x] Should FRACDASH use direct imports from `../dashiCORE`, local symlinks, or a small compatibility layer for shared GPU assets?
- [x] Should the first Vulkan kernel advance one trajectory exactly or prioritize multi-trajectory batching from the start?
