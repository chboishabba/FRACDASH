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

## What Is Not Yet Proven

- Which signed DASHI encoding is the canonical target.
- Whether GPU reuse through `../dashiCORE` is clean enough without a dedicated adapter.
- Whether a generalized threshold-aware LUT or another compiled-path optimization can beat `frac-opt`.
- Whether the minimal GPU path can preserve the same exact-step semantics and benchmark contract while keeping state device-resident.

## Next Checkpoint

Checkpoint goal:
- define and implement the minimal GPU path against the now-stable compiled CPU shape

Exit condition for this phase:
- first minimal GPU design/implementation checkpoint with CPU parity anchor preserved
