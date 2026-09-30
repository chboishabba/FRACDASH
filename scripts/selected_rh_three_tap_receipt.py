"""Executable receipt for the *actual selected RH detector* three-tap theorems.

Authority: chboishabba/dashi_lean4 PR #22, source-native Lean theorem surface.
This module does NOT reimplement the physical bump detector. It executes only
closed formulas already proved about that detector, so FRACDASH cannot drift
from the analytic authority by substituting a toy taper.

At t >= 200:
  * the shifted n=3 sample is exactly zero;
  * all n>=4 prime-power samples are zero;
  * g(0) = 2 * (quarticWindowMass R)^(-1);
  * the even-cone prime channel is a single n=2 frequency;
  * the pole-weighted projective prime response has the common-centre formula.

The zero/Gamma/pole/off-ordinate completed response remains owned by Lean PR #22.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, log, sqrt

LEAN_REPO = "chboishabba/dashi_lean4"
LEAN_PR = 22
LEAN_AUTHORITY_HEAD = "5ccfb78ceffac96996d67f85e6a25bfe39ab50e3"

THEOREMS = (
    "quarticFourPhysicalDetector_thirdPrimeShiftedSample_eq_zero",
    "quarticFourPhysicalDetector_threeTap_primeTerm_eq_first",
    "quarticFourPhysicalDetector_threeTap_primeChannel_eq",
    "quarticFourPhysicalDetector_centre_eq",
    "QuarticFourSignedPolePair.threeTapSignedPrimeCombination_eq_commonCentre",
    "QuarticFourSignedPolePair.threeTap_completed_increment",
)


@dataclass(frozen=True)
class SelectedDetectorPrimeReceipt:
    eps: float
    inv_window_mass: float
    t: float

    def validate(self) -> None:
        if self.t < 200:
            raise ValueError("source theorem requires t >= 200")
        if self.inv_window_mass <= 0:
            raise ValueError("quarticWindowMass(R)^(-1) must be positive")

    @property
    def centre(self) -> float:
        self.validate()
        return 2.0 * self.inv_window_mass

    def literal_n3_sample(self) -> float:
        self.validate()
        return 0.0

    def literal_prime_sample(self, n: int) -> float:
        """Source-certified detector value at positive log(n) after the tap.

        Only n=2 is potentially active at t>=200. This is detector sampling,
        not yet the von-Mangoldt coefficient or completed projective channel.
        """
        self.validate()
        if n == 2:
            return self.eps * self.centre
        if n >= 3:
            return 0.0
        raise ValueError("prime-power index must be >= 2")

    def prime_channel(self, s: float, von_mangoldt_2: float = log(2.0)) -> float:
        """Exact Lean theorem formula for the actual selected detector's
        one-frequency even-cone prime channel."""
        self.validate()
        return (
            4.0 * self.eps * (von_mangoldt_2 / sqrt(2.0))
            * self.centre
            * cos(s * log(2.0))
            * cos(self.t * log(2.0))
        )

    def signed_projective_prime_common_centre(
        self,
        pole_two: float,
        pole_half: float,
        prime_shape_half: float,
        prime_shape_two: float,
        von_mangoldt_2: float = log(2.0),
    ) -> float:
        """Exact RHS of Lean's common-centre signed prime theorem.

        prime_shape_* are source-native transformed even-response shapes and
        must come from the same selected W; FRACDASH does not invent them.
        """
        self.validate()
        return (
            8.0 * self.eps * (von_mangoldt_2 / sqrt(2.0))
            * self.inv_window_mass
            * cos(self.t * log(2.0))
            * (pole_two * prime_shape_half - pole_half * prime_shape_two)
        )


def resonance_height(k: int) -> float:
    """cos(t log 2)=0 for t=(pi/2+k*pi)/log2."""
    from math import pi
    return (pi / 2.0 + k * pi) / log(2.0)


if __name__ == "__main__":
    import json
    t = resonance_height(50)
    receipt = SelectedDetectorPrimeReceipt(eps=.05, inv_window_mass=1.0, t=t)
    print(json.dumps({
        "lean_authority_head": LEAN_AUTHORITY_HEAD,
        "n2_sample": receipt.literal_prime_sample(2),
        "n3_sample": receipt.literal_prime_sample(3),
        "n4_sample": receipt.literal_prime_sample(4),
        "prime_channel_at_resonance": receipt.prime_channel(1.0),
        "theorems": THEOREMS,
    }, indent=2))
