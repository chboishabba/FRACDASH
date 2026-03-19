#!/usr/bin/env python3
"""Validate the concrete numeric FRACTRAN macro realization for a physics-family slice."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from bridge_macro_soundness import MacroCheckRecord, check_macro_soundness_from_export
from export_physics_family_deltas import REGISTER_NAMES, SUPPORTED_TEMPLATE_SETS, physics_family_delta_records


def check_macro_soundness(template_set: str) -> tuple[list[MacroCheckRecord], dict[str, object]]:
    records, summary = physics_family_delta_records(template_set)
    return check_macro_soundness_from_export(records=records, summary=summary, registers=REGISTER_NAMES, template_set=template_set)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the concrete numeric FRACTRAN macro realization for a physics-family slice.")
    parser.add_argument("--template", required=True, choices=SUPPORTED_TEMPLATE_SETS)
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON output.")
    args = parser.parse_args()

    records, summary = check_macro_soundness(args.template)
    payload = {"summary": summary, "records": [asdict(record) for record in records]}

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported to {args.output}")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    if not args.output:
        print(f"{args.template} macro soundness")
        print(f"Rules checked: {summary['checked_rules']}")
        print(f"Passed: {summary['passed_rules']}")
        print(f"Macro soundness: {summary['macro_soundness']}")
        for record in records:
            print(f"- {record.name}: passed={record.passed} order={record.exact_order_preserved} final={record.final_matches_target}")


if __name__ == "__main__":
    main()
