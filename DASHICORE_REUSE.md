# dashiCORE Reuse Notes

## Summary

FRACDASH should reuse `../dashiCORE` by importing its host-side Vulkan helpers and shader assets by reference, not by copying files into this repo.

The current practical reuse target is **host/device plumbing**, not domain kernels:

- `gpu_common_methods.py`
- `gpu_vulkan_dispatcher.py`
- `gpu_vulkan_backend.py`
- `gpu_vulkan_adapter.py`
- `gpu_vulkan_gemv.py`
- shader/SPIR-V asset lookup from `gpu_shaders/` and `spv/`

The current non-targets are:

- CORE carrier/kernel semantics in `dashi_core/`
- PQ-specific storage/transport code
- vkFFT path unless FRACDASH later needs FFT specifically

## What Looks Reusable Now

### 1. Vulkan host-side plumbing

These files are the clearest immediate reuse candidates:

- `../dashiCORE/gpu_common_methods.py`
  - shader compilation
  - shader/SPIR-V path resolution
  - Vulkan memory helper utilities
- `../dashiCORE/gpu_vulkan_dispatcher.py`
  - Vulkan instance/device setup
  - buffer allocation and dispatch scaffolding
  - timestamp/query plumbing
- `../dashiCORE/gpu_vulkan_backend.py`
  - backend registration pattern
  - probe/register flow for optional Vulkan availability
- `../dashiCORE/gpu_vulkan_adapter.py`
  - adapter shape for keeping GPU code outside the pure core
- `../dashiCORE/gpu_vulkan_gemv.py`
  - useful as a worked example of a structured compute kernel wrapper

These are valuable even if FRACDASH does not reuse them unchanged, because they already encode the project’s Vulkan conventions and failure handling.

### 2. Shader asset layout

Useful existing asset locations:

- `../dashiCORE/gpu_shaders/`
- `../dashiCORE/spv/`

FRACDASH should not mirror these trees locally unless a kernel becomes broadly reusable and is intentionally upstreamed into CORE.

### 3. Integration guidance already written in dashiCORE

The most relevant existing design notes are:

- `../dashiCORE/CORE_TRANSITION.md`
- `../dashiCORE/SCALING_INFRA.md`
- `../dashiCORE/TESTING.md`
- `../dashiCORE/docs/dashibrain_core_integration.md`

These already support the “GPU helpers outside the pure core” approach, which matches FRACDASH’s needs.

## What Does Not Look Reusable Yet

### 1. Domain semantics

`dashi_core/` is about carrier/kernel/defect semantics for CORE itself. FRACDASH should not force FRACTRAN state evolution into those types just to claim reuse.

### 2. PQ and codec infrastructure

`pq.py`, `PQ_CODING.md`, and related shaders are not the right first abstraction for FRACTRAN execution. They may become relevant later for storage/transport, but not for the minimal GPU path.

### 3. FFT path

`gpu_vkfft_adapter.py` and `vkfft_vulkan_py*` are not on the critical path for FRACTRAN stepping. They should stay out unless FRACDASH later grows an FFT-shaped workload.

## Recommended Non-Duplicating Integration Shape

FRACDASH should add a **thin adapter layer** in this repo that imports from `../dashiCORE` at runtime.

Recommended approach:

1. Add one FRACDASH-local adapter module whose only job is to resolve and import the needed `../dashiCORE/gpu_*.py` helpers.
2. Keep all FRACDASH-specific state packing, dispatch metadata, and parity checks in this repo.
3. Treat shader paths as external assets passed by absolute/derived path into the reused CORE helpers.
4. If a FRACDASH shader becomes generally useful, upstream it into `dashiCORE` and switch FRACDASH to consume it there.

This gives:

- no duplicate Vulkan plumbing
- FRACDASH-specific execution semantics remain local
- clear path to upstream useful generic kernels later

Current FRACDASH bridge entrypoints:

- `gpu/dashicore_bridge.py`
- `scripts/check_dashicore_reuse.py`

The bridge inserts `../dashiCORE` onto `sys.path` at runtime and imports the reusable helper modules by their existing names. The smoke script proves that FRACDASH can resolve the external repo, import those helpers by reference, resolve shared shader/SPIR-V assets, and exercise the `VulkanBackendAdapter` passthrough path without copying CORE code.

For the first exact-step FRACTRAN GPU contract on top of that bridge, see `GPU_CONTRACT.md`. The key point is that exact FRACTRAN state is a dense exponent vector, not a `dashiCORE` ternary `Carrier`.

That contract now has a first real Vulkan step implementation:

- `gpu_shaders/fractran_step.comp`
- `gpu/vulkan_fractran_step.py`
- `scripts/check_fractran_vulkan_step.py`

## Proposed First Reuse Boundary

The first minimal GPU implementation should reuse:

- shader compilation/path resolution from `gpu_common_methods.py`
- Vulkan dispatch construction from `gpu_vulkan_dispatcher.py`

FRACDASH should provide locally:

- FRACTRAN state buffer layout
- one minimal step kernel contract
- exact-step parity harness against the compiled CPU baseline

## Upstreaming Rule

If FRACDASH produces a kernel/helper that is:

- not FRACTRAN-specific,
- useful for generic buffer math or dispatch,
- and stable enough to document,

then move it into `../dashiCORE` and keep FRACDASH consuming it by reference.

If a kernel is specific to FRACTRAN execution semantics, keep it in FRACDASH even if it uses CORE’s Vulkan plumbing.

Once the deterministic GPU routing rule is locked in (see `README.md` and `benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json` for the expanded matrix), the upstreaming trigger is simple: move any helper or adapter piece that is agnostic enough to document into `../dashiCORE`, then keep the FRACTRAN parser/contract here.
