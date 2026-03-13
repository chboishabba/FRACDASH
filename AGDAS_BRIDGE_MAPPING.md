# AGDAS Bridge Mapping

This file defines the concrete register mapping used by the FRACDASH-side AGDAS
bridge. It is intentionally small and executable rather than fully faithful.

## Register Roles

- `R1`: primary triadic carrier
- `R2`: overflow / stage flag
- `R3`: kernel polarity (for involution tests)
- `R4`: unused in wave 1 (reserved for parity / bookkeeping)

## TriTruth Mapping (Base369)

Map triadic values onto the signed ternary register:

- `tri-low`  -> `negative`
- `tri-mid`  -> `zero`
- `tri-high` -> `positive`

This allows `rotateTri` to be expressed as three explicit transitions on `R1`.

## Stage Mapping (LogicTlurey)

Represent the 4-stage cycle using `R1` plus a single overflow flag in `R2`:

- `seed`      -> `R1=negative, R2=zero`
- `counter`   -> `R1=zero,     R2=zero`
- `resonance` -> `R1=positive, R2=zero`
- `overflow`  -> `R1=negative, R2=positive`

This yields the deterministic stage cycle:

- `seed -> counter`: `R1 negative -> zero` (R2 stays zero)
- `counter -> resonance`: `R1 zero -> positive` (R2 stays zero)
- `resonance -> overflow`: `R1 positive -> negative`, `R2 zero -> positive`
- `overflow -> seed`: `R1 negative stays`, `R2 positive -> zero`

## Kernel Involution (Kernel.Algebra.ι)

Map the involution on `R3`:

- `R3 negative -> positive`
- `R3 positive -> negative`
- `R3 zero -> zero`

These become the kernel templates in the bridge.

## Notes

- This mapping is a bridge convenience, not a claim of full fidelity.
- The goal is to enable end-to-end FRACTRAN execution and parity checks
  against the toy baseline before expanding to richer state encodings.

## Wave 2: MonsterState / Monster.Step

The second wave does not attempt to encode the full 15-bit `Mask` or the full
unbounded `window : Nat`. It only encodes the executable seam that `Monster.Step`
actually exposes:

- `choose` picks either an admissible candidate or falls back to the current mask
- `step` increments the window after choosing

### Compressed roles

- `R1`: compressed mask summary
- `R2`: admissibility outcome summary
- `R3`: reserved for kernel/polarity experiments
- `R4`: compressed window phase (`Nat mod 3`)

### Compressed mask summary on `R1`

- `negative`: empty / aggressively reduced mask
- `zero`: current mask / fallback path
- `positive`: candidate-selected / retained mask

### Compressed admissibility summary on `R2`

- `negative`: candidate rejected, fallback path taken
- `zero`: no pending admissibility outcome
- `positive`: candidate accepted

### Compressed window phase on `R4`

- `zero`: phase 0
- `positive`: phase 1
- `negative`: phase 2

The `step` update is then modeled as:

- accepted step:
  - require `R1=zero` and promote it to `positive`
  - clear `R2` back to `zero`
  - rotate `R4` by one phase
- rejected step:
  - require `R1=zero` and keep it at `zero` (fallback/current mask)
  - clear `R2` back to `zero`
  - rotate `R4` by one phase

This is still a compression, but it is honest about what is being modeled:
deterministic choice outcome plus window advancement, not the full mask algebra.

## Wave 3: Enlarged Carrier Prototype

The next bridge step is a larger carrier rather than more compression. The
prototype lives in `scripts/agdas_wave3_state.py`.

Wave-3 splits the Monster seam into six signed-ternary registers:

- `R1`: mask summary
- `R2`: candidate / choice summary
- `R3`: admissibility summary
- `R4`: window low trit
- `R5`: window high trit
- `R6`: kernel / polarity

This increases the carrier from `3^4 = 81` states to `3^6 = 729` states and is
meant to preserve the Monster-side seam as an actually structured low-dimensional
system instead of forcing it into a nearly terminal 4-register compression.

## Physics 2 Carrier

For the next physics-facing pass, use a separate 6-register carrier:

- `R1`: left/source severity code
- `R2`: right/source severity code
- `R3`: effective joined severity
- `R4`: region flag (`positive = interior`, `negative = boundary`, `zero = latent`)
- `R5`: signature/scan latch (`positive = left`, `negative = right`, `zero = unset`)
- `R6`: action/energy phase (`negative = high`, `positive = mid`, `zero = spent`)

The intended update loop is:

1. scan a source code into `R5`
2. materialize effective severity in `R3`
3. relax `R3` under contraction in the interior
4. fall to boundary when relaxation completes
5. reset/re-arm at the boundary so the process can recur

## Physics 3 Refinement

The next refinement keeps the same 6-register carrier and adds:

- a latent cone shell on `R4` (`zero`) between boundary and interior
- an explicit action-phase monotonicity report on `R6`

Refined region semantics on `R4`:

- `positive`: interior
- `negative`: boundary
- `zero`: latent shell / recovery layer

Refined reset loop:

1. `boundary -> latent shell`
2. `latent shell -> interior rearm`

Action-phase rank on `R6`:

- `negative`: high
- `positive`: mid
- `zero`: spent

Artifacts should report how many transitions:

- decrease the action rank
- preserve it
- increase it

## Physics 4 Guard Tightening

`physics4` keeps the same 6-register carrier but tightens the reset discipline
instead of adding more carrier structure.

The stricter interpretation is:

- scan only from an explicitly armed interior state
  - require `R4 = positive`
  - require `R5 = zero`
  - require `R6 = negative`
- enter the latent shell only from a discharged boundary state
  - require `R3 = zero`
  - require `R4 = negative`
  - require `R6 = zero`
- re-arm the interior only from a cleared shell state
  - require `R3 = zero`
  - require `R4 = zero`
  - require `R5 = zero`
  - require `R6 = zero`

This improves action-order cleanliness substantially, but it also eliminates the
recurrent loop. So `physics4` should be treated as a constraint probe, not the
new default semantics.

## Physics 5 Target

The next bridge pass should be a hybrid:

- keep the `physics4` scan guard
- keep the discharged-boundary requirement for shell entry
- selectively relax shell-to-interior rearm just enough to restore recurrence

The design goal is the narrow recurrent band between the loose `physics3`
rearm and the overconstrained `physics4` reset.
