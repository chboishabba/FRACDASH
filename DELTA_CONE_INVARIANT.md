# Δ-Cone Invariant (Execution vs. Source)

Status: `2026-03-23`

Purpose: keep execution inside the source-attractor cone by testing deltas, not absolute states.

Runtime rule (enforced optionally via `physics_invariant_analysis.py --enforce-delta-cone`):

```
Given states s, s'
Δ = s' - s
π = projection (drop registers or multiply by user matrix; current hook supports drop only)
Q(Δ) = Σ_i w_i * (Δ_i)^2   (default: all w_i = -1)
Reject edge if Q(π(Δ)) > 0
```

Guidance:
- Drop time/arrow-like coordinates from the cone check.
- Choose an indefinite metric (e.g., Minkowski - + +) or a strict contraction metric (all -1) depending on the experiment.
- Treat Q as a *delta-cone* compatibility test, not a global Lyapunov descent.

Next Agda sketch (to be formalized):
1. Define `ΔState` over the carrier with projection `π`.
2. Define cone predicate `ConeQ Δ = Q (π Δ) ≤ 0`.
3. For each transition `τ`, prove `ConeQ (Δτ)`; compose to traces.
4. Expose a witness that execution preserves the cone: `execCone : ∀ trace. All ConeQ (Δ trace)`.

Notes:
- This aligns with the ZKP alignment requirement: compare `Δtrace` inside the projected cone; do not test `j_fixed(trace)` directly.
- For quick offline checks, use `scripts/compute_delta_cone_signature.py` on deterministic-walk artifacts.
