# Signed shift-operator experiment (independent of RH-worker branch)

Status: **implemented finite operator algebra; not an RH estimate**.

Source inspiration: DASHI signed SSP/FRACTRAN indexed composition and the
separate Lean RH three-tap detector. This experiment introduces **explicit**
analytic semantics for operator words rather than interpreting FRACTRAN prime
addresses as the primes in the Riemann explicit formula.

A finite word is a Laurent polynomial in a translation operator:
`K = sum_{j in Z} c_j Shift(j*L)`, `c_j in Q`,
where `Shift(a) g(u) = g(u-a)`. Its representation contains *both*
its normal form and an ordered history of named generating operations.
Composition is exact rational convolution of tap lists. Two histories
can produce the same operator: provenance is intentionally retained.

The three-tap example is `Identity + epsilon * (Shift(1) + Shift(-1))`.
For `L=log(2)` and a function supported in `(-L,L)`, this model:
- can sample at `log(2)` with value `epsilon*g(0)`;
- can sample at `log(3)` with value `epsilon*g(log(3/2))`;
- is zero at prime-power logs `log(n)` for integers `n>=4`.

The mathematical *support* claim follows from the support of translated
functions, not from floating-point sampling. The script only *tests*
those identities for a chosen compactly supported toy function.

Invariants: exact tap coefficients, associativity of composition,
distributivity, identity, and provenance history. No change of real
spectral/Gamma/pole functional is constructed in this repository.
An external RH producer must supply its actual detector, normalization,
and completed explicit-formula response independently.

Reproduce: `python3 -m unittest scripts.test_signed_shift_operator`.
Run demonstration: `python3 scripts/signed_shift_operator.py`.
