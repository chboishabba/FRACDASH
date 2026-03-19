# Bridge Correctness

This note records the current formal target for the FRACDASH bridge.

The point is not to re-prove the upstream AGDA formalism inside this repo. The
point is to state what FRACDASH must establish for its executable reduction to
count as a faithful semantic bridge rather than a suggestive toy.

## Problem Statement

FRACDASH is an executable Agda -> FRACTRAN bridge over signed register and
factor-exponent state vectors.

The core open question is therefore a compiler-correctness question for a
structured dynamical system:

- what is the source semantics,
- what is the target semantics,
- what quotient is being taken,
- what invariants and observables must survive,
- what parts are exact, weak, or only empirical.

Downstream physics language only becomes admissible after those obligations are
clear.

## Three-Layer Compiler View

The bridge should now be read as three layers, not two:

1. source semantics
   - canonical DASHI / AGDA state and step objects
2. signed executable IR
   - exponent-vector states in `Z^n`
   - finite signed delta updates
3. vanilla FRACTRAN realization
   - nonnegative prime-exponent encoding
   - fraction or macro realization of the signed IR

This matters because signed exponent-vector motion is the right semantic target
for the compiler, while plain FRACTRAN still needs an explicit realization layer
for negative coordinates.

## Formal Package

The minimal bridge package is:

- source state space `X`
- source transition semantics `T_X`
- source invariants / observables / geometry / Lyapunov package
  - `I_X`
  - `A`
  - `d_X`
  - `L_X`
- target executable state space `Y`
- target transition semantics `T_Y`
- target invariants / observables / geometry / Lyapunov package
  - `I_Y`
  - `D`
  - `d_Y`
  - `L_Y`
- bridge maps
  - compile / encode `C : X -> Y`
  - optional quotient `q : X -> Xbar`
  - decoder / readout `D : Y -> O`
  - source abstraction `A : X -> O`

This can be summarized as:

- `B = (X, T_X, I_X, d_X, L_X; Y, T_Y, I_Y, d_Y, L_Y; C, D, A)`

For the FRACDASH-specific arithmetic path, the effective target should be split:

- signed IR state space `Z`
- signed IR step semantics `T_Z`
- FRACTRAN realization map `Rz`

so the executable story is:

- `X --C--> Z --Rz--> Y`

## Required Obligations

### 1. Source and Target Semantics

FRACDASH needs both sides stated explicitly.

- source semantics: canonical DASHI / AGDA state and step objects
- target semantics: FRACDASH carrier/template or FRACTRAN/register execution

Without this split there is no precise preservation statement to prove or test.

### 2. Encode / Decode / Abstraction

The bridge must state:

- compile map `C : X -> Y`
- decode map `D : Y -> O`
- source abstraction `A : X -> O`

The minimal readout condition is:

- `D o C = A`

or an explicitly weaker approximate form.

### 3. Simulation / Refinement

The strongest step-preservation target is:

- `C(T_X(x)) = T_Y(C(x))`

If exact commutation is too strong, FRACDASH should state the weaker notion in
use:

- weak or k-step simulation,
- forward simulation,
- observable refinement,
- or simulation up to an equivalence relation.

The missing formal object should now be stated explicitly:

- refinement relation `R subseteq X x Y`

with the strongest initial choice:

- `R(x, y) := (C(x) = y)`

and weaker observational or quotient relations introduced only when exact
one-step equality is too strong for the chosen executable carrier.

### 4. Quotient Correctness

Because the local bridge uses compressed carriers and executable templates,
FRACDASH must state the quotient explicitly.

- quotient / reduction map `q : X -> Xbar`
- preserved invariants `I_j`

A quotient is semantically justified only if the invariants it forgets are not
required for the claim currently being made.

### 5. Arithmetic State Model

The target semantics should be formalized in prime-exponent space rather than
only as integers.

- prime basis `(p_1, ..., p_n)`
- executable state `y = (e_1, ..., e_n)`
- transition deltas `Delta in Z^n`

This exposes the actual target geometry:

- reachability,
- cone / semigroup structure,
- rank,
- basin decomposition,
- obstruction dimension.

For bridge proofs, this signed exponent-vector space should be treated as the
semantic IR even when the final execution path is vanilla FRACTRAN.

### 5a. FRACTRAN Realization Layer

Vanilla FRACTRAN still exposes only nonnegative prime exponents, so FRACDASH
must state how the signed IR is realized:

- paired-prime encoding,
- exclusivity constraints,
- or short FRACTRAN macros implementing signed deltas.

This yields a second proof obligation:

- signed delta semantics -> vanilla FRACTRAN realization.

### 6. Reachability and Obstruction Theory

Given transition generators `Gamma = {Delta_1, ..., Delta_m}`, FRACDASH should
analyze:

- reachable sets,
- linear span,
- positive cone,
- semigroup `N Gamma`,
- chamber / face structure.

This is the clean way to state rank-4 or chain-height claims without inflating
interpretation.

### 7. Lyapunov / MDL Preservation

If the source semantics uses an MDL-style Lyapunov order, the bridge should
state how that order survives compilation.

Minimal target:

- accepted source descent implies accepted target descent

Stronger target:

- target Lyapunov is a monotone image of source Lyapunov.

### 8. Ultrametric / Contraction Preservation

If contraction and fixed-point uniqueness are part of the source semantics,
FRACDASH should state whether the target preserves:

- an induced metric / pseudometric,
- contraction on the compiled image,
- or only a weaker nonexpansion property.

### 9. Decoder Correctness

Each reported observable should come with one of:

- exact semantic interpretation,
- conservative bound,
- stability across equivalent implementations.

Otherwise the observable remains a heuristic report, not a semantic witness.

### 10. Robustness / Artifact-Independence

FRACDASH should distinguish semantic invariants from implementation accidents by
introducing a perturbation class `P` of bridge-preserving changes, for example:

- prime/register renamings,
- equivalent fraction orderings,
- template refactorings,
- decoder refactorings.

An invariant is stronger when it is stable across that perturbation class.

## First Formal Objects To Add

The next formal objects should be kept minimal:

- `TransitionSystem`
- `Compiler`
- `Refinement`
- `ForwardSimulation`
- `StepDelta`
- `FractranRealization`

The first bridge theorem should be:

- each canonical source step compiles to an exact signed exponent delta

and only after that:

- each signed exponent delta is realized by a FRACTRAN fraction or short macro.

## First Concrete Instance

The first concrete `StepDelta` instance should stay small and executable.

Current choice:

- `physics1` template slice
- 4-register carrier (`R1..R4`)
- exact template-level step relation

## Physics1 Gold Slice

The `physics1` slice is now the first explicit `X -> Z -> Y` bridge instance.

### Source `X`

- source state: `Physics1State`
- source step: the seven `physics1` template constructors in [formalism/Physics1StepDelta.agda](/home/c/Documents/code/FRACDASH/formalism/Physics1StepDelta.agda)

### Signed IR `Z`

- IR state: `Exp4`
- signed delta: `Delta4`
- deterministic normalization:
  - register order `R1, R2, R3, R4`
  - repeated unit steps stay in-place in that order

### FRACTRAN target `Y`

The current concrete paired-prime encoding is:

- `R1`
  - `negative = 5`
  - `zero = 2`
  - `positive = 3`
- `R2`
  - `negative = 13`
  - `zero = 7`
  - `positive = 11`
- `R3`
  - `negative = 23`
  - `zero = 17`
  - `positive = 19`
- `R4`
  - `negative = 37`
  - `zero = 29`
  - `positive = 31`

The exclusivity invariant is:

- exactly one state-prime per register divides the encoded integer

Each normalized unit step is realized as one guarded FRACTRAN swap on the
active prime for that register. Example swaps:

- `R3 : negative -> zero` uses `17/23`
- `R3 : zero -> positive` uses `19/17`
- `R4 : positive -> zero` uses `29/31`
- `R4 : zero -> negative` uses `37/29`

So the concrete multi-step macros are now:

- `physics_contract_high`
  - delta `[0, 0, 2, 0]`
  - macro `17/23, 19/17`
- `physics_contract_mid`
  - delta `[0, 0, -1, -2]`
  - macro `17/19, 29/31, 37/29`
- `physics_boundary_reset`
  - delta `[0, 0, 0, 2]`
  - macro `29/37, 31/29`

### Current checked statement

The checked statement for this gold slice is:

- standard ordered FRACTRAN execution of the exported macro fractions matches the normalized signed-IR action on all seven `physics1` rules

Artifacts and checks:

- oracle export:
  - [scripts/export_physics1_deltas.py](/home/c/Documents/code/FRACDASH/scripts/export_physics1_deltas.py)
  - [benchmarks/results/2026-03-19-physics1-deltas.json](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-physics1-deltas.json)
- numeric soundness validation:
  - [scripts/check_physics1_macro_soundness.py](/home/c/Documents/code/FRACDASH/scripts/check_physics1_macro_soundness.py)
  - [benchmarks/results/2026-03-19-physics1-macro-soundness.json](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-physics1-macro-soundness.json)
- formal slice:
  - [formalism/AgdaToFracdashBridge.agda](/home/c/Documents/code/FRACDASH/formalism/AgdaToFracdashBridge.agda)
  - [formalism/Physics1StepDelta.agda](/home/c/Documents/code/FRACDASH/formalism/Physics1StepDelta.agda)

### Closed local bridge slices

- the first invariant-preservation pass is now present on `physics1`:
  - conserved quantity: `R1/R2` source signature and its paired-prime product
  - monotone quantity: residual signed-IR `L1` distance to target decreases by exactly `1` per macro step
  - artifact: [benchmarks/results/2026-03-19-physics1-bridge-invariants.json](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-physics1-bridge-invariants.json)
- the same first invariant-preservation pass is now present on `physics3`:
  - conserved quantity: `R1/R2` source signature and its paired-prime product
  - monotone quantity: residual signed-IR `L1` distance to target decreases by exactly `1` per macro step
  - artifact: [benchmarks/results/2026-03-19-physics3-bridge-invariants.json](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-physics3-bridge-invariants.json)
- the shared bridge-core validator artifacts now also expose:
  - terminal basin counts keyed by final decoded target state
  - macro-length, executed-fraction-count, and contraction-step histograms
  - artifacts:
    - [benchmarks/results/2026-03-19-physics1-bridge-core-validators.json](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-physics1-bridge-core-validators.json)
    - [benchmarks/results/2026-03-19-physics3-bridge-core-validators.json](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-physics3-bridge-core-validators.json)
- local formal slices:
  - [formalism/Physics1StepDelta.agda](/home/c/Documents/code/FRACDASH/formalism/Physics1StepDelta.agda)
  - [formalism/Physics3StepDelta.agda](/home/c/Documents/code/FRACDASH/formalism/Physics3StepDelta.agda)
- shared Python execution/validation layer:
  - [scripts/bridge_macro_common.py](/home/c/Documents/code/FRACDASH/scripts/bridge_macro_common.py)
  - [scripts/bridge_macro_soundness.py](/home/c/Documents/code/FRACDASH/scripts/bridge_macro_soundness.py)
  - [scripts/bridge_core_validators.py](/home/c/Documents/code/FRACDASH/scripts/bridge_core_validators.py)
- reusable Agda execution layer:
  - [formalism/GenericMacroBridge.agda](/home/c/Documents/code/FRACDASH/formalism/GenericMacroBridge.agda)
  - now includes a generic `RegimeValidBridge` surface for strict contraction, bounded transmutation, classification, and well-formedness preservation
- thin master instantiation layer:
  - [formalism/BridgeInstances.agda](/home/c/Documents/code/FRACDASH/formalism/BridgeInstances.agda)
  - keeps `physics1`, `physics3`, and `physics15` separate as concrete witnesses while stating the current bridge family once
  - now exposes exact per-slice `slice-regime-valid` witnesses over source-step constructors, not only the weaker shared bridge interface
- shared regime-valid bridge layer is no longer placeholder-strength:
  - `RegimeValidBridge` now carries explicit contraction/transmutation witness types keyed by `RegimeClass`
  - the master instances now classify `physics1` and `physics3` as conservative and `physics15` as mixed conservative/transmuting at the shared theorem surface
- first numeric master-level theorem layer:
  - [formalism/BridgeInstances.agda](/home/c/Documents/code/FRACDASH/formalism/BridgeInstances.agda) now also proves slice-dispatched target-relative residual decrease for `physics1`, `physics3`, and `physics15`
  - [`formalism/Physics20StepDelta.agda`](/home/c/Documents/code/FRACDASH/formalism/Physics20StepDelta.agda) now proves the second widened Batch C slice and wires `S20` into the master numeric theorem layer so `slice-step-distance-decreases` and `slice-transmutation-bounded` stay uniform across physics15/19/20.
  - [`formalism/Physics21StepDelta.agda`](/home/c/Documents/code/FRACDASH/formalism/Physics21StepDelta.agda) now proves a third widened Batch C slice without changing the theorem surface, which is the strongest current signal that the family-level residual/transmutation contract is stable rather than slice-local.
  - [`formalism/Physics22StepDelta.agda`](/home/c/Documents/code/FRACDASH/formalism/Physics22StepDelta.agda) now closes the current widened Batch C family end-to-end, so the master-layer numeric contract in [`formalism/BridgeInstances.agda`](/home/c/Documents/code/FRACDASH/formalism/BridgeInstances.agda) should now be treated as the stable bridge claim for the currently formalized family rather than a provisional slice bundle.
  - the same master file now proves bounded `R1/R2` transmutation for the current slices, with `physics15` using its local conservative/transmuting regime split
  - this numeric layer is intentionally master-level rather than built directly into `RegimeValidBridge`
- structural prime-state well-formedness is now substantive rather than placeholder:
  - `WellFormedY` is no longer `⊤` on the closed slices
  - both `physics1` and `physics3` now require per-coordinate paired-prime family membership at the `Y` layer
  - realized unit execution preserves that invariant through the shared generic macro bridge
- next hard gap: keep this generic macro contract stable while widening into the next bridge slice batch and adding cost/basin summaries without weakening the current soundness surface
- next hard gap: keep this generic macro contract stable while widening into the next bridge slice batch without weakening the current soundness surface

These were the right first targets because they isolate:

- source step constructors already present in the bridge templates,
- a compact compile map,
- a direct delta proof,
- and no immediate need for weakened simulation.

Practical workflow for these first instances:

- **Python proposes deltas**: acts as an oracle expressing concrete source -> target transitions and signed exponent deltas.
- **Agda certifies deltas**: certifies the corresponding `StepDelta` statement to ensure the IR exactly matches the symbolic DASHI semantics.
- **FRACTRAN realizes normalized unit steps**: realizes those deltas as deterministic unit steps via a nonnegative encoding (paired-prime registers or short macros).

Current delta extractors:

- [`scripts/export_physics1_deltas.py`](/home/c/Documents/code/FRACDASH/scripts/export_physics1_deltas.py)
- [`scripts/export_physics3_deltas.py`](/home/c/Documents/code/FRACDASH/scripts/export_physics3_deltas.py)
- [`scripts/export_physics15_deltas.py`](/home/c/Documents/code/FRACDASH/scripts/export_physics15_deltas.py)

Current widened bridge result:

- `physics15_boundary_crossfeed_neutral` is now treated as intended semantic widening rather than a bridge regression
- `R1/R2` source-signature conservation is regime-specific rather than universal
- the same classifier pipeline now covers `physics19`, `physics20`, `physics21`, and `physics22`
- the canonical cross-slice regime table now lives at:
  - [`benchmarks/results/2026-03-19-bridge-regime-summary.md`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-bridge-regime-summary.md)
  - [`benchmarks/results/2026-03-19-bridge-regime-summary.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-19-bridge-regime-summary.json)
- Batch C now stabilizes a widened but still regime-valid class:
  - `physics15`: `28 conservative_contracting + 1 transmuting_contracting`
  - `physics19`: `30 conservative_contracting + 3 transmuting_contracting`
  - `physics20`: `31 conservative_contracting + 3 transmuting_contracting`
  - `physics21`: `32 conservative_contracting + 3 transmuting_contracting`
  - `physics22`: `33 conservative_contracting + 3 transmuting_contracting`

## Bridge Status Table

| Template Family | Exact `StepDelta` | Normalization | FRACTRAN Realization | Invariants | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `physics1` | Exact slice-local `StepDelta`, instantiated through `GenericMacroBridge` | Deterministic unit-step normalization | Paired-prime macro realization with checked soundness | `conservative_contracting`: conservation + exact L1 descent + strictly contracting validator trace | `implemented` |
| `physics3` | Exact slice-local `StepDelta`, instantiated through `GenericMacroBridge` | Deterministic unit-step normalization | Paired-prime macro realization with checked soundness | `conservative_contracting`: conservation + exact L1 descent + strictly contracting validator trace | `implemented` |
| `physics15` | Exact slice-local `StepDelta`, instantiated through the same generic macro layer as `physics1`/`physics3` | Deterministic unit-step normalization | Paired-prime macro realization with checked soundness | `28 conservative_contracting + 1 transmuting_contracting`; exact decode-back, strict contraction witness, exclusivity, and bounded-transmutation regime witness now live in the Agda slice; `R1/R2` source-signature conservation is not universal on this slice | `implemented` |
| `physics19..physics22` | Exact slice-local `StepDelta`, instantiated through the same master theorem layer as `physics15` | Deterministic unit-step normalization | Paired-prime macro realization with checked soundness | Stable widened Batch C regime: each slice remains `regime-valid`, strictly contracting, and contains the same three transmuting rules (`physics15_boundary_crossfeed_neutral`, `physics17_boundary_handoff_left_to_mid`, `physics19_tail_handoff_n0_to_nn`) | `implemented` |
| `wave1` | Python proposing | TBD | TBD | `Base369` | `assumed` |
| `monster` | Python proposing | TBD | TBD | `Monster.Step` | `conjectural` |

## Current Status Split

### Already present in repo form

- explicit executable carrier/template families
- signed encodings and decoders for the toy bridge
- prime-exponent execution substrate
- invariant and observable artifact generation
- contraction / closure intake against upstream `../dashi_agda`

### Not yet formalized tightly enough

- a single explicit source/target semantics package for the AGDAS -> FRACDASH bridge
- named simulation/refinement obligations
- a quotient-validity section stating exactly what each reduced carrier forgets
- decoder-validity claims for the physics-facing observables
- robustness tests separating semantic invariants from artifact-sensitive metrics
- keep the current split for now:
  - `formalism/GenericMacroBridge.agda` remains the structural/class-indexed bridge contract
  - `formalism/BridgeInstances.agda` remains the stronger numeric theorem layer for the currently closed slice family
- the numeric-layer decision is now fixed:
  - keep the stronger residual/transmutation theorems at the master layer in `formalism/BridgeInstances.agda`
  - keep only the stable class-indexed witness/bound extractors in `formalism/GenericMacroBridge.agda`

## Priority Order

The formalization order should be:

1. source/target semantics
2. simulation/refinement obligations
3. invariant preservation
4. Lyapunov / MDL preservation
5. ultrametric / contraction preservation
6. decoder correctness
7. robustness / artifact-independence
8. only then downstream physics / Weyl / moonshine interpretation

## Interpretation Boundary

The following remain downstream hypotheses, not bridge-correctness premises:

- root-system or Weyl-chamber identification
- geodesic / curvature interpretation of surrogate metrics
- GR / QFT identification of the measured laws
- moonshine / exceptional-lattice interpretation
- quantum-shell narratives

Those only become admissible claims after the bridge obligations above are
either proved or validated strongly enough to rule out implementation artifacts.
