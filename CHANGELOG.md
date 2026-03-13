# Changelog

## 2026-03-13

- Added a top-level [`README.md`](/home/c/Documents/code/FRACDASH/README.md) summarizing the repo mission, current CPU-first status, benchmark workflow, structure, and guardrails.
- Initialized repo-facing project memory for FRACDASH.
- Added [`AGENTS.md`](/home/c/Documents/code/FRACDASH/AGENTS.md) to define the mission, guardrails, and experiment priorities.
- Added [`COMPACTIFIED_CONTEXT.md`](/home/c/Documents/code/FRACDASH/COMPACTIFIED_CONTEXT.md) with resolved conversation metadata and current project truth.
- Added [`TODO.md`](/home/c/Documents/code/FRACDASH/TODO.md) to capture the initial execution queue for the DASHI-to-FRACTRAN work.
- Added implementation-planning notes from `Modern FRACTRAN Implementations`, clarifying that FRACDASH should begin with CPU-first benchmarking and only treat GPU execution as a later, measurement-driven optimization.
- Recorded that the fast interpreter now lives in [`fractran/`](/home/c/Documents/code/FRACDASH/fractran) and that FRACDASH should prefer referencing `../dashiCORE` GPU/Vulkan helpers instead of duplicating them.
- Added [`ROADMAP.md`](/home/c/Documents/code/FRACDASH/ROADMAP.md) with a repo-specific port plan from the local CPU baseline to a reused-GPU-infrastructure path.
- Added a first non-interactive benchmark path in [`fractran/src/Bench.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Bench.hs) and [`fractran/src/bench_main.hs`](/home/c/Documents/code/FRACDASH/fractran/src/bench_main.hs), and updated [`fractran/build.sh`](/home/c/Documents/code/FRACDASH/fractran/build.sh) to build dynamically by default on this machine.
- Added an explicit compilation seam in [`fractran/src/Compiled.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Compiled.hs) and exposed a `compiled` benchmark engine so the current evaluator can be compared against a reusable exponent-vector representation.
- Added initial benchmark artifacts under [`benchmarks/results/`](/home/c/Documents/code/FRACDASH/benchmarks/results) and recorded that the new compiled path currently matches sampled outputs but does not yet beat `frac-opt`.
- Added canonical GSD planning documents: [`spec.md`](/home/c/Documents/code/FRACDASH/spec.md), [`architecture.md`](/home/c/Documents/code/FRACDASH/architecture.md), [`plan.md`](/home/c/Documents/code/FRACDASH/plan.md), [`status.md`](/home/c/Documents/code/FRACDASH/status.md), and [`devlog.md`](/home/c/Documents/code/FRACDASH/devlog.md).
- Expanded the benchmark harness with scenario presets, logical-step execution, repeats, and JSONL output, and added CPU matrix runner/summary tooling under [`benchmarks/`](/home/c/Documents/code/FRACDASH/benchmarks).
- Ran the CPU matrix and saved artifacts in [`benchmarks/results/2026-03-13-cpu-matrix.jsonl`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix.jsonl) and [`benchmarks/results/2026-03-13-cpu-matrix-summary.json`](/home/c/Documents/code/FRACDASH/benchmarks/results/2026-03-13-cpu-matrix-summary.json).
- Recorded the benchmark-backed next optimization target as LUT/divisibility-mask CPU work.
- Hardened the benchmark contract with explicit checkpoint policies, corrected `mult_smoke` to a valid exact logical-step target, and regenerated the canonical CPU matrix artifacts under the corrected semantics.
- Added a binary-threshold LUT execution path in [`fractran/src/Compiled.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Compiled.hs) and exposed it through the `lut` engine in [`fractran/src/Bench.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Bench.hs).
- Fixed a LUT runner strictness bug that was preventing benchmark checkpoint streaming.
- Re-ran the canonical CPU matrix with `lut` included; parity held, `hamming` remained intentionally incompatible with the v1 LUT design, and the summary now keeps `frac-opt` as the practical CPU baseline.
- Parked the LUT path as a completed experiment, promoted compiled-path tuning to the active CPU optimization track, and documented explicit CPU-to-GPU handoff criteria.
- Ported `frac-opt`-style rule-order narrowing into [`fractran/src/Compiled.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Compiled.hs), updated the active benchmark matrix to focus on `reg`/`frac-opt`/`cycle`/`compiled`, and regenerated the canonical summary so the next target now resolves to continued compiled-path tuning.
- Added a compiled-specific benchmark summary path in [`fractran/src/Bench.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Bench.hs) so compiled runs stay in exponent-vector form until checksum/hash evaluation, then regenerated the canonical matrix and summary with `compiled` ahead of `frac-opt` on the sampled `primegame` scenarios.
- Updated [`fractran/build.sh`](/home/c/Documents/code/FRACDASH/fractran/build.sh) so `--profile` uses static profiling on this host, enabling real GHC cost-centre profiling after installing `ghc-static`.
- Ran the final profiling-driven CPU pass and recorded that compiled-run cost is currently dominated by benchmark-side `unfExpVec`/checksum work, with `applyRule` the largest engine-side hotspot and rule selection materially smaller.
- Rewrote [`Compiled.applyRule`](/home/c/Documents/code/FRACDASH/fractran/src/Compiled.hs) to use element-wise zipping instead of repeated array indexing, then regenerated the canonical matrix with improved compiled timings.
- Updated the compiled benchmark path in [`fractran/src/Bench.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Bench.hs) and [`fractran/src/Compiled.hs`](/home/c/Documents/code/FRACDASH/fractran/src/Compiled.hs) to track emitted integer values directly, removing the dominant `unfExpVec` checksum overhead.
- After two additional profiling-guided CPU rounds, promoted `compiled` to the active exact-step CPU baseline and pivoted the next milestone toward minimal GPU implementation.
- Added [`DASHICORE_REUSE.md`](/home/c/Documents/code/FRACDASH/DASHICORE_REUSE.md) to document which `../dashiCORE` modules are actually reusable for FRACDASH, what should stay local, and how to integrate without duplicating code.
