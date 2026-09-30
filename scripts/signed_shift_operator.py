"""Exact finite signed translation algebra; NOT an RH analytic estimate.

A tap at integer j means (Shift(j*L) g)(u) = g(u-j*L).
Coefficients are rational; history records the *chosen* compilation path.
Nothing identifies SSP prime labels with Riemann von Mangoldt samples.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import log
from typing import Callable


@dataclass(frozen=True)
class SignedShiftOperator:
    taps: tuple[tuple[int, Fraction], ...]
    history: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if tuple(sorted(self.taps)) != self.taps:
            raise ValueError("taps must be sorted by shift")
        if len({j for j, _ in self.taps}) != len(self.taps):
            raise ValueError("duplicate shifts")
        if any(c == 0 or not isinstance(c, Fraction) for _, c in self.taps):
            raise ValueError("taps must be nonzero exact rationals")

    @classmethod
    def of(cls, entries, history=()) -> "SignedShiftOperator":
        total: dict[int, Fraction] = {}
        for shift, coefficient in entries:
            if not isinstance(shift, int):
                raise TypeError("shifts must be integer multiples of L")
            total[shift] = total.get(shift, Fraction(0)) + Fraction(coefficient)
        return cls(tuple(sorted((j, c) for j, c in total.items() if c)), tuple(history))

    @classmethod
    def identity(cls) -> "SignedShiftOperator":
        return cls.of([(0, 1)], ("identity",))

    @classmethod
    def shift(cls, j: int) -> "SignedShiftOperator":
        return cls.of([(j, 1)], (f"shift({j})",))

    def add(self, other: "SignedShiftOperator") -> "SignedShiftOperator":
        return self.of(self.taps + other.taps, self.history + ("add",) + other.history)

    def scale(self, coefficient) -> "SignedShiftOperator":
        c = Fraction(coefficient)
        return self.of(((j, c * v) for j, v in self.taps),
                       self.history + (f"scale({c})",))

    def compose(self, other: "SignedShiftOperator") -> "SignedShiftOperator":
        # Shift(a) after Shift(b) equals Shift(a+b).
        return self.of(((a+b, ca*cb) for a, ca in self.taps
                        for b, cb in other.taps),
                       self.history + ("compose",) + other.history)

    def apply(self, g: Callable[[float], float], u: float, L: float) -> float:
        if not L > 0:
            raise ValueError("L must be positive")
        return sum(float(c) * g(u - j*L) for j, c in self.taps)

    def exponential_symbol(self, z: complex, L: float) -> complex:
        """Eigenvalue on exp(z*u); the sign follows Shift(a)g(u)=g(u-a).

        Finite exact tap algebra; complex exponential evaluation is numerical.
        This is NOT the full Riemann explicit-formula response.
        """
        from cmath import exp
        if not L > 0:
            raise ValueError("L must be positive")
        return sum(float(c) * exp(-z*j*L) for j, c in self.taps)

    def support_envelope(self, R: float, L: float) -> tuple[float, float] | None:
        """If supp(g) subset (-R,R), output supported in union of shifted
        intervals. Returns a containing envelope (not its exact support)."""
        if R <= 0 or L <= 0:
            raise ValueError("R,L must be positive")
        if not self.taps:
            return None
        return (min(j*L-R for j, _ in self.taps),
                max(j*L+R for j, _ in self.taps))


def three_tap(epsilon) -> SignedShiftOperator:
    eps = Fraction(epsilon)
    return SignedShiftOperator.identity().add(
        SignedShiftOperator.shift(-1).add(
            SignedShiftOperator.shift(1)).scale(eps))


def compact_toy(u: float, R: float) -> float:
    """Compactly supported even bump, sampled numerically only."""
    if abs(u) >= R:
        return 0.0
    q = u/R
    return (1-q*q)**3


def trial(epsilon=Fraction(1, 20)) -> dict:
    L = log(2)
    # Explicitly narrower than (-L,L), not a claim about the RH source.
    R = 0.9 * L
    op = three_tap(epsilon)
    return {
        "taps": [(j, str(c)) for j, c in op.taps],
        "history": list(op.history),
        "support_envelope": op.support_envelope(R, L),
        "positive_samples": {
            n: op.apply(lambda u: compact_toy(u, R), log(n), L)
            for n in (2, 3, 4, 5)
        },
        "interpretation": "toy support/samples only; no RH sign result",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(trial(), indent=2))
