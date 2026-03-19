#!/usr/bin/env python3
"""Shared macro-soundness checker for bridge slices."""

from __future__ import annotations

from dataclasses import dataclass

from bridge_macro_common import decode_integer_state, fractran_execute, parse_fraction_strings


@dataclass(frozen=True)
class MacroCheckRecord:
    name: str
    source_integer: int
    target_integer: int
    macro_fraction_strings: list[str]
    applied_fraction_strings: list[str]
    applied_fraction_indices: list[int]
    intermediate_integers: list[int]
    intermediate_states: list[dict[str, str]]
    exact_order_preserved: bool
    halted_after_macro: bool
    final_matches_target: bool
    exclusivity_preserved: bool
    passed: bool


def check_macro_soundness_from_export(
    *,
    records: list[object],
    summary: dict[str, object],
    registers: tuple[str, ...],
    template_set: str,
) -> tuple[list[MacroCheckRecord], dict[str, object]]:
    signed_state_primes = summary["signed_state_primes"]

    check_records: list[MacroCheckRecord] = []
    for record in records:
        program = parse_fraction_strings(record.macro_fraction_strings)
        final_integer, applied_indices, intermediates = fractran_execute(record.source_integer, program)
        intermediate_states: list[dict[str, str]] = []
        exclusivity_preserved = True
        for encoded in intermediates:
            try:
                intermediate_states.append(decode_integer_state(encoded, registers, signed_state_primes))
            except ValueError:
                exclusivity_preserved = False
                intermediate_states.append({"decode_error": str(encoded)})

        applied_fraction_strings = [str(program[index]) for index in applied_indices]
        exact_order_preserved = applied_indices == list(range(len(program)))
        halted_after_macro = len(applied_indices) == len(program)
        final_matches_target = final_integer == record.target_integer
        passed = exact_order_preserved and halted_after_macro and final_matches_target and exclusivity_preserved

        check_records.append(
            MacroCheckRecord(
                name=record.name,
                source_integer=record.source_integer,
                target_integer=record.target_integer,
                macro_fraction_strings=record.macro_fraction_strings,
                applied_fraction_strings=applied_fraction_strings,
                applied_fraction_indices=applied_indices,
                intermediate_integers=intermediates,
                intermediate_states=intermediate_states,
                exact_order_preserved=exact_order_preserved,
                halted_after_macro=halted_after_macro,
                final_matches_target=final_matches_target,
                exclusivity_preserved=exclusivity_preserved,
                passed=passed,
            )
        )

    return check_records, {
        "template_set": template_set,
        "checked_rules": len(check_records),
        "passed_rules": sum(1 for record in check_records if record.passed),
        "macro_soundness": all(record.passed for record in check_records),
        "macro_encoding": summary["macro_encoding"],
        "macro_ordering": summary["macro_ordering"],
        "signed_state_primes": signed_state_primes,
        "exclusivity_invariant": "exactly one state-prime per register divides the encoded integer",
        "soundness_statement": (
            f"standard ordered FRACTRAN execution of the exported macro fractions matches "
            f"the normalized signed-IR action on the {template_set} slice"
        ),
    }
