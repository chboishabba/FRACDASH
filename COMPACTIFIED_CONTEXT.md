# Compactified Context

## Resolved Conversation

- Title: `Dashi and FRACTRAN Analysis`
- Online UUID: `69b35d79-1d90-839f-a358-5a26949aebd2`
- Canonical thread ID: `afc007c96393bf9b32c8029bc7d510bfc4947b63`
- Source used: `db`
- Resolution date: `2026-03-13`

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
- A suggested experiment path was:
  - build a basin graph
  - encode DASHI transitions as FRACTRAN rules
  - compare reachable regions under different prime-basis policies
  - test parity, chamber, and closure behavior
- The implementation-oriented thread suggests using prime exponent vectors as the execution substrate and treating GPU work as a later optimization step, not the initial architecture.
- The updated live thread added a concrete port sequence: baseline benchmark harness, exponent-vector representation, LUT/divisibility-mask lookup, vectorized CPU batches, then GPU batches.
- The updated live thread also emphasized throughput-oriented GPU design: DMA overlap, fused or persistent kernels, device-resident state, and per-state independence so out-of-order execution stays safe.
- Local seam finding: in [`fractran/src/Fractran.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Fractran.hs), both `fracOpt` and `cycles` already begin by compiling rationals into exponent maps. That compile step is the right insertion point for an alternate dense/vector execution backend.

## Repo State

- No implementation exists yet.
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

## Guardrails

- Default unknown claims to conjecture.
- Prefer minimal explicit models.
- Keep experiments reproducible and logged.
