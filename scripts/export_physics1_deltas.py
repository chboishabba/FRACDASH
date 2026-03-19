#!/usr/bin/env python3
"""Export the physics1 template slice as explicit signed-delta data.

This script treats the Python bridge templates as an executable oracle/spec
runner for delta extraction. It does not claim that Python is the ground truth
for DASHI semantics. The intended loop is:

1. Python exposes concrete source -> target transitions and signed deltas.
2. Agda proves the corresponding StepDelta statement at the signed IR level.
3. FRACTRAN later realizes those signed deltas via a nonnegative encoding.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from fractions import Fraction
from dataclasses import asdict, dataclass
from pathlib import Path

from bridge_macro_common import delta_vector, encode_state_integer, macro_fractions, unit_steps, vectorize_state


REGISTERS = ("R1", "R2", "R3", "R4")
STATE_TO_INT = {"negative": -1, "zero": 0, "positive": 1}


def _load_agdas_bridge_module():
    bridge_path = Path(__file__).resolve().parent / "agdas_bridge.py"
    module_name = "agdas_bridge_physics1_delta_export"
    spec = importlib.util.spec_from_file_location(module_name, bridge_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load agdas bridge module from {bridge_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


@dataclass(frozen=True)
class Physics1DeltaRecord:
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
    source = {register: "zero" for register in REGISTERS}
    for register, state in condition.items():
        source[register] = state
    for register, state in action.items():
        if register not in condition:
            # If a register is in action but not in condition, we assume it was zero
            # unless it's being set to negative, which shouldn't happen in simple cases
            # but we follow the logic from the previous version.
            source[register] = "zero"
    return source


def _apply_action(source: dict[str, str], action: dict[str, str]) -> dict[str, str]:
    target = dict(source)
    target.update(action)
    return target


def physics1_delta_records() -> tuple[list[Physics1DeltaRecord], dict[str, object]]:
    bridge = _load_agdas_bridge_module()
    signed_state_primes = bridge.DEFAULT_SIGNED_STATE_PRIMES
    template_rules = [
        rule for rule in bridge._template_rules("physics1") if set(rule.condition) | set(rule.action) <= set(REGISTERS)
    ]

    records: list[Physics1DeltaRecord] = []
    for rule in template_rules:
        source_state = _base_source_state(dict(rule.condition), dict(rule.action))
        target_state = _apply_action(source_state, dict(rule.action))
        source_vector = vectorize_state(source_state, REGISTERS)
        target_vector = vectorize_state(target_state, REGISTERS)
        delta_values = delta_vector(source_vector, target_vector)
        source_integer = encode_state_integer(source_state, REGISTERS, signed_state_primes)
        target_integer = encode_state_integer(target_state, REGISTERS, signed_state_primes)
        norm_1 = sum(abs(x) for x in delta_values)
        norm_inf = max((abs(x) for x in delta_values), default=0)
        normalized_unit_steps = unit_steps(delta_values)
        macro_fraction_strings = macro_fractions(source_state, normalized_unit_steps, REGISTERS, signed_state_primes)

        records.append(
            Physics1DeltaRecord(
                name=rule.name,
                module=rule.module,
                description=rule.description,
                source_state=source_state,
                target_state=target_state,
                source_vector=source_vector,
                target_vector=target_vector,
                delta_vector=delta_values,
                fraction=str(bridge._rule_fraction(rule)),
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
        "template_set": "physics1",
        "registers": list(REGISTERS),
        "record_count": len(records),
        "role": "python_oracle_for_delta_extraction",
        "signed_state_primes": signed_state_primes,
        "macro_encoding": "three-state-prime swap per register",
        "macro_ordering": "register order R1,R2,R3,R4 with repeated unit steps in that order",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the physics1 template slice as explicit signed deltas.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output to stdout.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON output.")
    parser.add_argument("--canonical", action="store_true", help="Save to the canonical benchmark path.")
    args = parser.parse_args()

    records, summary = physics1_delta_records()
    payload = {
        "summary": summary,
        "records": [asdict(record) for record in records],
    }

    output_paths = []
    if args.output:
        output_paths.append(args.output)
    
    if args.canonical:
        results_dir = Path(__file__).resolve().parents[1] / "benchmarks" / "results"
        output_paths.append(results_dir / "physics1_deltas_canonical.json")
        # Also save a timestamped one for reproducibility if desired, 
        # but the request says "keep one canonical named artifact for regression"
        # and "keep timestamped outputs for experiments".
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        output_paths.append(results_dir / f"{timestamp}_physics1_deltas.json")

    for path in output_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported to {path}")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    if not output_paths:
        print("Physics1 delta export")
        print(f"Records: {summary['record_count']}")
        for record in records:
            print(f"- {record.name}: {record.source_vector} -> {record.target_vector} delta={record.delta_vector} (norm1={record.delta_norm_1})")


if __name__ == "__main__":
    main()
