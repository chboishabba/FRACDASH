# Physics Bridge Notes

This is the current high-priority AGDAS bridge direction for FRACDASH.

## Why This Path

The Monster seam has been useful as a probe, but the current results show the
main limitation is the state carrier and refresh semantics, not missing bridge
plumbing. For the next pass, the more relevant path is a compact physics-facing
seam that is closer to:

- severity propagation
- contraction / descent
- interior vs boundary behavior

These are more likely to stay relevant to James than a deeper Monster detour.

## Semantic Sources

- `../dashi_agda/UFTC_Lattice.agda`
- `../dashi_agda/Contraction.agda`
- `../dashi_agda/ActionMonotonicity.agda`
- `../dashi_agda/DASHI/Algebra/PhysicsSignature.agda`

## Local Formalism

The local-only sketch is:

- `formalism/PhysicsBridgeRefreshSketch.agda`

That file is not intended as upstream truth. It exists to pin down the local
FRACDASH executable seam before any formal upstream version is attempted.

## First Executable Physics Seam

The first physics-facing executable seam should model:

1. join / propagation of effective severity
2. contraction-style relaxation in the interior
3. a boundary reset that re-arms the local environment

The goal is not full physical fidelity. The goal is to get a small recurrent
bridge with nontrivial multi-step behavior that is closer to the physics path
than the current Monster compression.

## Intended Next Layer

The next physics layer (`physics2`) should widen that seam without changing its
basic story.

Carrier split:

- `R1`: left/source severity code
- `R2`: right/source severity code
- `R3`: effective joined severity
- `R4`: region flag (`interior` vs `boundary`)
- `R5`: signature/scan latch
- `R6`: action/energy phase

Behavior:

1. scan left/right source codes into a signature latch
2. materialize joined severity from the latched source
3. apply contraction-style relaxation in the interior
4. drop to the boundary after the final relaxation step
5. re-arm the interior and action phase at the boundary

This is still a local FRACDASH formalism, not an upstream claim. But it is the
intended executable bridge behavior for the next implementation pass.

Current result:

- `physics2` is now implemented on a dedicated 6-register carrier.
- artifact: `benchmarks/results/2026-03-14-agdas-physics2-phase2.json`
- first measured shape:
  - `729` states
  - `657` edges
  - longest chain `12`
  - deterministic canonical cycle length `4`
