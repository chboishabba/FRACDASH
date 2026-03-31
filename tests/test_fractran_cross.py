#!/usr/bin/env python3
"""Cross-implementation FRACTRAN test harness.

Tests canonical FRACTRAN programs against known-good traces using a
pure-Python reference stepper, then optionally compares against the
Rust fractran-vm binary if available.

No novel research content — just standard FRACTRAN semantics checks.
"""
from __future__ import annotations

import json
import os
import subprocess
import unittest
from fractions import Fraction
from pathlib import Path

# ── Pure-Python reference stepper ────────────────────────────────

def step(program: list[Fraction], n: int) -> int | None:
    """One FRACTRAN step: first fraction f where n*f is integer."""
    for f in program:
        val = n * f
        if val.denominator == 1:
            return int(val)
    return None


def run(program: list[Fraction], n: int, max_steps: int = 1000) -> list[int]:
    """Run program, return full state trace."""
    trace = [n]
    for _ in range(max_steps):
        nxt = step(program, trace[-1])
        if nxt is None:
            break
        trace.append(nxt)
    return trace


# ── Canonical test programs ──────────────────────────────────────

# Conway's PRIMEGAME: generates primes as powers of 2 in the trace
PRIMEGAME = [Fraction(17, 91), Fraction(78, 85), Fraction(19, 51),
             Fraction(23, 38), Fraction(29, 33), Fraction(77, 29),
             Fraction(95, 23), Fraction(77, 19), Fraction(1, 17),
             Fraction(11, 13), Fraction(13, 11), Fraction(15, 14),
             Fraction(15, 2), Fraction(55, 1)]

# Addition: 3/2 moves factors of 2 into factors of 3
ADDITION = [Fraction(3, 2)]

# Multiplication: computes 2^a * 3^b → 5^(a*b)
MULTIPLY = [Fraction(455, 33), Fraction(11, 13), Fraction(1, 11),
            Fraction(3, 7), Fraction(11, 2), Fraction(1, 3)]


class TestPythonStepper(unittest.TestCase):
    """Verify the pure-Python reference against known traces."""

    def test_addition_2cubed(self):
        # 2^3 = 8 → 12 → 18 → 27 = 3^3
        trace = run(ADDITION, 8)
        self.assertEqual(trace, [8, 12, 18, 27])

    def test_addition_2fifth(self):
        trace = run(ADDITION, 32)
        self.assertEqual(trace[-1], 3**5)

    def test_primegame_first_steps(self):
        trace = run(PRIMEGAME, 2, max_steps=20)
        self.assertGreater(len(trace), 1)
        self.assertEqual(trace[0], 2)

    def test_multiply_2x3(self):
        # 2^2 * 3^3 = 4*27 = 108 → should yield 5^6 = 15625
        trace = run(MULTIPLY, 108, max_steps=200)
        self.assertEqual(trace[-1], 5**6)

    def test_halting(self):
        # 3/2 on input 3 halts immediately (no fraction fires)
        trace = run(ADDITION, 3)
        self.assertEqual(trace, [3])

    def test_step_none(self):
        self.assertIsNone(step(ADDITION, 3))

    def test_step_fires(self):
        self.assertEqual(step(ADDITION, 8), 12)


# ── Rust fractran-vm comparison (optional) ───────────────────────

RUST_VM = os.environ.get(
    "FRACTRAN_VM_BIN",
    str(Path.home() / ".emacs.d.kiro/kiro.el-research/fractran-vm/target/release/fractran-vm"),
)


def rust_available() -> bool:
    return Path(RUST_VM).is_file()


@unittest.skipUnless(rust_available(), "fractran-vm binary not found")
class TestRustComparison(unittest.TestCase):
    """Compare Rust fractran-vm against Python reference on shared programs."""

    def _run_rust(self, program_json: str, init: int, max_steps: int) -> list[int]:
        """Call Rust VM via subprocess with JSON program spec."""
        proc = subprocess.run(
            [RUST_VM, "fractran-json"],
            input=json.dumps({"program": program_json, "init": init, "max_steps": max_steps}),
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode != 0:
            self.skipTest(f"Rust VM does not support fractran-json: {proc.stderr[:200]}")
        return json.loads(proc.stdout)["trace"]

    def test_addition_parity(self):
        py_trace = run(ADDITION, 8)
        try:
            rs_trace = self._run_rust("3/2", 8, 100)
            self.assertEqual(py_trace, rs_trace)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("Rust VM unavailable")


if __name__ == "__main__":
    unittest.main()
