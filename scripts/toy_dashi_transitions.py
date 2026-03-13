#!/usr/bin/env python3
from __future__ import annotations

"""
Toy DASHI transition helpers for Phase 2 CORE experiments.

Provides a signed-ternary 4-register set, mapping it into FRACTRAN fractions, and
exposes utilities for tracing basins, verifying invariants, and summarizing
state traversal statistics.
"""

import argparse
import importlib.util
import json
import sys
from collections import deque
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class RegisterPrimes:
    name: str
    zero: int
    positive: int
    negative: int


REGISTERS: Sequence[RegisterPrimes] = (
    RegisterPrimes("R1", zero=2, positive=3, negative=5),
    RegisterPrimes("R2", zero=7, positive=11, negative=13),
    RegisterPrimes("R3", zero=17, positive=19, negative=23),
    RegisterPrimes("R4", zero=29, positive=31, negative=37),
)

STATE_BY_SYMBOL = {
    "−1": "negative",
    "-1": "negative",
    "0": "zero",
    "+1": "positive",
    "1": "positive",
}

SYMBOL_BY_STATE = {
    "zero": "0",
    "negative": "-1",
    "positive": "+1",
}

SIGNED_STATE_VALUES = ("negative", "zero", "positive")
SIGNED_STATE_NUMBERS = {"negative": -1, "zero": 0, "positive": 1}
SIGNED_STATE_SYMBOLS = {"negative": "-1", "zero": "0", "positive": "+1"}
SIGNED_NUMBER_TO_STATE = {value: name for name, value in SIGNED_STATE_NUMBERS.items()}
REGISTER_INDEX = {reg.name: idx for idx, reg in enumerate(REGISTERS)}

STATE_PRIMES = {
    reg.name: {"zero": reg.zero, "positive": reg.positive, "negative": reg.negative}
    for reg in REGISTERS
}

ALL_PRIMES = [prime for reg in REGISTERS for prime in (reg.zero, reg.positive, reg.negative)]


@dataclass(frozen=True)
class Transition:
    name: str
    condition: Mapping[str, str]
    action: Mapping[str, str]
    description: str


TOY_TRANSITIONS: tuple[Transition, ...] = (
    Transition(
        name="flip_r1_to_negative",
        condition={"R1": "positive"},
        action={"R1": "negative"},
        description="Flip R1 from +1 to −1 while leaving all other registers untouched.",
    ),
    Transition(
        name="flip_r1_to_positive",
        condition={"R1": "negative"},
        action={"R1": "positive"},
        description="Flip R1 from −1 back to +1.",
    ),
    Transition(
        name="ignite_r2_from_r1",
        condition={"R1": "positive", "R2": "zero"},
        action={"R1": "positive", "R2": "positive"},
        description="If R1 is +1 and R2 is zero, seed R2 as +1 while keeping R1 positive.",
    ),
    Transition(
        name="settle_parity",
        condition={"R1": "positive", "R2": "positive", "R4": "zero"},
        action={"R1": "positive", "R2": "positive", "R4": "positive"},
        description="Mark parity register R4 as +1 when the first two registers are +1.",
    ),
    Transition(
        name="reset_r2",
        condition={"R2": "negative"},
        action={"R2": "zero"},
        description="Bring R2 back to zero when it is negative.",
    ),
)


DEFAULT_START_STATE = {"R1": "positive", "R2": "zero", "R3": "zero", "R4": "zero"}
DEFAULT_START_VECTOR: tuple[int, ...] = (
    SIGNED_STATE_NUMBERS[DEFAULT_START_STATE["R1"]],
    SIGNED_STATE_NUMBERS[DEFAULT_START_STATE["R2"]],
    SIGNED_STATE_NUMBERS[DEFAULT_START_STATE["R3"]],
    SIGNED_STATE_NUMBERS[DEFAULT_START_STATE["R4"]],
)
DEFAULT_CHAIN_BOUND = 2


def _load_agdas_bridge_module() -> Any:
    bridge_path = Path(__file__).resolve().parent / "agdas_bridge.py"
    module_name = "agdas_bridge_local"
    spec = importlib.util.spec_from_file_location(module_name, bridge_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load agdas bridge module from {bridge_path}")
    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def transitions_from_agdas(
    agdas_path: str,
    *,
    max_rules: int | None = None,
) -> tuple[tuple[Transition, ...], dict[str, object]]:
    bridge = _load_agdas_bridge_module()
    scan = bridge.scan_agdas(Path(agdas_path))

    transition_records = []
    transitions: list[Transition] = []
    skipped: list[dict[str, object]] = []
    for index, payload in enumerate(scan.parsed_rules):
        if max_rules is not None and index >= max_rules:
            break
        invalid: list[str] = []
        for register in payload.condition.keys() | payload.action.keys():
            if register not in REGISTER_INDEX:
                invalid.append(register)
            state = payload.condition.get(register) or payload.action.get(register)
            if state not in SIGNED_STATE_NUMBERS:
                invalid.append(f"{register}:{state}")
        if invalid:
            skipped.append(
                {
                    "module": payload.module,
                    "line": payload.line,
                    "invalid": invalid,
                    "source_text": payload.source_text,
                }
            )
            continue
        transitions.append(
            Transition(
                name=f"{payload.module}:{payload.name}",
                condition=dict(payload.condition),
                action=dict(payload.action),
                description=(
                    f"AGDAS transition from {payload.module} "
                    f"line {payload.line}: {payload.source_text}"
                ),
            )
        )
        transition_records.append(
            {
                "name": payload.name,
                "module": payload.module,
                "line": payload.line,
                "condition": payload.condition,
                "action": payload.action,
                "source_text": payload.source_text,
            }
        )

    if not transitions:
        raise RuntimeError(f"no typed AGDAS transitions found in {agdas_path}")

    return tuple(transitions), {
        "source": str(bridge.AGDAS_FILENAME if hasattr(bridge, "AGDAS_FILENAME") else "all_dashi_agdas.txt"),
        "path": str(Path(agdas_path)),
        "transition_count": len(transitions),
        "scan_signature": scan.scan_signature,
        "source_transitions": transition_records,
        "skipped_rules": skipped,
        "malformed_rules": scan.malformed_rules,
    }


def transitions_from_agdas_templates(
    template_set: str = "wave1",
) -> tuple[tuple[Transition, ...], dict[str, object]]:
    bridge = _load_agdas_bridge_module()
    template_rules = bridge._template_rules(template_set)
    transitions: list[Transition] = []
    for rule in template_rules:
        transitions.append(
            Transition(
                name=rule.name,
                condition=dict(rule.condition),
                action=dict(rule.action),
                description=rule.description,
            )
        )
    summary = {
        "source": "agdas_templates",
        "template_set": template_set,
        "template_count": len(template_rules),
        "template_modules": sorted({rule.module for rule in template_rules}),
    }
    return tuple(transitions), summary


def prime_for(register: str, state: str) -> int:
    try:
        primes = STATE_PRIMES[register]
    except KeyError as exc:
        raise KeyError(f"unknown register {register}") from exc
    try:
        return primes[state]
    except KeyError as exc:
        raise KeyError(f"unknown state {state} for {register}") from exc


def encode_state(register_states: Mapping[str, str]) -> int:
    value = 1
    for reg in REGISTERS:
        state = register_states.get(reg.name, "zero")
        value *= prime_for(reg.name, state)
    return value


def encode_signed_state(register_values: Mapping[str, int]) -> int:
    normalized = {}
    for reg in REGISTERS:
        value = register_values.get(reg.name, 0)
        if value not in (-1, 0, 1):
            raise ValueError(f"invalid signed value {value} for {reg.name}")
        if value == -1:
            normalized[reg.name] = "negative"
        elif value == 0:
            normalized[reg.name] = "zero"
        else:
            normalized[reg.name] = "positive"
    return encode_state(normalized)


def decode_state(value: int) -> dict[str, str]:
    decoded: dict[str, str] = {}
    remaining = value
    for reg in REGISTERS:
        for state_name, prime in STATE_PRIMES[reg.name].items():
            count = 0
            while remaining % prime == 0:
                remaining //= prime
                count += 1
            if count > 1:
                raise ValueError(f"{reg.name} has invalid multiplicity for {state_name}")
            if count == 1:
                decoded[reg.name] = state_name
                break
        else:
            raise ValueError(f"{reg.name} missing a canonical prime")
    if remaining != 1:
        raise ValueError("value contains unexpected primes")
    return decoded


def decode_signed_state(value: int) -> tuple[int, ...]:
    decoded = decode_state(value)
    return tuple(SIGNED_STATE_NUMBERS[decoded[reg.name]] for reg in REGISTERS)


def transition_denominator(transition: Transition) -> int:
    denom = 1
    for register, state in transition.condition.items():
        denom *= prime_for(register, state)
    return denom


def transition_numerator(transition: Transition) -> int:
    num = 1
    for register, state in transition.action.items():
        num *= prime_for(register, state)
    return num


def transition_fraction(transition: Transition) -> Fraction:
    return Fraction(transition_numerator(transition), transition_denominator(transition))


def transition_matches(value: int, transition: Transition) -> bool:
    denom = transition_denominator(transition)
    return value % denom == 0


def transition_matches_vector(state: Sequence[int], transition: Transition) -> bool:
    vector = normalize_signed_vector(state)
    for register, required_state in transition.condition.items():
        idx = REGISTER_INDEX[register]
        if vector[idx] != SIGNED_STATE_NUMBERS[required_state]:
            return False
    return True


def apply_transition_vector(
    state: Sequence[int],
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> tuple[Transition, tuple[int, ...]] | tuple[None, None]:
    vector = normalize_signed_vector(state)
    for transition in transitions:
        if transition_matches_vector(vector, transition):
            next_state = list(vector)
            for register, new_state in transition.action.items():
                next_state[REGISTER_INDEX[register]] = SIGNED_STATE_NUMBERS[new_state]
            return transition, tuple(next_state)
    return None, None


def parse_signed_vector(raw: str) -> tuple[int, ...]:
    items = tuple(raw.split(","))
    if len(items) != len(REGISTERS):
        raise ValueError(f"need {len(REGISTERS)} values, got {len(items)}")
    values = []
    for item in items:
        key = item.strip()
        state = STATE_BY_SYMBOL.get(key)
        if state is None:
            raise ValueError(f"invalid state token '{key}'")
        values.append(SIGNED_STATE_NUMBERS[state])
    return tuple(values)


def _number_to_symbol_state(value: int) -> str:
    try:
        state_name = SIGNED_NUMBER_TO_STATE[value]
    except KeyError as exc:
        raise ValueError(f"invalid signed value {value}; expected -1, 0, 1") from exc
    return state_name


def normalize_signed_vector(register_values: Sequence[int] | Mapping[str, int]) -> tuple[int, ...]:
    if isinstance(register_values, Mapping):
        return tuple(
            int(register_values.get(reg.name, 0))
            for reg in REGISTERS
        )
    if len(register_values) != len(REGISTERS):
        raise ValueError(f"expected {len(REGISTERS)} register values, got {len(register_values)}")
    return tuple(int(register_values[idx]) for idx in range(len(REGISTERS)))


def vector_to_state_dict(register_values: Sequence[int] | Mapping[str, int]) -> dict[str, str]:
    vector = normalize_signed_vector(register_values)
    return {reg.name: _number_to_symbol_state(vector[idx]) for idx, reg in enumerate(REGISTERS)}


def vector_to_symbol_tuple(register_values: Sequence[int] | Mapping[str, int]) -> tuple[str, ...]:
    return tuple(
        SYMBOL_BY_STATE[state_name]
        for state_name in vector_to_state_dict(register_values).values()
    )


def apply_transition(
    value: int,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> tuple[Transition, int] | tuple[None, None]:
    for transition in transitions:
        if transition_matches(value, transition):
            frac = transition_fraction(transition)
            next_value = (value * frac.numerator) // frac.denominator
            return transition, next_value
    return None, None


def matching_transitions(
    value: int,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> list[tuple[Transition, int]]:
    matches = []
    for transition in transitions:
        if transition_matches(value, transition):
            frac = transition_fraction(transition)
            next_value = (value * frac.numerator) // frac.denominator
            matches.append((transition, next_value))
    return matches


def trace_steps(
    start_value: int,
    max_steps: int = 12,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> list[tuple[int, Transition, int]]:
    trail: list[tuple[int, Transition, int]] = []
    current = start_value
    for _ in range(max_steps):
        transition, next_value = apply_transition(current, transitions=transitions)
        if transition is None:
            break
        trail.append((current, transition, next_value))
        current = next_value
    return trail


def trace_signed_steps(
    start_value: int,
    max_steps: int = 12,
    max_depth: int | None = None,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> list[tuple[tuple[int, ...], Transition, tuple[int, ...]]]:
    vector = decode_signed_state(start_value)
    trail: list[tuple[tuple[int, ...], Transition, tuple[int, ...]]] = []
    current = vector
    step_cap = max_steps if max_depth is None else min(max_steps, max_depth)
    for _ in range(step_cap):
        transition, next_state = apply_transition_vector(current, transitions=transitions)
        if transition is None or next_state is None:
            break
        trail.append((tuple(current), transition, next_state))
        current = next_state
    return trail


def build_graph(
    start_value: int,
    max_depth: int = 8,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> dict[int, list[tuple[Transition, int]]]:
    queue = deque([(start_value, 0)])
    graph: dict[int, list[tuple[Transition, int]]] = {}
    seen = {start_value}
    while queue:
        value, depth = queue.popleft()
        matches = matching_transitions(value, transitions=transitions)
        if matches:
            graph.setdefault(value, []).extend(matches)
            for _, next_value in matches:
                if next_value not in seen and depth + 1 <= max_depth:
                    seen.add(next_value)
                    queue.append((next_value, depth + 1))
        else:
            graph.setdefault(value, [])
    return graph


def fixed_prime_walk(
    start_vector: Sequence[int],
    max_steps: int = 16,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> dict[str, object]:
    current = normalize_signed_vector(start_vector)
    trail: list[dict[str, object]] = []
    seen: dict[tuple[int, ...], int] = {}
    current_tuple = tuple(current)
    status: str = "timeout"
    cycle_start = None
    final_state = current_tuple
    for step in range(max_steps):
        if current_tuple in seen:
            cycle_start = seen[current_tuple]
            status = "cycle"
            break
        seen[current_tuple] = step
        transition, next_state = apply_transition_vector(current_tuple, transitions=transitions)
        if transition is None or next_state is None:
            status = "terminal"
            break
        next_tuple = tuple(next_state)
        trail.append(
            {
                "step": step + 1,
                "state": current_tuple,
                "transition": transition.name,
                "next_state": next_tuple,
            }
        )
        current_tuple = next_tuple
        final_state = current_tuple
    if status == "timeout":
        final_state = current_tuple
    return {
        "status": status,
        "start": tuple(current),
        "final_state": final_state,
        "steps": len(trail),
        "max_steps": max_steps,
        "cycle_start": cycle_start,
        "path": trail,
    }


def verify_monotone_chain_bound(
    max_chain: int,
    scan_steps: int = 128,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> dict[str, object]:
    state_space = all_signed_state_vectors()
    bound = max(1, max_chain)
    state_space_size = len(state_space)
    chain_max = 0
    timed_out_states: list[str] = []
    exceeding: list[str] = []

    for state_vector in state_space:
        outcome = fixed_prime_walk(state_vector, max_steps=scan_steps, transitions=transitions)
        steps = int(outcome["steps"])  # type: ignore[arg-type]
        status = str(outcome["status"])
        state_key = str(state_vector)
        chain_max = max(chain_max, steps)
        if status == "timeout":
            timed_out_states.append(state_key)
        elif steps > bound:
            exceeding.append(state_key)

    return {
        "claimed_bound": bound,
        "state_space_size": state_space_size,
        "scan_steps": scan_steps,
        "max_observed_chain": chain_max,
        "timed_out_count": len(timed_out_states),
        "states_exceeding_bound": exceeding[:20],
        "exceeded_count": len(exceeding),
        "timed_out_states": timed_out_states[:20],
        "verified": len(timed_out_states) == 0 and len(exceeding) == 0,
    }


def compare_fixed_prime_and_explicit(
    start_vector: Sequence[int],
    max_steps: int = 16,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> dict[str, object]:
    fixed_state = normalize_signed_vector(start_vector)
    start_state = fixed_state
    explicit_state = encode_signed_state(
        {reg.name: fixed_state[idx] for idx, reg in enumerate(REGISTERS)}
    )
    trail: list[dict[str, object]] = []

    for step in range(1, max_steps + 1):
        fixed_transition, fixed_next = apply_transition_vector(
            fixed_state,
            transitions=transitions,
        )
        explicit_transition, explicit_next = apply_transition(
            explicit_state,
            transitions=transitions,
        )

        if fixed_transition is None and explicit_transition is None:
            return {
                "start": start_state,
                "status": "match",
                "comparison_status": "terminal",
                "steps": step - 1,
                "max_steps": max_steps,
                "path": trail,
            }

        if fixed_transition is None:
            return {
                "start": start_state,
                "status": "mismatch",
                "comparison_status": "fixed-terminal",
                "steps": step - 1,
                "max_steps": max_steps,
                "path": trail,
                "message": "explicit dynamics continues while fixed-prime dynamics is terminal",
            }

        if explicit_transition is None:
            return {
                "start": start_state,
                "status": "mismatch",
                "comparison_status": "explicit-terminal",
                "steps": step - 1,
                "max_steps": max_steps,
                "path": trail,
                "message": "fixed-prime dynamics continues while explicit dynamics is terminal",
            }

        fixed_name = fixed_transition.name
        explicit_name = explicit_transition.name
        explicit_decoded = decode_signed_state(explicit_next)
        if fixed_name != explicit_name:
            return {
                "start": start_state,
                "status": "mismatch",
                "comparison_status": "transition-name",
                "steps": step - 1,
                "max_steps": max_steps,
                "path": trail,
                "message": "transition names diverged",
                "fixed_transition": fixed_name,
                "explicit_transition": explicit_name,
            }
        if fixed_next != explicit_decoded:
            return {
                "start": start_state,
                "status": "mismatch",
                "comparison_status": "next-state",
                "steps": step - 1,
                "max_steps": max_steps,
                "path": trail,
                "message": "next-state vectors diverged",
                "fixed_next": fixed_next,
                "explicit_next": explicit_decoded,
            }

        trail.append(
            {
                "step": step,
                "state": fixed_state,
                "transition": fixed_name,
                "explicit_state": explicit_state,
                "next_state": fixed_next,
            }
        )
        fixed_state = fixed_next
        explicit_state = explicit_next

    return {
        "start": start_state,
        "status": "match",
        "comparison_status": "timeout",
        "steps": max_steps,
        "max_steps": max_steps,
        "path": trail,
    }


def summarize_fixed_vs_explicit_dynamics(
    max_steps: int = 16,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> dict[str, object]:
    outcomes: dict[str, object] = {}
    mismatches: list[dict[str, object]] = []
    mismatch_count = 0
    terminal = 0
    timeout_count = 0
    status_histogram: dict[str, int] = {}

    for state_vector in all_signed_state_vectors():
        result = compare_fixed_prime_and_explicit(
            state_vector,
            max_steps=max_steps,
            transitions=transitions,
        )
        result_copy = {
            "status": result["status"],
            "comparison_status": result["comparison_status"],
            "steps": result["steps"],
        }
        key = str(state_vector)
        outcomes[key] = result_copy
        status_histogram[str(result["comparison_status"])] = status_histogram.get(
            str(result["comparison_status"]), 0
        ) + 1
        mismatch_count += 0 if result["status"] == "match" else 1
        if result["comparison_status"] == "terminal":
            terminal += 1
        if result["comparison_status"] == "timeout":
            timeout_count += 1
        if result["status"] == "mismatch":
            mismatches.append(
                {
                    "start": key,
                    "comparison_status": str(result["comparison_status"]),
                    "steps": int(result["steps"]),  # type: ignore[arg-type]
                    "message": str(result.get("message", "")),
                }
            )

    if mismatches:
        mismatches = sorted(mismatches, key=lambda item: (item["comparison_status"], item["steps"]))[:20]
    state_count = len(all_signed_state_vectors())
    match_count = state_count - mismatch_count
    return {
        "max_steps": max_steps,
        "state_count": state_count,
        "comparison_match_count": match_count,
        "mismatch_count": mismatch_count,
        "terminal": terminal,
        "timeout": timeout_count,
        "comparison_status_histogram": status_histogram,
        "mismatches": mismatches,
        "outcomes": outcomes,
    }


def summarize_deterministic_basin_walks(
    max_steps: int = 16,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> dict[str, object]:
    basin_to_states: dict[str, list[str]] = {}
    states = all_signed_state_vectors()
    for state_vector in states.keys():
        outcome = fixed_prime_walk(
            state_vector,
            max_steps=max_steps,
            transitions=transitions,
        )
        status = str(outcome["status"])
        if status == "terminal":
            key_state = outcome["final_state"]
            basin_key = ("terminal", tuple(key_state))  # type: ignore[arg-type]
        elif status == "cycle":
            cycle_start = outcome.get("cycle_start")
            path = outcome["path"]  # type: ignore[arg-type]
            if isinstance(cycle_start, int) and cycle_start < len(path):
                cycle_entry = path[cycle_start]["state"]  # type: ignore[index]
            else:
                cycle_entry = outcome["final_state"]  # type: ignore[assignment]
            basin_key = ("cycle", tuple(cycle_entry))
        else:
            cycle_entry = outcome["final_state"]  # type: ignore[assignment]
            basin_key = ("timeout", tuple(cycle_entry))
        basin_id = f"{basin_key[0]}:{basin_key[1]}"
        basin_to_states.setdefault(basin_id, []).append(str(state_vector))

    top_basins = sorted(
        ((basin_id, len(members)) for basin_id, members in basin_to_states.items()),
        key=lambda item: (-item[1], item[0]),
    )[:10]

    return {
        "max_steps": max_steps,
        "basin_count": len(basin_to_states),
        "target_walk_count": 10,
        "has_target_walker_count": len(basin_to_states) >= 10,
        "top_10_basins_by_size": top_basins,
        "sample_basin_walks": sorted(
            (basin_id, len(members), sorted(members)[:3])
            for basin_id, members in basin_to_states.items()
        )[:10],
    }


def summarize_fixed_prime_walks(
    max_steps: int = 16,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> dict[str, object]:
    state_space = all_signed_state_vectors()
    outcomes: dict[str, object] = {}
    terminals = 0
    cycles = 0
    timeouts = 0
    max_length = 0
    longest_paths: list[tuple[str, int, str]] = []
    max_examples: list[tuple[str, int, str]] = []
    for state_vector in state_space:
        result = fixed_prime_walk(state_vector, max_steps=max_steps, transitions=transitions)
        outcome = result["status"]
        length = int(result["steps"])  # type: ignore[arg-type]
        if outcome == "terminal":
            terminals += 1
        elif outcome == "cycle":
            cycles += 1
        else:
            timeouts += 1
        max_length = max(max_length, length)
        key = str(state_vector)
        outcomes[key] = {
            "status": outcome,
            "steps": length,
        }
        longest_paths.append((key, length, str(outcome)))
        if len(max_examples) < 10:
            max_examples.append((key, length, str(outcome)))
    if max_examples:
        max_examples.sort(key=lambda item: item[1], reverse=True)
    return {
        "max_steps": max_steps,
        "state_count": len(state_space),
        "terminal": terminals,
        "cycle": cycles,
        "timeout": timeouts,
        "max_steps_observed": max_length,
        "longest_paths": sorted(longest_paths, key=lambda item: (-item[1], item[0]))[:10],
        "samples_by_length": max_examples[:5],
        "outcomes": outcomes,
    }


def build_space_stats(graph: dict[int, list[tuple[Transition, int]]]) -> dict[str, object]:
    profile = profile_graph(graph)
    chain_lengths = {
        str(value): longest_chain(value, graph) for value in sorted(graph.keys())
    }
    counts: dict[str, int] = {}
    for length in chain_lengths.values():
        label = str(length)
        counts[label] = counts.get(label, 0) + 1
    return {
        **profile,
        "chain_length_histogram": counts,
        "max_chain_start_states": sorted(
            (k for k, v in chain_lengths.items() if v == profile["longest_chain"]),
            key=int,
        )[:5],
    }


def longest_chain(state: int, graph: dict[int, list[tuple[Transition, int]]], seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    if state in seen:
        return 0
    seen.add(state)
    neighbors = graph.get(state, [])
    if not neighbors:
        seen.remove(state)
        return 0
    best = 0
    for _, next_state in neighbors:
        best = max(best, 1 + longest_chain(next_state, graph, seen))
    seen.remove(state)
    return best


def profile_graph(graph: dict[int, list[tuple[Transition, int]]]) -> dict[str, int]:
    nodes = len(graph)
    edges = sum(len(edge_list) for edge_list in graph.values())
    terminal_states = sum(1 for edge_list in graph.values() if not edge_list)
    longest = max((longest_chain(state, graph) for state in graph), default=0)
    return {
        "nodes": nodes,
        "edges": edges,
        "terminal_states": terminal_states,
        "longest_chain": longest,
    }


def decode_tuple(value: int) -> tuple[str, ...]:
    decoded = decode_state(value)
    return tuple(decoded[reg.name] for reg in REGISTERS)


def summarize_graph(graph: dict[int, list[tuple[Transition, int]]], limit: int = 5, title: str = "Basin") -> None:
    summary = profile_graph(graph)
    print(f"{title} graph summary:")
    for key, val in summary.items():
        print(f"- {key}: {val}")

    printed = 0
    for source, edges in graph.items():
        if printed >= limit:
            break
        if not edges:
            continue
        transition, target = edges[0]
        print(f"- {decode_tuple(source)} ->[{transition.name}] -> {decode_tuple(target)}")
        printed += 1


def all_state_encodings() -> dict[tuple[str, ...], int]:
    combos = {}
    options = ("zero", "positive", "negative")
    for combo in product(options, repeat=len(REGISTERS)):
        state = {reg.name: combo[idx] for idx, reg in enumerate(REGISTERS)}
        combos[combo] = encode_state(state)
    return combos


def all_signed_state_vectors() -> dict[tuple[int, ...], int]:
    combos: dict[tuple[int, ...], int] = {}
    options = tuple(SIGNED_STATE_NUMBERS[s] for s in ("negative", "zero", "positive"))
    for combo in product(options, repeat=len(REGISTERS)):
        state = {reg.name: combo[idx] for idx, reg in enumerate(REGISTERS)}
        combos[combo] = encode_signed_state(state)
    return combos


def build_full_space_graph(
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> dict[int, list[tuple[Transition, int]]]:
    graph: dict[int, list[tuple[Transition, int]]] = {}
    for value in all_state_encodings().values():
        graph[value] = matching_transitions(value, transitions=transitions)
    return graph


def explore_fixed_prime_dynamics(
    start_value: int,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> None:
    print("Fixed-prime encoding invariants:")
    decoded = decode_state(start_value)
    print(f"- start value: {start_value}")
    for register, state in decoded.items():
        print(f"  {register}: {state} (prime {prime_for(register,state)})")

    graph = build_graph(start_value, max_depth=8, transitions=transitions)
    summarize_graph(graph, limit=5, title="Basin")

    trail = trace_steps(start_value, max_steps=12, transitions=transitions)
    print("Sample transition trail:")
    for idx, (source, transition, target) in enumerate(trail, start=1):
        print(
            f"  {idx}. {transition.name}: {decode_tuple(source)} -> {decode_tuple(target)} ({transition_fraction(transition)})"
        )
    if not trail:
        print("  No transitions fired from the start state.")


def summarize_transitions(transitions: Sequence[Transition] = TOY_TRANSITIONS) -> list[dict[str, str]]:
    return [
        {
            "name": transition.name,
            "description": transition.description,
            "fraction": str(transition_fraction(transition)),
        }
        for transition in transitions
    ]


def validate_full_round_trip() -> list[dict[str, object]]:
    errors = []
    for combo, value in all_signed_state_vectors().items():
        decoded = decode_signed_state(value)
        if tuple(decoded) != tuple(combo):
            errors.append(
                {
                    "expected": combo,
                    "encoded": value,
                    "decoded": decoded,
                }
            )
    return errors


def summarize(
    start_vector: tuple[int, ...] = DEFAULT_START_VECTOR,
    fixed_prime_steps: int = 16,
    max_steps: int = 12,
    compare_explicit_steps: int | None = None,
    max_chain_bound: int | None = None,
    max_chain_scan: int = 128,
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
    transition_source: str = "toy",
    transition_source_path: str | None = None,
    transition_source_summary: dict[str, object] | None = None,
) -> dict[str, object]:
    if len(start_vector) != len(REGISTERS):
        raise ValueError(f"expected start vector length {len(REGISTERS)}, got {len(start_vector)}")

    start_named = {reg.name: start_vector[idx] for idx, reg in enumerate(REGISTERS)}
    start_value = encode_signed_state(start_named)
    basin_graph = build_graph(start_value, max_depth=max_steps, transitions=transitions)
    full_graph = build_full_space_graph(transitions=transitions)
    basin_trail = trace_steps(start_value, max_steps=max_steps, transitions=transitions)
    explicit_steps = compare_explicit_steps if compare_explicit_steps is not None else max_steps
    fixed_prime_walks = {
        str(state): fixed_prime_walk(state, max_steps=fixed_prime_steps, transitions=transitions)
        for state, _ in all_signed_state_vectors().items()
    }
    fixed_prime_summary = {
        "max_steps": fixed_prime_steps,
        "state_count": len(all_signed_state_vectors()),
        "terminal": sum(1 for outcome in fixed_prime_walks.values() if outcome["status"] == "terminal"),
        "cycle": sum(1 for outcome in fixed_prime_walks.values() if outcome["status"] == "cycle"),
        "timeout": sum(1 for outcome in fixed_prime_walks.values() if outcome["status"] == "timeout"),
        "max_steps_observed": max(
            int(outcome["steps"]) for outcome in fixed_prime_walks.values()
        ),
        "samples_by_length": sorted(
            [
                (state, int(outcome["steps"]), str(outcome["status"]))
                for state, outcome in fixed_prime_walks.items()
            ],
            key=lambda item: item[1],
            reverse=True,
        )[:5],
        "outcomes": {state: {"status": outcome["status"], "steps": outcome["steps"]} for state, outcome in fixed_prime_walks.items()},
        "longest_paths": sorted(
            ((state, int(outcome["steps"]), str(outcome["status"])) for state, outcome in fixed_prime_walks.items()),
            key=lambda item: (-item[1], item[0]),
        )[:10],
    }
    monotone_chain_summary = None
    if max_chain_bound is not None:
        monotone_chain_summary = verify_monotone_chain_bound(
            max_chain_bound,
            scan_steps=max_chain_scan,
            transitions=transitions,
        )
    round_trip_errors = validate_full_round_trip()
    return {
        "register_count": len(REGISTERS),
        "state_space_size": len(all_signed_state_vectors()),
        "start_signed": start_vector,
        "start_value": start_value,
        "start_decoded_signed": decode_signed_state(start_value),
        "start_decoded_names": decode_tuple(start_value),
        "transitions": summarize_transitions(transitions=transitions),
        "transition_source": transition_source,
        "transition_source_path": transition_source_path,
        "transition_source_summary": transition_source_summary,
        "basin_profile": build_space_stats(basin_graph),
        "full_space_profile": build_space_stats(full_graph),
        "basin_path": [
            {
                "step": index + 1,
                "value": source,
                "transition": transition.name,
                "next": target,
                "fraction": str(transition_fraction(transition)),
                "source_signed": decode_signed_state(source),
                "next_signed": decode_signed_state(target),
            }
            for index, (source, transition, target) in enumerate(basin_trail)
        ],
        "round_trip_checks": {
            "status": "ok" if not round_trip_errors else "failed",
            "failure_count": len(round_trip_errors),
            "failures": round_trip_errors,
        },
        "fixed_prime_walk_summary": fixed_prime_summary,
        "fixed_prime_basin_walks": summarize_deterministic_basin_walks(
            max_steps=fixed_prime_steps,
            transitions=transitions,
        ),
        "fixed_prime_vs_explicit_summary": summarize_fixed_vs_explicit_dynamics(
            max_steps=explicit_steps,
            transitions=transitions,
        ),
        "fixed_prime_walks": fixed_prime_walks,
        "fixed_prime_chain_bound_check": monotone_chain_summary,
    }


def print_summary_report(
    start_value: int,
    start_vector: tuple[int, ...],
    transitions: Sequence[Transition] = TOY_TRANSITIONS,
) -> None:
    data = summarize(start_vector, transitions=transitions)
    print("Toy DASHI transition fractions:")
    for summary in data["transitions"]:
        print(
            f"- {summary['name']}: {summary['fraction']} ({summary['description']})"
        )
    print("Reference start state (symbolic):", data["start_signed"])
    print("Reference start state (decode):", data["start_decoded_signed"])
    print("Decoded start state:", decode_state(data["start_value"]))
    print("Encoded round-trip status:", data["round_trip_checks"]["status"])
    print(f"Encoded round-trip failures: {data['round_trip_checks']['failure_count']}")
    print("Full encoded space profile:")
    for key, value in data["full_space_profile"].items():
        print(f"- {key}: {value}")
    print("Basin summary:")
    summarize_graph(
        build_graph(start_value, max_depth=8, transitions=transitions),
        limit=8,
        title="Basin",
    )
    print("Basin path (up to 12 transitions):")
    for step in data["basin_path"]:
        print(
            f"  {step['step']}. {step['transition']}: "
            f"{step['source_signed']} -> {step['next_signed']} ({step['fraction']})"
        )
    if not data["basin_path"]:
        print("  No transitions from the start state.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Phase 2 toy DASHI FRACTRAN experiments."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument(
        "--start",
        default=",".join(SYMBOL_BY_STATE[DEFAULT_START_STATE[reg.name]] for reg in REGISTERS),
        help="Comma-separated start state in {-1,0,+1} form.",
    )
    parser.add_argument("--max-depth", type=int, default=8, help="Basin build depth.")
    parser.add_argument("--max-steps", type=int, default=12, help="Max transitions to trace.")
    parser.add_argument(
        "--fixed-prime-steps",
        type=int,
        default=16,
        help="Max transitions to use for all fixed-prime walk summaries.",
    )
    parser.add_argument(
        "--compare-explicit-steps",
        type=int,
        default=None,
        help="Max transitions to use for fixed-prime vs explicit FRACTRAN comparison (defaults to --max-steps).",
    )
    parser.add_argument(
        "--max-chain-bound",
        type=int,
        default=None,
        help="Assert all fixed-prime trajectories are <= this monotone chain length. In JSON mode this defaults to 2 unless disabled.",
    )
    parser.add_argument(
        "--disable-chain-bound",
        action="store_true",
        help="Skip chain-bound assertion when running JSON artifact mode.",
    )
    parser.add_argument(
        "--max-chain-scan",
        type=int,
        default=128,
        help="Maximum step cap used when scanning fixed-prime monotone chains.",
    )
    parser.add_argument(
        "--agdas-path",
        default=None,
        help="Load and execute transitions parsed from optional AGDAS markers in this file.",
    )
    parser.add_argument(
        "--agdas-templates",
        action="store_true",
        help="Load and execute the built-in FRACDASH-side AGDAS template transitions.",
    )
    parser.add_argument(
        "--agdas-template-set",
        default="wave1",
        choices=("wave1", "wave2", "wave3", "physics1", "all"),
        help="Which FRACDASH-side AGDAS template set to execute.",
    )
    parser.add_argument(
        "--agdas-max-rules",
        type=int,
        default=None,
        help="Limit the number of parsed AGDAS transitions to include in the run.",
    )
    parser.add_argument("--check-only", action="store_true", help="Only report encode/decode checks.")
    args = parser.parse_args()
    if args.json and args.max_chain_bound is None and not args.disable_chain_bound:
        args.max_chain_bound = DEFAULT_CHAIN_BOUND

    transitions = TOY_TRANSITIONS
    transition_source = "toy"
    transition_source_path: str | None = None
    transition_source_summary: dict[str, object] | None = None

    if args.agdas_templates and args.agdas_path is not None:
        raise SystemExit("Choose either --agdas-templates or --agdas-path, not both.")

    if args.agdas_templates:
        bridge_transitions, bridge_summary = transitions_from_agdas_templates(
            template_set=args.agdas_template_set,
        )
        transitions = bridge_transitions
        transition_source = "agdas_templates"
        transition_source_path = None
        transition_source_summary = bridge_summary
    elif args.agdas_path is not None:
        bridge_transitions, bridge_summary = transitions_from_agdas(
            args.agdas_path,
            max_rules=args.agdas_max_rules,
        )
        if not bridge_transitions:
            raise SystemExit(f"no AGDAS transitions loaded from {args.agdas_path}")
        transitions = bridge_transitions
        transition_source = "agdas"
        transition_source_path = str(Path(args.agdas_path))
        transition_source_summary = bridge_summary

    start_vector = parse_signed_vector(args.start)
    start_value = encode_signed_state({reg.name: start_vector[idx] for idx, reg in enumerate(REGISTERS)})
    basin_graph = build_graph(start_value, max_depth=args.max_depth, transitions=transitions)
    full_graph = build_full_space_graph(transitions=transitions)
    round_trip_errors = validate_full_round_trip()

    if args.check_only:
        result = {
            "status": "ok" if not round_trip_errors else "failed",
            "failure_count": len(round_trip_errors),
            "failures": round_trip_errors,
        }
        print(json.dumps(result, indent=2))
        return

    basin = {
        "path": [
            {
                "step": index + 1,
                "value": source,
                "transition": transition.name,
                "next": target,
                "fraction": str(transition_fraction(transition)),
            }
            for index, (source, transition, target) in enumerate(
                trace_steps(start_value, max_steps=args.max_steps, transitions=transitions)
            )
        ],
        "profile": build_space_stats(basin_graph),
        "graph": {
            str(source): {transition.name: next_state for transition, next_state in edges}
            for source, edges in basin_graph.items()
        },
    }

    if args.json:
        data = summarize(
            start_vector,
            fixed_prime_steps=args.fixed_prime_steps,
            max_steps=args.max_steps,
            compare_explicit_steps=args.compare_explicit_steps
            or args.max_steps,
            max_chain_bound=args.max_chain_bound,
            max_chain_scan=args.max_chain_scan,
            transitions=transitions,
            transition_source=transition_source,
            transition_source_path=transition_source_path,
            transition_source_summary=transition_source_summary,
        )
        data["start_value"] = start_value
        data["start_signed_vector"] = start_vector
        data["basin_profile_for_start"] = basin["profile"]
        data["full_space_nodes"] = len(full_graph)
        data["start_graph"] = basin["graph"]
        data["fixed_prime_steps"] = args.fixed_prime_steps
        if args.max_chain_bound is not None:
            chain_check = data["fixed_prime_chain_bound_check"]
            if isinstance(chain_check, dict) and not chain_check["verified"]:
                print("fixed-prime chain bound assertion failed", file=sys.stderr)
                print(json.dumps(chain_check, indent=2), file=sys.stderr)
                raise SystemExit(1)
        print(json.dumps(data, indent=2))
        return

    print_summary_report(start_value, start_vector, transitions=transitions)
    print(f"Start state override: {start_vector}")
    print(f"Start encoded value: {start_value}")
    print("Basin profile:")
    for key, value in basin["profile"].items():
        print(f"- {key}: {value}")
    print("Basin transitions:")
    for transition in basin["path"]:
        print(
            f"- step={transition['step']} value={transition['value']} transition={transition['transition']} next={transition['next']} fraction={transition['fraction']}"
        )
    print("Full encoded space:")
    full_profile = build_space_stats(full_graph)
    for key, value in full_profile.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
