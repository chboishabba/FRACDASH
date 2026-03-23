# Cross-Carrier Baseline Summary

| Template | Carrier | States | Det. Edges | Terminal | Longest Chain | Fixed-Walk Cycle | Best Candidate | Geo Near-Min | Curvature Spread | Boundary->Interior |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: |
| `physics22` | `physics_local_6` | 729 | 476 | 365 | 32 | 290 | distance_to_cycle | 0.9206896551724137 | 1.9931412894375857 | 63 |
| `carrier8_physics1` | `physics_local_8` | 6561 | 2709 | 3852 | 12 | 2475 | action_rank | - | 0.0 | 0 |
| `carrier8_physics2` | `physics_local_8` | 6561 | 6561 | 0 | 10 | 6561 | action_rank | 0.990990990990991 | 0.7966101694915254 | 0 |
| `carrier8_physics3` | `physics_local_8` | 6561 | 6561 | 0 | 10 | 6561 | action_rank | 0.990990990990991 | 0.7966101694915254 | 0 |
| `carrier8_physics4` | `physics_local_8` | 6561 | 6561 | 0 | 10 | 6561 | action_rank | 0.990990990990991 | 0.7966101694915254 | 0 |
| `carrier8_physics5` | `physics_local_8` | 6561 | 6561 | 0 | 10 | 6561 | action_rank | 0.9913793103448276 | 0.7634069400630915 | 6 |
| `carrier8_physics6` | `physics_local_8` | 6561 | 6561 | 0 | 10 | 6561 | action_rank | 0.9893617021276596 | 0.9727891156462585 | 6 |

## Interpretation

- The active 6-register baseline remains easier to interpret: `physics22` combines strong direct re-entry with a still-disciplined recurrent core and a stable best-candidate signal.
- `carrier8_physics1` is useful mainly as an observable branch: it exposes boundary-return and transport/debt structure, but its current invariant surface is weaker and its best candidate is not aligned with the 6-register lane.
- `carrier8_physics2` is the stronger 8-register challenger: it has very strong cycle-bearing geometry and a full recurrent graph, but it is not yet directly comparable to `physics22` as a replacement baseline because its branch-local behavior is qualitatively different.
- `carrier8_physics3` does not yet move the carrier8 baseline meaningfully beyond `carrier8_physics2`; the added direct re-entry hook is currently too weak to change the main summary axes.
- `carrier8_physics4` still leaves the shared summary surface flat against `carrier8_physics2`, so the earlier re-entry hook is not yet strong enough to count as a branch handoff.
- `carrier8_physics5` is the first carrier8 branch to move boundary-to-interior recovery inside the sampled active basin by preempting the boundary discharge/join bottlenecks.
- `carrier8_physics6` does not yet change the shared cross-carrier surface beyond `carrier8_physics5`; if curvature stays low, `carrier8_physics2` remains the baseline.
- The 8-register lane should now be treated as a serious parallel experiment track, not just instrumentation, because `carrier8_physics2` already beats the 6-register baseline on at least one geometry surrogate.

## Branch-Local Observables

- `carrier8_physics1` boundary_return_profile = `{'deterministic_sources': {'negative': 21, 'zero': 104, 'positive': 52}, 'cycle_reachable_sources': {'negative': 0, 'zero': 0, 'positive': 0}}`
- `carrier8_physics1` transport_debt_profile = `{'deterministic_sources': {'negative': 50, 'zero': 71, 'positive': 56}, 'cycle_reachable_sources': {'negative': 0, 'zero': 0, 'positive': 0}}`
- `carrier8_physics2` boundary_return_profile = `{'deterministic_sources': {'negative': 19, 'zero': 177, 'positive': 56}, 'cycle_reachable_sources': {'negative': 7, 'zero': 78, 'positive': 26}}`
- `carrier8_physics2` transport_debt_profile = `{'deterministic_sources': {'negative': 56, 'zero': 132, 'positive': 64}, 'cycle_reachable_sources': {'negative': 26, 'zero': 67, 'positive': 18}}`
- `carrier8_physics3` boundary_return_profile = `{'deterministic_sources': {'negative': 19, 'zero': 177, 'positive': 56}, 'cycle_reachable_sources': {'negative': 7, 'zero': 78, 'positive': 26}}`
- `carrier8_physics3` transport_debt_profile = `{'deterministic_sources': {'negative': 56, 'zero': 132, 'positive': 64}, 'cycle_reachable_sources': {'negative': 26, 'zero': 67, 'positive': 18}}`
- `carrier8_physics4` boundary_return_profile = `{'deterministic_sources': {'negative': 19, 'zero': 177, 'positive': 56}, 'cycle_reachable_sources': {'negative': 7, 'zero': 78, 'positive': 26}}`
- `carrier8_physics4` transport_debt_profile = `{'deterministic_sources': {'negative': 56, 'zero': 132, 'positive': 64}, 'cycle_reachable_sources': {'negative': 26, 'zero': 67, 'positive': 18}}`
- `carrier8_physics5` boundary_return_profile = `{'deterministic_sources': {'negative': 19, 'zero': 177, 'positive': 61}, 'cycle_reachable_sources': {'negative': 7, 'zero': 78, 'positive': 32}}`
- `carrier8_physics5` transport_debt_profile = `{'deterministic_sources': {'negative': 58, 'zero': 134, 'positive': 65}, 'cycle_reachable_sources': {'negative': 29, 'zero': 69, 'positive': 19}}`
- `carrier8_physics6` boundary_return_profile = `{'deterministic_sources': {'negative': 16, 'zero': 159, 'positive': 58}, 'cycle_reachable_sources': {'negative': 7, 'zero': 56, 'positive': 32}}`
- `carrier8_physics6` transport_debt_profile = `{'deterministic_sources': {'negative': 56, 'zero': 107, 'positive': 70}, 'cycle_reachable_sources': {'negative': 29, 'zero': 40, 'positive': 26}}`
