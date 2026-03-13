# TODO

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
  - [x] implement FRACDASH-side wave-1 template transitions in `scripts/agdas_bridge.py`
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
  - [ ] design a `physics5` hybrid that restores recurrence while keeping most of the `physics4` monotonicity gain
- [ ] Introduce a prime-exponent-vector engine for batched runs and compare it against the bigint/cycle-detecting baseline.
- [ ] Prototype LUT or divisibility-mask rule selection on CPU before any GPU port.

## Phase 3: Interpretation

- [ ] Measure which invariants survive translation: locality, parity, reversibility, contraction, chamber structure.
- [ ] Decide whether the `113` total degeneracy has structural support or should be discarded as coincidence.
- [ ] Write a short result note distinguishing observations from conjectures.

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
