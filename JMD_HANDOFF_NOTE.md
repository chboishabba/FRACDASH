# JMD Handoff Note

Status date: `2026-03-20`

This note is the short handoff for the current FRACDASH bridge/result state and for the still-open 10-walk / rank-4 semantics question.

## What Is Established In FRACDASH

For the currently closed bridge family, FRACDASH now has:

- exact paired-prime macro realization
- well-formedness preservation
- strict contraction
- bounded transmutation
- stable regime taxonomy

Current regime split:

- `physics1`, `physics3` = `conservative_contracting`
- `physics15`, `physics19`, `physics20`, `physics21`, `physics22` = widened `regime-valid` family with bounded transmutation

Current active exploratory baseline:

- `physics22` is the leading 6-register branch on the widened-family summary
  axes currently tracked in-repo:
  - largest deterministic recurrent core in the widened family
  - lowest terminal-state count in the widened family
  - strongest direct `boundary -> interior` re-entry currently observed on the
    6-register lane

The important change is:

- conservation is not the universal bridge invariant
- conservation is the zero-transmutation special case
- the wider valid bridge claim is strict contraction plus bounded transmutation
- physics-facing interpretation docs are now being aligned to that split, so the
  old conservation-only framing should be treated as a conservative-subregime
  description rather than the universal bridge frame

Repo-facing summary:

- structural bridge contract: [formalism/GenericMacroBridge.agda](/home/c/Documents/code/FRACDASH/formalism/GenericMacroBridge.agda)
- stronger numeric family theorem: [formalism/BridgeInstances.agda](/home/c/Documents/code/FRACDASH/formalism/BridgeInstances.agda)
- short result statement: [CURRENT_FORMAL_RESULT.md](/home/c/Documents/code/FRACDASH/CURRENT_FORMAL_RESULT.md)

## GPU / FRACTRAN Execution Note

FRACDASH is also carrying a GPU path, but the current stance is still:

- FRACTRAN is the auditable execution target
- CPU remains the first exact benchmark baseline
- GPU support is being added as an execution optimization layer, not as a change to the bridge semantics

So if the wider stack is already running directly on FRACTRAN, that is compatible with the current FRACDASH direction. The intended layering is:

- bridge semantics and proofs stay at the signed-IR / paired-prime realization level
- CPU FRACTRAN execution stays the correctness baseline
- GPU FRACTRAN execution is added underneath as a performance path once parity and routing stay stable

In other words: the bridge/result story does not depend on GPU, but the stack is being prepared so a FRACTRAN-first execution model can still pick up GPU acceleration later without changing the theorem surface.

## What The `physics15` Fork Meant

The key rule was:

- `physics15_boundary_crossfeed_neutral`

It breaks the old `R1/R2` conservation package while preserving:

- macro soundness
- exact decode-back
- strict contraction
- paired-prime exclusivity
- bounded transmutation

So this is now treated as intended widened semantics, not a bridge bug.

## What Is Established About The 10-Walk

FRACDASH has an executable, reproducible 10-walk lock:

- canonical lock artifact:
  - [benchmarks/results/2026-03-15-monster10walk-canonical.json](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-15-monster10walk-canonical.json)
- canonical semantics note:
  - [MONSTER10WALK_CANONICAL.md](/home/c/Documents/code/FRACDASH/MONSTER10WALK_CANONICAL.md)

What is currently supported:

- the canonical 10-node walk topology is locked as executable data
- FRACDASH transition-data derivations from `physics8|physics9` support that canonical adjacency under strict lock
- the executable chain/rank proxy on the locked artifact is `4`

This is enough to say:

- the extracted/canonical dataset exhibits a max-chain / rank proxy of `4`

## What Is Not Yet Established About The 10-Walk

This stronger claim is not yet closed:

- that the 10-node edge set is the complete true transition semantics of the full formal stack
- that the Lean-side theorem surface is fully closed with no remaining `sorry` / `axiom`
- that the rank-4 reading is already identified with a specific root system (`D4`, `F4`, etc.)

So the current status is:

- computationally proven for the locked extracted/canonical dataset
- not yet semantics-complete for the full upstream formal stack

## Clean Claim Boundary

Safe current statement:

> FRACDASH has a closed bridge family with exact paired-prime macro realization, strict contraction, and bounded transmutation. Separately, the locked canonical 10-walk dataset exhibits a rank/chain proxy of `4`. That is evidence for a rank-4 obstruction story at the dataset level, but not yet a completed theorem identifying the full formal semantics with a specific rank-4 root/Weyl object.

Unsafe current statement:

- “FRACDASH proves the Monster bridge”
- “the full formal stack is already D4/F4/E8”
- “the 10-walk rank-4 story is theorem-complete”

## Practical Next Questions For JMD

If the aim is to connect the current FRACDASH bridge results to the 10-walk / rank-4 story, the useful questions are:

1. Which exact edge policy should count as the true 10-walk semantics, beyond the current locked extracted dataset?
2. Which remaining Lean files or theorem surfaces still block claiming semantics-complete closure?
3. Is the right next discriminator for the rank-4 reading:
   - triality-like symmetry (`D4`)
   - short/long root splitting (`F4`)
   - or something weaker that should stay at “rank-4 obstruction” only?
4. Which currently observed bridge quantities should be mapped into the 10-walk story:
   - conservative vs transmuting regime split
   - strict contraction / residual descent
   - basin-side rank/chain statistics

## Bottom Line

FRACDASH is now in a good handoff state:

- the bridge side is frozen enough to stop redesigning it
- the theorem split is explicit and stable
- the 10-walk side is computationally real but still needs semantics-complete closure before making stronger root-system or moonshine claims
