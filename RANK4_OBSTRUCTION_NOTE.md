# Rank-4 Obstruction Note (Empirical)

This note captures the rank-4 basin-geometry statement in research form.

Claim status:

- `observed experimentally`: rank-4 effective dimension and chain-height signal
- `conjectured`: specific Weyl/root-system identity

## Theorem-style empirical statement

Let `M in R^(10x15)` be the basin-prime matrix (10 basins, 15 primes in the
monster-walk coordinate system), and let `s : B -> R` be the basin stability
function.

Observed diagnostics:

1. Effective dimension:
   - PCA indicates an effective rank-4 structure (first four PCs dominate).
2. Chain height:
   - The longest monotone chain in the stability order has length `4`.
3. Independence:
   - PCA and chain-height computations are independent diagnostics and both
     indicate rank `4`.

Empirical conclusion:

- The basin system behaves as if controlled by a rank-4 latent structure.

## Interpretation (conjectural)

Natural candidate symmetry families are rank-4 root systems (`B4`, `D4`, `F4`)
with chamber-style geometry.

This note does **not** claim:

- exact Bruhat-order equivalence
- proven identification with `W(D4)`, `W(F4)`, or `W(B4)`
- direct Monster/moonshine identity

## Discriminator experiments

1. Root-length test (`D4` vs `F4`):
   - test single-scale vs two-scale adjacency distances in 4D embedding
2. Reflection-closure test:
   - fit four reflection hyperplanes and test closure on basin adjacency/Gram
3. Orbit-multiplicity test:
   - test repeated degeneracies as reflection orbits
4. Clifford reflection test:
   - extend rotor-only action with reflection sandwiches in the Clifford path
5. Stability-gradient chamber test:
   - test monotonicity inside chambers vs across chamber walls

## FRACDASH stance

This note is a research target, not a proven repository theorem.

Before promoting any conjectural part to an implemented claim, FRACDASH should
leave behind:

- script entrypoint(s)
- artifact path(s)
- reproducible pass/fail criteria
