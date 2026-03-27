# AGDAS Formalism Intake

This file records the current FRACDASH stance toward the upstream formalism in
`../dashi_agda`.

## Current Decision

FRACDASH should treat `../dashi_agda` as the authoritative formal source for
the canonical physics-closure semantics that the local bridge is trying to
approximate.

That does **not** mean FRACDASH already executes the full formal closure.

Current practical status:

- upstream AGDA contains a concrete closure/audit surface for the canonical
  physics path,
- upstream minimal-credible closure now also carries explicit execution
  admissibility and family-classification witnesses through the core/full
  closure witness records,
- upstream PR `#1` additionally adds a small witness/perf surface
  (`Kernel/KAlgebra.agda`, `Monster/MUltrametric.agda`, `Moonshine.agda`,
  `MoonshineEarn.agda`, `JFixedPoint.agda`, `PerfHistory.agda`, and
  `perf_da51.py`); FRACDASH should treat these as auxiliary witness artifacts
  rather than canonical closure modules,
- FRACDASH currently executes a deliberately compressed subset of that surface
  through local carrier/template experiments,
- local claims about "physics closure" must stay at the level of implemented
  extraction and measured artifacts, not at the level of upstream theorem names.

## High-Signal Upstream Modules

These files are the current intake spine for FRACDASH.

1. `../dashi_agda/UFTC_Lattice.agda`
   - local severity lattice
   - join / monotonicity seam
   - cone-interior monotonicity comments that already match the current
     `physics*` bridge vocabulary
2. `../dashi_agda/Contraction.agda`
   - contraction and fixed-point contracts
3. `../dashi_agda/MaassRestoration.agda`
   - stability/repair seam and testable contraction-facing statements
4. `../dashi_agda/MonsterState.agda`
   - canonical state record / mask / admissibility seam
5. `../dashi_agda/Monster/Step.agda`
   - canonical step/update seam
6. `../dashi_agda/MonsterSpec.agda`
   - spec step plus encode/decode contract
7. `../dashi_agda/Ontology/Hecke/Scan.agda`
   - scan/compatibility/signature seam
8. `../dashi_agda/DASHI/Physics/LiftToFullState.agda`
   - lift seam from compressed objects into full state
9. `../dashi_agda/DASHI/Physics/Closure/CanonicalPhysicsPathPostulateAudit.agda`
   - explicit no-essential-postulates audit surface for the canonical physics
     path
10. `../dashi_agda/DASHI/Physics/Closure/PhysicsClosureValidationSummary.agda`
    - repo-facing validation summary for the current Stage C closure stack
11. `../dashi_agda/DASHI/Physics/Closure/PhysicsClosureCoreWitness.agda`
    - core witness bundle for the authoritative closure surface
    - now includes explicit execution-admissibility and family-classification
      witness fields in addition to dynamics and observable agreement
12. `../dashi_agda/DASHI/Physics/Closure/PhysicsClosureFullInstance.agda`
    - canonical instance wiring for the current minimal/full closure
    - now populates the execution-admissibility and family-classification
      witnesses from current-trace/current-family modules
13. `../dashi_agda/DASHI/Physics/Closure/ExecutionAdmissibilityWitness.agda`
    - shared witness vocabulary for execution admissibility and family
      classification
14. `../dashi_agda/DASHI/Physics/Closure/ExecutionAdmissibilityCurrentTraceWitness.agda`
    - current-trace admissibility witness chosen by the authoritative minimal
      closure
15. `../dashi_agda/DASHI/Physics/Closure/ExecutionAdmissibilityCurrentFamilyWitness.agda`
    - current-family classification witness chosen by the authoritative minimal
      closure

## FRACDASH Interpretation Rule

Use the upstream modules in two layers:

- **formal source-of-truth layer**
  - module names
  - canonical closure chain
  - no-essential-postulates audit status
  - validation/rigidity status surfaces
- **local executable bridge layer**
  - explicit carriers
  - state decoders/encoders
  - FRACTRAN-facing transition templates
  - measured invariants and observables

FRACDASH should not silently collapse the first layer into the second.

## Current Audit Scope (2026-03-15)

Inspected upstream formal surfaces and docs:

- Docs: `Docs/MinimalCrediblePhysicsClosure.md`, `Docs/PhysicsClosureImplementationChecklist.md`, `Docs/CanonicalPhysicsPathPostulateAudit.md`
- Closure / Stage C: `DASHI/Physics/Closure/CanonicalStageC.agda`, `.../CanonicalPhysicsPathPostulateAudit.agda`, `.../PhysicsClosureValidationSummary.agda`, `.../MinimalCrediblePhysicsClosure.agda`, `.../PhysicsClosureCoreWitness.agda`, `.../PhysicsClosureFullInstance.agda`, `.../PhysicsClosureTheoremChecklist.agda`
- Execution admissibility / family classification: `.../ExecutionAdmissibilityWitness.agda`, `.../ExecutionAdmissibilityCurrentTraceWitness.agda`, `.../ExecutionAdmissibilityCurrentFamilyWitness.agda`
- Dynamics / MDL / seams: `.../MDLFejerAxiomsShift.agda`, `.../ShiftSeamCertificates.agda`, `.../ObservablePredictionPackage.agda`
- Known-limits bridge: `.../KnownLimitsQFTBridgeTheorem.agda`
- Monster path and lift: `MonsterState.agda`, `Monster/Step.agda`, `MonsterSpec.agda`, `Ontology/Hecke/Scan.agda`, `DASHI/Physics/LiftToFullState.agda`
- Contraction / lattice: `UFTC_Lattice.agda`, `Contraction.agda`, `MaassRestoration.agda`

## Where to Find What (authoritative formal source → FRACDASH hook)

- **Stage C closure boundary:** `.../CanonicalStageC.agda`, summary bundles and audit/validation modules; hook to `AGDAS_BRIDGE_MAPPING.md`, `scripts/agdas_bridge.py`, `scripts/physics_invariant_analysis.py`
- **Minimal credible closure adapter:** `.../MinimalCrediblePhysicsClosure.agda`; hook to invariant analysis and observable export (`scripts/physics_invariant_analysis.py`). Current upstream shape now explicitly exposes authoritative execution-admissibility and family-classification witnesses.
- **Core/full witness wiring:** `.../PhysicsClosureCoreWitness.agda`, `.../PhysicsClosureFullInstance.agda`; hook to bridge regime reporting and local theorem naming so FRACDASH does not overstate what is currently executable.
- **Execution admissibility / family classification:** `.../ExecutionAdmissibilityWitness.agda`, `.../ExecutionAdmissibilityCurrentTraceWitness.agda`, `.../ExecutionAdmissibilityCurrentFamilyWitness.agda`; hook to `formalism/GenericMacroBridge.agda` and `formalism/BridgeInstances.agda` as the nearest local analogs, but currently only as a partial executable surrogate rather than a full upstream mirror.
- **Theorem checklist ladder:** `.../PhysicsClosureTheoremChecklist.agda`; hook to bridge mapping (tracks contraction→quadratic→signature→Clifford→spin/Dirac→closure)
- **MDL/Fejér + seams:** `.../MDLFejerAxiomsShift.agda`, `.../ShiftSeamCertificates.agda`; hook to physics target suite and geometry surrogates
- **Observable boundary:** `.../ObservablePredictionPackage.agda`; hook to `PHYSICS_INVARIANT_TARGETS.md` observable blocks and artifact reporters
- **Known-limits QFT bridge:** `.../KnownLimitsQFTBridgeTheorem.agda`; hook to long-run target setting, not yet executable locally
- **Monster state/step/spec + Hecke scan + lift:** core state/transition/scan formalism; hook to template generation (`scripts/agdas_bridge.py`, `scripts/toy_dashi_transitions.py`, carrier definitions)
- **Contraction / lattice / restoration:** `UFTC_Lattice.agda`, `Contraction.agda`, `MaassRestoration.agda`; hook to severity lattice, contraction invariants, and repair semantics in the physics templates

## What FRACDASH Needs for Bulk Wiring

- Mirror the Stage C boundary and minimal-credible adapter as explicit target surfaces in the invariant/observable reporters, instead of generic “physics closure” wording.
- Add an explicit local status line for upstream execution-admissibility and family-classification witnesses, so FRACDASH can report whether a slice only has local regime surrogates or actually matches the upstream witness vocabulary.
- Surface the MDL/Fejér and seam certificates as concrete checks (or TODO stubs) in the physics target suite so failures are visible.
- Track the theorem-checklist ladder as a dependency list in `AGDAS_BRIDGE_MAPPING.md` so bridge generation can flag missing links (e.g., contraction→quadratic→signature→spin).
- Add lift/scan provenance (Monster state/step/spec, Hecke scan) to emitted templates for bulk wiring and debugging.
- Keep known-limits bridges (QFT/GR) as non-claims until executable counterparts exist; note their upstream location for later wiring.

## Immediate Implementation Consequence

The next local requirement is an explicit intake/check artifact that records:

- which upstream closure/audit modules exist,
- which current FRACDASH modules correspond to them,
- which parts are only documented locally,
- which parts are actually executable in FRACDASH today.

That intake artifact is the minimum step needed before claiming that the full
AGDA formalism is "available for implementation" in this repo.

Current checker:

- `scripts/check_dashi_agda_formalism.py`
- artifact:
  `benchmarks/results/2026-03-15-dashi-agda-formalism-check.json`
- markdown summary:
  `benchmarks/results/2026-03-15-dashi-agda-formalism-check.md`
