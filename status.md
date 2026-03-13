# FRACDASH Status

## Snapshot

- Date: `2026-03-13`
- Phase: `Compiled-path tuning`
- State: `active`

## What Exists

- repo-facing mission/context docs
- checked-out fast FRACTRAN baseline in `fractran/`
- working `fractran-bench` CLI
- CPU matrix artifacts in `benchmarks/results/`
- initial compiled exponent-vector prototype in `fractran/src/Compiled.hs`
- LUT-specialized compiled path for binary-threshold programs in `fractran/src/Compiled.hs`

## What Is Proven

- The local baseline builds and runs on this machine when built dynamically.
- The benchmark CLI works for multiple engines.
- The compiled path matches `reg` and `frac-opt` across the current benchmark matrix.
- The benchmark matrix now uses explicit checkpoint semantics: `exact` for `reg`/`frac-opt`/`compiled`/`lut` and `at-least` for `cycle`.
- The LUT path preserves parity for current LUT-compatible scenarios and cleanly rejects incompatible programs such as `hamming`.
- The current decision rule keeps `frac-opt` as the practical CPU baseline; the LUT path does not outperform it on `primegame_medium` and `primegame_large`.
- GPU work is still intentionally deferred until CPU optimization flattens out and a batch-oriented execution shape is chosen.
- A first compiled tuning round ported `frac-opt`-style rule-order narrowing into `Compiled.hs`, and the current matrix now routes to continued compiled-path tuning instead of GPU work.
- A compiled-specific benchmark summary path now keeps compiled states as exponent vectors until checksum/hash evaluation, and the latest canonical matrix has `compiled` ahead of `frac-opt` on the sampled `primegame_*` scenarios.

## What Is Not Yet Proven

- Which signed DASHI encoding is the canonical target.
- Whether GPU reuse through `../dashiCORE` is clean enough without a dedicated adapter.
- Whether a generalized threshold-aware LUT or another compiled-path optimization can beat `frac-opt`.
- Whether the new compiled lead survives another round of tuning and wider workloads.

## Next Checkpoint

Checkpoint goal:
- benchmark a compiled-path tuning round against the existing matrix

Exit condition for this phase:
- measured decision on whether the compiled seam is converging toward `frac-opt` or should be deprioritized
