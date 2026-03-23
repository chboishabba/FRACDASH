# Physics23 Target Note

Status date: `2026-03-23`

This note defines the design target for the next 6-register refinement after
`physics22`.

## Baseline To Beat

The active baseline is `physics22`, with the handoff gain quantified in:

- `benchmarks/results/2026-03-23-physics22-baseline-delta.json`
- `benchmarks/results/2026-03-23-physics22-baseline-delta.md`

Relative to `physics21`, `physics22` adds one transition rule and currently
improves:

- deterministic recurrent edges: `395 -> 476` (`+81`)
- terminal states: `419 -> 365` (`-54`)
- direct `boundary_to_interior` re-entry: `9 -> 63` (`+54`)

while leaving these quantities flat:

- fixed-walk cycle count: `290 -> 290`
- fixed-walk terminal count: `439 -> 439`
- best invariant candidate: `distance_to_cycle -> distance_to_cycle`
- corrected geometry surrogates (`geodesic_like_flow`, `curvature_like_concentration`)

## Target For Physics23

The next 6-register refinement should be judged against the `physics22` gain
shape, not merely against older widened-family branches.

Minimum success conditions:

- preserve the current fixed-walk cycle/terminal split
- preserve `distance_to_cycle` as the best current invariant candidate
- keep current geometry-surrogate values at least flat
- improve the deterministic recurrent core beyond the current `physics22`
  baseline

Preferred improvement directions:

- raise deterministic recurrent edges above `476`
- lower terminal states below `365`
- raise direct `boundary_to_interior` re-entry above `63`

## First Trial Outcome

The first concrete `physics23` trial now exists in:

- `benchmarks/results/2026-03-23-agdas-physics23-phase2.json`
- `benchmarks/results/2026-03-23-physics-invariants-physics23.json`

Current read:

- deterministic recurrent edges improve from `476 -> 503`
- terminal states stay flat at `365`
- longest chain stays flat at `32`
- direct `boundary_to_interior` re-entry stays flat at `63`
- fixed-walk cycle/terminal split stays flat
- `distance_to_cycle` stays the best current invariant candidate
- current geometry-surrogate values stay flat

So this first trial clears the minimum success condition (improve the
deterministic recurrent core without giving back the current invariant/geometry
surface), but it does not yet clear the preferred target of improving terminal
mass or direct re-entry beyond `physics22`.

## Interpretation Rule

If a candidate branch improves only the fixed-walk side while losing recurrent
core or re-entry structure, it should not replace `physics22` as the active
baseline.

If a candidate branch preserves the fixed-walk and geometry surface while
improving recurrent-core and re-entry structure, it is a legitimate successor
candidate even if it remains in the same mixed-transmuting regime.
