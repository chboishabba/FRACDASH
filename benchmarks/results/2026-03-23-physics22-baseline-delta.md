# Physics22 Baseline Delta

- Baseline comparison: `physics21` -> `physics22`

## Delta

- Transition count: `35 -> 36` (`delta = 1`)
- Deterministic edges: `395 -> 476` (`delta = 81`)
- Terminal states: `419 -> 365` (`delta = -54`)
- Longest chain: `32 -> 32` (`delta = 0`)
- Boundary->interior count: `9 -> 63` (`delta = 54`)
- Boundary->interior ratio: `0.02903225806451613 -> 0.17307692307692307` (`delta = 0.14404466501240695`)
- Geodesic near-min ratio: `0.9206896551724137 -> 0.9206896551724137`
- Curvature spread: `1.9931412894375857 -> 1.9931412894375857`

## Stable

- Best invariant candidate: `distance_to_cycle -> distance_to_cycle`
- Fixed-walk cycle count: `290 -> 290`
- Fixed-walk terminal count: `439 -> 439`
- Fixed-walk timeout count: `0 -> 0`
- Geodesic exact-min ratio: `0.4482758620689655 -> 0.4482758620689655`

## Interpretation

- The physics22 gain over physics21 is primarily a deterministic recurrent-core and re-entry gain, not a change in the fixed-walk cycle/terminal split.
- The main new effect is stronger direct boundary-to-interior reinjection while keeping the current geometry-surrogate values flat at the physics21 level.
- This makes physics22 a better comparison baseline for the next 6-register branch than physics21, because the gain is concentrated in the deterministic recurrent core where future refinements should compete.
