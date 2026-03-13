# FRACDASH Devlog

## 2026-03-13

- Initialized repo memory around the DASHI-to-FRACTRAN objective.
- Resolved the primary conversation `Dashi and FRACTRAN Analysis`.
- Resolved and refreshed `Modern FRACTRAN Implementations`; noted the live thread was newer than the DB copy.
- Recorded the decision to treat `fractran/` as the CPU baseline and `../dashiCORE` as the external GPU helper source.
- Added `fractran-bench` and adjusted `fractran/build.sh` to compile dynamically on this machine.
- Added `fractran/src/Compiled.hs` as an explicit seam for compiled exponent-vector execution.
- Saved first benchmark artifacts under `benchmarks/results/`.
- Expanded `fractran-bench` with scenario presets, logical-step mode, repeats, and JSONL output.
- Added `benchmarks/run_cpu_matrix.sh` and `benchmarks/summarize_cpu_matrix.py`.
- Ran the CPU matrix across `mult_smoke`, `primegame_small`, `primegame_medium`, and `primegame_large`.
- Verified parity for `reg`, `frac-opt`, and `compiled` across the matrix.
- Recorded the benchmark-backed next target: CPU LUT/divisibility-mask work.
- Hardened the benchmark contract by adding explicit checkpoint policy semantics.
- Fixed `mult_smoke` to use its real exact logical-step target (`2`) so the matrix no longer contains invalid runs.
- Re-ran the canonical matrix and confirmed the corrected artifact set still points to LUT/divisibility-mask CPU work.
- Implemented a binary-threshold LUT path in `fractran/src/Compiled.hs` and exposed it as the `lut` engine in `fractran-bench`.
- Fixed a strictness bug in the LUT runner so benchmark checkpoints stream lazily instead of forcing the entire execution.
- Verified that `lut` matches exact-step parity on `mult_smoke` and `primegame_*`, and that it rejects `hamming` as incompatible because `hamming` requires denominator thresholds greater than `1`.
- Re-ran the canonical matrix with `lut` included and recorded the result that `frac-opt` remains the practical CPU baseline.
- Parked LUT as a completed side experiment and pivoted the active optimization track back to compiled-path tuning.
- Added explicit CPU-to-GPU handoff criteria so `../dashiCORE` integration does not begin before CPU work has genuinely flattened out.
- Ported `frac-opt`-style rule-order narrowing into the compiled evaluator and reran the canonical matrix without `lut` in the active set.
- Verified that parity still holds and that the updated summary now routes to `continue compiled-path tuning`.
- Added a compiled-specific benchmark summary path that keeps compiled states as exponent vectors until checksum/hash evaluation instead of decoding every step to `IntMap`.
- Re-ran the canonical matrix and measured `compiled` ahead of `frac-opt` on `primegame_small`, `primegame_medium`, and `primegame_large`.
- Installed the host GHC static profiling package and updated `fractran/build.sh --profile` to use static profiling on this machine.
- Ran real cost-centre profiling on `compiled` for `primegame_medium` and `primegame_large`, with RTS comparison runs against `frac-opt`.
- Confirmed that compiled profiling is dominated by benchmark-side `unfExpVec`/checksum work, with `applyRule` the largest remaining engine-side hotspot and rule matching smaller.
- Rewrote `applyRule` to use element-wise zipping over the compiled state and rule delta instead of repeated array indexing in the hot path.
- Added direct integer-value tracking to the compiled benchmark trace so checksum generation no longer reconstructs every emitted state with `unfExpVec`.
- Re-ran the canonical matrix and confirmed `compiled` now leads `frac-opt` on `primegame_small`, `primegame_medium`, and `primegame_large`.
- Declared the compiled path the active exact-step CPU baseline and pivoted the next milestone toward the minimal GPU path.
- Audited `../dashiCORE` for actual FRACDASH reuse candidates and documented a non-duplicating integration boundary centered on `gpu_common_methods.py`, `gpu_vulkan_dispatcher.py`, `gpu_vulkan_backend.py`, `gpu_vulkan_adapter.py`, and `gpu_vulkan_gemv.py`.
- Documented the rule that generic helpers should be upstreamed back into `dashiCORE`, while FRACTRAN-specific kernels remain local to FRACDASH.
