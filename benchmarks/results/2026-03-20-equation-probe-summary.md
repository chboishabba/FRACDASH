# Named Equation Probe Summary

Date: `2026-03-20`

Artifacts:

- [`2026-03-20-equation-probe-wave.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-20-equation-probe-wave.json)
- [`2026-03-20-equation-probe-heat.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-20-equation-probe-heat.json)

## Current Result

- `wave` / Schrödinger-like probe: `mismatch_requires_fallback`
  - current DASHI-style balanced-ternary local dynamics do not look like a good direct solver path for the oscillatory/unitary target
  - the probe recommends `heat` as the next family
- `heat` / diffusion second shot: `qualitative_only`
  - switching from the earlier saturating sign-of-laplacian rule to a quantized explicit diffusion step materially improved the fit
  - current metrics are still short of a same-accuracy solver claim: `normalized_l2_error ~ 0.456`, `correlation ~ 0.917`, runtime roughly at parity/slightly slower than the transparent NumPy reference
  - this is good enough to keep `heat` as an interpretation-facing baseline probe, but not good enough to justify a solver-speed claim

## Practical Reading

- The first named-equation stress test did its job.
- The present bridge/execution stack looks much more naturally aligned with deterministic auditable execution and dissipative interpretation than with a direct wave-equation runtime win.
- One extra solver-speed shot improved the heat fit but did not produce a convincing runtime or accuracy win.
- The repo should now proceed primarily on the proof-carrying / auditable execution lane, while retaining `heat` as the least-bad named-equation comparison family if the solver track is revisited later.
