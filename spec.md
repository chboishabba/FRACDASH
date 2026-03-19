# FRACDASH Spec

## Objective

Build an executable bridge from DASHI-style balanced ternary dynamics to FRACTRAN, then use that bridge to run controlled experiments about reachability, basin structure, and translation invariants.

In parallel, run a separate solver-oriented probe lane that tests whether
DASHI-style local dynamics can compete with a named-equation reference solver on
a matched discrete problem.

## Problem Statement

The project is not to "argue that DASHI resembles FRACTRAN." It is to encode a concrete subset of DASHI behavior into FRACTRAN-compatible state transitions, then measure what survives and what fails.

## Scope

In scope:

- CPU-first FRACTRAN evaluation and benchmarking
- explicit signed-state encodings suitable for balanced ternary behavior
- parity checks between baseline FRACTRAN execution and alternative exponent-vector execution paths
- experiments on fixed-prime reachability and the 10-basin obstruction
- named-equation probe comparisons between transparent NumPy references and DASHI-style local dynamics
- reuse of external GPU infrastructure from `../dashiCORE` once CPU baselines are stable

Out of scope for the current phase:

- theorem-grade moonshine claims
- GPU-first implementation work before CPU hotspots are measured
- duplicating `../dashiCORE` GPU helper files inside this repo

## Inputs

- Archived thread `Dashi and FRACTRAN Analysis`
- Archived/live thread `Modern FRACTRAN Implementations`
- Local checked-out baseline interpreter in `fractran/`
- Local external GPU/Vulkan helper code in `../dashiCORE`

## Success Criteria

1. A documented minimal DASHI subset is chosen for translation.
2. At least one explicit signed encoding is implemented and benchmarked.
3. CPU benchmark artifacts are reproducible and stored in-repo.
4. The exponent-vector engine matches baseline outputs on selected workloads.
5. The next CPU optimization target is chosen using measured results, not guesswork.
6. The repo reaches a decision-quality answer about whether its strongest near-term value is solver speed, qualitative dynamics, or proof-carrying execution.

## Non-Goals

- proving DASHI implies Monster/moonshine structures
- early optimization work not backed by benchmark evidence
- ad hoc one-off scripts without recorded artifacts
