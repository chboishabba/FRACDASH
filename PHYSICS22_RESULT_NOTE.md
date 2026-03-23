# Physics22 Result Note

Status date: `2026-03-23`

This note records the current claim boundary for the active 6-register
exploratory baseline, `physics22`.

## Observed

- `physics22` is the leading branch within the current widened 6-register family
  (`physics15`, `physics19`, `physics20`, `physics21`, `physics22`) on the
  summary axes currently tracked in-repo.
- In the widened-family summary artifact,
  `benchmarks/results/2026-03-23-widened-invariant-family-summary.{json,md}`,
  `physics22` currently has:
  - deterministic recurrent edges = `364`
  - terminal states = `365`
  - longest chain = `32`
  - direct `boundary_to_interior` re-entry count = `63`
  - `distance_to_cycle` as the best current invariant candidate
  - corrected `geodesic_like_flow.near_min_ratio = 0.9206896551724137`
- The widened family remains mixed-transmuting throughout this range rather than
  splitting into a new bridge-validity class after `physics15`.
- The current local execution-status surface remains consistent with this read:
  admissibility is tracked as preserved paired-prime well-formedness, and
  family usage is tracked through the regime-class summary.

## Not Yet Established

- `physics22` is not yet a theorem-complete semantic endpoint for the full
  upstream formal stack.
- The current widened-family summary does not yet prove that mixed-transmuting
  usage is the unique or optimal explanation of the branch improvements.
- The current evidence does not yet identify the observed geometry surrogates
  with a specific GR/QFT/root-system semantics.
- The 8-register branch has not yet been compared against `physics22` on the
  same widened-family summary axes, so `physics22` is only the active
  6-register baseline, not a universal repo-wide winner.

## Safe Current Statement

> `physics22` is the active 6-register exploratory baseline in FRACDASH. Within
> the current widened family it gives the strongest recurrent-core and direct
> re-entry result while preserving the bridge-valid mixed-transmuting regime and
> keeping the current geometry surrogates strong.

## Unsafe Current Statement

- `physics22` is the final correct physics branch
- mixed transmutation is now proven necessary in full generality
- the current geometry-surrogate signal already identifies the full semantics
  with a specific physical or root-system interpretation
