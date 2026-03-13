# FRACDASH Agent Guide

## Mission

FRACDASH exists to reimplement core DASHI dynamics in FRACTRAN form and run the experiments implied by the conversation `Dashi and FRACTRAN Analysis`.

This repo is for executable models and experiment records, not for informal speculation. Treat structural analogies to `B4`, `D4`, `F4`, `E8`, moonshine, and Weyl-chamber geometry as hypotheses to test, not as established results.

## Canonical Conversation Context

- Title: `Dashi and FRACTRAN Analysis`
- Online UUID: `69b35d79-1d90-839f-a358-5a26949aebd2`
- Canonical thread ID: `afc007c96393bf9b32c8029bc7d510bfc4947b63`
- Source: `db`
- Main topics:
  - Recast DASHI transitions as FRACTRAN exponent-vector walks.
  - Preserve balanced ternary behavior using an explicit signed encoding.
  - Investigate the 10-basin obstruction: the stability order is not globally linearizable and appears to have maximum monotone-chain length `4`.
  - Test whether fixed prime sets restrict reachability and when primes must be removed and re-added.
  - Separate theorem-grade results from suggestive geometry.

Related implementation context:

- Title: `Modern FRACTRAN Implementations`
- Online UUID: `69b36d70-35c8-839c-9cdf-4f2ab0b072a1`
- Canonical thread ID: `0696f31b7716594d42a5fe27d2a2c1a789b6ecd2`
- Source: `web` for the latest refresh on `2026-03-13` (`db` copy is stale)
- Main topics:
  - There is no established widely used GPU FRACTRAN interpreter.
  - Fast CPU execution should be the baseline.
  - Cycle detection and fast-forwarding likely matter more than naive parallelism.
  - Prime exponent vectors are the natural execution representation.
  - A practical port path is: CPU benchmark harness -> exponent-vector engine -> LUT rule selection -> vectorized batch engine -> GPU batch engine.
  - GPU wins depend on batching, persistent/fused kernels, DMA overlap, and keeping state resident on device.
  - Out-of-order execution is acceptable if each worker owns its own state and shared data remains read-only.

Read [`COMPACTIFIED_CONTEXT.md`](/home/c/Documents/code/FRACDASH/COMPACTIFIED_CONTEXT.md) before making substantial changes.

## Working Rules

1. Docs before code. Update intent and experiment notes before changing implementations.
2. No theorem inflation. Do not claim DASHI derives the Monster, umbral moonshine, or exceptional lattices unless the repo contains an actual derivation.
3. Keep every experiment reproducible. Record inputs, encoding choices, outputs, and failure cases.
4. Prefer small executable kernels over grand frameworks. A verified toy model beats a broad untested abstraction.
5. Preserve the distinction between:
   - DASHI local state grammar
   - FRACTRAN encoding mechanics
   - mathematical interpretation of observed behavior

## Current Technical Direction

### 1. DASHI state model

Assume the starting object is a DASHI-style balanced ternary local state alphabet, especially the `3 x 3 x 3` voxel-style cube indexed by `{-1, 0, +1}^3`.

Agents should treat signed local coordinates, parity constraints, chamber transitions, and ultrametric clustering as the core structural features worth preserving.

### 2. FRACTRAN target model

Represent FRACTRAN states as prime exponent vectors. Because vanilla FRACTRAN only exposes nonnegative exponents, any signed DASHI quantity must be compiled through an explicit encoding such as:

- paired primes for positive/negative occupancy
- constrained register families with exclusivity invariants
- another documented reversible signed representation

Do not hand-wave signed behavior. State the encoding and its invariants explicitly.

Performance stance:

- Do not assume GPU acceleration is the first win.
- Start with a strong CPU implementation and benchmark it.
- Prefer algorithmic acceleration such as cycle detection, memoization, compiled transition tables, or fast-forwarding before GPU work.
- Only pursue GPU kernels after a clear hotspot is measured.

Dependency stance:

- `fractran/` is the checked-out local CPU baseline and reference interpreter.
- Reuse GPU infrastructure from `../dashiCORE` by reference, adapter, or documented local symlink targets; do not copy those files into FRACDASH unless a hard fork is justified.
- Treat `../dashiCORE/gpu_common_methods.py`, `../dashiCORE/gpu_vulkan_dispatcher.py`, `../dashiCORE/gpu_vulkan_backend.py`, and SPIR-V assets under `../dashiCORE/spv/` as the first places to look before writing new Vulkan plumbing.

### 3. Required experiment track

Agents should prioritize work that supports these questions:

1. Can a DASHI voxel transition rule be compiled into a FRACTRAN program with a clear decode map?
2. What invariants survive the translation: locality, reversibility, parity, ultrametric contraction, chamber structure?
3. Does a fixed prime basis force the same kind of reachability obstruction described in the 10-basin discussion?
4. Can the basin graph be formalized well enough to prove the maximum monotone-chain length is `4`?
5. Is the total degeneracy `113` structural or just numerology? Default to "coincidence until proven otherwise."

## Deliverable Standards

- Every new model must state:
  - source DASHI operation being modeled
  - FRACTRAN encoding
  - state decoder
  - invariants
  - known limitations
- Every experiment must leave behind:
  - a script or notebook entrypoint
  - a short result summary
  - raw output or saved artifact paths
- Every mathematical claim must be marked as one of:
  - `implemented`
  - `observed experimentally`
  - `conjectured`

## Immediate Priorities

1. Define the minimal DASHI state and transition vocabulary to encode.
2. Choose and document a signed-register encoding for FRACTRAN.
3. Select a CPU-first FRACTRAN execution strategy and benchmark baseline options.
4. Implement a small interpreter or compiler path for the chosen encoding.
5. Reproduce the 10-basin obstruction as executable data.
6. Build experiments that compare fixed-prime and prime-reintroduction dynamics.

## Repo Conventions

- Keep durable context in [`COMPACTIFIED_CONTEXT.md`](/home/c/Documents/code/FRACDASH/COMPACTIFIED_CONTEXT.md).
- Track near-term tasks in [`TODO.md`](/home/c/Documents/code/FRACDASH/TODO.md).
- Record material workflow changes in [`CHANGELOG.md`](/home/c/Documents/code/FRACDASH/CHANGELOG.md).
- Keep the implementation roadmap in [`ROADMAP.md`](/home/c/Documents/code/FRACDASH/ROADMAP.md).
- If code is added later, keep runnable experiments under a clearly named top-level directory such as `experiments/` or `src/`.

## What To Avoid

- Do not collapse balanced ternary into naive binary without documenting the loss.
- Do not treat metaphorical links to root systems as proofs.
- Do not mix multiple encodings in one experiment unless the comparison is the point.
- Do not leave undocumented one-off scripts behind.
