# FRACDASH Status

## Snapshot

- Date: `2026-03-13`
- Phase: `CPU seam extraction`
- State: `active`

## What Exists

- repo-facing mission/context docs
- checked-out fast FRACTRAN baseline in `fractran/`
- working `fractran-bench` CLI
- initial benchmark artifacts in `benchmarks/results/`
- initial compiled exponent-vector prototype in `fractran/src/Compiled.hs`

## What Is Proven

- The local baseline builds and runs on this machine when built dynamically.
- The benchmark CLI works for multiple engines.
- The compiled path matches sampled outputs for tested runs.

## What Is Not Yet Proven

- That the compiled path is consistently faster across representative workloads.
- Which signed DASHI encoding is the canonical target.
- Whether LUT work is the next best CPU optimization.
- Whether GPU reuse through `../dashiCORE` is clean enough without a dedicated adapter.

## Next Checkpoint

Checkpoint goal:
- enough benchmark coverage to choose the next CPU optimization step with confidence

Exit condition for this phase:
- benchmark-backed decision between compiled-path optimization and LUT work
