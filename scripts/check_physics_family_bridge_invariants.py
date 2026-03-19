#!/usr/bin/env python3
"""Check bridge-local invariants on a physics-family slice."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from bridge_core_validators import BridgeCoreValidatorRecord, validate_bridge_core
from check_physics_family_macro_soundness import check_macro_soundness
from export_physics_family_deltas import REGISTER_NAMES, SUPPORTED_TEMPLATE_SETS


def check_bridge_invariants(template_set: str) -> tuple[list[BridgeCoreValidatorRecord], dict[str, object]]:
    macro_records, macro_summary = check_macro_soundness(template_set)
    records, validator_summary = validate_bridge_core(
        macro_records=macro_records,
        macro_summary=macro_summary,
        registers=REGISTER_NAMES,
        template_set=template_set,
    )
    return records, {
        "template_set": template_set,
        "checked_rules": len(records),
        "passed_rules": sum(1 for record in records if record.passed),
        "bridge_invariants_pass": validator_summary["bridge_core_validators_pass"],
        "regime_valid_rules": validator_summary["regime_valid_rules"],
        "regime_validator_pass": validator_summary["regime_validator_pass"],
        "conserved_quantity": validator_summary["conservation_validator"],
        "monotone_quantity": validator_summary["lyapunov_validator"],
        "transmutation_quantity": validator_summary["transmutation_validator"],
        "trajectory_kind_counts": validator_summary["trajectory_kind_counts"],
        "dynamical_class_counts": validator_summary["dynamical_class_counts"],
        "terminal_basin_counts": validator_summary["terminal_basin_counts"],
        "macro_length_histogram": validator_summary["macro_length_histogram"],
        "execution_length_histogram": validator_summary["execution_length_histogram"],
        "contraction_step_histogram": validator_summary["contraction_step_histogram"],
        "scope": f"bridge-local compiler correctness on the {template_set} slice",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check bridge-local invariants on a physics-family slice.")
    parser.add_argument("--template", required=True, choices=SUPPORTED_TEMPLATE_SETS)
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON output.")
    args = parser.parse_args()

    records, summary = check_bridge_invariants(args.template)
    payload = {"summary": summary, "records": [asdict(record) for record in records]}

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported to {args.output}")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    if not args.output:
        print(f"{args.template} bridge invariants")
        print(f"Rules checked: {summary['checked_rules']}")
        print(f"Passed: {summary['passed_rules']}")
        print(f"Bridge invariants pass: {summary['bridge_invariants_pass']}")
        print(f"Regime-valid: {summary['regime_valid_rules']}/{summary['checked_rules']} pass={summary['regime_validator_pass']}")
        print(f"Trajectory kinds: {summary['trajectory_kind_counts']}")
        print(f"Dynamical classes: {summary['dynamical_class_counts']}")
        for record in records:
            print(
                f"- {record.name}: source_preserved={record.source_signature_conserved} "
                f"class={record.dynamical_class} residual_l1={record.residual_l1_sequence}"
            )


if __name__ == "__main__":
    main()
