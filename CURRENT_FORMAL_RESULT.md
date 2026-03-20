# Current Formal Result

Status: `implemented`

## Theorem Split

- [`formalism/GenericMacroBridge.agda`](/home/c/Documents/code/FRACDASH/formalism/GenericMacroBridge.agda) is the structural, class-indexed bridge contract.
- [`formalism/BridgeInstances.agda`](/home/c/Documents/code/FRACDASH/formalism/BridgeInstances.agda) is the stronger numeric theorem layer for the currently closed slice family.

This split is intentional for the current phase. The generic layer fixes the reusable execution/realization shape. The master layer carries the stronger residual and transmutation inequalities for the currently closed family without asserting that those exact numeric choices belong in every future bridge instance.

## Structural Result

Across the current closed family, FRACDASH has:

- exact signed-IR compilation into paired-prime target execution
- deterministic unit-step normalization
- exact decode-back after macro execution
- structural well-formedness preservation at the paired-prime `Y` layer
- class-indexed regime witnesses for strict contraction and bounded transmutation

## Numeric Result

Across the currently closed family, the master theorem layer proves:

- target-relative residual decrease
- strict contraction
- bounded transmutation

The conservative slices are the zero-transmutation subregime:

- `physics1`
- `physics3`

The widened Batch C slices show that bounded transmutation is also regime-valid:

- `physics15`
- `physics19`
- `physics20`
- `physics21`
- `physics22`

## Current Bridge Claim

FRACDASH currently has a structural bridge contract at the generic layer and a stronger numeric theorem package for the closed slice family. Across the current closed family, exact paired-prime macro executions preserve well-formedness, satisfy target-relative residual decrease, and remain within the bounded conservative/transmuting regime taxonomy.

Conservative slices are the zero-transmutation special case. Widened Batch C slices show that bounded transmutation is also regime-valid.

## Not Claimed Here

This note does not claim:

- a fully numeric generic theorem inside `RegimeValidBridge`
- a proof that every future slice must use the same residual notion or numeric bounds
- any downstream physics interpretation beyond the current regime-valid bridge taxonomy
