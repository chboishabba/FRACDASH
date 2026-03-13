# Changelog

## 2026-03-13

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
