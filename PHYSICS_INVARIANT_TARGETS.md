# Physics Invariant Targets

This file fixes the concrete target table for the current physics lane.

The suite is intentionally split into:

- `implemented`: enforced by script checks.
- `observed experimentally`: measured and recorded in artifacts, but not part of the hard lock yet.
- `conjectured`: interpretation only.

The current version is `physics_target_suite_v1`.

## Regime Taxonomy

The current physics-facing interpretation layer now distinguishes two bridge-valid
regimes:

- `conservative_contracting`
  - strict contraction with zero transmutation
  - exact `R1/R2` source-signature conservation remains in force
- `transmuting_contracting`
  - strict contraction with bounded transmutation
  - exact `R1/R2` conservation is not required, but decode correctness,
    well-formedness, and regime validity still hold

The locked `physics2..physics8` exact-law package below remains the canonical
conservative subregime lock. It should not be read as the universal bridge
invariant set for every widened family.

## Canonical Artifact Inputs

- Phase-2 physics templates: `benchmarks/results/*-agdas-physics[2-8]-phase2.json` (locked set)
- Invariant diagnostics: `benchmarks/results/*-physics-invariants-physics[2-8].json` (locked set)

The checker resolves the latest artifact per template by filename date prefix.

## V1 Exact Laws (`implemented`)

These are enforced by [`scripts/check_physics_invariant_targets.py`](/home/c/Documents/code/FRACDASH/scripts/check_physics_invariant_targets.py).
They define the current conservative subregime lock on the canonical
`physics2..physics8` family.

1. `source_charge_conservation`
   - deterministic edges preserve `R1` and `R2` exactly
   - `changed_edges_by_register.R1 == 0`
   - `changed_edges_by_register.R2 == 0`
2. `source_parity_sector_preservation`
   - deterministic edges preserve nonzero-occupancy parity for `R1`, `R2`, and the combined `(R1,R2)` source pair
3. `locality_radius_bound`
   - deterministic edges satisfy `max_changed_registers <= 3`
   - deterministic edges satisfy `max_l1_step_delta <= 5`
4. `forward_cone_bound`
   - for one-register perturbation pairs with deterministic successors, `max_successor_hamming <= 5`
5. `cycle_distance_nonincrease`
   - `distance_to_cycle.nonincrease_ratio == 1.0`
   - `distance_to_cycle.increases == 0`

Carrier-aware note:

- The 8-register physics-local branch (`carrier8_*`) uses two additional memory registers (`R7` return, `R8` debt). To keep the same locality/forward-cone flavor without over-penalizing the wider carrier, the analyzer applies relaxed bounds only for that carrier: `max_changed_registers <= 5`, `max_l1_step_delta <= 7`, `max_successor_hamming <= 6`. The locked `physics2..physics8` set continues to use the original bounds.

## V1 Statistical Laws (`implemented`)

These are also enforced on the locked `physics2..physics8` set, with `physics4` treated as the explicit overconstrained exception for cycle-based geometry metrics.

1. `perturbation_stability`
   - `single_register_sign_flip.nonexpansion_ratio >= 0.80`
   - `single_register_zero_toggle.nonexpansion_ratio >= 0.65`
   - `paired_defect.nonexpansion_ratio >= 0.49`
2. `geodesic_like_flow`
   - compare only against one-register neighbors that are themselves cycle-reachable (`distance_to_cycle >= 0`)
   - for cycle-bearing templates (`physics2,3,5,6,7,8`), `near_min_ratio >= 0.74`
   - `physics4` is exempt because the cycle structure collapses and `distance_to_cycle` is globally flat
3. `curvature_like_concentration`
   - compute spread only over cycle-reachable one-register neighbors
   - for cycle-bearing templates (`physics2,3,5,6,7,8`), `mean_neighbor_spread >= 0.80`
   - `physics4` is expected to show the flat overconstraint signature (`mean_neighbor_spread == 0.0`)
4. `defect_attraction`
   - `defect_nonincrease_ratio >= 0.43`

## Existing Structural Lock (`implemented`)

The previous relationship-level lock remains active and is still checked:

1. Best-candidate identity:
   - `physics2,3,5,6,7,8`: `best_candidate.name == distance_to_cycle`
   - `physics4`: `best_candidate.name in {distance_to_cycle, weighted_abs_search}`
2. Controlled-hybrid progression (`physics5..physics8`):
   - action-rank increase count stays fixed at `27`
   - edge count grows strictly: `physics5 < physics6 < physics7 < physics8`
   - cyclic starts grow strictly: `physics5 < physics6 < physics7 < physics8`
   - longest-chain depth is nondecreasing with `physics8 >= 13`
3. Long-tail resolution (`physics6..physics8`):
   - `long_tail_diagnosis.still_timeout == 0`
4. Physics4 overconstraint signature:
   - `physics4.fixed_walk_summary.cycle == 0`
   - `physics4.full_space_profile.edges < physics5.full_space_profile.edges`

## Current V1 Baseline Numbers (`observed experimentally`)

The V1 suite is anchored to the current `physics2..physics8` artifacts:

- exact source conservation basis: `R1`, `R2`
- exact source parity basis: `R1_nonzero`, `R2_nonzero`, `R1R2_nonzero_pair`
- exact locality bound: `max_changed_registers = 3`, `max_l1_step_delta <= 5`
- exact forward-cone bound: `max_successor_hamming <= 5`
- exact cycle-distance law: `nonincrease_ratio = 1.0`, `increases = 0`
- sign-flip nonexpansion ratio band: `0.8053 .. 0.9138`
- zero-toggle nonexpansion ratio band: `0.6561 .. 0.7759`
- paired-defect nonexpansion ratio band: `0.4925 .. 0.5537`
- cycle-bearing geodesic-like `near_min_ratio` band: `0.7440 .. 0.8663`
- cycle-bearing curvature-like `mean_neighbor_spread` band: `0.8323 .. 2.5830`
- defect nonincrease ratio band: `0.4321 .. 0.6124`

## Exploratory Continuation (`observed experimentally`)

- `physics9..physics20` are allowed to extend the physics lane without changing the hard lock.
- Their artifacts are measured against the same V1 suite, but they are not yet used as canonical gate inputs.
- `physics19` currently preserves the conservative exact laws and the corrected cycle-reachable geometry surrogates, but it does not yet improve the deterministic recurrent core beyond `physics18`.
- `physics20` is the first post-correction widening branch that changes the deterministic recurrent core:
  - deterministic edges `274 -> 301`
  - phase graph edges `359 -> 386`
  - terminal states `455 -> 428`
  - corrected `geodesic_like_flow.near_min_ratio 0.9094 -> 0.9181`
  - corrected `curvature_like_concentration.mean_neighbor_spread 1.8258 -> 1.9273`
  - `defect_attraction.nonincrease_ratio 0.6496 -> 0.6811`
  - remains in the `conservative_contracting` subregime on the current checked branch
- `physics22` is now the leading 6-register exploratory branch:
  - deterministic edges `310 -> 364`
  - boundary-to-interior re-entry `9 -> 63`
  - corrected `geodesic_like_flow.near_min_ratio = 0.9207` (still strong)
  - remains in the `conservative_contracting` subregime on the current checked branch
- A separate exploratory branch now exists for a physics-local 8-register carrier (`carrier8_physics1`); it is excluded from the hard lock and should be interpreted through branch-local observables rather than direct comparison to the locked `physics2..physics8` lineage.
  - first artifact: `benchmarks/results/2026-03-15-agdas-carrier8-physics1-phase2.json`
  - first invariant artifact: `benchmarks/results/2026-03-15-physics-invariants-carrier8_physics1.json`
  - current role: expose return/debt occupancy explicitly, not replace the 6-register exact-law baseline

## Wider Bridge Reading (`observed experimentally`)

The bridge result is now wider than the locked conservative exact-law package:

- conservation is not the universal bridge invariant
- conservation is the zero-transmutation special case
- the wider valid bridge claim is strict contraction plus bounded transmutation

For the currently closed widened family, the stable interpretation split is:

- `conservative_contracting`
  - exact source-signature conservation remains visible
- `transmuting_contracting`
  - exact source-signature conservation can fail locally while strict contraction
    and bounded transmutation remain intact

This wider bridge-valid regime taxonomy should be used for `physics15`,
`physics19`, `physics20`, `physics21`, and `physics22`, rather than treating any
departure from the conservative exact-law package as an automatic bridge failure.

## Observable Surrogates (`observed experimentally`)

Invariant artifacts now also emit `observable_surrogates`:

- `region_mass`: cycle-reachable and deterministic-source occupancy split across boundary/shell/interior
- `action_phase_profile`: action register occupancy split across deterministic and cycle-reachable sources
- `reentry_flow`: shell-to-interior and boundary-to-interior transition counts/ratios
- `source_latch_alignment`: whether latch polarity aligns with the active source side
- `source_defect_coupling`: mean defect load by source-activity class (`neutral`, `left_only`, `right_only`, `dual_active`)
- `boundary_return_profile`: return-memory occupancy split for the exploratory 8-register carrier
- `transport_debt_profile`: transport/debt occupancy split for the exploratory 8-register carrier

## Not Yet Locked (`conjectured`)

- Mapping these discrete laws to specific GR/QFT identities is not yet established.
- `geodesic_like_flow` is a shortest-descent surrogate, not a literal geodesic proof.
- `curvature_like_concentration` is a neighborhood anisotropy statistic, not a derived curvature tensor.
- Any claim about gravity emergence remains hypothesis until these laws remain stable under broader perturbation families and larger carrier extensions.
