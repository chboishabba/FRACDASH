# FRACDASH Devlog

## 2026-03-13

- Initialized repo memory around the DASHI-to-FRACTRAN objective.
- Resolved the primary conversation `Dashi and FRACTRAN Analysis`.
- Resolved and refreshed `Modern FRACTRAN Implementations`; noted the live thread was newer than the DB copy.
- Recorded the decision to treat `fractran/` as the CPU baseline and `../dashiCORE` as the external GPU helper source.
- Added `fractran-bench` and adjusted `fractran/build.sh` to compile dynamically on this machine.
- Added `fractran/src/Compiled.hs` as an explicit seam for compiled exponent-vector execution.
- Saved first benchmark artifacts under `benchmarks/results/`.
