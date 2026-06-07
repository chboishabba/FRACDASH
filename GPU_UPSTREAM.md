# GPU Upstream Plan

## Gatekeeper

The routing evidence captured in
`benchmarks/results/2026-03-13-gpu-routing-matrix-extended.json` is a
host-local heuristic, not a portable binary gate. On this host the defensible
read is:

- default to CPU for tiny batches (`batch_size <= 4`)
- prefer GPU for warm resident batches in the consistently sampled region
  `batch_size >= 32 && steps >= 8`
- treat smaller or scenario-specific wins as measurement candidates, not
  project-wide gates

When the measured matrix continues to support those boundaries and `compiled`
remains the active CPU baseline, upstream reusable dispatch/adapter plumbing
instead of keeping it local to FRACDASH. Re-measure before using this heuristic
as a release or CI gate.

## Steps Before Upstreaming

1. Re-run `benchmarks/run_cpu_matrix.sh` (or targeted `fractran-bench` runs) whenever CPU code changes significantly to confirm `compiled` still matches `reg`, `frac-opt`, and the baseline parity contract.
2. Validate that the extended GPU routing artifacts still show the same hints when re-running `scripts/benchmark_fractran_gpu.py` with the same `--scenario`/`--batch-size`/`--steps` sweep.
3. Keep the Phase 2 CORE experiments advancing, using `scripts/toy_dashi_transitions.py` outputs as reproducible data for basin and fixed-prime explorations; do not touch GPU helpers until the gate is satisfied.

## Upstreaming Sequence

1. Identify helper modules that are not `FRACDASH`-specific:
   - `gpu_common_methods.py`
   - `gpu_vulkan_dispatcher.py`
   - `gpu_vulkan_backend.py`
   - `gpu_vulkan_adapter.py`
   - `gpu_vulkan_gemv.py`
   These already exist in `../dashiCORE` and already follow the project's Vulkan conventions.
2. Once the gate is open, port any FRACDASH improvements or stabilizations for those helpers into `../dashiCORE` (e.g., ping-pong descriptor handling, shader path lookups, buffer creation patterns).
3. After upstreaming, switch FRACDASH to import the upstreamed helpers via `gpu/dashicore_bridge.py` rather than keep local copies, ensuring the GPU contract stays FRACTRAN-specific.

## Post-Upstream Monitoring

- Continue capturing routing metrics so that the host-local heuristic remains defensible.
- Keep logging CPU baseline checkpoints (e.g., `benchmarks/results/2026-03-13-cpu-matrix.jsonl`) so GPU comparisons stay anchored to a known-good exact-step path.
