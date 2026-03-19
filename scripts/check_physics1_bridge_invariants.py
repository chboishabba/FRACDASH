#!/usr/bin/env python3
"""Check the first end-to-end bridge invariants on the physics1 gold slice.

This checker stays at the bridge-correctness level. It does not claim any
physics meaning beyond the concrete `physics1` macro realization.

The current invariants are:

1. Conserved source signature:
   `R1` and `R2` stay fixed through `X -> Z -> Y` and across every macro
   intermediate. This is checked both as decoded state labels and as the
   corresponding paired-prime product.

2. Monotone execution Lyapunov:
   the residual `L1` distance from each decoded macro-intermediate state to the
   target signed-IR state decreases by exactly `1` at each macro step.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bridge_core_validators import BridgeCoreValidatorRecord, validate_bridge_core
from check_physics1_macro_soundness import check_macro_soundness
from export_physics1_deltas import REGISTERS


def check_physics1_bridge_invariants() -> tuple[list[BridgeCoreValidatorRecord], dict[str, object]]:
    macro_records, macro_summary = check_macro_soundness()
    records, validator_summary = validate_bridge_core(
        macro_records=macro_records,
        macro_summary=macro_summary,
        registers=REGISTERS,
        template_set="physics1",
    )
    return records, {
        "template_set": "physics1",
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
        "scope": "bridge-local compiler correctness on the physics1 gold slice",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check bridge-local invariants on the physics1 gold slice.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON output.")
    parser.add_argument("--canonical", action="store_true", help="Save to canonical benchmark paths.")
    args = parser.parse_args()

    records, summary = check_physics1_bridge_invariants()
    payload = {
        "summary": summary,
        "records": [asdict(record) for record in records],
    }

    output_paths: list[Path] = []
    if args.output:
        output_paths.append(args.output)

    if args.canonical:
        results_dir = Path(__file__).resolve().parents[1] / "benchmarks" / "results"
        output_paths.append(results_dir / "physics1_bridge_invariants_canonical.json")

    for path in output_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported to {path}")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    if not output_paths:
        print("Physics1 bridge invariants")
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
