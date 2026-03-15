# MonsterLean Intake (Local Clone)

This note captures what FRACDASH can realistically reuse from the locally cloned `monster` repo Lean surface, without theorem inflation.

## Source

- Local clone path: `monster/`
- Index file used: `monster/CODE_INDEX.md`
- Lean subtree used: `monster/MonsterLean/`

## Why this matters for FRACDASH

FRACDASH needs executable and checkable bridges, not broad symbolic overlays. The `MonsterLean` tree can provide candidate formal vocabulary for:

- prime-basis lists and walk step structures
- factor-removal/walk definitions
- ring/CRT-style decomposition claims
- complexity/ordering structures

## FRACDASH-relevant candidate files

1. `monster/MonsterLean/MonsterWalkPrimes.lean`
2. `monster/MonsterLean/MonsterWalk.lean`
3. `monster/MonsterLean/MonsterWalkRings.lean`
4. `monster/MonsterLean/ComplexityLattice.lean`

These files contain walk/factorization data structures and statements closest to current FRACDASH concerns (fixed prime sets, walk structure, basin/ordering proxies).

## Immediate caveat: proof completeness

Prioritized closure is now done for the four high-signal files:

- `MonsterWalkPrimes.lean` has no `sorry`/`axiom`
- `MonsterWalk.lean` has no `sorry`/`axiom`
- `MonsterWalkRings.lean` has no `sorry`/`axiom`
- `BottPeriodicity.lean` has no `sorry`/`axiom`

Broader `MonsterLean` still includes quarantined files (for example `ComplexityLattice.lean`), so FRACDASH must continue to treat only closed files as local claim support.

## Intake policy for FRACDASH

- Reuse only explicit definitions and concrete constants where they align with existing FRACDASH artifacts.
- Do not import or cite `axiom`/`sorry` statements as evidence.
- Any adopted claim must be reproduced as executable FRACDASH experiment output (JSON artifact + script).
- Keep monster-repo references as optional external context, not hard dependencies for the main FRACTRAN path.

## First extracted clue (constants-only)

FRACDASH now includes a constants-only extractor:

- `scripts/extract_monsterlean_10walk.py`
- artifact: `benchmarks/results/2026-03-15-monsterlean-10walk-extract.json`

Observed (not proven):

- Parsing `BottPeriodicity.monsterWalkGroups` yields explicit 10 labels:
  `8080, 1742, 479, 451, 2875, 8864, 5990, 496, 1710, 7570`.
- With sequence-only edges (`0->1->...->9`) and the observed degeneracy table from prior notes, the extracted candidate graph has longest strict descending chain `4`.
- If periodic/clue edges are added (`8->0`, `9->1`, and `479->451->496->1742`), the same chain diagnostic rises to `5`.

Interpretation boundary:

- This is a useful structural clue for the 10-walk target.
- It is not yet a validated transition-semantics derivation from Lean or FRACDASH dynamics.

## Canonical lock and independent derivation (`implemented`)

FRACDASH now also includes:

- `scripts/freeze_monster10walk_canonical.py`
- lock artifact: `benchmarks/results/2026-03-15-monster10walk-canonical.json`

Current locked result (`--strict-lock`, default `physics8,physics9`):

- canonical edge semantics (`0->1->...->9`) pass
- canonical degeneracy-chain height is `4`
- independent FRACDASH transition-data derivation yields a 10-node path with full direct support (`9/9`) for both `physics8` and `physics9`
- derivation match check passes

## File-by-file theorem quarantine (`implemented`)

FRACDASH now includes:

- `scripts/quarantine_monsterlean_claims.py`
- artifacts:
  - `benchmarks/results/2026-03-15-monsterlean-claim-status.json`
  - `benchmarks/results/2026-03-15-monsterlean-claim-status.md`

Current scan over `monster/MonsterLean/*.lean`:

- files scanned: `94`
- closed for local claim reuse: `35`
- quarantined (contains `axiom` or `sorry`): `59`
- prioritized closure queue is now reported explicitly for:
  - `MonsterWalk.lean`
  - `MonsterWalkPrimes.lean`
  - `MonsterWalkRings.lean`
  - `BottPeriodicity.lean`
  Current status: all four are `closed_for_local_claim_reuse`.
