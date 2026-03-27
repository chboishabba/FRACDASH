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

The first bounded perf-compression slice is now real on `2026-03-27`:
`scripts/compact_zkperf_trace.py` compresses the checked-in normalized zkperf
waveform JSON by storing only the raw sample facts needed to reconstruct the
derived trace contract. The first DA51 sample artifact shrank from `5875` bytes
to `1695` bytes with exact round-trip reconstruction, so the current codec
target is no longer hypothetical. This remains a narrow zkperf-side witness
codec, not yet the general perf-output or Zelph shard packaging solution.

Follow-up clarification from the main thread on `2026-03-27`:
- source: current working turn
- online UUID: not provided in-turn
- main decision:
  - the current codec should be understood as
    `projection(model) + residual = exact reconstruction`
  - the win comes from dropping duplicated derived structure (`matrix`,
    expanded annotations) and keeping only the canonical generating fields
  - this is the first concrete MDL-style witness in FRACDASH, not merely a
    generic compressor
  - the next compression increment should be motif compression on top of the
    current compact rows, not a replacement of the projection layer
- first motif target:
  - repeated `(event_idx, pid, tid, cpu_mode)` structure with timestamp/period
    parameters
- followthrough:
  - the first motif layer is now implemented in
    `scripts/compact_zkperf_trace.py`
  - it lifts repeated `(event_idx, pid, tid, cpu_mode)` tuples into a motif
    table and keeps row-local `step`, `timestamp`, `period`, and `cid`
    parameters
  - on the checked-in DA51 sample it finds `2` motifs and shrinks the compact
    artifact from `1695` bytes to `1539` bytes with exact round-trip back to
    the compact rows
  - current read: the motif layer is valid, but the measured gain on this tiny
    sample is modest, so richer traces are now the more important next test
- next Dashi-facing test:
  add `dashi_class` / `dashi_family` labels to the compact rows and rerun
  motif extraction over semantic labels rather than only surface tuples
- followthrough:
  - the compact rows now carry heuristic `dashi_class` / `dashi_family` labels
  - `scripts/compact_zkperf_trace.py` now supports side-by-side comparison of:
    - raw -> compact
    - raw -> compact -> surface motif
    - raw -> compact -> semantic motif
  - on the checked-in DA51 sample:
    - compact with semantic labels: `2139` bytes
    - surface motif: `1687` bytes with `2` motifs
    - semantic motif: `1658` bytes with `1` motif
  - current read:
    semantic labeling helps, but only slightly on this tiny trace; projection
    remains the dominant gain source and richer traces are still needed before
    claiming strong Dashi-native compression
  - next concrete target:
    `../dashi_agda/da51_shards/summary.json`, because it is directly emitted by
    `perf_da51.py` and carries real Agda module names suitable for better
    `dashi_class` / `dashi_family` labeling than the tiny zkperf sample
  - followthrough:
    `scripts/compact_dashi_perfhistory.py` now normalizes that summary and
    compares compact, surface-motif, and semantic-motif layers over the
    Dashi-linked rows
  - current result on the upstream summary:
    - raw summary: `9758` bytes
    - normalized analysis form: `23722` bytes
    - compact normalized form: `14245` bytes
    - surface motif: `16586` bytes
    - semantic motif: `14156` bytes
  - current read:
    the summary path is a useful Dashi-linked semantic calibration target, but
    not yet the correct compression target if the goal is to beat the raw
    upstream artifact on storage
  - next concrete target:
    the aggregate CBOR shard set under `../dashi_agda/da51_shards/*.cbor`
  - reason:
    the shard set still carries repeated CBOR keys, repeated FRACTRAN program
    skeletons, and real module-family semantics that `summary.json` already
    collapsed away
  - measured regularity before implementation:
    - `41` shard files totaling `15658` bytes
    - `24` shards share the exact FRACTRAN fractions
      `('47/2', '59/3', '71/5')`
    - `40` shards share `steps = 3`, `trace` length `4`, and
      `earns_moonshine = True`
    - `MonsterVectors.cbor` is the only current negative case, with no full
      FRACTRAN trace and `earns_moonshine = False`
  - constraint:
    the next codec should compare aggregate shard bytes against a compact
    aggregate representation with exact shard-byte reconstruction, not against
    another analysis-only JSON expansion
  - followthrough:
    `scripts/compact_dashi_da51_shards.py` now compacts the entire
    `../dashi_agda/da51_shards/*.cbor` corpus into a single aggregate CBOR
    payload and decodes exactly back to the original per-file shard bytes
  - first aggregate result:
    - raw shard set: `15658` bytes across `41` files
    - compact surface aggregate: `9275` bytes with `33` repeated program motifs
    - semantic aggregate: `9971` bytes with `22` semantic motifs
  - current read:
    aggregate CBOR factorization is the first Dashi-linked storage win that
    beats the raw upstream artifact itself; the remaining open decision is
    whether the next gain should come from deeper trace payloads beneath the
    current shard level or whether this aggregate boundary is already the right
    publish/export unit

Upstream `../dashi_agda` now has PR `#1` merged on `2026-03-27`, which adds a
small witness/perf surface on top of the existing closure spine:
`Kernel/KAlgebra.agda`, `Monster/MUltrametric.agda`, `Moonshine.agda`,
`MoonshineEarn.agda`, `JFixedPoint.agda`, `PerfHistory.agda`, and
`perf_da51.py`. FRACDASH should treat those as auxiliary witness artifacts, not
as a replacement for the canonical closure/audit intake.

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
- Batch C bridge result on `2026-03-19`: the widened bridge pipeline now covers `physics15`, `physics19`, `physics20`, `physics21`, and `physics22` with saved delta, macro-soundness, invariant, and validator artifacts plus a canonical cross-slice regime summary at `benchmarks/results/2026-03-19-bridge-regime-summary.{json,md}`. The stable current class is no longer "strictly contracting and conservative" but "strictly contracting and regime-valid, with conservative and bounded-transmuting subregimes." The stable widened transmuting rules are currently `physics15_boundary_crossfeed_neutral`, `physics17_boundary_handoff_left_to_mid`, and `physics19_tail_handoff_n0_to_nn`. `formalism/Physics15StepDelta.agda`, `formalism/Physics19StepDelta.agda`, `formalism/Physics20StepDelta.agda`, `formalism/Physics21StepDelta.agda`, and `formalism/Physics22StepDelta.agda` now close the current widened Agda family, while `formalism/BridgeInstances.agda` carries the shared numeric theorem layer across `physics1`, `physics3`, `physics15`, `physics19`, `physics20`, `physics21`, and `physics22` unchanged. That split is now frozen for this phase: `formalism/GenericMacroBridge.agda` stays structural/class-indexed, and `formalism/BridgeInstances.agda` stays the stronger numeric theorem layer for the closed family.
- Widened-family follow-up on `2026-03-23`: the repo now has a second comparison layer at `benchmarks/results/2026-03-23-widened-invariant-family-summary.{json,md}` backed by refreshed invariant artifacts for `physics15`, `physics19`, `physics20`, `physics21`, and `physics22`. The current read is that all five slices remain in the mixed-transmuting widened regime, but recurrent-core size, terminal-state reduction, and direct boundary-to-interior re-entry improve monotonically through `physics22`, while `distance_to_cycle` remains the best invariant candidate and the geometry surrogates remain strong. Operationally, this makes `execution_status` a stable reporting contract and leaves `physics22` as the leading 6-register exploratory branch unless a later branch beats it on the same summary axes.
- Physics22 baseline lock-in on `2026-03-23`: the repo now also has a local `physics21 -> physics22` delta artifact at `benchmarks/results/2026-03-23-physics22-baseline-delta.{json,md}` plus a short claim-boundary note at `PHYSICS22_RESULT_NOTE.md`. The key read is that `physics22` improves the deterministic recurrent core sharply (`395 -> 476` edges, `419 -> 365` terminal states, `9 -> 63` direct boundary-to-interior re-entries) with only one extra transition rule, while the fixed-walk cycle/terminal split and current geometry-surrogate values stay flat. This now defines the comparison target for the next 6-register refinement: future branches should beat the `physics22` recurrent-core gain profile without giving back the current invariant/geometry surface.
- Cross-carrier follow-up on `2026-03-23`: the repo now also has a cross-carrier comparison artifact at `benchmarks/results/2026-03-23-cross-carrier-baseline-summary.{json,md}` plus a short 6-register successor target note at `PHYSICS23_TARGET_NOTE.md`. Current read: `physics22` remains the clearer active 6-register baseline because it combines strong direct re-entry with a disciplined recurrent core and a stable best-candidate signal; `carrier8_physics1` remains mainly an observable branch; `carrier8_physics2` should now be treated as a serious parallel 8-register experiment track because it already beats the 6-register baseline on at least one geometry surrogate, even though its branch-local behavior is still too different for it to replace `physics22` as the main baseline.
- First successor trials on `2026-03-23`: the repo now also contains `physics23` and `carrier8_physics3` artifacts. Current read: `physics23` is the first genuine 6-register successor candidate because it improves the deterministic recurrent core (`476 -> 503` edges) while keeping the fixed-walk split, best-candidate signal, and geometry surrogates flat, but it does not yet improve terminal mass or direct re-entry beyond `physics22`. By contrast, `carrier8_physics3` does not materially move the current `carrier8_physics2` baseline on the shared cross-carrier axes, so the serious 8-register track should still be read through `carrier8_physics2` for now.
- Decision lock on `2026-03-23`: `physics23` should remain a successor candidate rather than replace `physics22` as the active 6-register baseline, because it only improves the recurrent-core side of the `physics21 -> physics22` gain shape. In parallel, `carrier8_physics2` is now explicitly the active 8-register experiment track, and the next branch target is an earlier boundary-return re-entry hook rather than another late-added memory rule. See `CARRIER8_PHYSICS4_TARGET_NOTE.md`.
- Carrier8 follow-up on `2026-03-23`: the first `carrier8_physics4` trial moved the boundary-return re-entry hook earlier, ahead of the broad return-memory damping rules, and still left the shared cross-carrier summary flat (`6561` deterministic edges, `0` terminals, `10` longest chain, `boundary_to_interior = 0`, same best candidate and geometry surrogates). Current read: the 8-register blocker is deeper than rule placement alone, so `carrier8_physics2` remains the active parallel baseline and `carrier8_physics4` should be treated as a useful negative result.
- Source-aligned cone enforcement status on `2026-03-24`: Δ-cone machinery is stable; physics6 remains the 8-register baseline. Multiple cones tested (generic drop, simple source basis, ERDFA-ish basis, hand-crafted contrasts) all rejected 0 edges. Aggressive sign-flip cones reject many edges but destroy boundary/curvature metrics. Next action requires a real attractor/eigen basis from source data; placeholder bases are exhausted.
- Visualization split on `2026-03-25`: FRACDASH now has two distinct local trace surfaces. The existing deterministic-walk waveform remains the time/register view, while `scripts/render_trace_waveform.py --mode branch-density` adds a graph-facing spectrogram for the canonical rank-4 surface. That branch-density lane is now explicitly projection-indexed: `raw-state` is the detailed/debug view, `basin` is the preferred canonical explanation surface for the 10-basin / chain-height-4 story, and `bucket` is an exploratory Gödel/fraction-band view for the "jumping between fractions" question. Current implementation scope remains deliberately 6-register/rank-4 only. Repo-status boundary recorded at the same time: branch-density work is confined to the renderer/docs plus `rank4-dataset-latest.branch-density-view.branch-density.{html,png}`; unrelated `.gitmodules`, dirty `fractran`, and untracked `scripts/render_trace_graph.py` state was not part of that change.
- Carrier8 curvature-recovery follow-up on `2026-03-23`: `carrier8_physics6` keeps `boundary_to_interior = 6`, restores curvature to `~0.9728`, geodesic-like near-min dips slightly to `~0.9894`, and best-candidate strict decrease returns to `~0.515`. Current read: promote `carrier8_physics6` as the provisional 8-register baseline and aim the next refinement at recovering the small geodesic/strict-decrease loss without giving back boundary recovery or curvature.
- Solver-track decision on `2026-03-20`: the repo now explicitly runs a dual track. Python remains the equation-probe/benchmark layer; FRACTRAN remains the deterministic/auditable bridge-execution layer. The first named-equation stress test lives in `scripts/named_equation_probe.py` with saved artifacts at `benchmarks/results/2026-03-20-equation-probe-{wave,heat}.json`. Result: `wave` is structurally mismatched and falls back to `heat`; one extra `heat` shot using a quantized explicit diffusion step improves the fit to `qualitative_only` (`normalized_l2_error ~ 0.456`, `correlation ~ 0.917`) but still does not justify a same-accuracy speed claim. The near-term project win should therefore be treated as proof-carrying / auditable execution first, with `heat` retained only as the least-bad named-equation comparison family if the solver lane is revisited.
- Upstream-wave boundary check on `2026-03-20`: after re-reading `../dashi_agda`, FRACDASH should stop treating the wave/heat split as a mere heuristic. Upstream Agda contains a real wave/unitary semantic lane (`DASHI.Unifier.WaveLift`, `DASHI.Quantum.Stone`, `DASHI.Physics.WaveLiftEvenSubalgebra`, and the broader `DASHI.Physics.Closure.*Wave*` surface), while the local FRACDASH executable subset remains empirically dissipative and contraction-heavy. The actionable split is therefore: keep `wave` alive as a formal bridge target and use `heat` only as the least-bad current runtime comparison family. The reproducible local artifact for that read is `benchmarks/results/2026-03-20-dashi-agda-wave-surface.{json,md}` from `scripts/check_dashi_agda_wave_surface.py`.
- Performance-profiling pivot on `2026-03-20`: before any further CPU or GPU tuning, FRACDASH should now run an explicit profiling milestone. Current local evidence says there is no obvious large remaining exact-step CPU win beyond the `compiled`/`frac-opt` race on the sampled matrix, while the GPU path already has a real batch win in parts of the measured region. The next correct question is therefore not "optimize what?" but "where does current time actually go on CPU and GPU?" The profiling deliverables should separate exact-step CPU timing from `cycle` checkpoint timing and should separate GPU cold-start cost from warm-resident execution cost.
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
