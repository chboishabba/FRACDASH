# Compactified Context

## Resolved Conversation

- Title: `Dashi and FRACTRAN Analysis`
- Online UUID: `69b35d79-1d90-839f-a358-5a26949aebd2`
- Canonical thread ID: `afc007c96393bf9b32c8029bc7d510bfc4947b63`
- Source used: `db`
- Resolution date: `2026-03-14`

Secondary resolved conversation:

- Title: `Modern FRACTRAN Implementations`
- Online UUID: `69b36d70-35c8-839c-9cdf-4f2ab0b072a1`
- Canonical thread ID: `0696f31b7716594d42a5fe27d2a2c1a789b6ecd2`
- Source used: `web` on refresh `2026-03-13` (`--check-web-newer` reported DB older than web)
- Resolution date: `2026-03-13`
- Note: web view succeeded, but persistence back into `~/chat_archive.sqlite` timed out during the download step, so the archive copy may still lag the live thread.

## Current Project Truth

FRACDASH is a fresh repo whose immediate purpose is to reimplement DASHI-style dynamics in FRACTRAN and evaluate the mathematical behavior experimentally.

The conversation sharpened these decisions:

1. The repo should aim for an executable bridge from DASHI to FRACTRAN, not a rhetorical comparison.
2. Balanced ternary matters. DASHI appears to rely on signed local states, so the FRACTRAN encoding must preserve sign information explicitly.
3. The 10-basin discussion is a concrete experiment target. The stated obstruction is that the basin stability order is not globally linearizable and has longest monotone descent length `4`.
4. Fixed prime sets likely impose reachability limits. A useful experiment is to compare fixed-prime walks against systems that can remove and reintroduce primes.
5. Moonshine and exceptional-lattice language should remain interpretive unless backed by proofs or compelling experimental structure.
6. For execution speed, the current working assumption should be CPU-first. The fetched implementation thread did not identify a standard GPU FRACTRAN engine and instead pointed toward algorithmic acceleration such as cycle detection and fast-forwarding.
7. The local repo now contains `fractran/`, which should be treated as the initial benchmark baseline and correctness reference for execution behavior.
8. FRACDASH should reuse `../dashiCORE` Vulkan and GEMV infrastructure by reference where possible instead of cloning or copying those files into this repo.

## High-Signal Notes From The Conversation

- DASHI's `3 x 3 x 3` balanced ternary cube was treated as the main local coordinate grammar.
- FRACTRAN was treated as motion on prime exponent lattices.
- The likely translation problem is not just "encode transitions", but "encode signed transitions without losing the geometry."
- Refreshed thread signal on `2026-03-14`: the basin-side story is now framed around two independent rank-4 diagnostics, namely longest monotone chain `4` and PCA effective dimension `4` on the `10 x 15` basin-prime matrix. For FRACDASH this strengthens one practical requirement: richer AGDAS/Monster bridge encodings should preserve nontrivial low-dimensional structure, not collapse into a nearly terminal toy compression.
- A suggested experiment path was:
  - build a basin graph
  - encode DASHI transitions as FRACTRAN rules
  - compare reachable regions under different prime-basis policies
  - test parity, chamber, and closure behavior
- The implementation-oriented thread suggests using prime exponent vectors as the execution substrate and treating GPU work as a later optimization step, not the initial architecture.
- The updated live thread added a concrete port sequence: baseline benchmark harness, exponent-vector representation, LUT/divisibility-mask lookup, vectorized CPU batches, then GPU batches.
- The updated live thread also emphasized throughput-oriented GPU design: DMA overlap, fused or persistent kernels, device-resident state, and per-state independence so out-of-order execution stays safe.
- Local seam finding: in [`fractran/src/Fractran.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Fractran.hs), both `fracOpt` and `cycles` already begin by compiling rationals into exponent maps. That compile step is the right insertion point for an alternate dense/vector execution backend.
- Benchmark-backed decision: after running the CPU matrix, parity held for `reg`, `frac-opt`, and `compiled`, and the current decision rule selected LUT/divisibility-mask CPU work as the next target.
- Benchmark contract decision: `cycle` is now treated as an `at-least` checkpoint engine because leap compression can overshoot target steps. Exact-step parity remains reserved for `reg`, `frac-opt`, and `compiled`.
- LUT experiment result: a binary-threshold `mask -> rule index` path was implemented for LUT-compatible programs. It preserves parity on `mult_smoke` and `primegame_*`, rejects `hamming` as incompatible, and does not beat `frac-opt` on the current primegame matrix. The active CPU baseline therefore remains `frac-opt`.
- Active optimization pivot: LUT is now parked. The compiled evaluator has gained `frac-opt`-style rule-order narrowing, the active benchmark matrix no longer includes `lut`, and the current matrix summary routes to `continue compiled-path tuning`.
- Latest compiled-path result: the benchmark harness now summarizes compiled runs directly from exponent vectors instead of decoding every state to `IntMap`. Parity still holds, and the current canonical matrix has `compiled` ahead of `frac-opt` on the sampled `primegame_*` scenarios.
- Routing expansion: the GPU matrix now includes `primegame_small`, `mult_smoke`, `paper_smoke`, and `hamming_smoke` across `batch_size = 4, 16, 32, 64, 128` and `steps = 4, 8, 16`, which generated `benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json` and a deterministic CPU/GPU rule that will also trigger upstreaming the reusable helper plumbing.
- Phase 2 launch: `scripts/toy_dashi_transitions.py` now encodes a toy signed 4-register (`3^4 = 81`) transition set, provides the FRACTRAN fractions that drive it, and decodes the signed state so the CORE experiments have a concrete artifact instead of a blank slate.

## Repo State

- Project memory was initialized on `2026-03-13` with:
  - [`spec.md`](/home/c/Documents/code/FRACDASH/spec.md)
  - [`architecture.md`](/home/c/Documents/code/FRACDASH/architecture.md)
  - [`plan.md`](/home/c/Documents/code/FRACDASH/plan.md)
  - [`status.md`](/home/c/Documents/code/FRACDASH/status.md)
  - [`devlog.md`](/home/c/Documents/code/FRACDASH/devlog.md)
  - [`AGENTS.md`](/home/c/Documents/code/FRACDASH/AGENTS.md)
  - [`ROADMAP.md`](/home/c/Documents/code/FRACDASH/ROADMAP.md)
  - [`TODO.md`](/home/c/Documents/code/FRACDASH/TODO.md)
  - [`CHANGELOG.md`](/home/c/Documents/code/FRACDASH/CHANGELOG.md)
- The repo now also contains a checked-out `fractran/` directory for the fast CPU baseline.
- Initial benchmark artifacts now live under [`benchmarks/results/`](/home/c/Documents/code/FRACDASH/benchmarks/results).
- The repo now also contains:
  - a stable CPU benchmark harness and canonical matrix artifacts
  - a reused-by-reference Vulkan/GPU path through `../dashiCORE`
  - a toy signed 4-register DASHI/FRACTRAN experiment harness
  - FRACDASH-side AGDAS bridge mappings and template execution paths
  - local formalism sketches and physics-facing bridge experiments (`physics1`, `physics2`)
  - a local `monster/` clone with `MonsterLean/` reference material; current intake is documented in [`MONSTERLEAN_INTAKE.md`](/home/c/Documents/code/FRACDASH/MONSTERLEAN_INTAKE.md) and treated as external, non-authoritative until FRACDASH reproduces claims as artifacts
  - a locked Monster 10-walk canonical artifact at `benchmarks/results/2026-03-15-monster10walk-canonical.json` backed by independent FRACDASH transition-data derivations (`physics8|physics9`) and strict lock checks
  - file-by-file Lean claim quarantine artifacts at `benchmarks/results/2026-03-15-monsterlean-claim-status.{json,md}`
- The full CPU comparison matrix and summary now live in:
  - corrected scenario set includes `mult_smoke` at exact logical-step target `2`
  - [`benchmarks/results/2026-03-13-cpu-matrix.jsonl`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix.jsonl)
  - [`benchmarks/results/2026-03-13-cpu-matrix-summary.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix-summary.json)
  - the active matrix currently compares `reg`, `frac-opt`, `cycle`, and `compiled`
  - the current summary resolves the next target to `continue compiled-path tuning`

## Guardrails

- Default unknown claims to conjecture.
- Prefer minimal explicit models.
- Keep experiments reproducible and logged.
