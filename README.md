# FRACDASH

FRACDASH is a research repo for translating a minimal, explicit subset of DASHI-style dynamics into FRACTRAN and testing what survives that translation.

The current project stance is strict:

- treat DASHI to FRACTRAN as an executable modeling problem, not a metaphor
- preserve signed balanced-ternary behavior with an explicit encoding
- keep claims about basin structure, geometry, and degeneracy at the level the repo can actually support
- prefer CPU-first measurement and reproducible artifacts before any GPU work

The repo is now running two coordinated tracks:

- a **solver track**, where Python DASHI-style local dynamics are compared against named-equation reference implementations
- a **guarantee track**, where signed IR plus paired-prime FRACTRAN realization provides deterministic, auditable, proof-carrying execution claims

## Current Status

The repo already contains a checked-out FRACTRAN baseline in [`fractran/`](/home/c/Documents/code/FRACDASH/fractran) plus a benchmark harness and recorded CPU matrix artifacts under [`benchmarks/results/`](/home/c/Documents/code/FRACDASH/benchmarks/results).

What exists now:

- a trusted local CPU reference implementation in [`fractran/`](/home/c/Documents/code/FRACDASH/fractran)
- a deterministic benchmark CLI via `fractran-bench`
- a compiled exponent-vector execution path for comparison against the baseline
- benchmark summaries showing the current optimization focus is still CPU work, specifically compiled-path tuning
- an expanded GPU routing matrix that now includes `primegame_small`, `mult_smoke`, `paper_smoke`, and the new `hamming_smoke` headless program across the batch_size `16..64` / steps `4..16` band
- three closed local bridge slices:
  - [`formalism/Physics1StepDelta.agda`](/home/c/Documents/code/FRACDASH/formalism/Physics1StepDelta.agda)
  - [`formalism/Physics3StepDelta.agda`](/home/c/Documents/code/FRACDASH/formalism/Physics3StepDelta.agda)
  - [`formalism/Physics15StepDelta.agda`](/home/c/Documents/code/FRACDASH/formalism/Physics15StepDelta.agda)
- one thin master instantiation layer over those witnesses:
  - [`formalism/BridgeInstances.agda`](/home/c/Documents/code/FRACDASH/formalism/BridgeInstances.agda)
- a stable cross-slice bridge regime summary at [`benchmarks/results/2026-03-19-bridge-regime-summary.md`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-bridge-regime-summary.md)

What does not exist yet:

- the executable 10-basin obstruction experiments
- the canonical Phase 2 AGDAS bridge path from `all_dashi_agdas.txt` into executable FRACTRAN physics
- a fully numeric generic Agda theorem built directly into `RegimeValidBridge`; the current numeric layer is master-level and slice-dispatched in `formalism/BridgeInstances.agda`
- a confirmed runtime win over a standard named-equation reference solver

## Research Goals

The near-term questions are:

1. Can a small DASHI voxel transition system be compiled into FRACTRAN with a clear decode map?
2. Which invariants survive translation: locality, parity, reversibility, chamber structure, ultrametric behavior?
3. Do fixed prime sets impose the same kind of reachability obstruction discussed in the 10-basin analysis?
4. Can the basin graph be formalized well enough to verify a deterministic monotone-chain bound over the full `3^4` signed space?
5. Is the reported total degeneracy `113` structural or just coincidence?

## Repo Structure

- [`COMPACTIFIED_CONTEXT.md`](/home/c/Documents/code/FRACDASH/COMPACTIFIED_CONTEXT.md): durable project context and resolved conversation metadata
- [`AGENTS.md`](/home/c/Documents/code/FRACDASH/AGENTS.md): repo-specific working rules and deliverable standards
- [`spec.md`](/home/c/Documents/code/FRACDASH/spec.md): project objective, scope, and success criteria
- [`architecture.md`](/home/c/Documents/code/FRACDASH/architecture.md): current execution architecture and CPU-to-GPU boundary
- [`ROADMAP.md`](/home/c/Documents/code/FRACDASH/ROADMAP.md): phased implementation path
- [`TODO.md`](/home/c/Documents/code/FRACDASH/TODO.md): active task queue and open decisions
- [`CHANGELOG.md`](/home/c/Documents/code/FRACDASH/CHANGELOG.md): material repo changes
- [`MONSTER10WALK_CANONICAL.md`](/home/c/Documents/code/FRACDASH/MONSTER10WALK_CANONICAL.md): frozen canonical semantics and lock criteria for the Monster 10-walk lane
- [`MONSTERLEAN_INTAKE.md`](/home/c/Documents/code/FRACDASH/MONSTERLEAN_INTAKE.md): intake notes for the local `monster/MonsterLean` clone and proof-completeness caveats
- [`AGDAS_FORMALISM_INTAKE.md`](/home/c/Documents/code/FRACDASH/AGDAS_FORMALISM_INTAKE.md): authoritative intake note for the upstream `../dashi_agda` physics/closure formalism
- [`BRIDGE_CORRECTNESS.md`](/home/c/Documents/code/FRACDASH/BRIDGE_CORRECTNESS.md): formal target note for semantics-preserving compilation, quotient validity, decoder correctness, and robustness
- [`benchmarks/`](/home/c/Documents/code/FRACDASH/benchmarks): benchmark runners, summaries, and result artifacts
- [`fractran/`](/home/c/Documents/code/FRACDASH/fractran): local FRACTRAN baseline interpreter and benchmark binary

## Getting Started

### Prerequisites

- `ghc`
- standard shell tooling for the benchmark scripts

### Build The FRACTRAN Binaries

```sh
cd fractran
./build.sh
```

This produces:

- `./fractran`
- `./fractran-bench`

### Run A Quick Benchmark

```sh
cd fractran
./fractran-bench --scenario primegame_small --engine compiled --mode logical-steps --checkpoint-policy exact
```

Available benchmark engines currently include:

- `naive-fast`
- `reg`
- `frac-opt`
- `cycle`
- `compiled`
- `lut`

Notes:

- `cycle` is treated as an `at-least` checkpoint engine because fast-forwarding can overshoot a target logical step.
- The active benchmark matrix currently compares `reg`, `frac-opt`, `cycle`, and `compiled`.
- The `lut` path remains available for manual experiments but is not part of the active canonical matrix.

### Run The Canonical CPU Matrix

```sh
./benchmarks/run_cpu_matrix.sh
python3 benchmarks/summarize_cpu_matrix.py benchmarks/results/2026-03-13-cpu-matrix.jsonl
```

The benchmark artifacts currently tracked in-repo include:

- [`benchmarks/results/2026-03-13-cpu-matrix.jsonl`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix.jsonl)
- [`benchmarks/results/2026-03-13-cpu-matrix-summary.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix-summary.json)
- [`benchmarks/results/2026-03-13-toy-dashi-phase2.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-toy-dashi-phase2.json)

### Timing Regression Check

Use the timing regression gate to ensure new CPU work does not materially regress wall-clock:

```sh
scripts/run_cpu_regression.sh \
  benchmarks/results/2026-03-13-cpu-matrix.jsonl \
  benchmarks/results/2026-03-13-cpu-matrix-regression-<timestamp>.jsonl \
  0.50
```

Or invoke the checker directly:

```sh
python3 scripts/check_timing_regression.py \
  --baseline benchmarks/results/2026-03-13-cpu-matrix.jsonl \
  --current benchmarks/results/2026-03-13-cpu-matrix-regression-*.jsonl \
  --engine compiled \
  --engine frac-opt \
  --engine reg \
  --min-baseline-seconds 0.0001 \
  --tolerance 0.20
```

It compares median `cpu_seconds` across the tracked `(scenario, engine)` pairs and exits non-zero if slowdowns exceed tolerance.

### Physics Invariant Target Check

Use the physics target gate after AGDAS/physics template or invariant-analysis changes:

```sh
python3 scripts/check_physics_invariant_targets.py
```

For CI-style output:

```sh
python3 scripts/check_physics_invariant_targets.py --json
```

This checks the current V1 physics target suite over the latest locked `physics2..physics8` artifacts:

- exact source-charge conservation and source-parity preservation
- exact locality and forward-cone bounds
- exact cycle-distance nonincrease
- perturbation-stability thresholds
- geodesic-like and curvature-like geometry surrogates evaluated over cycle-reachable local neighborhoods
- defect-attraction thresholds
- the existing controlled-hybrid progression and `physics4` overconstraint signature

The canonical target table lives in `PHYSICS_INVARIANT_TARGETS.md`.

Each invariant artifact now also emits an `observable_surrogates` block with shell/interior occupancy, action-phase occupancy, re-entry flow, latch alignment, and source-defect coupling summaries for exploratory physics interpretation.

### AGDA Formalism Check

Use the upstream formalism intake check when `../dashi_agda` semantics or the local bridge assumptions change:

```sh
python3 scripts/check_dashi_agda_formalism.py
```

This writes:

- [`benchmarks/results/2026-03-15-dashi-agda-formalism-check.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-15-dashi-agda-formalism-check.json)
- [`benchmarks/results/2026-03-15-dashi-agda-formalism-check.md`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-15-dashi-agda-formalism-check.md)

The checker now covers the canonical closure/audit spine plus Stage C, minimal-credible adapter, MDL/Fejér, seam certificates, observable package, and known-limits QFT bridge modules, and records their local counterparts or gaps. The current result is `authoritative_formalism_detected=True`.

The next physics split is now explicit. The narrow branch stays on the existing 6-register carrier and tries to produce the first direct `boundary -> interior` re-entry (`physics21`) without breaking the exact V1 laws. In parallel, FRACDASH is adding a separate physics-local 8-register carrier (`carrier8_physics1`) that preserves the current `R1..R6` semantics and adds `R7` boundary-return memory plus `R8` transport/debt memory so later experiments can measure return type and deferred transport load directly instead of overloading the 6-register grammar.

That split is now implemented. `physics22` is the current best 6-register exploratory branch: it lifts deterministic edges to `364` and raises direct `boundary_to_interior` re-entry to `63` while keeping the exact V1 laws intact and keeping corrected `geodesic_like_flow.near_min_ratio` at `~0.92`. The 8-register branch now exists as `scripts/agdas_physics8_state.py` plus `scripts/agdas_physics8_experiments.py`, with artifacts at `benchmarks/results/2026-03-15-agdas-carrier8-physics1-phase2.json` and `benchmarks/results/2026-03-15-physics-invariants-carrier8_physics1.json`; its current job is to expose `boundary_return_profile` and `transport_debt_profile`, not to replace the 6-register lock.

### Bridge Correctness Framing

The main open math problem is now stated as bridge correctness, not just
interpretation.

FRACDASH needs to make explicit:

- the source DASHI / AGDA transition semantics,
- the signed exponent-vector IR used as the compiled semantics,
- the final FRACTRAN realization layer for that signed IR,
- the compile and decode maps,
- the refinement relation used for exact or weak simulation,
- the quotient assumptions behind the reduced carriers,
- the simulation or refinement obligation actually claimed,
- the Lyapunov / contraction / decoder-validity / robustness obligations.

See [`BRIDGE_CORRECTNESS.md`](/home/c/Documents/code/FRACDASH/BRIDGE_CORRECTNESS.md).

The first concrete oracle/proof loop now exists for `physics1`:

- Python delta extractor: [`scripts/export_physics1_deltas.py`](/home/c/Documents/code/FRACDASH/scripts/export_physics1_deltas.py)
- Agda signed-IR proof scaffold: [`formalism/Physics1StepDelta.agda`](/home/c/Documents/code/FRACDASH/formalism/Physics1StepDelta.agda)

In this workflow, Python exposes `source -> target -> delta` records, Agda
certifies the signed-IR step law, and FRACTRAN remains the later nonnegative
realization target rather than the immediate semantic surface.

The current stable bridge claim is narrower and stronger than the earlier conservative-only reading:

- `physics1` and `physics3` are `conservative_contracting`
- the currently formalized Batch C family (`physics15`, `physics19`, `physics20`, `physics21`, `physics22`) now shows a stable mixed regime rather than a one-off anomaly
- `physics15` is the first formal widened slice, and the same master-layer bridge contract now survives through `physics22` without introducing a new regime class or bound shape

So the current bridge target is:

> exact paired-prime macro realization with well-formedness preservation, strict contraction, and bounded transmutation, where conservative slices are the zero-transmutation special case

The current guarantee story should be read as:

- FRACTRAN is presently the best **auditable execution target**
- Python is presently the best **equation-probe and benchmark layer**
- if solver-style wins appear, they should be measured first on the Python side and only then used to motivate deeper FRACTRAN execution work for that family

### Named-Equation Probe

The first solver-oriented harness now lives at:

- [`scripts/named_equation_probe.py`](/home/c/Documents/code/FRACDASH/scripts/named_equation_probe.py)

It compares a transparent NumPy reference implementation against a DASHI-style
balanced-ternary local update path for:

- `wave` as the first stress-test probe
- `heat` as the planned fallback family if the current dissipative bridge makes the wave probe structurally mismatched

The intent is decision-quality, not hype:

- if the probe aligns numerically and economically, the solver track gets promoted
- if it only aligns qualitatively, it stays interpretation-facing
- if it mismatches structurally, the repo records that the stronger win is currently proof-carrying execution rather than speed

Current recorded outcome:

- `wave` probe: structural mismatch, fallback to `heat`
- `heat` second shot: qualitatively aligned after switching to a quantized explicit diffusion update, but still not competitive enough for a same-accuracy speed claim

See:

- [`benchmarks/results/2026-03-20-equation-probe-summary.md`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-20-equation-probe-summary.md)

Current practical conclusion:

- keep `heat` as the least-bad named-equation baseline if the solver lane is revisited
- treat the near-term project win as **proof-carrying / auditable execution**, not solver speed

### MonsterLean Intake Check

If you have the local `monster/` clone, run:

```sh
python3 scripts/check_monsterlean_intake.py
```

This writes a machine-readable intake summary and flags `axiom`/`sorry` usage in the shortlisted `MonsterLean` files so FRACDASH does not treat incomplete Lean claims as established results.

To extract a constants-only 10-walk candidate from `BottPeriodicity.lean`:

```sh
python3 scripts/extract_monsterlean_10walk.py
```

This emits a diagnostic JSON with parsed group constants and monotone-chain summaries under multiple stability definitions.

To freeze/lock the canonical 10-walk model and verify an independent FRACDASH transition-data derivation:

```sh
python3 scripts/freeze_monster10walk_canonical.py --strict-lock
```

Default lock mode requires transition-witness support from `physics8` and `physics9`. Use `--template-set <name>` only for one-off single-template checks.

To generate file-by-file Lean claim quarantine status:

```sh
python3 scripts/quarantine_monsterlean_claims.py
```

## Working Principles

- Docs before code. Update intent and experiment notes before changing implementations.
- No theorem inflation. Root-system, lattice, and moonshine language stays conjectural unless the repo contains an actual derivation.
- Signed behavior must be encoded explicitly. Do not hand-wave balanced ternary into unsigned FRACTRAN.
- Reproducibility is mandatory. Experiments need an entrypoint, summary, and saved artifacts.
- GPU work is downstream. The current baseline assumption is that algorithmic CPU wins matter more than naive early parallelism.

## External Reuse Boundary

FRACDASH should reuse GPU infrastructure from [`../dashiCORE`](/home/c/Documents/code/dashiCORE) by reference, adapter, or documented linkage when that becomes necessary. It should not copy those helper modules into this repo without a specific justification.

The first candidate files to reuse later are:

- [`../dashiCORE/gpu_common_methods.py`](/home/c/Documents/code/dashiCORE/gpu_common_methods.py)
- [`../dashiCORE/gpu_vulkan_dispatcher.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_dispatcher.py)
- [`../dashiCORE/gpu_vulkan_backend.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_backend.py)
- [`../dashiCORE/spv/`](/home/c/Documents/code/dashiCORE/spv)

The concrete FRACDASH bridge for that boundary now lives in:

- [`gpu/dashicore_bridge.py`](/home/c/Documents/code/FRACDASH/gpu/dashicore_bridge.py)
- [`scripts/check_dashicore_reuse.py`](/home/c/Documents/code/FRACDASH/scripts/check_dashicore_reuse.py)

Run the reuse smoke test with:

```sh
python3 scripts/check_dashicore_reuse.py
```

Override the default `../dashiCORE` location by setting `FRACDASH_DASHICORE_ROOT` if needed.

The current exact-step FRACTRAN GPU contract is documented in:

- [`GPU_CONTRACT.md`](/home/c/Documents/code/FRACDASH/GPU_CONTRACT.md)
- [`gpu/fractran_layout.py`](/home/c/Documents/code/FRACDASH/gpu/fractran_layout.py)
- [`scripts/check_fractran_gpu_layout.py`](/home/c/Documents/code/FRACDASH/scripts/check_fractran_gpu_layout.py)

Run the contract parity smoke with:

```sh
python3 scripts/check_fractran_gpu_layout.py
```

The first real Vulkan step smoke now lives in:

- [`gpu_shaders/fractran_step.comp`](/home/c/Documents/code/FRACDASH/gpu_shaders/fractran_step.comp)
- [`gpu/vulkan_fractran_step.py`](/home/c/Documents/code/FRACDASH/gpu/vulkan_fractran_step.py)
- [`scripts/check_fractran_vulkan_step.py`](/home/c/Documents/code/FRACDASH/scripts/check_fractran_vulkan_step.py)

Run it on the host with Vulkan access:

```sh
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.x86_64.json python3 scripts/check_fractran_vulkan_step.py --batch-size 4 --multi-steps 3
```

That entrypoint now validates single-state, batched one-step, and batched multi-step resident dispatch.

The first routing benchmark artifact now lives in:

- [`benchmarks/results/2026-03-13-gpu-benchmark-primegame-small.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-gpu-benchmark-primegame-small.json)
- [`benchmarks/results/2026-03-13-gpu-routing-matrix.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-gpu-routing-matrix.json)
- [`benchmarks/results/2026-03-13-gpu-routing-paper.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-gpu-routing-paper.json)
- [`benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json)

Current measured hint on this host:

- for `primegame_small`-like resident workloads at `32` exact steps, GPU already wins at batch sizes `32`, `128`, and `512`
- in the broader matrix, CPU remains the safe default for `batch_size <= 4`, GPU is already preferred for `batch_size >= 128`, and `primegame_small` reaches the GPU-preferred region at `batch_size = 32`, `steps >= 8`
- `paper_smoke` shows the same threshold behavior, with GPU preferred at `batch_size = 32`, `steps >= 8`

## Deterministic GPU Routing Rule

The new extended matrix (`benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json`) now samples the `16..64` batch / `4..16` step band for `primegame_small`, `mult_smoke`, `paper_smoke`, and the new `hamming_smoke` program. The measured shape lets us commit to a deterministic CPU/GPU rule on this host:

- Route to CPU when `batch_size <= 4` or when `batch_size = 16` and `steps < 16`.
- Route to GPU when `batch_size >= 32` and `steps >= 8`, or when the run has at least `16` exact steps regardless of batch size.
- The measurement still notes scenario-specific wins at `batch_size = 16`, `steps = 8` (particularly `hamming_smoke`) and at `batch_size = 32`, `steps = 4` for non-`primegame_small` workloads, but the deterministic rule above keeps the routing policy stable until we intentionally tune further.

This deterministic routing rule now feeds the GPU handoff plan: once the rule stabilizes, FRACDASH will upstream reusable dispatch helpers while keeping FRACTRAN semantics local.

## GPU Upstream Plan

The deterministic routing rule also serves as the gatekeeper for elevating reusable GPU helpers into `../dashiCORE`. See [`GPU_UPSTREAM.md`](/home/c/Documents/code/FRACDASH/GPU_UPSTREAM.md) for the checklist: it reiterates the rule, requires rerunning the extended matrix after any CPU change to keep `compiled` stable, and then stages the actual upstream work module by module.

## Phase 2: Toy DASHI transitions

A new experimental entrypoint, [`scripts/toy_dashi_transitions.py`](/home/c/Documents/code/FRACDASH/scripts/toy_dashi_transitions.py), defines a minimal FRACTRAN program for a signed 4-register ternary state space (`3^4 = 81` encodings). Each register state is encoded by one of three dedicated primes, and the script prints the FRACTRAN fractions plus a reference encoding and decoder. This gives us a concrete starting point for the Phase 2 CORE experiments (toy transitions, decoder, basin traversal) before we bring GPU scheduling into the mix. The script also explores the basin graph from a selected start value, reports monotone-chain statistics, compares fixed-prime and explicit-prime stepping across all states, and can emit a deterministic JSON artifact for reproducible basin and walk data.

[`scripts/agdas_bridge.py`](/home/c/Documents/code/FRACDASH/scripts/agdas_bridge.py) is now the first executable AGDAS bridge stage. The AGDA code in `../dashi_agda` should now be treated as the authoritative formal source for the canonical closure semantics, especially the closure/audit surfaces under `DASHI/Physics/Closure/`. FRACDASH still executes only a compressed subset of that formalism, maintained locally via `AGDAS_BRIDGE_MAPPING.md`, `AGDAS_FORMALISM_INTAKE.md`, and the carrier/template experiments. The parser for source-coupled transition markers still exists, but it remains optional rather than the main path.
The current primary bridge baseline is the template transition set exposed by `scripts/agdas_bridge.py --emit-templates --template-set wave1`, and the Phase 2 runner can exercise template sets with `scripts/run_agdas_template_phase2.sh`. The template runner defaults to disabling the chain bound (set `FRACDASH_TOY_CHAIN_BOUND_TEMPLATE=2` to re-enable it) and selects the template set via `FRACDASH_AGDAS_TEMPLATE_SET=wave1|wave2|all`.
The wave-2 `MonsterState` / `Monster.Step` probe now runs as `FRACDASH_AGDAS_TEMPLATE_SET=wave2`, but its artifact is mostly terminal under the current 4-register encoding, which is evidence that richer Monster-style dynamics likely need a larger encoded state model.
That larger carrier prototype now exists in `scripts/agdas_wave3_state.py`: it expands the bridge carrier from `3^4 = 81` to `3^6 = 729` states so mask summary, candidate/admissibility, and a 2-trit window can live on distinct registers before we attempt the next Monster-facing experiment pass.
The first wave-3 execution path now exists in `scripts/agdas_wave3_experiments.py` and writes `benchmarks/results/2026-03-14-agdas-template-wave3-phase2.json`. It confirms the larger carrier is wired, but it also shows the next missing piece clearly: the current Monster-facing wave-3 templates still model only a single step because no rule reintroduces pending choice/admissibility state after a transition.
For a more physics-facing path, FRACDASH now also has a local formal sketch in `formalism/PhysicsBridgeRefreshSketch.agda` and a recurrent `physics1` template set covering severity join, contraction-style relaxation, and boundary reset. Its artifact is `benchmarks/results/2026-03-14-agdas-physics1-phase2.json`, and it already shows nontrivial recurrent behavior on the existing 4-register carrier, making it the higher-signal bridge direction for now.
The widened `physics2` layer is implemented on a dedicated 6-register carrier with separate source severities, effective joined severity, region flag, signature latch, and action/energy phase. The carrier lives in `scripts/agdas_physics2_state.py`, the runner in `scripts/agdas_physics_experiments.py`, and the canonical artifact in `benchmarks/results/2026-03-14-agdas-physics2-phase2.json`. On the first pass it produces a substantially denser recurrent structure than `physics1`, with `657` edges over `729` states, longest chain `12`, and a canonical 4-step scan -> join -> contract -> rearm cycle.
The `physics3` refinement is also implemented on the same 6-register carrier. It adds an explicit latent cone shell between boundary and interior and reports action-phase monotonicity directly in the artifact. The canonical result is `benchmarks/results/2026-03-14-agdas-physics3-phase2.json`, which increases the graph to `900` edges over `729` states, raises longest chain to `15`, and makes the canonical loop explicitly 5-step by splitting `boundary -> shell -> interior rearm`. Its first monotonicity split is mixed rather than cleanly ordered: `234` decreases, `504` preserves, `162` increases.
That next pass is now implemented as `physics4` on the same 6-register carrier. Its artifact is `benchmarks/results/2026-03-14-agdas-physics4-phase2.json`. The result is informative but not yet the new lead: stricter shell/interior guards cut action-rank increases from `162` to `9`, but they also collapse the recurrent structure to `162` edges, longest chain `9`, and `0` cycles, so every fixed walk terminates. In other words, `physics4` improves order cleanliness by overconstraining the bridge.
The `physics5` hybrid is now implemented as the next recovery pass. It keeps the `physics4` scan guard and discharged-boundary shell entry, but splits shell-to-interior rearm into a cleared rearm plus latched left/right rearms. Its artifact is `benchmarks/results/2026-03-14-agdas-physics5-phase2.json`. The result lands in the intended middle band: recurrence returns (`100` cyclic starts), action-rank increases stay far below `physics3` (`27` vs `162`), and the canonical deterministic walk becomes cyclic again. But it is still much sparser than `physics3` overall (`180` edges, longest chain `10`), so `physics3` remains the best current lead while `physics5` becomes the best ordered hybrid so far.
The `physics6` refinement is now implemented on top of `physics5`. It adds a narrow shell-refresh branch for latched shell states before cleared rearm. Its artifact is `benchmarks/results/2026-03-14-agdas-physics6-phase2.json`. This moves the ordered-hybrid line forward again: the graph grows to `198` edges, longest chain rises to `12`, cyclic starts rise to `115`, and action-rank increases stay flat at `27`. The canonical deterministic walk becomes a 6-step cycle with an explicit shell-refresh step. `physics3` still leads on overall richness, but `physics6` is now the best controlled hybrid. The earlier apparent timeout tail is now resolved inside the artifact: the one state that timed out at `--max-steps 12` becomes a cycle under the built-in diagnostic cap of `32`, so there is currently no evidence of a broader runaway tail.
The `physics7` refinement is now implemented on top of `physics6`. It adds a very narrow shell-local latch-probe path from cleared shell states. Its artifact is `benchmarks/results/2026-03-14-agdas-physics7-phase2.json`. This gives another controlled gain: the graph rises to `204` edges, cyclic starts rise to `116`, and action-rank increases stay flat at `27`. Longest chain remains `12`, so the gain is mostly breadth via preserve edges, not deeper chains. `physics3` still leads on total richness, but `physics7` is now the best controlled hybrid and does not show the earlier timeout ambiguity at `--max-steps 12`.
The `physics8` refinement is now implemented on top of `physics7`. It inserts a staged shell-release micro-step (`probe -> stage -> release -> refresh -> rearm`) while preserving the same action-rank jump surface. Its artifact is `benchmarks/results/2026-03-14-agdas-physics8-phase2.json`. This is the first constrained pass that improves both breadth and depth from the hybrid baseline: `222` edges, longest chain `13`, `132` cyclic starts, `0` timeouts at `max-steps 12`, and still `27` action-rank increases. `physics3` still leads on total richness, but `physics8` is now the strongest constrained hybrid path.
The `physics9` refinement is now implemented on top of `physics8`. It adds shell-stage mid probes while preserving the same release/rearm chain. Its artifact is `benchmarks/results/2026-03-15-agdas-physics9-phase2.json`. This keeps the current constraints (`action-rank increases = 27`, `timeouts = 0`) and improves breadth to `228` edges, while keeping longest chain `13` and cyclic starts `132`.

[`scripts/toy_dashi_transitions.py`](/home/c/Documents/code/FRACDASH/scripts/toy_dashi_transitions.py) is now wired to consume AGDAS candidates either from optional parsed source markers via `--agdas-path` or from the primary FRACDASH-side bridge templates via `--agdas-templates --agdas-template-set wave1|wave2|all`. This keeps the verifier and basin tooling usable without editing upstream AGDA sources.

The canonical artifact generation is now pinned to a monotone-chain bound of `2` for the full `3^4` fixed-prime walk space.
That pinning is a regression gate for this artifact stream: the command exits non-zero if any fixed-prime trajectory in the captured space exceeds the bound. It is not a claim of a global theorem unless we later pass additional evidence.

```sh
scripts/run_toy_dashi_phase2.sh
```

That script writes `benchmarks/results/YYYY-MM-DD-toy-dashi-phase2.json` and enforces the fixed-prime chain check by default (`2`), unless `--disable-chain-bound` is supplied (or `FRACDASH_TOY_CHAIN_BOUND=disable` is set).

You can keep the check interactive by adding `--disable-chain-bound` or using custom values with `--max-chain-bound`.

## Rank-4 Reproduction Artifacts

FRACDASH now has a local, reproducible rank-4 analysis pipeline that derives a canonical basin dataset from existing artifacts and runs both diagnostics and discriminator tests as scripts.

Entry points:

- [`scripts/derive_rank4_dataset.py`](/home/c/Documents/code/FRACDASH/scripts/derive_rank4_dataset.py)
- [`scripts/run_rank4_diagnostics.py`](/home/c/Documents/code/FRACDASH/scripts/run_rank4_diagnostics.py)
- [`scripts/run_rank4_discriminators.py`](/home/c/Documents/code/FRACDASH/scripts/run_rank4_discriminators.py)
- [`scripts/run_rank4_canonical_gpu_parity.py`](/home/c/Documents/code/FRACDASH/scripts/run_rank4_canonical_gpu_parity.py)

Run:

```sh
python3 scripts/derive_rank4_dataset.py
python3 scripts/run_rank4_diagnostics.py
python3 scripts/run_rank4_discriminators.py
python3 scripts/run_rank4_canonical_gpu_parity.py
python3 scripts/ablate_prime_triplets.py --template-set physics8
```

Strict-mode checks:

```sh
python3 scripts/run_rank4_diagnostics.py --strict-stable
python3 scripts/run_rank4_diagnostics.py --strict-lock
```

Current artifacts:

- `benchmarks/results/2026-03-15-rank4-dataset.json`
- `benchmarks/results/rank4-dataset-latest.json`
- `benchmarks/results/2026-03-15-rank4-diagnostics.json`
- `benchmarks/results/2026-03-15-rank4-discriminators.json`
- `benchmarks/results/2026-03-15-rank4-discriminators.md`
- `benchmarks/results/2026-03-15-rank4-canonical-gpu-parity.json`
- `benchmarks/results/2026-03-15-prime-triplet-ablation.json`

Claim boundary remains strict:

- rank-4 identity-level claims are unproven
- diagnostics/discriminators are reported as experimental outputs, not proofs

## Read First

# Minimal DASHI state space

- `DASHI_STATE.md` describes the smallest signed ternary registers and the FRACTRAN encoding we target.

Before making substantial changes, read:

1. [`COMPACTIFIED_CONTEXT.md`](/home/c/Documents/code/FRACDASH/COMPACTIFIED_CONTEXT.md)
2. [`AGENTS.md`](/home/c/Documents/code/FRACDASH/AGENTS.md)
3. [`TODO.md`](/home/c/Documents/code/FRACDASH/TODO.md)
4. [`AGDAS_BRIDGE_NOTES.md`](/home/c/Documents/code/FRACDASH/AGDAS_BRIDGE_NOTES.md)
5. [`AGDAS_BRIDGE_MAPPING.md`](/home/c/Documents/code/FRACDASH/AGDAS_BRIDGE_MAPPING.md)
6. [`RANK4_OBSTRUCTION_NOTE.md`](/home/c/Documents/code/FRACDASH/RANK4_OBSTRUCTION_NOTE.md)

That is the current source of truth for project intent, guardrails, and active priorities.
