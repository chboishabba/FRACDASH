#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOTT = ROOT / "monster" / "MonsterLean" / "BottPeriodicity.lean"
DEFAULT_OUT = ROOT / "benchmarks" / "results" / f"{date.today().isoformat()}-monsterlean-10walk-extract.json"

# Optional observed degeneracy table from prior 10-basin discussion.
JAMES_DEGENERACY_BY_LABEL = {
    "8080": 2,
    "1742": 11,
    "479": 32,
    "451": 27,
    "2875": 7,
    "8864": 2,
    "5990": 3,
    "496": 20,
    "1710": 7,
    "7570": 2,
}


@dataclass(frozen=True)
class Group:
    idx: int
    position: int
    label: str
    digits_preserved: int
    factors_removed: int
    symmetry_class: str


GROUP_RE = re.compile(
    r'\|\s*(\d+)\s*=>\s*\{\s*group_number\s*:=\s*\d+,\s*position\s*:=\s*(\d+),\s*digit_sequence\s*:=\s*"([^"]+)",\s*digits_preserved\s*:=\s*(\d+),\s*factors_removed\s*:=\s*(\d+)\s*\}'
)
SYMM_RE = re.compile(r"\|\s*(\d+)\s*=>\s*SymmetryClass\.([A-Za-z0-9_]+)")


def parse_groups(path: Path) -> list[Group]:
    text = path.read_text(encoding="utf-8")
    groups_raw = {int(m.group(1)): m.groups()[1:] for m in GROUP_RE.finditer(text)}
    symm_raw = {int(m.group(1)): m.group(2) for m in SYMM_RE.finditer(text)}
    groups: list[Group] = []
    for idx in range(10):
        if idx not in groups_raw:
            raise ValueError(f"missing group index {idx} in {path}")
        if idx not in symm_raw:
            raise ValueError(f"missing symmetry map for index {idx} in {path}")
        position_s, label, dp_s, fr_s = groups_raw[idx]
        groups.append(
            Group(
                idx=idx,
                position=int(position_s),
                label=label,
                digits_preserved=int(dp_s),
                factors_removed=int(fr_s),
                symmetry_class=symm_raw[idx],
            )
        )
    return groups


def build_edges(groups: list[Group], include_periodic_links: bool, include_clue_chain: bool) -> list[tuple[int, int, str]]:
    by_label = {g.label: g.idx for g in groups}
    edges: list[tuple[int, int, str]] = []
    # Base walk order from group index.
    for idx in range(len(groups) - 1):
        edges.append((idx, idx + 1, "index_sequence"))
    if include_periodic_links:
        # From BottPeriodicity comments/theorems: 8 relates to 0, 9 relates to 1.
        edges.append((8, 0, "bott_periodic_relation"))
        edges.append((9, 1, "bott_periodic_relation"))
    if include_clue_chain:
        # Known descending chain example from prior discussion: 479 -> 451 -> 496 -> 1742
        clue_labels = [("479", "451"), ("451", "496"), ("496", "1742")]
        for src_label, dst_label in clue_labels:
            if src_label in by_label and dst_label in by_label:
                edges.append((by_label[src_label], by_label[dst_label], "reported_descending_chain"))
    # Deduplicate preserving order.
    seen: set[tuple[int, int, str]] = set()
    out: list[tuple[int, int, str]] = []
    for e in edges:
        if e in seen:
            continue
        seen.add(e)
        out.append(e)
    return out


def longest_desc_chain(node_count: int, edges: list[tuple[int, int, str]], stability: list[int]) -> int:
    graph = {i: [] for i in range(node_count)}
    for src, dst, _kind in edges:
        if 0 <= src < node_count and 0 <= dst < node_count and stability[src] > stability[dst]:
            graph[src].append(dst)
    memo: dict[int, int] = {}

    def dfs(node: int) -> int:
        if node in memo:
            return memo[node]
        best = 1
        for nxt in graph[node]:
            best = max(best, 1 + dfs(nxt))
        memo[node] = best
        return best

    return max((dfs(i) for i in range(node_count)), default=0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a candidate 10-walk dataset from MonsterLean BottPeriodicity constants.")
    parser.add_argument("--bott-file", default=str(DEFAULT_BOTT), help="Path to BottPeriodicity.lean.")
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output JSON path.")
    parser.add_argument("--include-periodic-links", action="store_true", help="Add periodic relation links (8->0, 9->1).")
    parser.add_argument("--include-clue-chain", action="store_true", help="Add known descending-chain edges (479->451->496->1742).")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    args = parser.parse_args()

    groups = parse_groups(Path(args.bott_file))
    edges = build_edges(groups, include_periodic_links=args.include_periodic_links, include_clue_chain=args.include_clue_chain)

    stability_digits = [g.digits_preserved for g in groups]
    stability_removed = [g.factors_removed for g in groups]
    stability_deg = [JAMES_DEGENERACY_BY_LABEL.get(g.label, -1) for g in groups]

    chain_digits = longest_desc_chain(len(groups), edges, stability_digits)
    chain_removed = longest_desc_chain(len(groups), edges, stability_removed)
    chain_deg = None if any(v < 0 for v in stability_deg) else longest_desc_chain(len(groups), edges, stability_deg)

    payload = {
        "source_file": str(Path(args.bott_file)),
        "group_count": len(groups),
        "groups": [
            {
                "idx": g.idx,
                "position": g.position,
                "label": g.label,
                "digits_preserved": g.digits_preserved,
                "factors_removed": g.factors_removed,
                "symmetry_class": g.symmetry_class,
                "james_degeneracy": JAMES_DEGENERACY_BY_LABEL.get(g.label),
            }
            for g in groups
        ],
        "edges": [{"from": s, "to": d, "kind": k} for s, d, k in edges],
        "diagnostics": {
            "stability_digits_preserved": {
                "values": stability_digits,
                "longest_desc_chain": chain_digits,
            },
            "stability_factors_removed": {
                "values": stability_removed,
                "longest_desc_chain": chain_removed,
            },
            "stability_james_degeneracy": {
                "values": stability_deg,
                "longest_desc_chain": chain_deg,
            },
        },
        "notes": {
            "status": "observed_extraction_only",
            "claim_boundary": "constants parsed from Lean source; no Lean proof checking performed",
            "warning": "edges are policy-derived (sequence/periodic/clue), not extracted transition semantics",
        },
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
