# FRACDASH Roadmap

## Goal

Use the checked-out [`fractran/`](/home/c/Documents/code/FRACDASH/fractran) project as the fast CPU baseline, then port the useful execution core toward a batched exponent-vector engine that can eventually reuse Vulkan and GEMV-oriented infrastructure from [`../dashiCORE`](/home/c/Documents/code/dashiCORE).

This roadmap assumes:

- CPU correctness and benchmark baselines come first.
- GPU work must justify itself with measured hotspots.
- Existing GPU plumbing in `../dashiCORE` should be referenced, adapted, or linked rather than duplicated.

## External Dependencies

### Local baseline

- [`fractran/README.md`](/home/c/Documents/code/FRACDASH/fractran/README.md)
- Likely implementation seam:
  - [`fractran/src/Fractran.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Fractran.hs)

### Existing GPU/Vulkan infrastructure

- [`../dashiCORE/gpu_common_methods.py`](/home/c/Documents/code/dashiCORE/gpu_common_methods.py)
- [`../dashiCORE/gpu_vulkan_dispatcher.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_dispatcher.py)
- [`../dashiCORE/gpu_vulkan_backend.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_backend.py)
- [`../dashiCORE/gpu_vulkan_gemv.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_gemv.py)
- [`../dashiCORE/CORE_TRANSITION.md`](/home/c/Documents/code/dashiCORE/CORE_TRANSITION.md)
- [`../dashiCORE/README.md`](/home/c/Documents/code/dashiCORE/README.md)

## Phases

### Phase 0: Benchmark Harness

Deliverable:
- reproducible CPU baseline against the checked-out `fractran/` interpreter

Tasks:
- identify how to run fixed FRACTRAN programs non-interactively
- create a benchmark set with fixed programs and fixed step budgets
- record throughput, step counts, and output parity

Artifacts:
- `benchmarks/`
- `results/`
- benchmark notes in repo docs

### Phase 1: Exponent-Vector CPU Engine

Deliverable:
- a second execution path that uses prime exponent vectors instead of raw big integers

Tasks:
- define prime basis extraction
- define rule representation as denominator exponents plus delta vector
- implement integer-state decode/encode parity tests against the baseline
- support batched state updates on CPU

Current status:
- A first compilation seam now exists in [`fractran/src/Compiled.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Compiled.hs).
- This prototype matches baseline outputs on sampled workloads but is not yet faster than `frac-opt`, so optimization should focus on data layout and rule compatibility checks rather than adding more abstraction.

### Phase 2: LUT and Batch Optimization

Deliverable:
- CPU batch engine using divisibility masks or LUT-driven rule selection

Tasks:
- prototype `mask -> rule` and possibly `mask -> delta` lookup
- benchmark scan-based versus LUT-based selection
- determine how many primes can stay in-cache before the table shape becomes unattractive

### Phase 3: FRACDASH Adapter To dashiCORE GPU Infrastructure

Deliverable:
- thin adapter layer that reuses `../dashiCORE` Vulkan helpers without vendoring them

Tasks:
- decide whether the cleanest mechanism is import-by-path, symlinked helper paths, or a small compatibility package
- keep shader compilation and dispatch logic outside the FRACTRAN semantics layer
- prove the adapter can launch at least one trivial batch update path

Constraint:
- do not copy `dashiCORE` helper modules into this repo unless the dependency boundary becomes unworkable

### Phase 4: Streaming GPU Engine

Deliverable:
- GPU batch execution for many independent states

Tasks:
- upload many states once
- run many FRACTRAN steps per transfer
- keep rule tables and metadata resident on device
- use fused or persistent kernels where the implementation cost is justified

Design rules:
- each worker owns one state trajectory
- shared GPU data stays read-only
- out-of-order execution is acceptable because work items are independent

### Phase 5: Heterogeneous Scheduling

Deliverable:
- deterministic CPU/GPU routing based on measured cost, not guesswork

Tasks:
- calibrate CPU and GPU throughput on this machine
- model transfer and launch overhead explicitly
- route small or single-orbit jobs to CPU
- route large batched orbit exploration to GPU

## Current Recommendation

Do not start by writing new Vulkan code in FRACDASH.

Start with:
1. benchmark harness around [`fractran/`](/home/c/Documents/code/FRACDASH/fractran)
2. exponent-vector prototype on CPU
3. only then a thin reuse layer over [`../dashiCORE`](/home/c/Documents/code/dashiCORE)

## Bridge Roadmap

This section supersedes any vague "physics bridge next" wording with a more
concrete compiler-correctness sequence.

### Truth / Execution Split

Lock this separation across the bridge work:

1. Agda / DASHI owns semantic truth.
2. Python owns extraction, fixture generation, and fast falsification.
3. Signed exponent IR `Z` is the semantic compilation target.
4. FRACTRAN `Y` is the performance-oriented execution target.

Practical rule:
- do not grow Python into the main runtime
- only extend Python when it reduces uncertainty for `X -> Z` or `Z -> Y`
- keep the main engineering effort focused on reusable FRACTRAN realization

### Hard Tasks

These are the tasks most likely to change the actual truth-status of the bridge.

1. Finish the `X -> Z -> Y` semantics package explicitly.
   - define source DASHI / AGDA semantics `X, T_X`
   - define signed exponent IR `Z, T_Z`
   - define FRACTRAN realization semantics `Y, T_Y`
   - define compile / decode / abstraction maps and the exact refinement relation
2. Replace the remaining FRACTRAN-realization placeholder with a real soundness statement.
   - keep soundness at macro execution, not single-fraction execution
   - prove or tightly validate `execute(realize(normalize Δ)) = applyDelta(Δ)` on the chosen slice
3. Lock the unit-step normalization contract.
   - prove deterministic `Delta -> List UnitDelta`
   - prove normalization preserves the signed IR action exactly
   - keep ordering explicit so FRACTRAN scheduling is not under-specified
4. Turn the current symbolic paired-prime macro layer into a concrete numeric FRACTRAN program.
   - choose the exact paired-prime encoding and exclusivity invariants
   - define per-unit guarded FRACTRAN macros
   - test them against the saved `physics1` delta artifact
5. Extend exact `StepDelta` beyond `physics1`.
   - recommended order: `physics3`, `physics15`, `physics19`, `physics20`, `physics21`, `physics22`
   - only then move to `carrier8_physics1` and `carrier8_physics2`
6. Add end-to-end invariant preservation checks across the bridge.
   - at least one conserved quantity
   - at least one monotone / Lyapunov-style quantity
   - robustness under implementation-preserving perturbations
7. Only after the above, promote rank/cone/chamber interpretation work.
   - rank-4 and chamber language should be tied to the transition-generator set `Gamma`
   - GR/QFT / Weyl / moonshine language remains downstream until bridge preservation is stable

## Solver Probe Roadmap

This lane is explicitly separate from the bridge theorem lane.

### Goal

Test whether DASHI-style local dynamics can act as a useful solver path for a
named equation family before making any stronger runtime claims.

### Phase A: Decision-Quality Probe

Deliverable:
- one benchmark harness comparing a transparent NumPy reference against a DASHI-style local update path

Tasks:
- start with a `wave` / Schrödinger-like probe as a stress test
- classify the result as solver-shaped, qualitative-only, or structurally mismatched
- if the mismatch is structural, pivot the main benchmark family to `heat` / diffusion

Current implementation seam:
- [`scripts/named_equation_probe.py`](/home/c/Documents/code/FRACDASH/scripts/named_equation_probe.py)

### Phase B: Same-Equation Comparison

Deliverable:
- matched-grid, matched-timestep, matched-observable runtime and error comparison against the reference solver

Tasks:
- freeze grid, timestep, boundary condition, and initial-condition policy
- compare runtime, memory, normalized error, and correlation
- only escalate to optimized solver baselines after the transparent baseline is understood

### Phase C: Bridge Reuse Decision

Deliverable:
- explicit repo decision on whether the real win is speed, qualitative physics structure, or proof-carrying execution

Tasks:
- if the solver track looks viable, connect it back to the bridge family
- if it does not, document that FRACTRAN remains primarily the guarantee/audit path

### Easier Tasks

These are support tasks that improve reproducibility, visibility, and workflow
without changing the core bridge obligations.

1. Save all oracle outputs as reproducible artifacts under `benchmarks/results/`.
   - `physics1` delta export is the current template
   - future template families should use the same artifact shape
2. Add normalization metadata to the Python export artifacts.
   - `delta_norm_1`
   - `delta_norm_inf`
   - normalized unit-step list
   - macro length
3. Add a small bridge-status table to repo docs.
   - columns: template family, exact `StepDelta`, normalization, FRACTRAN realization, invariants, status
   - statuses: `inherited`, `assumed`, `observed`, `conjectural`
4. Add one runner that regenerates the `physics1` oracle artifact deterministically.
   - keep timestamped outputs for experiments
   - keep one canonical named artifact for regression comparison
5. Add a small consistency check between Python delta exports and the Agda-side rule inventory.
   - rule names align
   - coordinate order aligns
   - signed deltas align
6. Add bridge-oriented summaries to the current markdown docs.
   - explain that Python proposes deltas
   - Agda certifies deltas
   - FRACTRAN realizes normalized unit steps
7. Keep the changelog and TODOs synchronized whenever a bridge slice moves from symbolic to numeric realization.

### Recommended Order

1. Harden the generic macro FRACTRAN layer so `normalize`, paired-prime encoding, exclusivity, and `realizeUnit` stop being slice-local across the now-closed `physics1` and `physics3` slices.
2. Only then widen to the later `physics*` families and 8-register branches in batches.

### Hard-Track Priority Order

This is the main-line sequence for the hard bridge work. It assumes easier
artifact-hygiene work can proceed in parallel without blocking the next proof
or realization step.

#### Do Now

1. Use `physics1` and `physics3` together as the threshold for promoting slice-specific macro work into bridge-generic machinery.
2. Keep Python frozen at oracle/export/regression scope while the generic macro layer lands.
3. Treat later families as blocked until the shared macro contract is no longer slice-local.

#### Do Next

1. Finalize the reusable macro FRACTRAN layer:
   - `UnitDelta`
   - `normalize`
   - paired-prime encoding
   - exclusivity invariant
   - `realizeUnit`
   - generic macro execution soundness
2. Add the first bridge-core validator package on top of emitted FRACTRAN traces:
   - conservation
   - L1 / Lyapunov descent
   - reversibility / irreversibility classification
3. Benchmark macro length and macro execution cost on the FRACTRAN side.
4. Promote the macro layer from slice-specific to bridge-generic only after `physics1` and `physics3` share it cleanly.

#### Do Later

1. Roll out the remaining families in batches:
   - Batch A: `physics4..physics8`
   - Batch B: `physics9..physics13`
   - Batch C: `physics15`, `physics19`, `physics20`, `physics21`, `physics22`
   - Batch D: `carrier8_physics1`, `carrier8_physics2`
2. Shift emphasis from Python fixtures to FRACTRAN execution benchmarking once at least one post-`physics3` batch is closed.
3. Keep rank/cone/chamber interpretation and any GR/QFT/Weyl/moonshine language downstream until bridge preservation is stable across those batches.

### Delegated Support Track

These tasks are valuable, but they should not block the hard-track sequence
above if another agent is available to carry them.

1. Save normalization and macro metadata into the canonical `physics1` oracle artifact.
2. Maintain deterministic reproduction runners and artifact naming.
3. Add bridge-status tables and consistency checks between Python exports and Agda rule inventories.
4. Keep changelog, TODOs, and status snapshots synchronized as hard milestones land.
