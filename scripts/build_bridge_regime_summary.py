#!/usr/bin/env python3
"""Build a canonical cross-slice bridge regime summary table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_bridge_core_validators import _load_template
from bridge_core_validators import validate_bridge_core


TEMPLATES = ("physics1", "physics3", "physics15", "physics19", "physics20", "physics21", "physics22")


def _summary_row(template: str) -> dict[str, object]:
    macro_records, macro_summary, registers = _load_template(template)
    records, summary = validate_bridge_core(
        macro_records=macro_records,
        macro_summary=macro_summary,
        registers=registers,
        template_set=template,
    )
    broken_old_invariants = sorted(
        record.name for record in records if not (record.source_signature_conserved and record.source_prime_product_conserved)
    )
    return {
        "template_set": template,
        "rule_count": summary["checked_rules"],
        "macro_length_histogram": summary["macro_length_histogram"],
        "max_macro_length": summary["max_macro_length"],
        "terminal_basin_count": len(summary["terminal_basin_counts"]),
        "conservative_contracting": summary["dynamical_class_counts"].get("conservative_contracting", 0),
        "transmuting_contracting": summary["dynamical_class_counts"].get("transmuting_contracting", 0),
        "transmuting_contracting_nonunit": summary["dynamical_class_counts"].get("transmuting_contracting_nonunit", 0),
        "regime_valid_rules": summary["regime_valid_rules"],
        "bridge_core_validators_pass": summary["bridge_core_validators_pass"],
        "notable_broken_old_invariants": broken_old_invariants,
    }


def _markdown_table(rows: list[dict[str, object]]) -> str:
    header = [
        "| Template | Rules | Max Macro | Basin Count | Conservative | Transmuting | Transmuting Nonunit | Regime-Valid | Bridge-Core Pass | Broken Old Invariants |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: | :--- |",
    ]
    body = []
    for row in rows:
        broken = ", ".join(row["notable_broken_old_invariants"]) if row["notable_broken_old_invariants"] else "-"
        body.append(
            f"| `{row['template_set']}` | {row['rule_count']} | {row['max_macro_length']} | {row['terminal_basin_count']} | "
            f"{row['conservative_contracting']} | {row['transmuting_contracting']} | {row['transmuting_contracting_nonunit']} | "
            f"{row['regime_valid_rules']}/{row['rule_count']} | {'yes' if row['bridge_core_validators_pass'] else 'no'} | {broken} |"
        )
    return "\n".join(header + body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a canonical cross-slice bridge regime summary table.")
    parser.add_argument("--json-output", type=Path, help="Optional path to write JSON output.")
    parser.add_argument("--md-output", type=Path, help="Optional path to write Markdown table.")
    args = parser.parse_args()

    rows = [_summary_row(template) for template in TEMPLATES]
    payload = {"templates": list(TEMPLATES), "rows": rows}
    markdown = _markdown_table(rows)

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Exported JSON to {args.json_output}")

    if args.md_output:
        args.md_output.parent.mkdir(parents=True, exist_ok=True)
        args.md_output.write_text(markdown + "\n", encoding="utf-8")
        print(f"Exported Markdown to {args.md_output}")

    if not args.json_output and not args.md_output:
        print(markdown)


if __name__ == "__main__":
    main()
