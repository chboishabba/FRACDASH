# FRACDASH Status

## Snapshot

- Date: `2026-03-14`
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
- Captured the extended Phase 2 deterministic artifact in `benchmarks/results/2026-03-13-toy-dashi-phase2.json`, including full 81-state round-trip validation, fixed-prime walk statistics, deterministic basin partition data, and fixed-prime-vs-explicit comparison checks.
- Added executable monotone-chain bound checks in `scripts/toy_dashi_transitions.py`; the current deterministic toy transition set has observed max fixed-prime chain length `2` across all `3^4` states.
- Canonical Phase 2 artifact generation is now explicitly locked to `--max-chain-bound 2` by default (via `scripts/run_toy_dashi_phase2.sh`), with `--disable-chain-bound` available for exploratory runs.

## What Is Not Yet Proven

- Which signed DASHI encoding is the canonical target.
- The full AGDAS-to-FRACTRAN bridge from the AGDA semantics into executable dynamics is still not proven: the wave-1 FRACDASH-side template bridge exists, the wave-2 and wave-3 Monster probes now run, but wave-3 is still effectively a one-shot surface because pending choice/admissibility state is not refreshed after a step.
- The first physics-facing bridge seam is more promising: `physics1` already produces nontrivial recurrent behavior on the existing 4-register carrier, so it is currently a higher-signal path than pushing Monster compression further.
- The widened physics layer is now also proven executable: `physics2` expands from the `physics1` carrier to `3^6 = 729` states and yields a much denser recurrent graph (`657` edges, longest chain `12`, deterministic 4-step cycle from the canonical start), so physics-facing bridge work is now the main experimental path.
- How the current middle region behaves on more programs and whether the provisional `batch_size = 32` boundary generalizes beyond `primegame_small` and `paper_smoke`.
- Whether a generalized threshold-aware LUT or another compiled-path optimization can beat `frac-opt`.
- Whether the minimal GPU path can preserve the same exact-step semantics and benchmark contract while keeping state device-resident.

## Next Checkpoint

Checkpoint goal:
- keep the compiled CPU baseline stable, document the deterministic GPU routing rule, and widen the FRACDASH-side AGDAS bridge from the current wave-1 templates toward richer executable seams in `scripts/toy_dashi_transitions.py`.

Exit condition for this phase:
- the routing rule is locked in by the extended matrix artifacts, the toy transition script is stored under `scripts/toy_dashi_transitions.py`, and the upstreaming plan for reusable GPU helpers is ready to execute.
