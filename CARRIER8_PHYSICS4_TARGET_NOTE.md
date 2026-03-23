# Carrier8 Physics4 Target Note

Status date: `2026-03-23`

This note defines the next 8-register refinement after `carrier8_physics2` and
the negative-result `carrier8_physics3` trial.

## Active 8-Register Baseline

The active parallel 8-register track remains `carrier8_physics2`.

Current comparison artifacts:

- `benchmarks/results/2026-03-23-cross-carrier-baseline-summary.json`
- `benchmarks/results/2026-03-23-cross-carrier-baseline-summary.md`
- `benchmarks/results/2026-03-23-physics-invariants-carrier8_physics3.json`

## What Failed In Carrier8 Physics3

`carrier8_physics3` added a direct boundary re-entry rule, but the shared
cross-carrier summary stayed flat against `carrier8_physics2`.

Current read:

- deterministic edges stayed saturated at `6561`
- terminal states stayed at `0`
- longest chain stayed at `10`
- fixed-walk cycle/terminal counts stayed flat at `6561 / 0`
- best candidate stayed `action_rank`
- geometry surrogates stayed flat
- direct `boundary_to_interior` stayed at `0`

So the issue is not "the 8-register lane is dead"; it is that the added hook did
not compete with the already-saturated return-memory dynamics strongly enough
to change the observed surface.

## Target For Carrier8 Physics4

The next 8-register refinement should:

- preserve the current exact-law surface
- preserve the current strong cycle-bearing geometry
- preserve `carrier8_physics2` as the comparison baseline on shared summary axes
- insert boundary-return re-entry earlier than the broad return-memory damping
  rules so the new hook can win on reachable states

Preferred movement directions:

- make `boundary_to_interior` nonzero on the 8-register lane
- improve branch-local boundary-return observables without collapsing the cycle
  surface
- keep the new behavior interpretable as a boundary-return refinement rather
  than a generic shell-memory rewrite

## Interpretation Rule

If a candidate branch changes only branch-local memory counts while the shared
cross-carrier summary remains flat, it should be treated as another negative
result.

If a candidate branch preserves the current cycle-bearing geometry and exact
laws while making boundary re-entry visible on the shared summary surface, it is
a legitimate successor to `carrier8_physics2` for the parallel 8-register lane.

## First Trial Outcome

The first concrete `carrier8_physics4` trial now exists in:

- `benchmarks/results/2026-03-23-agdas-carrier8-physics4-phase2.json`
- `benchmarks/results/2026-03-23-physics-invariants-carrier8_physics4.json`

Current read:

- deterministic edges stay saturated at `6561`
- terminal states stay at `0`
- longest chain stays at `10`
- fixed-walk cycle/terminal counts stay flat at `6561 / 0`
- best candidate stays `action_rank`
- geometry surrogates stay flat
- direct `boundary_to_interior` stays at `0`

So the early re-entry insertion is still not enough to move the shared
cross-carrier surface. The branch is a useful negative result because it shows
the remaining blocker is not just "move the rule earlier"; the active 8-register
baseline should still be read through `carrier8_physics2`.
