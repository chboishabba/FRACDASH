#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from itertools import product
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.agdas_physics2_state import REGISTERS
from scripts.agdas_physics_experiments import apply_transition, matches, transitions_from_templates


STATE_ORDER = (-1, 0, 1)
STATE_INDEX = {-1: 0, 0: 1, 1: 2}


@dataclass(frozen=True)
class Triplet:
    p1: int
    p2: int
    p3: int

    @property
    def as_tuple(self) -> tuple[int, int, int]:
        return (self.p1, self.p2, self.p3)

    @property
    def label(self) -> str:
        return f"{self.p1}-{self.p2}-{self.p3}"


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    k = 3
    while k * k <= n:
        if n % k == 0:
            return False
        k += 2
    return True


def parse_triplet(raw: str) -> Triplet:
    parts = [part.strip() for part in raw.split(",")]
    if len(parts) != 3:
        raise ValueError(f"triplet must have 3 comma-separated integers: {raw}")
    values = [int(part) for part in parts]
    if len(set(values)) != 3:
        raise ValueError(f"triplet values must be distinct: {raw}")
    for value in values:
        if not _is_prime(value):
            raise ValueError(f"triplet contains non-prime value {value}: {raw}")
    return Triplet(values[0], values[1], values[2])


def all_states() -> list[tuple[int, ...]]:
    return [tuple(int(v) for v in vec) for vec in product(STATE_ORDER, repeat=len(REGISTERS))]


def deterministic_successor(state: tuple[int, ...], transitions: tuple[Any, ...]) -> tuple[int, ...] | None:
    for transition in transitions:
        if matches(state, transition):
            return apply_transition(state, transition)
    return None


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


def q_sector(n_value: int, triplet: Triplet) -> int:
    return ((n_value % triplet.p1) + (n_value % triplet.p2) + (n_value % triplet.p3)) % 10


def pca_effective_dimension(matrix: list[list[float]], threshold: float = 0.997) -> int:
    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        raise SystemExit("numpy is required for ablation PCA diagnostics.") from exc
    arr = np.array(matrix, dtype=float)
    centered = arr - np.mean(arr, axis=0, keepdims=True)
    _u, singular, _vh = np.linalg.svd(centered, full_matrices=False)
    variances = singular ** 2
    total = float(np.sum(variances))
    if total <= 0.0:
        return 0
    running = 0.0
    for idx, value in enumerate(variances, start=1):
        running += float(value) / total
        if running >= threshold:
            return idx
    return int(len(variances))


def chain_height(stability: list[int], adjacency: set[tuple[int, int]]) -> int:
    descending = [(src, dst) for src, dst in adjacency if stability[src] > stability[dst]]
    graph = {node: [] for node in range(10)}
    for src, dst in descending:
        graph[src].append(dst)
    memo: dict[int, int] = {}

    def dfs(node: int) -> int:
        if node in memo:
            return memo[node]
        best = 1
        for child in graph[node]:
            best = max(best, 1 + dfs(child))
        memo[node] = best
        return best

    return max((dfs(node) for node in range(10)), default=0)


def build_sector_matrix(sector_members: dict[int, list[tuple[int, ...]]], register_limit: int = 5) -> list[list[float]]:
    width = register_limit * 3
    rows: list[list[float]] = []
    for sector in range(10):
        members = sector_members.get(sector, [])
        if not members:
            rows.append([0.0] * width)
            continue
        counts = [0.0] * width
        for state in members:
            for reg_idx in range(register_limit):
                offset = reg_idx * 3 + STATE_INDEX[int(state[reg_idx])]
                counts[offset] += 1.0
        norm = float(len(members))
        rows.append([count / norm for count in counts])
    return rows


def analyze_triplet(states: list[tuple[int, ...]], transitions: tuple[Any, ...], triplet: Triplet) -> dict[str, Any]:
    sector_members: dict[int, list[tuple[int, ...]]] = {idx: [] for idx in range(10)}
    state_sector: dict[tuple[int, ...], int] = {}
    for state in states:
        sector = q_sector(godel_value(state), triplet)
        sector_members[sector].append(state)
        state_sector[state] = sector

    adjacency: set[tuple[int, int]] = set()
    for state in states:
        nxt = deterministic_successor(state, transitions)
        if nxt is None:
            continue
        src = state_sector[state]
        dst = state_sector[nxt]
        if src != dst:
            adjacency.add((src, dst))

    matrix = build_sector_matrix(sector_members, register_limit=5)
    stability = [len(sector_members[idx]) for idx in range(10)]
    effective_dim = pca_effective_dimension(matrix, threshold=0.997)
    height = chain_height(stability, adjacency)
    occupied = sum(1 for value in stability if value > 0)
    mod3_signature = [p % 3 for p in triplet.as_tuple]

    return {
        "triplet": list(triplet.as_tuple),
        "label": triplet.label,
        "triplet_mod3": mod3_signature,
        "all_mod3_eq_2": all(v == 2 for v in mod3_signature),
        "occupied_sectors": occupied,
        "stability": stability,
        "adjacency_edge_count": len(adjacency),
        "descending_chain_height": height,
        "effective_dimension_997": effective_dim,
    }


def default_triplets() -> list[Triplet]:
    return [
        Triplet(47, 59, 71),
        Triplet(43, 53, 79),
        Triplet(41, 61, 73),
        Triplet(37, 43, 79),
        Triplet(29, 31, 37),
        Triplet(23, 47, 83),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Ablate q-map prime triplets against basin diagnostics.")
    parser.add_argument(
        "--template-set",
        default="physics8",
        choices=("physics2", "physics3", "physics4", "physics5", "physics6", "physics7", "physics8", "physics9", "physics10", "physics11", "physics12", "physics13", "physics14", "physics15", "physics16", "physics17", "physics18", "physics19", "physics20", "physics21"),
        help="Physics template set used to build deterministic state transitions.",
    )
    parser.add_argument(
        "--triplet",
        action="append",
        default=[],
        help="Prime triplet p1,p2,p3. Repeatable. Defaults to a built-in control set.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: benchmarks/results/<today>-prime-triplet-ablation.json).",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    args = parser.parse_args()

    triplets = [parse_triplet(raw) for raw in args.triplet] if args.triplet else default_triplets()
    transitions, transition_source_summary = transitions_from_templates(args.template_set)
    states = all_states()

    rows = [analyze_triplet(states, transitions, triplet) for triplet in triplets]
    baseline = next((row for row in rows if row["triplet"] == [47, 59, 71]), None)
    if baseline is not None:
        for row in rows:
            row["delta_vs_47_59_71"] = {
                "effective_dimension_997": int(row["effective_dimension_997"]) - int(baseline["effective_dimension_997"]),
                "descending_chain_height": int(row["descending_chain_height"]) - int(baseline["descending_chain_height"]),
                "adjacency_edge_count": int(row["adjacency_edge_count"]) - int(baseline["adjacency_edge_count"]),
            }

    rows_sorted = sorted(
        rows,
        key=lambda row: (
            abs(int(row["effective_dimension_997"]) - 4),
            abs(int(row["descending_chain_height"]) - 4),
            -int(row["adjacency_edge_count"]),
        ),
    )
    best = rows_sorted[0] if rows_sorted else None

    payload = {
        "template_set": args.template_set,
        "transition_source_summary": transition_source_summary,
        "state_space_size": len(states),
        "triplet_count": len(rows),
        "results": rows_sorted,
        "baseline_triplet": [47, 59, 71],
        "best_rank4_candidate": best,
    }

    output_path = (
        Path(args.output)
        if args.output
        else Path("benchmarks/results") / f"{date.today().isoformat()}-prime-triplet-ablation.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    print(f"wrote {output_path}")
    if best is not None:
        print(
            "best_triplet="
            f"{best['label']} "
            f"effective_dim={best['effective_dimension_997']} "
            f"chain_height={best['descending_chain_height']}"
        )


if __name__ == "__main__":
    main()
