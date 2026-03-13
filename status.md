# FRACDASH Status

## Snapshot

- Date: `2026-03-13`
- Phase: `CPU tuning checkpoint reached`
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
- batched one-step GPU parity through the same shader/runner path
- batched multi-step resident GPU parity through the same shader/runner path
- single-submit multi-dispatch optimization through ping-pong descriptor sets
- first GPU routing benchmark artifact in `benchmarks/results/2026-03-13-gpu-benchmark-primegame-small.json`
- broader GPU routing matrix artifact in `benchmarks/results/2026-03-13-gpu-routing-matrix.json`
- additional GPU routing artifact for `paper_smoke` in `benchmarks/results/2026-03-13-gpu-routing-paper.json`

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
- FRACDASH now has a first real Vulkan step implementation over that contract, and it matches the dense CPU step on `mult_smoke` and `primegame_small` when run on the host GPU with a valid ICD.
- The Vulkan path now also matches dense CPU parity for batched one-step dispatch, including per-state rule selection and halted-state reporting.
- The Vulkan runner now keeps batched state and rule buffers resident across repeated exact steps and still matches dense CPU parity on the final state, selected rule, and halted flags.
- The resident multi-step path now also runs as a single recorded command buffer submission with ping-pong descriptor sets and still preserves parity.
- The first routing benchmark now shows the resident GPU path ahead of the dense CPU contract on `primegame_small` for batch sizes `32`, `128`, and `512` at `32` exact steps.
- The broader routing matrix now supports a first conservative rule on this host: CPU for `batch_size <= 4`, GPU for `batch_size >= 128`, and a scenario-sensitive middle band that already favors GPU for `primegame_small` at `batch_size = 32`, `steps >= 8`.
- The `paper_smoke` matrix aligns with the same threshold, with GPU preferred at `batch_size = 32`, `steps >= 8`, and the `batch_size = 4`, `steps = 32` case still marked `measure-more`.

## What Is Not Yet Proven

- Which signed DASHI encoding is the canonical target.
- How the current middle region behaves on more programs and whether the provisional `batch_size = 32` boundary generalizes beyond `primegame_small` and `paper_smoke`.
- Whether a generalized threshold-aware LUT or another compiled-path optimization can beat `frac-opt`.
- Whether the minimal GPU path can preserve the same exact-step semantics and benchmark contract while keeping state device-resident.

## Next Checkpoint

Checkpoint goal:
- define and implement the minimal GPU path against the now-stable compiled CPU shape, starting from the working `../dashiCORE` bridge

Exit condition for this phase:
- first measured CPU/GPU routing checkpoint with parity anchor preserved
