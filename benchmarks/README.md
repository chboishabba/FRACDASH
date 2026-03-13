# Benchmarks

Initial FRACDASH benchmark artifacts live in `benchmarks/results/`.

Current baseline notes:

- The local `fractran/` checkout is the CPU reference implementation.
- `fractran-bench` exposes these engines for comparison:
  - `reg`
  - `frac-opt`
  - `cycle`
  - `compiled`
- The current `compiled` engine is a seam/prototype for exponent-vector execution, not yet a performance-optimized replacement.

Initial snapshot date:

- `2026-03-13`

Files captured so far:

- `2026-03-13-primegame-reg.txt`
- `2026-03-13-primegame-frac-opt.txt`
- `2026-03-13-primegame-compiled.txt`
