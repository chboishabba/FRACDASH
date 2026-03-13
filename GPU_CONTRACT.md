# FRACDASH GPU Contract

## Summary

The first honest FRACDASH GPU contract is **not** a `dashiCORE` `Carrier`.

`Carrier` is balanced ternary and forbids support creation. Exact-step FRACTRAN state is instead a dense exponent vector over the compiled prime basis, so the local GPU contract must stay FRACTRAN-specific even while reusing `../dashiCORE` Vulkan plumbing.

Current local implementation:

- `gpu/fractran_layout.py`
- `scripts/check_fractran_gpu_layout.py`

## State Layout

Per state:

- `exponents: int32[prime_count]`

Interpretation:

- `exponents[i]` is the exponent of `primes[i]` in the current integer state
- zero means the prime is absent
- positive values are required for the current exact-step workloads

This layout matches the current compiled CPU baseline in `fractran/src/Compiled.hs`.

## Rule Layout

Per rule:

- `den_thresholds: int32[prime_count]`
- `delta: int32[prime_count]`
- `required_mask: uint32`
- `numerator_value: integer`
- `denominator_value: integer`

Semantics:

1. A rule applies when `state >= den_thresholds` element-wise.
2. The next state is `state + delta`.
3. The tracked integer value updates as:
   - `next_value = current_value * numerator_value / denominator_value`

The current parity smoke uses `required_mask` only as derived metadata for future GPU-side rule screening. Exact applicability is still the threshold check.

## Dense Buffer Set

The current local contract exports the following GPU-oriented buffers:

- `primes: int32[prime_count]`
- `den_thresholds: int32[rule_count, prime_count]`
- `deltas: int32[rule_count, prime_count]`
- `required_masks: uint32[rule_count]`
- `numerator_values: object[rule_count]`
- `denominator_values: object[rule_count]`

The object-typed value arrays are fine for the current CPU contract proof. A real shader path will need fixed-width scalar choices for device-side arithmetic or a different host-side value-tracking strategy.

## What Is Proven

The current parity smoke:

- loads `primegame` and `mult` directly from `fractran/src/Demo.hs`
- compiles them into the dense layout above
- executes the dense threshold/delta contract on CPU
- compares the resulting checksum and final-state hash against `fractran-bench --engine compiled`

The current Vulkan smoke:

- compiles `gpu_shaders/fractran_step.comp`
- dispatches one exact FRACTRAN step on the host GPU through `gpu/vulkan_fractran_step.py`
- compares the selected rule index and next exponent vector against the dense CPU contract

The current batched Vulkan smoke:

- dispatches a flattened `state_count x prime_count` exponent buffer
- writes one selected-rule / halt pair per state
- matches the dense CPU contract across every slot in the tested batch

Current proven scenarios:

- `mult_smoke`
- `primegame_small`

Current proven execution shapes:

- single-state one-step dispatch
- batched one-step dispatch
- batched multi-step device-resident dispatch
- batched multi-step device-resident dispatch recorded into a single command buffer submission
- measured resident GPU throughput advantage on `primegame_small` for batches `32`, `128`, and `512` at `32` exact steps

## Reuse Boundary

Use `../dashiCORE` for:

- Vulkan instance/device setup
- shader compilation/path resolution
- dispatch and buffer plumbing

Keep local to FRACDASH:

- FRACTRAN exponent-vector state
- FRACTRAN rule thresholds and deltas
- exact-step parity logic
- any FRACTRAN-specific kernels

## Next Step

The first minimal Vulkan kernel interface now exists:

- shader: `gpu_shaders/fractran_step.comp`
- host runner: `gpu/vulkan_fractran_step.py`
- smoke entrypoint: `scripts/check_fractran_vulkan_step.py`

Immediate next expansion:

- the routing benchmark now spans `primegame_small`, `mult_smoke`, `paper_smoke`, and `hamming_smoke` over `batch_size = 4, 16, 32, 64, 128` and `steps = 4, 8, 16`, producing `benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json` so the `measure-more` band can be replaced with the deterministic rule in README
- decide whether tracked integer values stay on host or gain a device-side fixed-width representation
- preserve the current exact-step parity harness while moving toward real CPU/GPU routing decisions

Once the routing rule stabilizes, the next GPU helper upstream step is to fold any general-purpose dispatch/adapter helpers back into `../dashiCORE` while keeping the FRACTRAN-specific state layout local to FRACDASH.
