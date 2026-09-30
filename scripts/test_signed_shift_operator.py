"""Regression checks for the explicitly chosen shift-operator semantics."""
import math
import unittest
from fractions import Fraction

try:
    from scripts.signed_shift_operator import SignedShiftOperator, three_tap, compact_toy
except ModuleNotFoundError:
    from signed_shift_operator import SignedShiftOperator, three_tap, compact_toy


class SignedShiftTests(unittest.TestCase):
    def test_exact_three_tap(self):
        self.assertEqual(
            three_tap(Fraction(1, 20)).taps,
            ((-1, Fraction(1, 20)), (0, Fraction(1)),
             (1, Fraction(1, 20))))

    def test_composition_and_identity(self):
        a, b, c = (SignedShiftOperator.shift(j) for j in (-2, 1, 3))
        self.assertEqual(a.compose(b).compose(c).taps,
                         a.compose(b.compose(c)).taps)
        self.assertEqual(a.compose(SignedShiftOperator.identity()).taps, a.taps)
        self.assertEqual(a.compose(b).taps, ((-1, Fraction(1)),))

    def test_distribution_and_cancellation(self):
        a = three_tap(Fraction(1, 5))
        b = SignedShiftOperator.shift(2)
        c = SignedShiftOperator.shift(-1)
        self.assertEqual(a.compose(b.add(c)).taps,
                         a.compose(b).add(a.compose(c)).taps)
        self.assertEqual(a.add(a.scale(-1)).taps, ())
        self.assertNotEqual(a.history, a.add(
            SignedShiftOperator.identity().scale(0)).history)

    def test_support_and_only_first_two_primes(self):
        L = math.log(2)
        R = L * .9
        op = three_tap(Fraction(1, 20))
        g = lambda u: compact_toy(u, R)
        self.assertEqual(op.support_envelope(L, L), (-2*L, 2*L))
        self.assertAlmostEqual(op.apply(g, math.log(2), L),
                               (1/20) * g(0))
        self.assertAlmostEqual(op.apply(g, math.log(3), L),
                               (1/20) * g(math.log(3/2)))
        for n in (4, 5, 7, 8):
            self.assertEqual(op.apply(g, math.log(n), L), 0.0)

    def test_operator_composition_semantics(self):
        L = math.log(2)
        g = lambda u: compact_toy(u, 0.85 * L)
        a = three_tap(Fraction(1, 10))
        b = SignedShiftOperator.shift(2).add(
            SignedShiftOperator.shift(-1).scale(-2))
        for u in (-1.0, 0.0, .5, 2.0):
            self.assertAlmostEqual(
                a.compose(b).apply(g, u, L),
                a.apply(lambda v: b.apply(g, v, L), u, L))

    def test_exponential_symbol_and_composition(self):
        from cmath import exp
        L = math.log(2)
        z = .3 + .21j
        op = three_tap(Fraction(1, 20))
        multiplier = 1 + .05 * (exp(-z*L) + exp(z*L))
        self.assertAlmostEqual(op.exponential_symbol(z, L), multiplier)
        sh = SignedShiftOperator.shift(3)
        self.assertAlmostEqual(op.compose(sh).exponential_symbol(z, L),
                               op.exponential_symbol(z, L) *
                               sh.exponential_symbol(z, L))
        u = .7
        self.assertAlmostEqual(
            sum(float(c) * exp(z*(u-j*L)) for j, c in op.taps),
            exp(z*u)*op.exponential_symbol(z, L))

    def test_moment_transport_and_vanishing(self):
        op = three_tap(Fraction(1, 20))
        self.assertEqual(op.shift_moment(0), Fraction(11, 10))
        self.assertEqual(op.shift_moment(1), Fraction(0))
        self.assertEqual(op.shift_moment(2), Fraction(1, 10))
        self.assertEqual(op.transformed_moment_coefficients(2),
                         (Fraction(1, 10), Fraction(0), Fraction(11, 10)))
        # If source m0=m1=m2=0, transformed m2=0 exactly.
        left = op.transformed_moment_coefficients(2)
        self.assertEqual(sum(c*m for c, m in zip(left, (0, 0, 0))), 0)
        # A nonvanishing source integral changes under the three-tap.
        self.assertNotEqual(op.shift_moment(0), Fraction(1))
        # A first finite-difference operator kills constant moments.
        delta = SignedShiftOperator.shift(1).add(
            SignedShiftOperator.identity().scale(-1))
        self.assertEqual(delta.shift_moment(0), 0)
        self.assertEqual(delta.shift_moment(1), 1)
        self.assertEqual(delta.shift_moment(2), 1)

    def test_two_prime_phase_sign_flip_is_only_toy(self):
        from scripts.signed_shift_two_prime_phase import experiment
        result = experiment()
        self.assertTrue(result["dominance_certificate"])
        self.assertTrue(result["phase_sign_flips"])
        self.assertGreater(result["phase_zero_response"], 0)
        self.assertLess(result["phase_pi_over_log2_response"], 0)

    def test_actual_selected_rh_receipt(self):
        from scripts.selected_rh_three_tap_receipt import (
            SelectedDetectorPrimeReceipt, resonance_height
        )
        t = resonance_height(50)
        r = SelectedDetectorPrimeReceipt(
            eps=0.05, inv_window_mass=2.0, t=t)
        self.assertAlmostEqual(r.literal_prime_sample(2), 0.2)
        self.assertEqual(r.literal_prime_sample(3), 0.0)
        self.assertEqual(r.literal_prime_sample(4), 0.0)
        self.assertAlmostEqual(r.prime_channel(1.3), 0.0, places=12)
        self.assertAlmostEqual(
            r.signed_projective_prime_common_centre(
                7.0, 3.0, 2.0, -1.0),
            0.0, places=12)

    def test_shift_units_are_not_prime_labels(self):
        with self.assertRaises(TypeError):
            SignedShiftOperator.of([("SSP prime 3", 1)])
        with self.assertRaises(ValueError):
            SignedShiftOperator.identity().apply(lambda _: 1, 0, 0)


if __name__ == "__main__":
    unittest.main()
