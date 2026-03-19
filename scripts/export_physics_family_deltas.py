#!/usr/bin/env python3
"""Export a 6-register physics-family template slice as explicit signed-delta data."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path

from agdas_physics2_state import PRIMES, REGISTERS
from bridge_macro_common import delta_vector, encode_state_integer, macro_fractions, unit_steps, vectorize_state


REGISTER_NAMES = tuple(reg.name for reg in REGISTERS)
SUPPORTED_TEMPLATE_SETS = ("physics15", "physics19", "physics20", "physics21", "physics22")


def _load_agdas_bridge_module(module_name: str):
    bridge_path = Path(__file__).resolve().parent / "agdas_bridge.py"
    spec = importlib.util.spec_from_file_location(module_name, bridge_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load agdas bridge module from {bridge_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


@dataclass(frozen=True)
class PhysicsFamilyDeltaRecord:
    name: str
    module: str
    description: str
    source_state: dict[str, str]
    target_state: dict[str, str]
    source_vector: list[int]
    target_vector: list[int]
    delta_vector: list[int]
    fraction: str
    source_integer: int
    target_integer: int
    delta_norm_1: int
    delta_norm_inf: int
    normalized_unit_steps: list[list[int]]
    macro_fraction_strings: list[str]
    macro_length: int


def _base_source_state(condition: dict[str, str], action: dict[str, str]) -> dict[str, str]:
    source = {register: "zero" for register in REGISTER_NAMES}
    for register, state in condition.items():
        source[register] = state
    for register in action:
        if register not in condition:
            source[register] = "zero"
    return source


def _apply_action(source: dict[str, str], action: dict[str, str]) -> dict[str, str]:
    target = dict(source)
    target.update(action)
    return target


def _rule_fraction(source_state: dict[str, str], target_state: dict[str, str]) -> str:
    numerator = 1
    denominator = 1
    for register in REGISTER_NAMES:
        source_label = source_state[register]
        target_label = target_state[register]
        if source_label == target_label:
            continue
        denominator *= PRIMES[register][source_label]
        numerator *= PRIMES[register][target_label]
    return str(Fraction(numerator, denominator))


def physics_family_delta_records(template_set: str) -> tuple[list[PhysicsFamilyDeltaRecord], dict[str, object]]:
    if template_set not in SUPPORTED_TEMPLATE_SETS:
        raise ValueError(f"unsupported template set {template_set}")

    bridge = _load_agdas_bridge_module(f"agdas_bridge_{template_set}_delta_export")
    template_rules = [
        rule for rule in bridge._template_rules(template_set) if set(rule.condition) | set(rule.action) <= set(REGISTER_NAMES)
    ]

    records: list[PhysicsFamilyDeltaRecord] = []
    for rule in template_rules:
        source_state = _base_source_state(dict(rule.condition), dict(rule.action))
        target_state = _apply_action(source_state, dict(rule.action))
        source_vector = vectorize_state(source_state, REGISTER_NAMES)
        target_vector = vectorize_state(target_state, REGISTER_NAMES)
        delta_values = delta_vector(source_vector, target_vector)
        source_integer = encode_state_integer(source_state, REGISTER_NAMES, PRIMES)
        target_integer = encode_state_integer(target_state, REGISTER_NAMES, PRIMES)
        norm_1 = sum(abs(x) for x in delta_values)
        norm_inf = max((abs(x) for x in delta_values), default=0)
        normalized_unit_steps = unit_steps(delta_values)
        macro_fraction_strings = macro_fractions(source_state, normalized_unit_steps, REGISTER_NAMES, PRIMES)

        records.append(
            PhysicsFamilyDeltaRecord(
                name=rule.name,
                module=rule.module,
                description=rule.description,
                source_state=source_state,
                target_state=target_state,
                source_vector=source_vector,
                target_vector=target_vector,
                delta_vector=delta_values,
                fraction=_rule_fraction(source_state, target_state),
                source_integer=source_integer,
                target_integer=target_integer,
                delta_norm_1=norm_1,
                delta_norm_inf=norm_inf,
                normalized_unit_steps=normalized_unit_steps,
                macro_fraction_strings=macro_fraction_strings,
                macro_length=norm_1,
            )
        )

    return records, {
        "template_set": template_set,
        "registers": list(REGISTER_NAMES),
        "record_count": len(records),
        "role": "python_oracle_for_delta_extraction",
        "signed_state_primes": PRIMES,
        "macro_encoding": "three-state-prime swap per register",
        "macro_ordering": "register order R1,R2,R3,R4,R5,R6 with repeated unit steps in that order",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a physics-family template slice as explicit signed deltas.")
    parser.add_argument("--template", required=True, choices=SUPPORTED_TEMPLATE_SETS)
    parser.add_argument("--json", action="store_true", help="Emit JSON output to stdout.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON output.")
    args = parser.parse_args()

    records, summary = physics_family_delta_records(args.template)
    payload = {"summary": summary, "records": [asdict(record) for record in records]}

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported to {args.output}")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    if not args.output:
        print(f"{args.template} delta export")
        print(f"Records: {summary['record_count']}")
        for record in records:
            print(f"- {record.name}: {record.source_vector} -> {record.target_vector} delta={record.delta_vector}")


if __name__ == "__main__":
    main()
