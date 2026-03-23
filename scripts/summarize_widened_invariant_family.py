#!/usr/bin/env python3
"""Summarize the widened physics family against regime usage and invariant outcomes."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"
TEMPLATES = ("physics15", "physics19", "physics20", "physics21", "physics22")


def _latest_result(pattern: str) -> Path:
    matches = sorted(RESULTS.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"no matches for {pattern}")
    return matches[-1]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_paths(template: str) -> tuple[Path, Path]:
    inv = _latest_result(f"*-physics-invariants-{template}.json")
    phase2 = _latest_result(f"*-agdas-{template}-phase2.json")
    return inv, phase2


def _row(template: str) -> dict[str, object]:
    inv_path, phase2_path = _artifact_paths(template)
    inv = _load_json(inv_path)
    phase2 = _load_json(phase2_path)

    status = inv.get("execution_status", {}).get("bridge_instances", {}).get(template, {})
    reentry = inv.get("observable_surrogates", {}).get("reentry_flow", {})
    geo = inv.get("physics_target_suite", {}).get("statistical_laws", {}).get("geodesic_like_flow", {})
    curv = inv.get("physics_target_suite", {}).get("statistical_laws", {}).get("curvature_like_concentration", {})
    defect = inv.get("physics_target_suite", {}).get("statistical_laws", {}).get("defect_attraction", {})
    profile = phase2.get("full_space_profile", {})
    walk = phase2.get("fixed_walk_summary", {})

    return {
        "template_set": template,
        "invariant_artifact": str(inv_path.relative_to(ROOT)),
        "phase2_artifact": str(phase2_path.relative_to(ROOT)),
        "execution_status": {
            "regime_class": status.get("regime_class"),
            "family_tag": status.get("family_tag"),
            "regime_usage": status.get("regime_usage"),
            "admissibility": status.get("admissibility"),
        },
        "recurrent_core": {
            "deterministic_edges": inv.get("deterministic_edges", profile.get("edges")),
            "terminal_states": profile.get("terminal_states"),
            "longest_chain": profile.get("longest_chain"),
            "cycle_starts": walk.get("cycle"),
            "timeout_states": walk.get("timeout"),
        },
        "geometry_surrogates": {
            "best_candidate": inv.get("best_candidate", {}).get("name"),
            "geodesic_like_near_min_ratio": geo.get("near_min_ratio"),
            "curvature_like_mean_neighbor_spread": curv.get("mean_neighbor_spread"),
            "defect_nonincrease_ratio": defect.get("defect_nonincrease_ratio"),
        },
        "reentry_flow": {
            "shell_to_interior": reentry.get("shell_to_interior"),
            "boundary_to_interior": reentry.get("boundary_to_interior"),
            "boundary_to_interior_ratio": reentry.get("boundary_to_interior_ratio"),
        },
    }


def _interpretation(rows: list[dict[str, object]]) -> list[str]:
    notes: list[str] = []
    if rows:
        best_reentry = max(rows, key=lambda row: row["reentry_flow"].get("boundary_to_interior") or -1)
        notes.append(
            f"Highest direct boundary-to-interior re-entry is `{best_reentry['template_set']}` with `{best_reentry['reentry_flow'].get('boundary_to_interior')}`."
        )
        best_edges = max(rows, key=lambda row: row["recurrent_core"].get("deterministic_edges") or -1)
        notes.append(
            f"Largest deterministic recurrent core is `{best_edges['template_set']}` with `{best_edges['recurrent_core'].get('deterministic_edges')}` edges."
        )
    mixed = [row for row in rows if row["execution_status"].get("regime_usage", "").startswith("mixed")]
    if mixed:
        notes.append(
            "Mixed transmuting usage coexists with strong geometry-surrogate values; widened slices should be read through regime usage, not against the conservative-only lock."
        )
    return notes


def _markdown(rows: list[dict[str, object]], notes: list[str]) -> str:
    header = [
        "# Widened Invariant Family Summary",
        "",
        "| Template | Regime Usage | Det. Edges | Terminal | Longest Chain | Boundary->Interior | Geo Near-Min | Curvature Spread | Best Candidate |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |",
    ]
    body = []
    for row in rows:
        body.append(
            f"| `{row['template_set']}` | {row['execution_status']['regime_usage'] or '-'} | "
            f"{row['recurrent_core']['deterministic_edges'] or '-'} | "
            f"{row['recurrent_core']['terminal_states'] or '-'} | "
            f"{row['recurrent_core']['longest_chain'] or '-'} | "
            f"{row['reentry_flow']['boundary_to_interior'] or '-'} | "
            f"{row['geometry_surrogates']['geodesic_like_near_min_ratio'] if row['geometry_surrogates']['geodesic_like_near_min_ratio'] is not None else '-'} | "
            f"{row['geometry_surrogates']['curvature_like_mean_neighbor_spread'] if row['geometry_surrogates']['curvature_like_mean_neighbor_spread'] is not None else '-'} | "
            f"{row['geometry_surrogates']['best_candidate'] or '-'} |"
        )
    lines = header + body + ["", "## Interpretation", ""]
    lines.extend(f"- {note}" for note in notes)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize widened invariant family against regime usage.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--md-output", type=Path)
    args = parser.parse_args()

    rows = [_row(template) for template in TEMPLATES]
    notes = _interpretation(rows)
    payload = {
        "date": date.today().isoformat(),
        "templates": list(TEMPLATES),
        "rows": rows,
        "interpretation": notes,
    }
    markdown = _markdown(rows, notes)

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.json_output}")
    if args.md_output:
        args.md_output.parent.mkdir(parents=True, exist_ok=True)
        args.md_output.write_text(markdown + "\n", encoding="utf-8")
        print(f"wrote {args.md_output}")
    if not args.json_output and not args.md_output:
        print(markdown)


if __name__ == "__main__":
    main()
