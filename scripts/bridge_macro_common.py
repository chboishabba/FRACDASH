#!/usr/bin/env python3
"""Shared numeric macro helpers for signed-IR -> FRACTRAN bridge slices."""

from __future__ import annotations

from fractions import Fraction


STATE_TO_INT = {"negative": -1, "zero": 0, "positive": 1}
INT_TO_STATE = {-1: "negative", 0: "zero", 1: "positive"}
STEP_DELTA_TO_OFFSET = {-1: -1, 1: 1}
STATE_TRANSITIONS = {
    ("negative", 1): "zero",
    ("zero", 1): "positive",
    ("positive", -1): "zero",
    ("zero", -1): "negative",
}


def vectorize_state(state: dict[str, str], registers: tuple[str, ...]) -> list[int]:
    return [STATE_TO_INT[state[register]] for register in registers]


def delta_vector(source: list[int], target: list[int]) -> list[int]:
    return [after - before for before, after in zip(source, target, strict=True)]


def unit_steps(delta: list[int]) -> list[list[int]]:
    steps: list[list[int]] = []
    for index, value in enumerate(delta):
        if value == 0:
            continue
        step = [0] * len(delta)
        step[index] = 1 if value > 0 else -1
        for _ in range(abs(value)):
            steps.append(list(step))
    return steps


def encode_state_integer(
    state: dict[str, str],
    registers: tuple[str, ...],
    signed_state_primes: dict[str, dict[str, int]],
) -> int:
    encoded = 1
    for register in registers:
        encoded *= signed_state_primes[register][state[register]]
    return encoded


def decode_integer_state(
    encoded: int,
    registers: tuple[str, ...],
    signed_state_primes: dict[str, dict[str, int]],
) -> dict[str, str]:
    state: dict[str, str] = {}
    remainder = encoded
    for register in registers:
        active = [label for label, prime in signed_state_primes[register].items() if remainder % prime == 0]
        if len(active) != 1:
            raise ValueError(f"state exclusivity failed for {register}: found {active} in encoded value {encoded}")
        label = active[0]
        state[register] = label
        remainder //= signed_state_primes[register][label]
    if remainder != 1:
        raise ValueError(f"encoded value {encoded} has leftover factor {remainder}")
    return state


def apply_unit_step(
    state: dict[str, str],
    unit_step: list[int],
    registers: tuple[str, ...],
    signed_state_primes: dict[str, dict[str, int]],
) -> tuple[dict[str, str], Fraction]:
    nonzero = [index for index, value in enumerate(unit_step) if value != 0]
    if len(nonzero) != 1:
        raise ValueError(f"unit step must touch exactly one coordinate: {unit_step}")

    index = nonzero[0]
    direction = STEP_DELTA_TO_OFFSET[unit_step[index]]
    register = registers[index]
    from_state = state[register]
    to_state = STATE_TRANSITIONS.get((from_state, direction))
    if to_state is None:
        raise ValueError(f"invalid unit step {unit_step} from {register}={from_state}")

    numerator = signed_state_primes[register][to_state]
    denominator = signed_state_primes[register][from_state]

    next_state = dict(state)
    next_state[register] = to_state
    return next_state, Fraction(numerator, denominator)


def macro_fractions(
    source_state: dict[str, str],
    unit_step_list: list[list[int]],
    registers: tuple[str, ...],
    signed_state_primes: dict[str, dict[str, int]],
) -> list[str]:
    current_state = dict(source_state)
    fractions: list[str] = []
    for unit_step in unit_step_list:
        current_state, fraction = apply_unit_step(current_state, unit_step, registers, signed_state_primes)
        fractions.append(str(fraction))
    return fractions


def parse_fraction_strings(items: list[str]) -> list[Fraction]:
    return [Fraction(item) for item in items]


def fractran_execute(n: int, program: list[Fraction]) -> tuple[int, list[int], list[int]]:
    current = n
    applied_indices: list[int] = []
    intermediates = [current]

    while True:
        applied = False
        for index, fraction in enumerate(program):
            if current % fraction.denominator != 0:
                continue
            current = (current // fraction.denominator) * fraction.numerator
            applied_indices.append(index)
            intermediates.append(current)
            applied = True
            break
        if not applied:
            return current, applied_indices, intermediates
