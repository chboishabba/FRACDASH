# FRACDASH Status

## Snapshot

- Date: `2026-03-15`
- Phase: `Phase 2 CORE experiments running`
- State: `active`

## What Exists

- repo-facing mission/context docs
- checked-out fast FRACTRAN baseline in `fractran/`
- working `fractran-bench` CLI
- CPU matrix artifacts in `benchmarks/results/`
- initial compiled exponent-vector prototype in `fractran/src/Compiled.hs`
- LUT-specialized compiled path for binary-threshold programs in `fractran/src/Compiled.hs`
- documented `../dashiCORE` reuse boundary in `DASHICORE_REUSE.md`
- thin `../dashiCORE` bridge in `gpu/dashicore_bridge.py`
- by-reference reuse smoke script in `scripts/check_dashicore_reuse.py`
- FRACTRAN-specific dense GPU contract in `GPU_CONTRACT.md` and `gpu/fractran_layout.py`
- compiled-baseline parity smoke for that contract in `scripts/check_fractran_gpu_layout.py`
- one-step Vulkan shader in `gpu_shaders/fractran_step.comp`
- one-step Vulkan host runner in `gpu/vulkan_fractran_step.py`
- one-step GPU parity smoke in `scripts/check_fractran_vulkan_step.py`
- toy DASHI transition FRACTRAN generator and verifier in `scripts/toy_dashi_transitions.py`, which now exports basin summaries, deterministic basin partitions, and fixed-prime vs explicit-prime walk comparisons across all `3^4` states
- `scripts/agdas_bridge.py` now emits a typed AGDAS-to-transition IR with module/line provenance and also exposes FRACDASH-side wave-1 template transitions derived from selected AGDA definitions.
- `scripts/agdas_bridge.py` now also exposes a compressed wave-2 template set for `MonsterState` / `Monster.Step`.
- The AGDA tree in `../dashi_agda` is now treated as the semantic reference, while the active executable bridge lives in FRACDASH via `AGDAS_BRIDGE_MAPPING.md` and `scripts/agdas_bridge.py`.
- `scripts/toy_dashi_transitions.py` can now execute either parsed source transitions via `--agdas-path` or the primary FRACDASH-side template bridge via `--agdas-templates`.
- The wave-2 template probe artifact now lives at `benchmarks/results/2026-03-14-agdas-template-wave2-phase2.json`.
- `scripts/agdas_wave3_state.py` now defines and validates a prototype 6-register wave-3 carrier for richer Monster-style bridge experiments.
- The wave-3 carrier artifact now lives at `benchmarks/results/2026-03-14-agdas-wave3-state.json`.
- `scripts/agdas_wave3_experiments.py` now executes a wave-3 Monster-facing template set over the 6-register carrier and compares its graph shape against the stored wave-2 artifact.
- The wave-3 execution artifact now lives at `benchmarks/results/2026-03-14-agdas-template-wave3-phase2.json`.
- `formalism/PhysicsBridgeRefreshSketch.agda` now records the local-only formal design for the first physics-facing recurrent seam.
- `scripts/agdas_bridge.py` now also exposes a `physics1` template set based on severity join, contraction-style relaxation, and boundary reset.
- The first physics-facing artifact now lives at `benchmarks/results/2026-03-14-agdas-physics1-phase2.json`.
- `scripts/agdas_physics2_state.py` now defines and validates a dedicated 6-register carrier for the widened physics layer.
- The physics2 carrier artifact now lives at `benchmarks/results/2026-03-14-agdas-physics2-state.json`.
- `scripts/agdas_physics_experiments.py` now executes the widened `physics2` layer over that carrier, and the artifact lives at `benchmarks/results/2026-03-14-agdas-physics2-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics3` cone-shell refinement layer and reports action-phase monotonicity; the artifact lives at `benchmarks/results/2026-03-14-agdas-physics3-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the stricter `physics4` rearm variant; its artifact lives at `benchmarks/results/2026-03-14-agdas-physics4-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics5` hybrid rearm variant; its artifact lives at `benchmarks/results/2026-03-14-agdas-physics5-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics6` shell-refresh refinement; its artifact lives at `benchmarks/results/2026-03-14-agdas-physics6-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics7` shell-probe refinement; its artifact lives at `benchmarks/results/2026-03-14-agdas-physics7-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics8` shell-stage-release refinement; its artifact lives at `benchmarks/results/2026-03-14-agdas-physics8-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics9` shell-stage-mid-probe refinement; its artifact lives at `benchmarks/results/2026-03-15-agdas-physics9-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics10` neutral-shell-probe refinement; its artifact lives at `benchmarks/results/2026-03-15-agdas-physics10-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics11` boundary-discharge refinement; its artifact lives at `benchmarks/results/2026-03-15-agdas-physics11-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics12` staged-shell-detour refinement and `physics13` targeted mid-contract-detour refinement; artifacts live at `benchmarks/results/2026-03-15-agdas-physics12-phase2.json` and `benchmarks/results/2026-03-15-agdas-physics13-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics14` high-severity-shell-rearm refinement; artifact lives at `benchmarks/results/2026-03-15-agdas-physics14-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics15` narrow-boundary-crossfeed refinement; artifact lives at `benchmarks/results/2026-03-15-agdas-physics15-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics16` high-severity-boundary-discharge refinement and `physics17` narrow-boundary-handoff refinement; artifacts live at `benchmarks/results/2026-03-15-agdas-physics16-phase2.json` and `benchmarks/results/2026-03-15-agdas-physics17-phase2.json`.
- `scripts/agdas_physics_experiments.py` now also executes the `physics18` mid-severity-boundary-discharge refinement; artifact lives at `benchmarks/results/2026-03-15-agdas-physics18-phase2.json`.
- `scripts/check_physics_invariant_targets.py` now enforces canonical relationship-level checks over the latest `physics2..physics8` phase and invariant artifacts.
- `PHYSICS_INVARIANT_TARGETS.md` now records the concrete target table (numbers plus relationships) for the current physics lane.
- The first physics target-check artifact now lives at `benchmarks/results/2026-03-15-physics-invariant-target-check.json`.
- The physics lane is now explicitly split into exact substrate laws and statistical geometry surrogates. The next artifact pass should report direct V1 measurements for source-charge conservation, source-parity preservation, locality, forward-cone bounds, perturbation stability, geodesic-like flow, curvature-like concentration, and defect attraction instead of only ranking generic Lyapunov candidates.
- `scripts/physics_invariant_analysis.py` now emits those V1 measurements into every invariant artifact under `physics_target_suite`.
- The refreshed physics target gate still passes on the locked `physics2..physics8` set after the V1 expansion.
- The geometry surrogates now compare only against cycle-reachable local neighbors; this corrects the previous bias where `distance_to_cycle = -1` was treated as locally optimal.
- Under the corrected surrogate, `physics18` and `physics19` are currently equivalent on the deterministic recurrent graph seen by the analyzer; `physics19` remains exploratory but does not yet change the measured V1 physics profile.
- The next template branch is now defined more sharply: target a deterministic graph richer than the current `274`-edge `physics18/19` profile while keeping the exact V1 laws unchanged.
- The next analyzer expansion is also defined: add explicit observable surrogates for shell/interior occupancy, re-entry flow, and source-defect coupling so later physics claims are not bottlenecked on the current law table alone.
- `physics20` now exists as that next template branch. It widens the deterministic recurrent graph to `301` edges, raises the phase graph to `386` edges, lowers terminal states to `428`, and improves the corrected geometry/defect surrogates while preserving the exact V1 laws.
- `scripts/physics_invariant_analysis.py` now emits `observable_surrogates` so later physics interpretation can use region occupancy, action-phase occupancy, re-entry flow, latch alignment, and source-defect coupling directly.
- `scripts/check_physics_invariant_targets.py` now anchors its template matching correctly (`physics20` no longer aliases to `physics2` in the lock gate).
- The next physics implementation round is now split explicitly:
  - `physics21` will stay on the current 6-register carrier and target the first direct `boundary -> interior` re-entry without breaking the exact V1 laws.
  - `carrier8_physics1` will start a separate physics-local 8-register carrier with explicit boundary-return memory and transport/debt memory, and will remain exploratory until its branch-local observables stabilize.
- That split is now implemented:
  - `physics22` is the current active exploratory 6-register baseline: `364` deterministic edges, `boundary_to_interior = 63`, exact V1 laws intact, `geodesic_like_flow.near_min_ratio ~0.92`.
  - `carrier8_physics1` remains exploratory; it exposes `boundary_return_profile` and `transport_debt_profile` and now passes locality/forward-cone under the widened bounds, but it is still outside the lock until its geometry/perturbation signatures improve.
  - `carrier8_physics2` mirrors the `physics22` rules on the 8-register carrier (no return/debt tagging) and now includes interior reset/self-loop rules: locality/forward-cone pass under widened bounds, cycles exist, geodesic-like is strong, but curvature/perturbation metrics are still below target, so the branch stays exploratory.
- `../dashi_agda` should now be treated as the authoritative formal source for the canonical physics-closure semantics; the local bridge remains a compressed executable subset until an explicit intake/check artifact says otherwise.
- That intake/check artifact now exists:
  - `scripts/check_dashi_agda_formalism.py`
  - `benchmarks/results/2026-03-15-dashi-agda-formalism-check.json`
  - `benchmarks/results/2026-03-15-dashi-agda-formalism-check.md`
- Current result: `authoritative_formalism_detected=True`, meaning the expected upstream closure/audit modules are present and the local counterpart/gap mapping is now recorded explicitly.
- Formalism intake was deepened: `AGDAS_FORMALISM_INTAKE.md` now lists Stage C/minimal-credible/seam/observable/known-limits surfaces and their FRACDASH hooks, and the checker now covers those modules (Stage C, minimal-credible adapter, MDL/Fejér, seam certificates, observable package, known-limits QFT bridge) in addition to the original closure/audit spine.
- Carrier-aware locality/forward-cone bounds are now applied for the 8-register branch (`carrier8_*`), and `carrier8_physics1` now passes the exact locality/forward-cone laws under those bounds; the branch remains exploratory and outside the lock.
- canonical rank-4 dataset derivation in `scripts/derive_rank4_dataset.py` with artifacts at `benchmarks/results/2026-03-15-rank4-dataset.json` and `benchmarks/results/rank4-dataset-latest.json`
- rank-4 diagnostics runner in `scripts/run_rank4_diagnostics.py` with artifact `benchmarks/results/2026-03-15-rank4-diagnostics.json`
- rank-4 discriminator runner in `scripts/run_rank4_discriminators.py` with artifacts `benchmarks/results/2026-03-15-rank4-discriminators.json` and `benchmarks/results/2026-03-15-rank4-discriminators.md`
- lock-gated canonical GPU parity runner in `scripts/run_rank4_canonical_gpu_parity.py` with artifact `benchmarks/results/2026-03-15-rank4-canonical-gpu-parity.json`
- prime-triplet q-map ablation runner in `scripts/ablate_prime_triplets.py` with artifact `benchmarks/results/2026-03-15-prime-triplet-ablation.json`
- batched one-step GPU parity through the same shader/runner path
- batched multi-step resident GPU parity through the same shader/runner path
- single-submit multi-dispatch optimization through ping-pong descriptor sets
- first GPU routing benchmark artifact in `benchmarks/results/2026-03-13-gpu-benchmark-primegame-small.json`
- broader GPU routing matrix artifact in `benchmarks/results/2026-03-13-gpu-routing-matrix.json`
- additional GPU routing artifact for `paper_smoke` in `benchmarks/results/2026-03-13-gpu-routing-paper.json`
- extended GPU routing matrix artifact in `benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json`, which covers `primegame_small`, `mult_smoke`, `paper_smoke`, and `hamming_smoke` across the `batch_size = 4, 16, 32, 64, 128` / `steps = 4, 8, 16` band

## What Is Proven

- The local baseline builds and runs on this machine when built dynamically.
- The benchmark CLI works for multiple engines.
- The compiled path matches `reg` and `frac-opt` across the current benchmark matrix.
- The benchmark matrix now uses explicit checkpoint semantics: `exact` for `reg`/`frac-opt`/`compiled`/`lut` and `at-least` for `cycle`.
- The LUT path preserves parity for current LUT-compatible scenarios and cleanly rejects incompatible programs such as `hamming`.
- The LUT path remains parked; it is not the active CPU baseline.
- GPU work is still intentionally deferred until CPU optimization flattens out and a batch-oriented execution shape is chosen.
- A first compiled tuning round ported `frac-opt`-style rule-order narrowing into `Compiled.hs`, and the current matrix now routes to continued compiled-path tuning instead of GPU work.
- A compiled-specific benchmark summary path now keeps compiled states as exponent vectors until checksum/hash evaluation, and the latest canonical matrix has `compiled` ahead of `frac-opt` on the sampled `primegame_*` scenarios.
- Real GHC cost-centre profiling now works on this machine via static profiling, and the latest profiling pass shows benchmark-side `unfExpVec`/checksum work dominating compiled runs, with `applyRule` the largest remaining engine-side hotspot and rule matching materially smaller.
- Two additional profiling-guided CPU rounds landed successfully: `applyRule` now uses element-wise zipping instead of repeated array indexing, and the compiled benchmark path now tracks integer state values directly instead of reconstructing them with `unfExpVec`.
- The current canonical matrix now has `compiled` ahead of `frac-opt` on all sampled `primegame_*` scenarios.
- The reusable part of `../dashiCORE` has now been narrowed to Vulkan host/device plumbing and shader asset conventions, not CORE domain semantics.
- FRACDASH can now resolve `../dashiCORE`, import the reusable Vulkan helper modules by reference, resolve shared shader assets, and exercise the adapter passthrough path without copying CORE code.
- FRACDASH now has a first exact-step GPU contract based on dense exponent vectors and per-rule thresholds/deltas, and that contract matches the compiled CPU baseline on `mult_smoke` and `primegame_small`.
- The minimal DASHI signed-register state space and FRACTRAN encoding is now documented in `DASHI_STATE.md`.
- FRACDASH now has a first real Vulkan step implementation over that contract, and it matches the dense CPU step on `mult_smoke` and `primegame_small` when run on the host GPU with a valid ICD.
- The Vulkan path now also matches dense CPU parity for batched one-step dispatch, including per-state rule selection and halted-state reporting.
- The Vulkan runner now keeps batched state and rule buffers resident across repeated exact steps and still matches dense CPU parity on the final state, selected rule, and halted flags.
- The resident multi-step path now also runs as a single recorded command buffer submission with ping-pong descriptor sets and still preserves parity.
- The first routing benchmark now shows the resident GPU path ahead of the dense CPU contract on `primegame_small` for batch sizes `32`, `128`, and `512` at `32` exact steps.
- The broader routing matrix now supports a first conservative rule on this host: CPU for `batch_size <= 4`, GPU for `batch_size >= 128`, and a scenario-sensitive middle band that already favors GPU for `primegame_small` at `batch_size = 32`, `steps >= 8`.
- The `paper_smoke` matrix aligns with the same threshold, with GPU preferred at `batch_size = 32`, `steps >= 8`, and the `batch_size = 4`, `steps = 32` case still marked `measure-more`.
- The extended routing matrix now supports a deterministic rule (CPU when `batch_size <= 4` or `batch_size = 16` with `steps < 16`; GPU when `batch_size >= 32 && steps >= 8`, or whenever `steps >= 16`), and the artifact lives in `benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json`.
- The deterministic rule provides a stable trigger for upstreaming, so once the routing policy is validated we will move the reusable dispatch/adapter plumbing back into `../dashiCORE` while keeping the FRACTRAN state layout local to FRACDASH.
- Added a CPU timing-regression gate at `scripts/check_timing_regression.py` to catch material slowdowns between matrix artifacts.
- Added a physics relationship-regression gate at `scripts/check_physics_invariant_targets.py` and verified it passes on current `physics2..physics8` artifacts.
- Added `physics9` execution support across `scripts/agdas_bridge.py`, `scripts/agdas_physics_experiments.py`, `scripts/physics_invariant_analysis.py`, and `scripts/ablate_prime_triplets.py`.
- Added MonsterLean intake/lock tooling:
  - `scripts/check_monsterlean_intake.py`
  - `scripts/extract_monsterlean_10walk.py`
  - `scripts/freeze_monster10walk_canonical.py`
  - `scripts/quarantine_monsterlean_claims.py`
- The canonical 10-walk lock is now transition-witnessed and dual-template gated (`physics8|physics9`): `scripts/freeze_monster10walk_canonical.py --strict-lock` currently passes with full canonical support (`9/9`) for both templates.
- The Lean claim quarantine report now includes a prioritized closure queue for `MonsterWalk.lean`, `MonsterWalkPrimes.lean`, `MonsterWalkRings.lean`, and `BottPeriodicity.lean`.
- The prioritized four-file Lean closure pass is now complete: those files currently report `axiom=0`, `sorry=0` and are marked `closed_for_local_claim_reuse`.
- Captured the extended Phase 2 deterministic artifact in `benchmarks/results/2026-03-13-toy-dashi-phase2.json`, including full 81-state round-trip validation, fixed-prime walk statistics, deterministic basin partition data, and fixed-prime-vs-explicit comparison checks.
- Added executable monotone-chain bound checks in `scripts/toy_dashi_transitions.py`; the current deterministic toy transition set has observed max fixed-prime chain length `2` across all `3^4` states.
- Canonical Phase 2 artifact generation is now explicitly locked to `--max-chain-bound 2` by default (via `scripts/run_toy_dashi_phase2.sh`), with `--disable-chain-bound` available for exploratory runs.

## What Is Not Yet Proven

- Which signed DASHI encoding is the canonical target.
- The full AGDAS-to-FRACTRAN bridge from the AGDA semantics into executable dynamics is still not proven: the wave-1 FRACDASH-side template bridge exists, the wave-2 and wave-3 Monster probes now run, but wave-3 is still effectively a one-shot surface because pending choice/admissibility state is not refreshed after a step.
- The first physics-facing bridge seam is more promising: `physics1` already produces nontrivial recurrent behavior on the existing 4-register carrier, so it is currently a higher-signal path than pushing Monster compression further.
- The widened physics layer is now also proven executable: `physics2` expands from the `physics1` carrier to `3^6 = 729` states and yields a much denser recurrent graph (`657` edges, longest chain `12`, deterministic 4-step cycle from the canonical start), so physics-facing bridge work is now the main experimental path.
- The cone-refined physics layer is stronger again: `physics3` preserves the same 6-register carrier, increases the graph to `900` edges over `729` states, raises longest chain to `15`, and exposes an explicit action monotonicity summary, so it is now the leading physics-facing bridge layer.
- The stricter `physics4` layer answers the next question, but negatively: it cuts action-rank increases sharply (`162 -> 9`) and keeps the same carrier, yet collapses the graph to `162` edges with no cycles, so `physics3` remains the better current lead and the next task is a recurrent hybrid rather than tighter guards alone.
- The `physics5` hybrid answers that next question positively but only partially: it restores recurrence (`100` cyclic starts) and keeps action-rank increases much lower than `physics3` (`27` vs `162`), but the graph remains much sparser (`180` edges, longest chain `10`), so `physics3` stays the current lead while `physics5` is the best ordered hybrid so far.
- The `physics6` refinement improves that controlled-hybrid line again: it raises the graph to `198` edges, raises longest chain to `12`, raises cyclic starts to `115`, and keeps action-rank increases flat at `27`. That makes `physics6` the best controlled hybrid so far. The runner now also includes a built-in higher-cap diagnosis, and the one apparent timeout state resolves to a cycle, so the remaining gap is recurrence richness rather than tail instability.
- The `physics7` refinement improves the controlled-hybrid line again through preserve-only shell probes: it raises the graph to `204` edges, raises cyclic starts to `116`, keeps longest chain at `12`, keeps action-rank increases flat at `27`, and shows `0` fixed-walk timeouts at `max-steps 12`. `physics3` still leads on raw richness, but `physics7` is now the best controlled hybrid baseline.
- The `physics8` refinement improves the controlled-hybrid line again by adding staged shell release: it raises the graph to `222` edges, raises longest chain to `13`, raises cyclic starts to `132`, keeps action-rank increases flat at `27`, and keeps fixed-walk timeouts at `0` for `max-steps 12`. `physics3` still leads on raw richness, but `physics8` is now the strongest constrained baseline.
- The `physics9` refinement improves breadth from `physics8` while preserving all current constraints: `228` edges (up from `222`), longest chain `13`, cyclic starts `132`, action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics10` refinement improves cyclic coverage beyond `physics9` while preserving control bounds: `229` edges, longest chain `13`, cyclic starts `146` (up from `132`), action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics11` refinement improves the constrained line again while preserving control bounds: `256` edges, longest chain `13`, cyclic starts `161`, action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics12` refinement improves breadth again while preserving control bounds: `274` edges, longest chain `13`, cyclic starts `161`, action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics13` refinement reaches the next depth target while preserving control bounds: `275` edges, longest chain `14`, cyclic starts `161`, action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics14` refinement improves constrained recurrence strongly while preserving depth and control bounds: `302` edges, longest chain `14`, cyclic starts `194`, action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics15` refinement raises constrained depth strongly while preserving recurrence/control bounds: `303` edges, longest chain `22`, cyclic starts `194`, action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics16` refinement improves constrained recurrence and lowers terminal mass while preserving control bounds: `330` edges, longest chain `22`, cyclic starts `227`, action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics17` refinement raises constrained depth again while preserving recurrence/control bounds: `331` edges, longest chain `29`, cyclic starts `227`, action-rank increases `27`, and fixed-walk timeouts `0`.
- The `physics18` refinement lowers terminal mass again while preserving constrained depth/control bounds: `358` edges, longest chain `29`, cyclic starts `254`, action-rank increases `27`, and fixed-walk timeouts `0`.
- Added `RANK4_OBSTRUCTION_NOTE.md` as a research-grade statement with explicit claim-status boundaries (`observed experimentally` vs `conjectured`) and linked discriminator experiments; TODO Phase 3 now includes local reproduction tasks for those rank-4 diagnostics and tests.
- The local rank-4 reproduction pipeline is now executable and artifact-backed, but the current derived dataset does not yet reproduce the exact `effective dimension = 4` / `chain height = 4` signal; outputs remain report-only while dataset derivation and stability semantics are refined.
- The first prime-triplet ablation pass over `physics8` does not yet show a rank-4 lock signal for `{47,59,71}` versus controls; all sampled triplets remain in the `effective_dimension 8..9`, `chain_height 8..9` band in this projection-only sweep.
- The canonical Monster 10-walk lock artifact now passes in strict mode (`benchmarks/results/2026-03-15-monster10walk-canonical.json`): canonical chain/rank proxy is `4`, and independent FRACDASH transition-data derivations for both `physics8` and `physics9` match canonical adjacency with `9/9` direct support.
- File-by-file Lean claim quarantine is now artifact-backed (`benchmarks/results/2026-03-15-monsterlean-claim-status.{json,md}`): `94` files scanned, `35` closed for local claim reuse, `59` quarantined due to `axiom`/`sorry`.
- Diagnostics strict-mode is now split: `--strict-stable` enforces structural validity, and `--strict-lock` enforces the rank-4 lock gate on the selected canonical derivation.
- How the current middle region behaves on more programs and whether the provisional `batch_size = 32` boundary generalizes beyond `primegame_small` and `paper_smoke`.
- Whether a generalized threshold-aware LUT or another compiled-path optimization can beat `frac-opt`.
- Whether the minimal GPU path can preserve the same exact-step semantics and benchmark contract while keeping state device-resident.

## Next Checkpoint

Checkpoint goal:
- keep the compiled CPU baseline stable, document the deterministic GPU routing rule, and widen the FRACDASH-side AGDAS bridge from the current wave-1 templates toward richer executable seams in `scripts/toy_dashi_transitions.py`.

Exit condition for this phase:
- the routing rule is locked in by the extended matrix artifacts, the toy transition script is stored under `scripts/toy_dashi_transitions.py`, and the upstreaming plan for reusable GPU helpers is ready to execute.
