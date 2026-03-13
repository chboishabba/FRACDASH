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

## Intended Next Layer After `physics2`

The next refinement should be `physics3`, and it should do two things together:

1. add a cone-interior refinement step on the same 6-register carrier
2. report action-phase monotonicity on the resulting transition graph

Cone refinement:

- split the coarse boundary reset into:
  - `boundary -> latent shell`
  - `latent shell -> interior rearm`

This keeps the current scan/materialize/relax story, but gives the geometry a
more explicit interior/boundary seam.

Action monotonicity reporting:

- assign a simple rank to `R6` (`negative > positive > zero`)
- count how many transitions decrease, preserve, or increase that rank
- record the summary in the artifact rather than only relying on walk traces

This is the right next step because it strengthens the James-facing physics path
without inventing a separate branch of semantics.

Current result:

- `physics3` is now implemented on the same 6-register carrier.
- artifact: `benchmarks/results/2026-03-14-agdas-physics3-phase2.json`
- first measured shape:
  - `729` states
  - `900` edges
  - longest chain `15`
  - deterministic canonical cycle length `5`
  - action monotonicity summary:
    - decreases: `234`
    - preserves: `504`
    - increases: `162`

## `physics4` Result

`physics4` is now implemented on the same 6-register carrier.

- artifact: `benchmarks/results/2026-03-14-agdas-physics4-phase2.json`
- first measured shape:
  - `729` states
  - `162` edges
  - longest chain `9`
  - `0` cycles in the fixed-walk summary
  - action monotonicity summary:
    - decreases: `72`
    - preserves: `81`
    - increases: `9`

Interpretation:

- the stronger shell/interior guards did what they were supposed to do for
  action order
- but they also overconstrained the bridge and killed the recurrent loop that
  made `physics3` interesting

## Next Pass After `physics4`

The next pass should be `physics5`.

The target is to recover recurrence without returning all the way to the loose
`physics3` reset behavior. That likely means:

- keep scan rules tied to an explicitly armed interior
- keep shell entry tied to a discharged boundary state
- selectively relax shell-to-interior rearm so some recurrent trajectories
  survive without reopening the broad `physics3` increase surface

This is now the main physics design problem: not "more carrier" and not "more
scan", but finding the narrow recurrent hybrid between `physics3` and
`physics4`.
