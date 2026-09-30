"""Two-prime phase experiment for a signed nonlocal *toy* detector.

Conventions:
- L=log 2, centered real even compactly supported toy g;
- the three tap translates g_eps reach only n=2,3 (n>=4 vanish);
- cosine phase parameter theta represents s-t in the Zeta23 first-prime
  sample, but the total expression is NOT the complete explicit formula.
- coefficients use Lambda(n)/sqrt(n) and the factor 2 for two log signs.
"""
from __future__ import annotations

from fractions import Fraction
from math import cos, log, pi, sqrt
from scripts.signed_shift_operator import compact_toy, three_tap


def prime_coefficient_data(epsilon=Fraction(1, 20), relative_radius=0.9):
    L = log(2)
    R = relative_radius * L
    if not 0 < R < L:
        raise ValueError("need 0<R<log(2)")
    g = lambda u: compact_toy(u, R)
    op = three_tap(epsilon)
    a = 2 * L / sqrt(2) * op.apply(g, L, L)
    b = 2 * log(3) / sqrt(3) * op.apply(g, log(3), L)
    return a, b


def two_prime_cosine(theta, a, b):
    return a * cos(theta * log(2)) + b * cos(theta * log(3))


def experiment():
    a, b = prime_coefficient_data()
    positive = two_prime_cosine(0, a, b)
    negative = two_prime_cosine(pi/log(2), a, b)
    return {
        "two_prime_amplitudes": {"n2": a, "n3": b},
        "dominance_certificate": a > abs(b),
        "phase_zero_response": positive,
        "phase_pi_over_log2_response": negative,
        "phase_sign_flips": positive > 0 > negative,
        "interpretation": (
            "two-prime toy cosine channel, NOT completed Zeta23 and "
            "NOT an RH terminal gain"
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(experiment(), indent=2))
