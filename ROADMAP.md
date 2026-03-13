# FRACDASH Roadmap

## Goal

Use the checked-out [`fractran/`](/home/c/Documents/code/FRACDASH/fractran) project as the fast CPU baseline, then port the useful execution core toward a batched exponent-vector engine that can eventually reuse Vulkan and GEMV-oriented infrastructure from [`../dashiCORE`](/home/c/Documents/code/dashiCORE).

This roadmap assumes:

- CPU correctness and benchmark baselines come first.
- GPU work must justify itself with measured hotspots.
- Existing GPU plumbing in `../dashiCORE` should be referenced, adapted, or linked rather than duplicated.

## External Dependencies

### Local baseline

- [`fractran/README.md`](/home/c/Documents/code/FRACDASH/fractran/README.md)
- Likely implementation seam:
  - [`fractran/src/Fractran.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Fractran.hs)

### Existing GPU/Vulkan infrastructure

- [`../dashiCORE/gpu_common_methods.py`](/home/c/Documents/code/dashiCORE/gpu_common_methods.py)
- [`../dashiCORE/gpu_vulkan_dispatcher.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_dispatcher.py)
- [`../dashiCORE/gpu_vulkan_backend.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_backend.py)
- [`../dashiCORE/gpu_vulkan_gemv.py`](/home/c/Documents/code/dashiCORE/gpu_vulkan_gemv.py)
- [`../dashiCORE/CORE_TRANSITION.md`](/home/c/Documents/code/dashiCORE/CORE_TRANSITION.md)
- [`../dashiCORE/README.md`](/home/c/Documents/code/dashiCORE/README.md)

## Phases

### Phase 0: Benchmark Harness

Deliverable:
- reproducible CPU baseline against the checked-out `fractran/` interpreter

Tasks:
- identify how to run fixed FRACTRAN programs non-interactively
- create a benchmark set with fixed programs and fixed step budgets
- record throughput, step counts, and output parity

Artifacts:
- `benchmarks/`
- `results/`
- benchmark notes in repo docs

### Phase 1: Exponent-Vector CPU Engine

Deliverable:
- a second execution path that uses prime exponent vectors instead of raw big integers

Tasks:
- define prime basis extraction
- define rule representation as denominator exponents plus delta vector
- implement integer-state decode/encode parity tests against the baseline
- support batched state updates on CPU

Current status:
- A first compilation seam now exists in [`fractran/src/Compiled.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Compiled.hs).
- This prototype matches baseline outputs on sampled workloads but is not yet faster than `frac-opt`, so optimization should focus on data layout and rule compatibility checks rather than adding more abstraction.

### Phase 2: LUT and Batch Optimization

Deliverable:
- CPU batch engine using divisibility masks or LUT-driven rule selection

Tasks:
- prototype `mask -> rule` and possibly `mask -> delta` lookup
- benchmark scan-based versus LUT-based selection
- determine how many primes can stay in-cache before the table shape becomes unattractive

### Phase 3: FRACDASH Adapter To dashiCORE GPU Infrastructure

Deliverable:
- thin adapter layer that reuses `../dashiCORE` Vulkan helpers without vendoring them

Tasks:
- decide whether the cleanest mechanism is import-by-path, symlinked helper paths, or a small compatibility package
- keep shader compilation and dispatch logic outside the FRACTRAN semantics layer
- prove the adapter can launch at least one trivial batch update path

Constraint:
- do not copy `dashiCORE` helper modules into this repo unless the dependency boundary becomes unworkable

### Phase 4: Streaming GPU Engine

Deliverable:
- GPU batch execution for many independent states

Tasks:
- upload many states once
- run many FRACTRAN steps per transfer
- keep rule tables and metadata resident on device
- use fused or persistent kernels where the implementation cost is justified

Design rules:
- each worker owns one state trajectory
- shared GPU data stays read-only
- out-of-order execution is acceptable because work items are independent

### Phase 5: Heterogeneous Scheduling

Deliverable:
- deterministic CPU/GPU routing based on measured cost, not guesswork

Tasks:
- calibrate CPU and GPU throughput on this machine
- model transfer and launch overhead explicitly
- route small or single-orbit jobs to CPU
- route large batched orbit exploration to GPU

## Current Recommendation

Do not start by writing new Vulkan code in FRACDASH.

Start with:
1. benchmark harness around [`fractran/`](/home/c/Documents/code/FRACDASH/fractran)
2. exponent-vector prototype on CPU
3. only then a thin reuse layer over [`../dashiCORE`](/home/c/Documents/code/dashiCORE)
