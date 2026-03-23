# Carrier8 Physics5 Target Note

Status date: `2026-03-23`

This note defines the next 8-register refinement after the negative-result
`carrier8_physics4` trial.

## Active 8-Register Baseline

The active parallel 8-register track still remains `carrier8_physics2`.

Relevant artifacts:

- `benchmarks/results/2026-03-23-cross-carrier-baseline-summary.json`
- `benchmarks/results/2026-03-23-cross-carrier-baseline-summary.md`
- `benchmarks/results/2026-03-23-physics-invariants-carrier8_physics4.json`

## What Carrier8 Physics4 Clarified

`carrier8_physics4` proved that simple rule placement is not enough. Moving the
boundary-return re-entry hook ahead of the broad `carrier8_cycle_damp_return_*`
rules still left the shared cross-carrier surface flat.

The relevant local read is narrower than that:

- inside the full 8-register graph, `carrier8_physics4` only wins on a small
  boundary-memory slice
- inside the 512-state bounded analysis subset used by the invariant reporter,
  the dominant boundary rules are not the late cycle-damp rules
- the real subset bottlenecks are `carrier8_physics11_boundary_discharge` and
  the boundary occurrences of `carrier8_physics2_join_*`

So the next branch should not be "another earlier re-entry hook." It should
explicitly target the boundary discharge/join states that dominate the sampled
active basin.

## Target For Carrier8 Physics5

The next 8-register refinement should:

- preserve the current exact-law surface
- preserve the current cycle-bearing geometry
- preserve `carrier8_physics2` as the comparison baseline unless the shared
  cross-carrier surface actually moves
- preempt boundary `physics11_boundary_discharge` and boundary `physics2_join_*`
  states when return memory is already active, so the sampled basin sees a real
  boundary -> interior alternative

Preferred movement directions:

- make `boundary_to_interior` nonzero in the bounded analysis subset, not just
  somewhere in the full 6561-state graph
- reduce the share of sampled boundary states consumed by boundary discharge
  without collapsing the cycle surface
- keep the new behavior interpretable as memory-guided boundary recovery rather
  than a full rewrite of the 8-register carrier logic

## First Trial Outcome

The first concrete `carrier8_physics5` trial now exists in:

- `benchmarks/results/2026-03-23-agdas-carrier8-physics5-phase2.json`
- `benchmarks/results/2026-03-23-physics-invariants-carrier8_physics5.json`

Current read:

- deterministic edges stay saturated at `6561`
- terminal states stay at `0`
- longest chain stays at `10`
- fixed-walk cycle/terminal counts stay flat at `6561 / 0`
- best candidate stays `action_rank`
- `action_rank` strict-decrease ratio improves from `0.5159 -> 0.5253`
- direct `boundary_to_interior` becomes nonzero in the sampled basin: `0 -> 6`
- geodesic-like near-min ratio improves slightly: `0.99099 -> 0.99138`
- curvature-like mean neighbor spread drops: `0.79661 -> 0.76341`

So `carrier8_physics5` is the first real carrier8 successor candidate on the
shared summary surface, but not yet a clear handoff from `carrier8_physics2`:
it wins on sampled boundary recovery and slightly improves the best-candidate
signal while giving back some curvature spread.
