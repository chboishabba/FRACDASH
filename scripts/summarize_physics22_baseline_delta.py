#!/usr/bin/env python3
"""Summarize the delta from physics21 to the active physics22 baseline."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _phase2(template: str) -> dict[str, object]:
    return _load(RESULTS / f"2026-03-15-agdas-{template}-phase2.json")


def _invariants(template: str) -> dict[str, object]:
    return _load(RESULTS / f"2026-03-23-physics-invariants-{template}.json")


def _payload() -> dict[str, object]:
    p21 = _phase2("physics21")
    p22 = _phase2("physics22")
    i21 = _invariants("physics21")
    i22 = _invariants("physics22")

    p21_profile = p21["full_space_profile"]
    p22_profile = p22["full_space_profile"]
    r21 = i21["observable_surrogates"]["reentry_flow"]
    r22 = i22["observable_surrogates"]["reentry_flow"]
    g21 = i21["physics_target_suite"]["statistical_laws"]["geodesic_like_flow"]
    g22 = i22["physics_target_suite"]["statistical_laws"]["geodesic_like_flow"]
    c21 = i21["physics_target_suite"]["statistical_laws"]["curvature_like_concentration"]
    c22 = i22["physics_target_suite"]["statistical_laws"]["curvature_like_concentration"]

    return {
        "date": date.today().isoformat(),
        "baseline_from": "physics21",
        "baseline_to": "physics22",
        "delta_summary": {
            "transition_count": {"from": p21["transition_count"], "to": p22["transition_count"], "delta": p22["transition_count"] - p21["transition_count"]},
            "deterministic_edges": {"from": p21_profile["edges"], "to": p22_profile["edges"], "delta": p22_profile["edges"] - p21_profile["edges"]},
            "terminal_states": {"from": p21_profile["terminal_states"], "to": p22_profile["terminal_states"], "delta": p22_profile["terminal_states"] - p21_profile["terminal_states"]},
            "longest_chain": {"from": p21_profile["longest_chain"], "to": p22_profile["longest_chain"], "delta": p22_profile["longest_chain"] - p21_profile["longest_chain"]},
            "boundary_to_interior": {"from": r21["boundary_to_interior"], "to": r22["boundary_to_interior"], "delta": r22["boundary_to_interior"] - r21["boundary_to_interior"]},
            "boundary_to_interior_ratio": {"from": r21["boundary_to_interior_ratio"], "to": r22["boundary_to_interior_ratio"], "delta": r22["boundary_to_interior_ratio"] - r21["boundary_to_interior_ratio"]},
            "geodesic_like_near_min_ratio": {"from": g21["near_min_ratio"], "to": g22["near_min_ratio"], "delta": g22["near_min_ratio"] - g21["near_min_ratio"]},
            "curvature_like_mean_neighbor_spread": {"from": c21["mean_neighbor_spread"], "to": c22["mean_neighbor_spread"], "delta": c22["mean_neighbor_spread"] - c21["mean_neighbor_spread"]},
        },
        "stable_quantities": {
            "best_candidate": {"from": i21["best_candidate"]["name"], "to": i22["best_candidate"]["name"]},
            "cycle_count": {"from": p21["fixed_walk_summary"]["cycle"], "to": p22["fixed_walk_summary"]["cycle"]},
            "fixed_walk_terminal": {"from": p21["fixed_walk_summary"]["terminal"], "to": p22["fixed_walk_summary"]["terminal"]},
            "timeout_states": {"from": p21["fixed_walk_summary"]["timeout"], "to": p22["fixed_walk_summary"]["timeout"]},
            "geodesic_like_exact_min_ratio": {"from": g21["exact_min_ratio"], "to": g22["exact_min_ratio"]},
        },
        "interpretation": [
            "The physics22 gain over physics21 is primarily a deterministic recurrent-core and re-entry gain, not a change in the fixed-walk cycle/terminal split.",
            "The main new effect is stronger direct boundary-to-interior reinjection while keeping the current geometry-surrogate values flat at the physics21 level.",
            "This makes physics22 a better comparison baseline for the next 6-register branch than physics21, because the gain is concentrated in the deterministic recurrent core where future refinements should compete.",
        ],
    }


def _markdown(payload: dict[str, object]) -> str:
    d = payload["delta_summary"]
    s = payload["stable_quantities"]
    lines = [
        "# Physics22 Baseline Delta",
        "",
        f"- Baseline comparison: `{payload['baseline_from']}` -> `{payload['baseline_to']}`",
        "",
        "## Delta",
        "",
        f"- Transition count: `{d['transition_count']['from']} -> {d['transition_count']['to']}` (`delta = {d['transition_count']['delta']}`)",
        f"- Deterministic edges: `{d['deterministic_edges']['from']} -> {d['deterministic_edges']['to']}` (`delta = {d['deterministic_edges']['delta']}`)",
        f"- Terminal states: `{d['terminal_states']['from']} -> {d['terminal_states']['to']}` (`delta = {d['terminal_states']['delta']}`)",
        f"- Longest chain: `{d['longest_chain']['from']} -> {d['longest_chain']['to']}` (`delta = {d['longest_chain']['delta']}`)",
        f"- Boundary->interior count: `{d['boundary_to_interior']['from']} -> {d['boundary_to_interior']['to']}` (`delta = {d['boundary_to_interior']['delta']}`)",
        f"- Boundary->interior ratio: `{d['boundary_to_interior_ratio']['from']} -> {d['boundary_to_interior_ratio']['to']}` (`delta = {d['boundary_to_interior_ratio']['delta']}`)",
        f"- Geodesic near-min ratio: `{d['geodesic_like_near_min_ratio']['from']} -> {d['geodesic_like_near_min_ratio']['to']}`",
        f"- Curvature spread: `{d['curvature_like_mean_neighbor_spread']['from']} -> {d['curvature_like_mean_neighbor_spread']['to']}`",
        "",
        "## Stable",
        "",
        f"- Best invariant candidate: `{s['best_candidate']['from']} -> {s['best_candidate']['to']}`",
        f"- Fixed-walk cycle count: `{s['cycle_count']['from']} -> {s['cycle_count']['to']}`",
        f"- Fixed-walk terminal count: `{s['fixed_walk_terminal']['from']} -> {s['fixed_walk_terminal']['to']}`",
        f"- Fixed-walk timeout count: `{s['timeout_states']['from']} -> {s['timeout_states']['to']}`",
        f"- Geodesic exact-min ratio: `{s['geodesic_like_exact_min_ratio']['from']} -> {s['geodesic_like_exact_min_ratio']['to']}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {line}" for line in payload["interpretation"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the delta from physics21 to physics22.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--md-output", type=Path)
    args = parser.parse_args()

    payload = _payload()
    markdown = _markdown(payload)

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
