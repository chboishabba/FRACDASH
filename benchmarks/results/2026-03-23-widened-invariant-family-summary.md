# Widened Invariant Family Summary

| Template | Regime Usage | Det. Edges | Terminal | Longest Chain | Boundary->Interior | Geo Near-Min | Curvature Spread | Best Candidate |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| `physics15` | mixed (transmuting on r2=+2 deltas) | 220 | 509 | 22 | - | 0.9072164948453608 | 1.6333333333333333 | distance_to_cycle |
| `physics19` | mixed (transmuting on r2=+2 or r2=-1 deltas) | 274 | 455 | 32 | - | 0.9094488188976378 | 1.8257887517146776 | distance_to_cycle |
| `physics20` | mixed (transmuting on r2=+2 or r2=-1 deltas) | 301 | 428 | 32 | - | 0.9181494661921709 | 1.9272976680384089 | distance_to_cycle |
| `physics21` | mixed (transmuting on r2=+2 or r2=-1 deltas) | 310 | 419 | 32 | 9 | 0.9206896551724137 | 1.9931412894375857 | distance_to_cycle |
| `physics22` | mixed (transmuting on r2=+2 or r2=-1 deltas) | 364 | 365 | 32 | 63 | 0.9206896551724137 | 1.9931412894375857 | distance_to_cycle |

## Interpretation

- Highest direct boundary-to-interior re-entry is `physics22` with `63`.
- Largest deterministic recurrent core is `physics22` with `364` edges.
- Mixed transmuting usage coexists with strong geometry-surrogate values; widened slices should be read through regime usage, not against the conservative-only lock.
