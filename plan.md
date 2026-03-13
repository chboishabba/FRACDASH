# FRACDASH Plan

## Current Phase

Phase 1: CPU-side seam extraction and exponent-vector validation

## Milestones

### Milestone A: Baseline harness

Status: completed

- non-interactive benchmark CLI exists
- baseline artifacts are stored
- local build works on this machine

### Milestone B: Compiled seam prototype

Status: in progress

- explicit compiled representation exists
- sampled parity checks succeeded
- optimization target is still open

### Milestone C: CPU optimization loop

Status: pending

- compare `compiled`, `reg`, `frac-opt`, and `cycle` over a wider benchmark set
- tighten compiled path data layout
- decide whether LUT work or further compiled-path cleanup is next

### Milestone D: GPU reuse adapter

Status: pending

- define how FRACDASH references `../dashiCORE`
- prove one trivial dispatch path
- keep state movement and semantics isolated

## Immediate Next Actions

1. Expand the benchmark set beyond the current `primegame` snapshot.
2. Add result capture for multiple engines and workloads in a stable format.
3. Profile or at least structurally inspect the compiled path for avoidable overhead.
4. Decide whether the next code change is LUT-oriented or data-layout-oriented.

## Risks

- Benchmarks may be too noisy or too narrow to guide optimization well.
- The compiled path may add abstraction cost without enough structural gain.
- GPU reuse may become messy if the boundary to `../dashiCORE` is not explicit.
