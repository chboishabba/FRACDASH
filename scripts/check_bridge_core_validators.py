#!/usr/bin/env python3
"""Run the canonical bridge-core validators on a closed bridge slice."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from bridge_core_validators import validate_bridge_core
from check_physics1_macro_soundness import check_macro_soundness as check_physics1_macro_soundness
from check_physics15_macro_soundness import check_macro_soundness as check_physics15_macro_soundness
from check_physics3_macro_soundness import check_macro_soundness as check_physics3_macro_soundness
from check_physics_family_macro_soundness import check_macro_soundness as check_physics_family_macro_soundness
from export_physics1_deltas import REGISTERS as PHYSICS1_REGISTERS
from export_physics15_deltas import REGISTER_NAMES as PHYSICS15_REGISTERS
from export_physics_family_deltas import REGISTER_NAMES as PHYSICS_FAMILY_REGISTERS
from export_physics3_deltas import REGISTER_NAMES as PHYSICS3_REGISTERS


def _load_template(template_set: str) -> tuple[list[object], dict[str, object], tuple[str, ...]]:
    if template_set == "physics1":
        records, summary = check_physics1_macro_soundness()
        return records, summary, PHYSICS1_REGISTERS
    if template_set == "physics3":
        records, summary = check_physics3_macro_soundness()
        return records, summary, PHYSICS3_REGISTERS
    if template_set == "physics15":
        records, summary = check_physics15_macro_soundness()
        return records, summary, PHYSICS15_REGISTERS
    if template_set in {"physics19", "physics20", "physics21", "physics22"}:
        records, summary = check_physics_family_macro_soundness(template_set)
        return records, summary, PHYSICS_FAMILY_REGISTERS
    raise ValueError(f"unsupported template set {template_set}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the canonical bridge-core validators on a closed bridge slice.")
    parser.add_argument("--template", required=True, choices=["physics1", "physics3", "physics15", "physics19", "physics20", "physics21", "physics22"], help="Closed bridge slice to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output to stdout.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON output.")
    args = parser.parse_args()

    macro_records, macro_summary, registers = _load_template(args.template)
    records, summary = validate_bridge_core(
        macro_records=macro_records,
        macro_summary=macro_summary,
        registers=registers,
        template_set=args.template,
    )
    payload = {"summary": summary, "records": [asdict(record) for record in records]}

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported to {args.output}")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    if not args.output:
        print(f"Bridge-core validators: {args.template}")
        print(f"Rules checked: {summary['checked_rules']}")
        print(f"Passed: {summary['passed_rules']}")
        print(f"Bridge-core validators pass: {summary['bridge_core_validators_pass']}")
        print(f"Regime-valid: {summary['regime_valid_rules']}/{summary['checked_rules']} pass={summary['regime_validator_pass']}")
        print(f"Trajectory kinds: {summary['trajectory_kind_counts']}")
        print(f"Dynamical classes: {summary['dynamical_class_counts']}")
        print(f"Terminal basins: {summary['terminal_basin_counts']}")
        print(
            "Cost histograms: "
            f"macro={summary['macro_length_histogram']} "
            f"executed={summary['execution_length_histogram']} "
            f"contraction={summary['contraction_step_histogram']}"
        )
        for record in records:
            print(
                f"- {record.name}: passed={record.passed} "
                f"regime_valid={record.regime_valid} kind={record.trajectory_kind} residual_l1={record.residual_l1_sequence} "
                f"class={record.dynamical_class} terminal={record.terminal_state_key} macro={record.macro_length}"
            )


if __name__ == "__main__":
    main()
