# TODO

## Phase 1: Minimal Model

- [ ] Define the smallest DASHI state space that still preserves balanced ternary structure.
- [ ] Specify one signed-register FRACTRAN encoding and its invariants.
- [ ] Evaluate CPU-first FRACTRAN baselines, especially cycle-detecting or fast-forwarding interpreters.
- [ ] Inspect `fractran/src/Fractran.hs` and identify the seam where a benchmark harness or alternative state representation can be introduced with minimal disruption.
- [ ] Extend the new `fractran-bench` harness with representative workloads, result capture, and stable output files.
- [ ] Compare the new compiled exponent-vector path against `reg`, `frac-opt`, and `cycle` on the same workloads.
- [ ] Optimize the compiled path's compatibility checks and data layout; it currently validates parity but trails `frac-opt` on sampled `primegame` runs.
- [ ] Decide the initial deliverable:
  - a direct interpreter for the signed encoding
  - a compiler from DASHI transitions to vanilla FRACTRAN fractions
  - a benchmark harness around an existing fast CPU interpreter

## Phase 2: Core Experiments

- [ ] Implement a toy DASHI-to-FRACTRAN transition set for the `{-1, 0, +1}^3` cube or a smaller slice of it.
- [ ] Build a decoder that maps prime exponent vectors back to DASHI states.
- [ ] Compare fixed-prime dynamics against dynamics that explicitly reintroduce primes.
- [ ] Encode and test the 10-basin walk as data.
- [ ] Verify the claimed maximum monotone-chain length `4` by executable search or a stronger graph argument.
- [ ] Introduce a prime-exponent-vector engine for batched runs and compare it against the bigint/cycle-detecting baseline.
- [ ] Prototype LUT or divisibility-mask rule selection on CPU before any GPU port.

## Phase 3: Interpretation

- [ ] Measure which invariants survive translation: locality, parity, reversibility, contraction, chamber structure.
- [ ] Decide whether the `113` total degeneracy has structural support or should be discarded as coincidence.
- [ ] Write a short result note distinguishing observations from conjectures.

## Phase 4: GPU Reuse Path

- [ ] Confirm which `../dashiCORE` modules are stable enough to reference directly for Vulkan dispatch, shader compilation, and GEMV-style kernels.
- [ ] Design a thin FRACDASH adapter layer that imports or shells out to `../dashiCORE` GPU infrastructure without copying files.
- [ ] Keep GPU state resident across many FRACTRAN steps; avoid per-step host/device roundtrips.
- [ ] Add a deterministic CPU/GPU routing rule only after real baseline measurements exist.

## Open Decisions

- [ ] Which DASHI operations count as the canonical subset for reimplementation?
- [ ] Which signed encoding is simplest while remaining faithful?
- [ ] Should experiments start from a hand-written FRACTRAN kernel, a higher-level compiler, or a wrapper around an existing fast CPU evaluator?
- [ ] What measured hotspot, if any, would justify GPU work later?
- [ ] Should FRACDASH use direct imports from `../dashiCORE`, local symlinks, or a small compatibility layer for shared GPU assets?
