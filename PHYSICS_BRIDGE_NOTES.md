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

The concrete `physics5` plan is:

- keep the `physics4` scan guard unchanged
- keep the discharged-boundary requirement for `boundary -> shell`
- split `shell -> interior` into:
  - a cleared rearm when `R5 = zero`
  - a latched-left rearm when `R5 = positive`
  - a latched-right rearm when `R5 = negative`

This is the smallest semantic change that can plausibly restore recurrence,
because it only reopens rearm for shell states that already carry a specific
scan decision.

## `physics5` Result

`physics5` is now implemented on the same 6-register carrier.

- artifact: `benchmarks/results/2026-03-14-agdas-physics5-phase2.json`
- first measured shape:
  - `729` states
  - `180` edges
  - longest chain `10`
  - `100` cycles in the fixed-walk summary
  - action monotonicity summary:
    - decreases: `72`
    - preserves: `81`
    - increases: `27`

Interpretation:

- the hybrid works in the narrow sense: recurrence is back and the action-order
  profile is still far cleaner than `physics3`
- but it does not yet recover the graph richness of `physics3`
- so `physics5` is the best ordered hybrid so far, not the new overall lead

## Next Pass After `physics5`

The next pass should preserve the `physics5` rearm split and try to recover
more recurrent structure without reopening the broad `physics3` increase
surface.

The most likely move is to add a narrow shell-refresh path for selected latched
states, rather than weakening the scan guard.

The concrete `physics6` plan is:

- keep the `physics5` rearm split unchanged
- add a left-shell refresh that clears a positive latch while staying in the shell
- add a right-shell refresh that clears a negative latch while staying in the shell

This should add structure through extra shell-local preserve steps instead of
through broader rearm permission.

## `physics6` Result

`physics6` is now implemented on the same 6-register carrier.

- artifact: `benchmarks/results/2026-03-14-agdas-physics6-phase2.json`
- first measured shape:
  - `729` states
  - `198` edges
  - longest chain `12`
  - `115` cycles in the fixed-walk summary
  - action monotonicity summary:
    - decreases: `72`
    - preserves: `99`
    - increases: `27`
  - deterministic walk: 6-step cycle with an explicit shell-refresh step

Interpretation:

- this is a real improvement over `physics5`
- the extra structure came entirely from preserve edges, which is what we wanted
- `physics3` still leads on raw richness, but `physics6` is now the best
  controlled hybrid
- the built-in long-tail diagnosis resolves the one apparent timeout under a
  higher cap: it is a cycle, not evidence of a broader runaway tail

## Next Pass After `physics6`

The next pass should keep the `physics6` shell-refresh path and recover more
recurrent structure without giving back the current action-order profile.

The most likely move is:

- keep the built-in diagnostic rerun in place
- use `physics6` as the new controlled baseline
- only then decide whether to add another narrow shell-local transition

The concrete `physics7` plan is:

- keep all `physics6` transitions unchanged
- add two shell-local probe transitions from cleared shell states:
  - one left-high probe that sets a left latch
  - one right-high probe that sets a right latch

This keeps the change small and preserve-only at the new edge level, which is
the cleanest way to widen recurrence without inflating action-rank increases.

## `physics7` Result

`physics7` is now implemented on the same 6-register carrier.

- artifact: `benchmarks/results/2026-03-14-agdas-physics7-phase2.json`
- first measured shape:
  - `729` states
  - `204` edges
  - longest chain `12`
  - `116` cycles in the fixed-walk summary
  - action monotonicity summary:
    - decreases: `72`
    - preserves: `105`
    - increases: `27`
  - fixed-walk timeout count at `max-steps 12`: `0`

Interpretation:

- this widens recurrence from `physics6` in the intended way
- the improvement is mostly breadth through preserve edges, not deeper chains
- the action-jump count stays flat, so the constraint is still respected
- `physics3` still leads on raw richness, but `physics7` is now the best
  controlled hybrid

## Next Pass After `physics7`

The next pass should keep the `physics7` core and target chain depth rather
than only breadth.

The most likely move is:

- add one narrow chain-extending shell/interior micro-step that preserves the
  current increase count
- keep long-tail diagnosis enabled in the artifact
- reject variants that increase the action-jump count above `27`

## `physics8` Result

`physics8` is now implemented on the same 6-register carrier.

- artifact: `benchmarks/results/2026-03-14-agdas-physics8-phase2.json`
- first measured shape:
  - `729` states
  - `222` edges
  - longest chain `13`
  - `132` cycles in the fixed-walk summary
  - action monotonicity summary:
    - decreases: `72`
    - preserves: `123`
    - increases: `27`
  - fixed-walk timeout count at `max-steps 12`: `0`

Interpretation:

- this is the first constrained hybrid pass that improves both breadth and
  depth from the `physics7` baseline
- the increase count remains flat, so the jump constraint is still respected
- `physics3` still leads on raw richness, but `physics8` is now the strongest
  constrained baseline

## Next Pass After `physics8`

The next pass should continue from `physics8` and improve richness toward
`physics3` without relaxing the jump bound.

The most likely move is:

- add one more narrow shell/interior micro-step in high-source branches only
- keep the increase count at or below `27`
- reject variants that raise timeout count above `0` at `max-steps 12`
