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

Supplemental resolved conversations on `2026-03-19`:

- Title: `Quantum Computer in DASHI`
- Online UUID: `69b8ae74-0628-839f-ba14-0693459f6f83`
- Canonical thread ID: `65bba843349f781d7867537ceb18a65ced25d4c1`
- Source used: `db`
- Relevance: `adjacent, not canonical`
- Main topics:
  - treats DASHI as a contraction layer beneath a reversible or quantum-style shell
  - sketches hybrid DASHI/quantum execution and wave-lift style semantics
  - remains interpretive for FRACDASH until executable invariants or compiled transition data are attached

- Title: `DASHI vs QFT`
- Online UUID: `69bab071-8ddc-83a0-812d-5e14ed2485ca`
- Canonical thread ID: `7803b5747fd32ec453c8142f21a960e31c84e90d`
- Source used: `db`
- Relevance: `adjacent, not canonical`
- Main topics:
  - frames RG flow and fixed-point language around DASHI contraction semantics
  - proposes a `FixedPointCFT`-style module shape for perturbations near contractive fixed points
  - is useful only as downstream interpretation scaffolding unless FRACDASH reproduces the structure as artifacts

- Title: `ZKP/DASHI Formalism Sharing`
- Online UUID: `69bab0b8-062c-839c-85b9-9d4dcdae7ee3`
- Canonical thread ID: `1001eb5fde69406569a83e3def6552b1c2c649b1`
- Source used: `db`
- Relevance: `adjacent, not canonical`
- Main topics:
  - analyzes an external content-addressed semantic decomposition stack against DASHI-style formalism
  - suggests possible ingest/provenance or multi-scale text analogies
  - does not currently define FRACDASH experiment obligations

Out-of-scope fetched conversations on `2026-03-19`:

- `Stego with DCT and ECC` (`69b8b6d2-95e0-839f-a0e4-ad557778be5c`, canonical `73007c8071901b60eba4ec53a4ea6223bb048d43`)
- `Branch · Stego with DCT and ECC` (`69b8c284-8b04-83a1-a85e-8853bc796f88`, canonical `124bb1a5e69f7846fac3d61bb3107c1b5ec26f43`)
- `Embedding design for MDL` (`69baab50-cda4-839c-b7db-70b2d1b59f31`, canonical `11d8b420a1c60cc95c94b5006476e4ed9efc6de1`)
- `Gödel-style Factorisation` (`69babc4d-0ce4-83a0-899a-674b5c2b4ce5`, canonical `ef37214f136b8494fca5f1143b99f4c9fea6c800`)

These were fetched into the canonical archive for traceability but should not drive FRACDASH implementation or claims unless they later connect to a documented executable experiment.

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
9. The missing formal math is now framed as bridge-correctness math for a structured dynamical-system compiler: source/target transition semantics, compile/decode maps, quotient obligations, invariant preservation, Lyapunov preservation, contraction preservation, decoder validity, and artifact-independence.

## High-Signal Notes From The Conversation

- DASHI's `3 x 3 x 3` balanced ternary cube was treated as the main local coordinate grammar.
- FRACTRAN was treated as motion on prime exponent lattices.
- The likely translation problem is not just "encode transitions", but "encode signed transitions without losing the geometry."
- Refreshed thread signal on `2026-03-14`: the basin-side story is now framed around two independent rank-4 diagnostics, namely longest monotone chain `4` and PCA effective dimension `4` on the `10 x 15` basin-prime matrix. For FRACDASH this strengthens one practical requirement: richer AGDAS/Monster bridge encodings should preserve nontrivial low-dimensional structure, not collapse into a nearly terminal toy compression.
- Upstream-formalism decision on `2026-03-15`: `../dashi_agda` should now be treated as the authoritative formal source for the canonical physics-closure semantics, especially the closure/audit surfaces under `DASHI/Physics/Closure/`. FRACDASH still executes only a compressed subset of that formalism, so local docs and artifacts must distinguish upstream formal closure from local executable coverage explicitly.
- Supplemental-thread triage on `2026-03-19`: quantum/QFT/CFT-style threads are now recorded as adjacent interpretation sources only. They can inform wording around fixed points, perturbations, or shell semantics, but they do not alter the FRACDASH canonical task list until translated into executable invariants, decode maps, or benchmarked transition systems.
- Bridge-correctness reframing on `2026-03-19`: the core open question is no longer best stated as "does the physics interpretation look right?" but as "does the executable quotient/compilation preserve the intended semantics?" The required obligations are now explicitly split into source/target semantics, simulation/refinement, quotient invariants, prime-exponent transition geometry, Lyapunov/MDL monotonicity, ultrametric/contraction preservation, decoder correctness, and robustness under implementation-preserving perturbations.
- Batch C bridge result on `2026-03-19`: the widened bridge pipeline now covers `physics15`, `physics19`, `physics20`, `physics21`, and `physics22` with saved delta, macro-soundness, invariant, and validator artifacts plus a canonical cross-slice regime summary at `benchmarks/results/2026-03-19-bridge-regime-summary.{json,md}`. The stable current class is no longer "strictly contracting and conservative" but "strictly contracting and regime-valid, with conservative and bounded-transmuting subregimes." The stable widened transmuting rules are currently `physics15_boundary_crossfeed_neutral`, `physics17_boundary_handoff_left_to_mid`, and `physics19_tail_handoff_n0_to_nn`. `formalism/Physics15StepDelta.agda`, `formalism/Physics19StepDelta.agda`, `formalism/Physics20StepDelta.agda`, `formalism/Physics21StepDelta.agda`, and `formalism/Physics22StepDelta.agda` now close the current widened Agda family, while `formalism/BridgeInstances.agda` carries the shared numeric theorem layer across `physics1`, `physics3`, `physics15`, `physics19`, `physics20`, `physics21`, and `physics22` unchanged. The next hard formal decision is no longer Batch C closure; it is whether to freeze that master-layer numeric contract as the stable bridge-family theorem or lift parts of it upward into `formalism/GenericMacroBridge.agda`.
- Solver-track decision on `2026-03-20`: the repo now explicitly runs a dual track. Python remains the equation-probe/benchmark layer; FRACTRAN remains the deterministic/auditable bridge-execution layer. The first named-equation stress test lives in `scripts/named_equation_probe.py` with saved artifacts at `benchmarks/results/2026-03-20-equation-probe-{wave,heat}.json`. Result: `wave` is structurally mismatched and falls back to `heat`; one extra `heat` shot using a quantized explicit diffusion step improves the fit to `qualitative_only` (`normalized_l2_error ~ 0.456`, `correlation ~ 0.917`) but still does not justify a same-accuracy speed claim. The near-term project win should therefore be treated as proof-carrying / auditable execution first, with `heat` retained only as the least-bad named-equation comparison family if the solver lane is revisited.
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
