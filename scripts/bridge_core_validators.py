#!/usr/bin/env python3
"""Shared bridge-core validators over emitted macro-soundness traces."""

from __future__ import annotations

from dataclasses import dataclass

from bridge_macro_common import vectorize_state


@dataclass(frozen=True)
class BridgeCoreValidatorRecord:
    name: str
    source_signature: dict[str, str]
    target_signature: dict[str, str]
    intermediate_signatures: list[dict[str, str]]
    source_prime_product: int
    intermediate_prime_products: list[int]
    target_prime_product: int
    source_signed_mass: int
    intermediate_signed_mass: list[int]
    target_signed_mass: int
    signature_signed_mass_delta: int
    total_signed_mass_delta: int
    source_signature_conserved: bool
    source_prime_product_conserved: bool
    bounded_transmutation: bool
    transmutation_detected: bool
    residual_l1_sequence: list[int]
    residual_l1_strict_descent: bool
    residual_l1_unit_descent: bool
    state_repeat_detected: bool
    integer_repeat_detected: bool
    terminal_reached: bool
    trajectory_kind: str
    trajectory_is_irreversible: bool
    macro_length: int
    execution_length: int
    terminal_state_key: list[str]
    contraction_steps: int
    contraction_drop: int
    dynamical_class: str
    regime_valid: bool
    passed: bool


def _source_signature(state: dict[str, str], signature_registers: tuple[str, ...]) -> dict[str, str]:
    return {register: state[register] for register in signature_registers}


def _source_prime_product(
    state: dict[str, str],
    signature_registers: tuple[str, ...],
    signed_state_primes: dict[str, dict[str, int]],
) -> int:
    product = 1
    for register in signature_registers:
        product *= signed_state_primes[register][state[register]]
    return product


def _l1_distance(lhs: list[int], rhs: list[int]) -> int:
    return sum(abs(a - b) for a, b in zip(lhs, rhs, strict=True))


def _signed_mass(state: dict[str, str], registers: tuple[str, ...]) -> int:
    return sum(vectorize_state(state, registers))


def validate_bridge_core(
    *,
    macro_records: list[object],
    macro_summary: dict[str, object],
    registers: tuple[str, ...],
    template_set: str,
    signature_registers: tuple[str, ...] = ("R1", "R2"),
) -> tuple[list[BridgeCoreValidatorRecord], dict[str, object]]:
    signed_state_primes = macro_summary["signed_state_primes"]
    records: list[BridgeCoreValidatorRecord] = []
    trajectory_counts: dict[str, int] = {}
    dynamical_class_counts: dict[str, int] = {}
    terminal_basin_counts: dict[str, int] = {}
    macro_length_histogram: dict[str, int] = {}
    execution_length_histogram: dict[str, int] = {}
    contraction_step_histogram: dict[str, int] = {}
    max_macro_length = 0
    max_execution_length = 0

    for record in macro_records:
        source_state = record.intermediate_states[0]
        target_state = record.intermediate_states[-1]
        source_sig = _source_signature(source_state, signature_registers)
        target_sig = _source_signature(target_state, signature_registers)
        intermediate_sigs = [_source_signature(state, signature_registers) for state in record.intermediate_states]

        source_product = _source_prime_product(source_state, signature_registers, signed_state_primes)
        intermediate_products = [
            _source_prime_product(state, signature_registers, signed_state_primes)
            for state in record.intermediate_states
        ]
        target_product = _source_prime_product(target_state, signature_registers, signed_state_primes)
        source_signed_mass = _signed_mass(source_state, registers)
        intermediate_signed_mass = [_signed_mass(state, registers) for state in record.intermediate_states]
        target_signed_mass = _signed_mass(target_state, registers)
        signature_registers_mass = tuple(signature_registers)
        signature_signed_mass_delta = (
            _signed_mass(target_state, signature_registers_mass) - _signed_mass(source_state, signature_registers_mass)
        )
        total_signed_mass_delta = target_signed_mass - source_signed_mass

        target_vector = vectorize_state(target_state, registers)
        residual_l1_sequence = [
            _l1_distance(vectorize_state(state, registers), target_vector)
            for state in record.intermediate_states
        ]

        source_signature_conserved = all(sig == source_sig for sig in intermediate_sigs) and target_sig == source_sig
        source_prime_product_conserved = all(product == source_product for product in intermediate_products) and target_product == source_product
        bounded_transmutation = all(abs(later - earlier) <= 1 for earlier, later in zip(intermediate_signed_mass, intermediate_signed_mass[1:]))
        transmutation_detected = not (source_signature_conserved and source_prime_product_conserved)
        residual_l1_strict_descent = all(
            later < earlier for earlier, later in zip(residual_l1_sequence, residual_l1_sequence[1:])
        )
        residual_l1_unit_descent = all(
            earlier - later == 1 for earlier, later in zip(residual_l1_sequence, residual_l1_sequence[1:])
        )

        state_keys = [tuple((register, state[register]) for register in registers) for state in record.intermediate_states]
        state_repeat_detected = len(set(state_keys)) != len(state_keys)
        integer_repeat_detected = len(set(record.intermediate_integers)) != len(record.intermediate_integers)
        terminal_reached = record.final_matches_target and record.halted_after_macro
        macro_length = len(record.macro_fraction_strings)
        execution_length = len(record.applied_fraction_strings)
        terminal_state_key = [target_state[register] for register in registers]
        terminal_basin_key = "|".join(terminal_state_key)
        contraction_steps = max(len(residual_l1_sequence) - 1, 0)
        contraction_drop = residual_l1_sequence[0] - residual_l1_sequence[-1]

        if terminal_reached and residual_l1_unit_descent and not state_repeat_detected and not integer_repeat_detected:
            trajectory_kind = "strictly_contracting"
        elif terminal_reached and residual_l1_strict_descent and not state_repeat_detected and not integer_repeat_detected:
            trajectory_kind = "contracting_nonunit"
        elif state_repeat_detected or integer_repeat_detected:
            trajectory_kind = "revisiting_or_cyclic"
        else:
            trajectory_kind = "noncontracting_or_invalid"

        trajectory_counts[trajectory_kind] = trajectory_counts.get(trajectory_kind, 0) + 1
        terminal_basin_counts[terminal_basin_key] = terminal_basin_counts.get(terminal_basin_key, 0) + 1
        macro_length_histogram[str(macro_length)] = macro_length_histogram.get(str(macro_length), 0) + 1
        execution_length_histogram[str(execution_length)] = execution_length_histogram.get(str(execution_length), 0) + 1
        contraction_step_histogram[str(contraction_steps)] = contraction_step_histogram.get(str(contraction_steps), 0) + 1
        max_macro_length = max(max_macro_length, macro_length)
        max_execution_length = max(max_execution_length, execution_length)
        trajectory_is_irreversible = trajectory_kind in {"strictly_contracting", "contracting_nonunit"}

        if trajectory_kind == "strictly_contracting" and source_signature_conserved and source_prime_product_conserved:
            dynamical_class = "conservative_contracting"
        elif trajectory_kind == "strictly_contracting" and bounded_transmutation:
            dynamical_class = "transmuting_contracting"
        elif trajectory_kind == "contracting_nonunit" and bounded_transmutation:
            dynamical_class = "transmuting_contracting_nonunit"
        else:
            dynamical_class = "unclassified_or_invalid"
        dynamical_class_counts[dynamical_class] = dynamical_class_counts.get(dynamical_class, 0) + 1

        regime_valid = (
            bounded_transmutation
            and residual_l1_strict_descent
            and residual_l1_unit_descent
            and terminal_reached
            and record.exclusivity_preserved
        )

        passed = (
            source_signature_conserved
            and source_prime_product_conserved
            and residual_l1_strict_descent
            and residual_l1_unit_descent
            and terminal_reached
            and record.exclusivity_preserved
        )

        records.append(
            BridgeCoreValidatorRecord(
                name=record.name,
                source_signature=source_sig,
                target_signature=target_sig,
                intermediate_signatures=intermediate_sigs,
                source_prime_product=source_product,
                intermediate_prime_products=intermediate_products,
                target_prime_product=target_product,
                source_signed_mass=source_signed_mass,
                intermediate_signed_mass=intermediate_signed_mass,
                target_signed_mass=target_signed_mass,
                signature_signed_mass_delta=signature_signed_mass_delta,
                total_signed_mass_delta=total_signed_mass_delta,
                source_signature_conserved=source_signature_conserved,
                source_prime_product_conserved=source_prime_product_conserved,
                bounded_transmutation=bounded_transmutation,
                transmutation_detected=transmutation_detected,
                residual_l1_sequence=residual_l1_sequence,
                residual_l1_strict_descent=residual_l1_strict_descent,
                residual_l1_unit_descent=residual_l1_unit_descent,
                state_repeat_detected=state_repeat_detected,
                integer_repeat_detected=integer_repeat_detected,
                terminal_reached=terminal_reached,
                trajectory_kind=trajectory_kind,
                trajectory_is_irreversible=trajectory_is_irreversible,
                macro_length=macro_length,
                execution_length=execution_length,
                terminal_state_key=terminal_state_key,
                contraction_steps=contraction_steps,
                contraction_drop=contraction_drop,
                dynamical_class=dynamical_class,
                regime_valid=regime_valid,
                passed=passed,
            )
        )

    return records, {
        "template_set": template_set,
        "checked_rules": len(records),
        "passed_rules": sum(1 for record in records if record.passed),
        "bridge_core_validators_pass": all(record.passed for record in records),
        "regime_valid_rules": sum(1 for record in records if record.regime_valid),
        "regime_validator_pass": all(record.regime_valid for record in records),
        "conservation_validator": "R1/R2 source signature and paired-prime product stay fixed across all macro intermediates",
        "lyapunov_validator": "decoded signed-IR residual L1 distance to the target state decreases by exactly 1 at each macro step",
        "transmutation_validator": "signed-mass change per realized unit step stays bounded while the overall trajectory still contracts to target",
        "directionality_validator": "macro traces are classified from emitted FRACTRAN execution alone as strictly contracting, contracting_nonunit, revisiting_or_cyclic, or noncontracting_or_invalid",
        "trajectory_kind_counts": trajectory_counts,
        "dynamical_class_counts": dynamical_class_counts,
        "terminal_basin_counts": terminal_basin_counts,
        "macro_length_histogram": macro_length_histogram,
        "execution_length_histogram": execution_length_histogram,
        "contraction_step_histogram": contraction_step_histogram,
        "max_macro_length": max_macro_length,
        "max_execution_length": max_execution_length,
        "cost_surface_statement": "macro length, executed fraction count, and contraction-step count are reported as bridge-local execution-cost summaries",
        "basin_surface_statement": "terminal basin counts group traces by final decoded target state over the closed slice",
        "scope": f"bridge-core observational validators on the {template_set} slice",
    }
