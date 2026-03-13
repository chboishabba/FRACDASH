# AGDAS Bridge Notes

This repo treats the AGDA code in `../dashi_agda` as the semantic reference,
but the executable bridge is maintained in FRACDASH. The local bridge does not
require edits to the `.agda` sources; instead it maps selected AGDA definitions
into explicit FRACTRAN-facing transition templates and notes.

The concrete register mapping used for the first wave is captured in
`AGDAS_BRIDGE_MAPPING.md`.

## Bridge Plan

The primary route is:

1. choose a small executable AGDA definition surface
2. record the corresponding FRACDASH-side mapping
3. emit executable transition templates from `scripts/agdas_bridge.py`
4. run them through `scripts/toy_dashi_transitions.py`

Optional future route:
- add machine-readable source annotations in `.agda` files if we later want a
  tighter source-coupled extractor

The old marker format is retained as an optional parser format, not the main path:

```
-- agdas transition <name>: R1=+1, R2=0 -> R1=+1, R2=+1
```

Parsing rules (from `scripts/agdas_bridge.py`):

- marker prefix is `-- agdas transition` (also `agd` or `dashi` accepted)
- `R1..R4` register bindings only
- states must be `-1`, `0`, `+1` (or synonyms `negative/zero/positive`)
- condition and action must both bind at least one register

## Semantic Source Areas

These are the AGDA areas whose definitions the FRACDASH bridge should interpret first:

- `../dashi_agda/DASHI_Tests.agda`
- `../dashi_agda/Kernel/*`
- `../dashi_agda/ActionMonotonicity.agda`
- `../dashi_agda/Monster*/` (only if those transitions are part of the target)

Notes:
- Prefer mapping directly from executable definitions, not broad proof surfaces.
- Keep bridge names stable; they become `TransitionRule.name` in the bridge IR.

## Next Steps

1. Identify the first physics-derived transition(s) to encode.
2. Record the FRACDASH-side mapping/template.
3. Run:
   `python3 scripts/agdas_bridge.py --emit-templates`
4. Run:
   `python3 scripts/toy_dashi_transitions.py --agdas-templates --json`

## Decided First Targets

The first bridge pass should target small executable dynamics, not the broad
proof-heavy closure tree. The decision here is to start from modules that
already expose concrete step-like functions and finite state updates.

### Priority 1 modules

- `../dashi_agda/Base369.agda`
- `../dashi_agda/LogicTlurey.agda`
- `../dashi_agda/Kernel/Algebra.agda`

Reason:
- these define explicit finite state carriers and deterministic updates
- they map naturally into the current signed `R1..R4` FRACTRAN model
- they are small enough to validate parity and basin behavior quickly

### Priority 2 modules

- `../dashi_agda/MonsterState.agda`
- `../dashi_agda/Monster/Step.agda`

Reason:
- these define a real deterministic `step`
- they likely matter for the later full bridge
- but they require a less toy state packing than the current trit-first model

### Validation / reference-only modules

- `../dashi_agda/ActionMonotonicity.agda`
- `../dashi_agda/DASHI_Tests.agda`

Reason:
- these are useful to explain invariants and expected monotonic behavior
- they are not the first annotation target because they do not add enough new
  executable transition content on their own

### Explicit non-targets for the first pass

- `../dashi_agda/DASHI/Physics/Closure/...`
- broad `Monster*` theorem/proof surfaces beyond `MonsterState` and `Monster/Step`
- mirror files like `all_dashi_agdas.txt`

Reason:
- too large
- too proof-oriented
- not yet in a stable transition vocabulary that fits the current FRACTRAN verifier

## Exact First Transition Names

These are the names the bridge notes reserve for the first FRACDASH-side templates.
They are ordered by implementation value.

### Wave 1: triadic carrier / stage cycle

- `tri_rotate_low_to_mid`
- `tri_rotate_mid_to_high`
- `tri_rotate_high_to_low`
- `stage_seed_to_counter`
- `stage_counter_to_resonance`
- `stage_resonance_to_overflow`
- `stage_overflow_to_seed`

These are implemented as bridge templates in `scripts/agdas_bridge.py` and can
be emitted with `--emit-templates --template-set wave1` or included in JSON via
`--include-templates --template-set wave1`.

### Wave 2: kernel polarity/involution

- `kernel_flip_neg_to_zero`
- `kernel_flip_zero_to_pos`
- `kernel_flip_pos_to_zero`
- `kernel_involution_neg_to_pos`
- `kernel_involution_pos_to_neg`
- `kernel_involution_zero_fixed`

Notes:
- `Kernel.Algebra.ι` is the more principled source here:
  `neg -> pos`, `pos -> neg`, `zero -> zero`
- the `flip_*_to_zero` names are only appropriate if a local bridge chooses a
  staged encoding through zero; otherwise omit them and keep the involution-only set

The involution set is also implemented as templates in `scripts/agdas_bridge.py`.

### Wave 3: monster-step seam

- `monster_choose_leftmost_admissible`
- `monster_step_advance_window`
- `monster_step_keep_mask`

Notes:
- these are intentionally higher-level seam names, not final parser-ready rule names
- they should only be implemented after the trit/stage pass is proven useful

The first compressed executable form of this seam now exists as the `wave2`
template set in `scripts/agdas_bridge.py`, emitted with
`--emit-templates --template-set wave2`.

## Register Mapping Decision

For the first bridge wave, use the current signed 4-register FRACTRAN state as:

- `R1`: primary triadic carrier or stage value
- `R2`: secondary triadic/control carrier
- `R3`: kernel polarity / admissibility summary
- `R4`: parity, overflow, or bookkeeping marker

This is intentionally a compression of the AGDA semantics. The goal of the
first bridge is not full fidelity; it is to establish an executable translation
path that preserves selected transition structure and admits parity checks.

## Priority Order / Constraints

1. Implement bridge transitions only where there is an actual executable update function.
2. Prefer finite cyclic or involutive transitions before mask/list-heavy state updates.
3. Keep names stable because they become bridge IR identifiers.
4. Do not start with the giant physics closure surface; get one small end-to-end
   executable bridge working first.
5. Treat `MonsterState` and `Monster/Step` as second-wave targets once the
   current 4-register state packing is no longer the bottleneck.
