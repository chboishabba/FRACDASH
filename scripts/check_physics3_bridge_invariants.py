#!/usr/bin/env python3
"""Check the first end-to-end bridge invariants on the physics3 slice."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bridge_core_validators import BridgeCoreValidatorRecord, validate_bridge_core
from check_physics3_macro_soundness import check_macro_soundness
from export_physics3_deltas import REGISTER_NAMES


def check_physics3_bridge_invariants() -> tuple[list[BridgeCoreValidatorRecord], dict[str, object]]:
    macro_records, macro_summary = check_macro_soundness()
    records, validator_summary = validate_bridge_core(
        macro_records=macro_records,
        macro_summary=macro_summary,
        registers=REGISTER_NAMES,
        template_set="physics3",
    )
    return records, {
        "template_set": "physics3",
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
        "scope": "bridge-local compiler correctness on the physics3 slice",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check bridge-local invariants on the physics3 slice.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON output.")
    args = parser.parse_args()

    records, summary = check_physics3_bridge_invariants()
    payload = {"summary": summary, "records": [asdict(record) for record in records]}

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported to {args.output}")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    if not args.output:
        print("Physics3 bridge invariants")
        print(f"Rules checked: {summary['checked_rules']}")
        print(f"Passed: {summary['passed_rules']}")
        print(f"Bridge invariants pass: {summary['bridge_invariants_pass']}")
        print(f"Regime-valid: {summary['regime_valid_rules']}/{summary['checked_rules']} pass={summary['regime_validator_pass']}")
        print(f"Dynamical classes: {summary['dynamical_class_counts']}")
        for record in records:
            print(
                f"- {record.name}: source_preserved={record.source_signature_conserved} "
                f"class={record.dynamical_class} residual_l1={record.residual_l1_sequence}"
            )


if __name__ == "__main__":
    main()
