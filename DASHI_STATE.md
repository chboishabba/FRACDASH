# Minimal DASHI State Space

## Overview

The current experiment uses a fixed-length signed-ternary register tuple:

- `R1`, `R2`, `R3`, `R4`
- each register value is in `{ -1, 0, +1 }`

This keeps the state space intentionally small (`3^4 = 81`) while still representing a nontrivial signed transition system.

## FRACTRAN Encoding

Each register has three dedicated primes:

- **negative** state
- **zero** state
- **positive** state

Current prime assignment is:

- `R1`: `2, 3, 5`
- `R2`: `7, 11, 13`
- `R3`: `17, 19, 23`
- `R4`: `29, 31, 37`

Given a signed vector `(v1, v2, v3, v4)`, the encoded FRACTRAN state is:

- multiply by exactly one prime from each register’s triple according to each `vi`.

Example:

- `(+1, 0, 0, 0)` encodes as `3 * 7 * 17 * 29`.

The `3^4` injective map is implemented in:

- [`scripts/toy_dashi_transitions.py`](/home/c/Documents/code/FRACDASH/scripts/toy_dashi_transitions.py)

`decode_signed_state(...)` performs the inverse mapping and is used to validate full-space round-trip correctness.

## Current Experiment Coverage

- signed encoder / decoder correctness over all `81` states
- deterministic one-step transition matching
- basin walk and fixed-prime trajectory summaries over the same encoded space

This state space is intentionally minimal and local to FRACDASH for now; reusable Vulkan plumbing is still intended to remain in `../dashiCORE` via `gpu/dashicore_bridge.py`.
