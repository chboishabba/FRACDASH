#!/usr/bin/env python3
"""Validate the concrete numeric FRACTRAN macro realization for physics1.

This script treats the signed exponent IR as the semantic surface and checks
that the chosen paired-prime realization executes the normalized unit-step
macros exactly on the saved `physics1` rule slice.

For each exported rule it verifies:

1. the macro fractions are concrete numeric FRACTRAN fractions,
2. standard ordered FRACTRAN execution applies them in the intended order,
3. the final encoded integer decodes to the expected target state,
4. the exclusivity invariant (one active state-prime per register) is preserved
   at every intermediate step.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from bridge_macro_soundness import MacroCheckRecord, check_macro_soundness_from_export
from export_physics1_deltas import REGISTERS, physics1_delta_records


def check_macro_soundness() -> tuple[list[MacroCheckRecord], dict[str, object]]:
    records, summary = physics1_delta_records()
    return check_macro_soundness_from_export(records=records, summary=summary, registers=REGISTERS, template_set="physics1")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the concrete numeric FRACTRAN macro realization for physics1.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON output.")
    parser.add_argument("--canonical", action="store_true", help="Save to canonical benchmark paths.")
    args = parser.parse_args()

    records, summary = check_macro_soundness()
    payload = {
        "summary": summary,
        "records": [asdict(record) for record in records],
    }

    output_paths: list[Path] = []
    if args.output:
        output_paths.append(args.output)

    if args.canonical:
        results_dir = Path(__file__).resolve().parents[1] / "benchmarks" / "results"
        output_paths.append(results_dir / "physics1_macro_soundness_canonical.json")

    for path in output_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported to {path}")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    if not output_paths:
        print("Physics1 macro soundness")
        print(f"Rules checked: {summary['checked_rules']}")
        print(f"Passed: {summary['passed_rules']}")
        print(f"Macro soundness: {summary['macro_soundness']}")
        for record in records:
            print(
                f"- {record.name}: passed={record.passed} "
                f"order={record.exact_order_preserved} final={record.final_matches_target}"
            )


if __name__ == "__main__":
    main()
