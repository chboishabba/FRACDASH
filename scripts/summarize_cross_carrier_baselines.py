#!/usr/bin/env python3
"""Compare the active 6-register baseline against exploratory 8-register branches."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"
TEMPLATES = ("physics22", "carrier8_physics1", "carrier8_physics2", "carrier8_physics3", "carrier8_physics4", "carrier8_physics5", "carrier8_physics6")


def _latest(pattern: str) -> Path:
    matches = sorted(RESULTS.glob(pattern))
    if not matches:
        raise FileNotFoundError(pattern)
    return matches[-1]


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _phase2(template: str) -> dict[str, object]:
    if template == "physics22":
        path = _latest("*-agdas-physics22-phase2.json")
    else:
        path = _latest(f"*-agdas-{template.replace('_', '-')}-phase2.json")
    return _load(path)


def _invariants(template: str) -> dict[str, object]:
    return _load(_latest(f"*-physics-invariants-{template}.json"))


def _row(template: str) -> dict[str, object]:
    phase2 = _phase2(template)
    inv = _invariants(template)
    profile = phase2.get("full_space_profile", {})
    walk = phase2.get("fixed_walk_summary", {})
    obs = inv.get("observable_surrogates", {})
    reentry = obs.get("reentry_flow", {})
    boundary_return = obs.get("boundary_return_profile", {})
    transport_debt = obs.get("transport_debt_profile", {})
    geo = inv.get("physics_target_suite", {}).get("statistical_laws", {}).get("geodesic_like_flow", {})
    curv = inv.get("physics_target_suite", {}).get("statistical_laws", {}).get("curvature_like_concentration", {})

    return {
        "template_set": template,
        "carrier_family": inv.get("carrier_family", "carrier6"),
        "state_space_size": phase2.get("state_space_size", inv.get("state_space_size")),
        "deterministic_edges": profile.get("edges", inv.get("deterministic_edges")),
        "terminal_states": profile.get("terminal_states"),
        "longest_chain": profile.get("longest_chain"),
        "fixed_walk_cycle": walk.get("cycle"),
        "fixed_walk_terminal": walk.get("terminal"),
        "best_candidate": inv.get("best_candidate", {}).get("name"),
        "geodesic_like_near_min_ratio": geo.get("near_min_ratio"),
        "curvature_like_mean_neighbor_spread": curv.get("mean_neighbor_spread"),
        "boundary_to_interior": reentry.get("boundary_to_interior"),
        "boundary_to_interior_ratio": reentry.get("boundary_to_interior_ratio"),
        "boundary_return_profile": boundary_return,
        "transport_debt_profile": transport_debt,
    }


def _interpretation(rows: list[dict[str, object]]) -> list[str]:
    by_name = {row["template_set"]: row for row in rows}
    notes: list[str] = []
    p22 = by_name["physics22"]
    c1 = by_name["carrier8_physics1"]
    c2 = by_name["carrier8_physics2"]
    c3 = by_name["carrier8_physics3"]
    c4 = by_name["carrier8_physics4"]
    c5 = by_name["carrier8_physics5"]
    c6 = by_name["carrier8_physics6"]

    notes.append(
        "The active 6-register baseline remains easier to interpret: `physics22` combines strong direct re-entry with a still-disciplined recurrent core and a stable best-candidate signal."
    )
    notes.append(
        "`carrier8_physics1` is useful mainly as an observable branch: it exposes boundary-return and transport/debt structure, but its current invariant surface is weaker and its best candidate is not aligned with the 6-register lane."
    )
    notes.append(
        "`carrier8_physics2` is the stronger 8-register challenger: it has very strong cycle-bearing geometry and a full recurrent graph, but it is not yet directly comparable to `physics22` as a replacement baseline because its branch-local behavior is qualitatively different."
    )
    if c3.get("deterministic_edges") == c2.get("deterministic_edges"):
        notes.append(
            "`carrier8_physics3` does not yet move the carrier8 baseline meaningfully beyond `carrier8_physics2`; the added direct re-entry hook is currently too weak to change the main summary axes."
        )
    if (c4.get("boundary_to_interior") or 0) > (c2.get("boundary_to_interior") or 0):
        notes.append(
            "`carrier8_physics4` is the first carrier8 branch to make direct boundary-to-interior re-entry visible on the shared summary surface, which is exactly the weakness exposed by `carrier8_physics3`."
        )
    elif c4.get("deterministic_edges") == c2.get("deterministic_edges"):
        notes.append(
            "`carrier8_physics4` still leaves the shared summary surface flat against `carrier8_physics2`, so the earlier re-entry hook is not yet strong enough to count as a branch handoff."
        )
    if (c5.get("boundary_to_interior") or 0) > (c2.get("boundary_to_interior") or 0):
        notes.append(
            "`carrier8_physics5` is the first carrier8 branch to move boundary-to-interior recovery inside the sampled active basin by preempting the boundary discharge/join bottlenecks."
        )
    elif c5.get("deterministic_edges") == c2.get("deterministic_edges"):
        notes.append(
            "`carrier8_physics5` still leaves the shared summary surface flat against `carrier8_physics2`, so even subset-focused boundary recovery is not yet enough to force a carrier8 branch handoff."
        )
    if (c6.get("boundary_to_interior") or 0) > (c5.get("boundary_to_interior") or 0):
        notes.append(
            "`carrier8_physics6` keeps the new boundary recovery and adds a curvature-boost pulse after reentry; keep it as the current 8-register successor candidate if curvature improves without losing boundary gains."
        )
    elif c6.get("deterministic_edges") == c2.get("deterministic_edges"):
        notes.append(
            "`carrier8_physics6` does not yet change the shared cross-carrier surface beyond `carrier8_physics5`; if curvature stays low, `carrier8_physics2` remains the baseline."
        )
    if (c2.get("geodesic_like_near_min_ratio") or 0) > (p22.get("geodesic_like_near_min_ratio") or 0):
        notes.append(
            "The 8-register lane should now be treated as a serious parallel experiment track, not just instrumentation, because `carrier8_physics2` already beats the 6-register baseline on at least one geometry surrogate."
        )
    return notes


def _markdown(rows: list[dict[str, object]], notes: list[str]) -> str:
    lines = [
        "# Cross-Carrier Baseline Summary",
        "",
        "| Template | Carrier | States | Det. Edges | Terminal | Longest Chain | Fixed-Walk Cycle | Best Candidate | Geo Near-Min | Curvature Spread | Boundary->Interior |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['template_set']}` | `{row['carrier_family']}` | {row['state_space_size']} | {row['deterministic_edges']} | "
            f"{row['terminal_states']} | {row['longest_chain']} | {row['fixed_walk_cycle']} | {row['best_candidate']} | "
            f"{row['geodesic_like_near_min_ratio'] if row['geodesic_like_near_min_ratio'] is not None else '-'} | "
            f"{row['curvature_like_mean_neighbor_spread'] if row['curvature_like_mean_neighbor_spread'] is not None else '-'} | "
            f"{row['boundary_to_interior'] if row['boundary_to_interior'] is not None else '-'} |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "## Branch-Local Observables", ""])
    for row in rows:
        if row["boundary_return_profile"] or row["transport_debt_profile"]:
            lines.append(f"- `{row['template_set']}` boundary_return_profile = `{row['boundary_return_profile']}`")
            lines.append(f"- `{row['template_set']}` transport_debt_profile = `{row['transport_debt_profile']}`")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare physics22 against the exploratory 8-register branches.")
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
