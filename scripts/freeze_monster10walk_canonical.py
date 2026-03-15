#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any
from itertools import product


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BOTT = ROOT / "monster" / "MonsterLean" / "BottPeriodicity.lean"
DEFAULT_OUT = ROOT / "benchmarks" / "results" / f"{date.today().isoformat()}-monster10walk-canonical.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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


def _load_extract_parser():
    import importlib.util
    import sys

    path = Path(__file__).resolve().parent / "extract_monsterlean_10walk.py"
    spec = importlib.util.spec_from_file_location("extract_monsterlean_10walk_local", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load parser module from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["extract_monsterlean_10walk_local"] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def parse_groups(bott_file: Path) -> list[Group]:
    mod = _load_extract_parser()
    groups_raw = mod.parse_groups(bott_file)
    return [
        Group(
            idx=int(g.idx),
            position=int(g.position),
            label=str(g.label),
            digits_preserved=int(g.digits_preserved),
            factors_removed=int(g.factors_removed),
            symmetry_class=str(g.symmetry_class),
        )
        for g in groups_raw
    ]


def canonical_edges(n: int) -> list[tuple[int, int]]:
    return [(i, i + 1) for i in range(n - 1)]


def _undirected_pair(src: int, dst: int) -> tuple[int, int]:
    return (src, dst) if src <= dst else (dst, src)


def _canonical_undirected_pairs(n: int) -> set[tuple[int, int]]:
    return {_undirected_pair(i, i + 1) for i in range(n - 1)}


def longest_desc_chain(n: int, edges: list[tuple[int, int]], stability: list[int]) -> int:
    graph: dict[int, list[int]] = {i: [] for i in range(n)}
    for src, dst in edges:
        if stability[src] > stability[dst]:
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

    return max((dfs(i) for i in range(n)), default=0)


def out_in_degrees(n: int, edges: list[tuple[int, int]]) -> tuple[list[int], list[int]]:
    indeg = [0] * n
    outdeg = [0] * n
    for src, dst in edges:
        outdeg[src] += 1
        indeg[dst] += 1
    return indeg, outdeg


def is_directed_path_graph(n: int, edges: list[tuple[int, int]]) -> bool:
    if n == 0:
        return False
    if len(edges) != n - 1:
        return False
    indeg, outdeg = out_in_degrees(n, edges)
    starts = [i for i in range(n) if indeg[i] == 0 and outdeg[i] == 1]
    ends = [i for i in range(n) if indeg[i] == 1 and outdeg[i] == 0]
    mids = [i for i in range(n) if indeg[i] == 1 and outdeg[i] == 1]
    if len(starts) != 1 or len(ends) != 1 or len(mids) != n - 2:
        return False
    # Connectivity along edge direction from start.
    nxt_map = {s: d for s, d in edges}
    seen = set()
    node = starts[0]
    while node not in seen and node in nxt_map:
        seen.add(node)
        node = nxt_map[node]
    seen.add(node)
    return len(seen) == n and node == ends[0]


def extract_fractran_transition_edges(template_set: str) -> tuple[int, list[tuple[int, int]], dict[str, Any]]:
    from scripts.agdas_physics2_state import REGISTERS
    from scripts.agdas_physics_experiments import transitions_from_templates, matches, apply_transition

    transitions, source_summary = transitions_from_templates(template_set)

    def godel_value(state: tuple[int, ...]) -> int:
        value = 1
        for idx, signed in enumerate(state):
            reg = REGISTERS[idx]
            if signed == -1:
                value *= int(reg.negative)
            elif signed == 0:
                value *= int(reg.zero)
            else:
                value *= int(reg.positive)
        return value

    def q_sector(n_value: int) -> int:
        return ((n_value % 71) + (n_value % 59) + (n_value % 47)) % 10

    states = [tuple(int(v) for v in vec) for vec in product((-1, 0, 1), repeat=len(REGISTERS))]
    state_sector = {state: q_sector(godel_value(state)) for state in states}

    def deterministic_successor(state: tuple[int, ...]) -> tuple[int, ...] | None:
        for transition in transitions:
            if matches(state, transition):
                return apply_transition(state, transition)
        return None

    edges: set[tuple[int, int]] = set()
    for state in states:
        nxt = deterministic_successor(state)
        if nxt is None:
            continue
        src = state_sector[state]
        dst = state_sector[nxt]
        if src != dst:
            edges.add((src, dst))
    return 10, sorted(edges), source_summary


def derive_template_path(n: int, edges: list[tuple[int, int]]) -> dict[str, Any]:
    reach_edges = reachability_edges(n, edges)
    path, reach_supported = best_hamiltonian_path(n, reach_edges)
    path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)] if len(path) == n else []
    direct_supported = sum(1 for e in path_edges if e in set(edges))
    return {
        "source_direct_edge_count": len(edges),
        "source_reachability_edge_count": len(reach_edges),
        "hamiltonian_path": path,
        "hamiltonian_path_edge_count": len(path_edges),
        "supported_path_edges_direct": direct_supported,
        "supported_path_edges_reachability": reach_supported,
        "perfect_reachability_support_path": reach_supported == (n - 1),
        "is_directed_path": is_directed_path_graph(n, path_edges),
        "path_edges": path_edges,
    }


def parse_template_sets(args: argparse.Namespace) -> list[str]:
    if args.template_set:
        return [args.template_set]
    raw = [token.strip() for token in args.template_sets.split(",")]
    allowed = {"physics2", "physics3", "physics4", "physics5", "physics6", "physics7", "physics8", "physics9"}
    values = [token for token in raw if token]
    if not values:
        raise SystemExit("no template sets provided")
    out: list[str] = []
    for token in values:
        if token not in allowed:
            raise SystemExit(f"unsupported template set: {token}")
        if token not in out:
            out.append(token)
    return out


def reachability_edges(n: int, edges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    graph: dict[int, list[int]] = {i: [] for i in range(n)}
    for src, dst in edges:
        graph[src].append(dst)
    out: set[tuple[int, int]] = set()
    for src in range(n):
        stack = [src]
        seen = {src}
        while stack:
            node = stack.pop()
            for nxt in graph[node]:
                if nxt in seen:
                    continue
                seen.add(nxt)
                stack.append(nxt)
                out.add((src, nxt))
    return sorted(out)


def best_hamiltonian_path(n: int, edges: list[tuple[int, int]]) -> tuple[list[int], int]:
    edge_set = set(edges)
    neg_inf = -10**9

    @lru_cache(maxsize=None)
    def dp(mask: int, last: int) -> tuple[int, tuple[int, ...]]:
        if mask == (1 << last):
            return (0, (last,))
        best_score = neg_inf
        best_path: tuple[int, ...] = ()
        prev_mask = mask & ~(1 << last)
        for prev in range(n):
            if prev == last or ((prev_mask >> prev) & 1) == 0:
                continue
            score_prev, path_prev = dp(prev_mask, prev)
            add = 1 if (prev, last) in edge_set else 0
            score = score_prev + add
            if score > best_score:
                best_score = score
                best_path = path_prev + (last,)
        return (best_score, best_path)

    full = (1 << n) - 1
    best_score = neg_inf
    best_path: tuple[int, ...] = ()
    for last in range(n):
        score, path = dp(full, last)
        if score > best_score:
            best_score = score
            best_path = path
    return list(best_path), int(best_score)


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze canonical Monster 10-walk semantics and lock derivation artifact.")
    parser.add_argument("--bott-file", default=str(DEFAULT_BOTT), help="Path to BottPeriodicity.lean.")
    parser.add_argument(
        "--template-sets",
        default="physics8,physics9",
        help="Comma-separated FRACDASH physics template sets used for independent transition-derived 10-sector graph checks.",
    )
    parser.add_argument(
        "--template-set",
        default=None,
        choices=("physics2", "physics3", "physics4", "physics5", "physics6", "physics7", "physics8", "physics9"),
        help="Legacy single-template override; if set, overrides --template-sets.",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUT), help="Output JSON path.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    parser.add_argument("--strict-lock", action="store_true", help="Exit non-zero if lock gate fails.")
    args = parser.parse_args()

    groups = parse_groups(Path(args.bott_file))
    n = len(groups)
    lean_edges = canonical_edges(n)
    canonical_pairs = _canonical_undirected_pairs(n)
    lean_is_path = is_directed_path_graph(n, lean_edges)

    james = [JAMES_DEGENERACY_BY_LABEL[g.label] for g in groups]
    chain_james = longest_desc_chain(n, lean_edges, james)
    rank_proxy = chain_james

    template_sets = parse_template_sets(args)
    per_template: dict[str, Any] = {}
    for template_set in template_sets:
        tr_n, tr_edges, tr_source_summary = extract_fractran_transition_edges(template_set)
        if tr_n != n:
            raise SystemExit(f"FRACDASH node count ({tr_n}) does not match lean group count ({n})")
        tr_details = derive_template_path(tr_n, tr_edges)
        direct_pairs = {_undirected_pair(src, dst) for src, dst in tr_edges}
        reach_pairs = {_undirected_pair(src, dst) for src, dst in reachability_edges(tr_n, tr_edges)}
        path_pairs = {_undirected_pair(src, dst) for src, dst in tr_details["path_edges"]}
        tr_details["source_summary"] = tr_source_summary
        tr_details["source_template_set"] = template_set
        tr_details["canonical_edge_support_direct"] = sum(1 for pair in canonical_pairs if pair in direct_pairs)
        tr_details["canonical_edge_support_reachability"] = sum(1 for pair in canonical_pairs if pair in reach_pairs)
        tr_details["canonical_edge_support_path"] = sum(1 for pair in canonical_pairs if pair in path_pairs)
        tr_details["canonical_edge_support_direct_full"] = tr_details["canonical_edge_support_direct"] == (n - 1)
        tr_details["canonical_edge_support_reachability_full"] = tr_details["canonical_edge_support_reachability"] == (n - 1)
        tr_details["canonical_edge_support_path_full"] = tr_details["canonical_edge_support_path"] == (n - 1)
        tr_details["path_undirected_matches_canonical"] = path_pairs == canonical_pairs
        per_template[template_set] = tr_details

    derivation_match = bool(
        lean_is_path
        and all(
            details["is_directed_path"] and details["path_undirected_matches_canonical"]
            for details in per_template.values()
        )
    )

    template_lock_checks = {
        template_set: {
            "derivation_is_directed_path": bool(details["is_directed_path"]),
            "path_undirected_matches_canonical": bool(details["path_undirected_matches_canonical"]),
            "canonical_edge_support_direct_is_9": bool(details["canonical_edge_support_direct_full"]),
            "canonical_edge_support_reachability_is_9": bool(details["canonical_edge_support_reachability_full"]),
        }
        for template_set, details in per_template.items()
    }
    template_lock_pass = {template_set: all(checks.values()) for template_set, checks in template_lock_checks.items()}
    all_templates_lock_pass = all(template_lock_pass.values())

    payload: dict[str, Any] = {
        "canonical_semantics": {
            "vertex_source": str(Path(args.bott_file)),
            "vertex_order": "position_sequence",
            "edge_rule": "index_sequence_transition_witnessed",
            "edges": [{"from": s, "to": d} for s, d in lean_edges],
            "required_undirected_pairs": [{"a": a, "b": b} for a, b in sorted(canonical_pairs)],
            "required_template_sets": template_sets,
        },
        "lean_constants_derivation": {
            "groups": [
                {
                    "idx": g.idx,
                    "position": g.position,
                    "label": g.label,
                    "digits_preserved": g.digits_preserved,
                    "factors_removed": g.factors_removed,
                    "symmetry_class": g.symmetry_class,
                    "james_degeneracy": JAMES_DEGENERACY_BY_LABEL[g.label],
                }
                for g in groups
            ],
            "edge_count": len(lean_edges),
            "is_directed_path": lean_is_path,
            "chain_height_james_degeneracy": chain_james,
            "stability_order_rank_proxy": rank_proxy,
        },
        "fractran_transition_derivation": {
            "template_set_count": len(template_sets),
            "template_sets": template_sets,
            "per_template": per_template,
        },
        "derivation_match": {
            "criterion": "canonical_path plus per-template directed-path derivation with undirected canonical-edge match",
            "pass": derivation_match,
        },
        "lock_gate": {
            "checks": {
                "canonical_edge_count_is_9": len(lean_edges) == 9,
                "canonical_is_directed_path": lean_is_path,
                "canonical_chain_height_james_is_4": chain_james == 4,
                "canonical_rank_proxy_is_4": rank_proxy == 4,
                "all_templates_lock_pass": all_templates_lock_pass,
                "derivation_match_pass": derivation_match,
            },
            "per_template_checks": template_lock_checks,
            "per_template_pass": template_lock_pass,
        },
        "notes": {
            "status": "observed_experimentally",
            "boundary": "freeze/lock applies to FRACDASH canonical reproduction model; not a Lean theorem closure",
        },
    }
    payload["lock_gate"]["pass"] = all(payload["lock_gate"]["checks"].values())

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"wrote {out}")
        print(f"lock_pass={payload['lock_gate']['pass']}")
        print(f"chain_height_james={chain_james}")
        for template_set in template_sets:
            details = per_template[template_set]
            print(
                f"{template_set}: canonical_support_direct={details['canonical_edge_support_direct']}/9 "
                f"canonical_support_reachability={details['canonical_edge_support_reachability']}/9"
            )

    if args.strict_lock and not payload["lock_gate"]["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
