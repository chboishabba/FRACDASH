#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date
from itertools import combinations, product
from pathlib import Path
from statistics import mean
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

State = tuple[int, ...]

TARGET_SUITE_VERSION = "physics_target_suite_v1"
SOURCE_REGISTER_NAMES = ("R1", "R2")
REGISTERS = ()
SOURCE_REGISTER_INDEX: dict[str, int] = {}
PARITY_GROUPS: dict[str, tuple[int, ...]] = {}
LOCALITY_MAX_CHANGED_REGISTERS = 3
LOCALITY_MAX_L1_STEP_DELTA = 5
FORWARD_CONE_MAX_SUCCESSOR_HAMMING = 5
PERTURBATION_THRESHOLDS = {
    "single_register_sign_flip": 0.80,
    "single_register_zero_toggle": 0.65,
    "paired_defect": 0.49,
}
GEODESIC_NEAR_MIN_THRESHOLD = 0.74
CURVATURE_MEAN_SPREAD_THRESHOLD = 0.80
DEFECT_NONINCREASE_THRESHOLD = 0.43


def configure_registers(registers) -> None:
    global REGISTERS, SOURCE_REGISTER_INDEX, PARITY_GROUPS
    REGISTERS = registers
    SOURCE_REGISTER_INDEX = {
        reg.name: idx
        for idx, reg in enumerate(REGISTERS)
        if reg.name in SOURCE_REGISTER_NAMES
    }
    PARITY_GROUPS = {
        "R1_nonzero": (SOURCE_REGISTER_INDEX["R1"],),
        "R2_nonzero": (SOURCE_REGISTER_INDEX["R2"],),
        "R1R2_nonzero_pair": (SOURCE_REGISTER_INDEX["R1"], SOURCE_REGISTER_INDEX["R2"]),
    }


def load_runtime(template_set: str):
    if template_set.startswith("carrier8_"):
        state_module = importlib.import_module("scripts.agdas_physics8_state")
        experiment_module = importlib.import_module("scripts.agdas_physics8_experiments")
        carrier_family = "physics_local_8"
    else:
        state_module = importlib.import_module("scripts.agdas_physics2_state")
        experiment_module = importlib.import_module("scripts.agdas_physics_experiments")
        carrier_family = "physics_local_6"
    configure_registers(state_module.REGISTERS)
    return carrier_family, experiment_module


@dataclass(frozen=True)
class CandidateScore:
    name: str
    nonincrease_ratio: float
    strict_decrease_ratio: float
    increase_ratio: float
    increases: int
    edges: int
    details: dict[str, object]


def hamming_distance(lhs: State, rhs: State) -> int:
    return sum(a != b for a, b in zip(lhs, rhs))


def l1_distance(lhs: State, rhs: State) -> int:
    return sum(abs(a - b) for a, b in zip(lhs, rhs))


def one_register_neighbors(state: State) -> list[State]:
    out: list[State] = []
    for idx, value in enumerate(state):
        for nxt in (-1, 0, 1):
            if nxt == value:
                continue
            updated = list(state)
            updated[idx] = nxt
            out.append(tuple(updated))
    return out


def sign_flip_neighbors(state: State) -> list[State]:
    out: list[State] = []
    for idx, value in enumerate(state):
        if value == 0:
            continue
        updated = list(state)
        updated[idx] = -value
        out.append(tuple(updated))
    return out


def zero_toggle_neighbors(state: State) -> list[State]:
    out: list[State] = []
    for idx, value in enumerate(state):
        if value == 0:
            for nxt in (-1, 1):
                updated = list(state)
                updated[idx] = nxt
                out.append(tuple(updated))
        else:
            updated = list(state)
            updated[idx] = 0
            out.append(tuple(updated))
    return out


def paired_defect_neighbors(state: State) -> list[State]:
    out: list[State] = []
    for left, right in combinations(range(len(state)), 2):
        lhs = state[left]
        rhs = state[right]
        if lhs == 0 and rhs == 0:
            for a, b in ((1, -1), (-1, 1)):
                updated = list(state)
                updated[left] = a
                updated[right] = b
                out.append(tuple(updated))
        elif (lhs, rhs) in ((1, -1), (-1, 1)):
            updated = list(state)
            updated[left] = 0
            updated[right] = 0
            out.append(tuple(updated))
    return out


def unique_pair_iter(nodes: Iterable[State], generator: Callable[[State], list[State]]) -> Iterable[tuple[State, State]]:
    for state in nodes:
        for other in generator(state):
            if state < other:
                yield state, other


def source_charge_laws(succ: dict[State, State]) -> dict[str, object]:
    changed_edges_by_register: dict[str, int] = {}
    for register_name, idx in SOURCE_REGISTER_INDEX.items():
        changed_edges_by_register[register_name] = sum(
            1 for src, dst in succ.items() if src[idx] != dst[idx]
        )
    conserved = [name for name, count in changed_edges_by_register.items() if count == 0]
    return {
        "mode": "exact",
        "pass": all(changed_edges_by_register[name] == 0 for name in SOURCE_REGISTER_NAMES),
        "conserved_registers": conserved,
        "conserved_rank": len(conserved),
        "changed_edges_by_register": changed_edges_by_register,
    }


def nonzero_parity(state: State, indices: tuple[int, ...]) -> int:
    return sum(1 for idx in indices if abs(state[idx]) == 1) % 2


def source_parity_laws(succ: dict[State, State]) -> dict[str, object]:
    parity_breaks = {
        label: sum(
            1 for src, dst in succ.items() if nonzero_parity(src, indices) != nonzero_parity(dst, indices)
        )
        for label, indices in PARITY_GROUPS.items()
    }
    return {
        "mode": "exact",
        "pass": all(count == 0 for count in parity_breaks.values()),
        "parity_breaks": parity_breaks,
    }


def locality_law(succ: dict[State, State]) -> dict[str, object]:
    max_changed = 0
    max_l1 = 0
    samples: list[dict[str, object]] = []
    for src, dst in succ.items():
        changed = hamming_distance(src, dst)
        step_l1 = l1_distance(src, dst)
        max_changed = max(max_changed, changed)
        max_l1 = max(max_l1, step_l1)
        if len(samples) < 8 and (changed == max_changed or step_l1 == max_l1):
            samples.append(
                {
                    "source": list(src),
                    "target": list(dst),
                    "changed_registers": changed,
                    "l1_step_delta": step_l1,
                }
            )
    return {
        "mode": "exact",
        "pass": max_changed <= LOCALITY_MAX_CHANGED_REGISTERS and max_l1 <= LOCALITY_MAX_L1_STEP_DELTA,
        "max_changed_registers": max_changed,
        "max_l1_step_delta": max_l1,
        "samples": samples,
    }


def forward_cone_law(nodes: list[State], succ: dict[State, State]) -> dict[str, object]:
    max_successor_hamming = 0
    pair_count = 0
    for left, right in unique_pair_iter(nodes, one_register_neighbors):
        if left not in succ or right not in succ:
            continue
        pair_count += 1
        max_successor_hamming = max(
            max_successor_hamming,
            hamming_distance(succ[left], succ[right]),
        )
    return {
        "mode": "exact",
        "pass": max_successor_hamming <= FORWARD_CONE_MAX_SUCCESSOR_HAMMING,
        "pair_count": pair_count,
        "max_successor_hamming": max_successor_hamming,
    }


def cycle_distance_law(succ: dict[State, State], dist: dict[State, int]) -> dict[str, object]:
    score = evaluate_candidate("distance_to_cycle", lambda s: float(dist[s]), succ)
    return {
        "mode": "exact",
        "pass": score.increases == 0 and abs(score.nonincrease_ratio - 1.0) <= 1e-12,
        "nonincrease_ratio": score.nonincrease_ratio,
        "strict_decrease_ratio": score.strict_decrease_ratio,
        "increase_ratio": score.increase_ratio,
        "increases": score.increases,
        "edges": score.edges,
    }


def perturbation_family_score(
    name: str,
    nodes: list[State],
    succ: dict[State, State],
    generator: Callable[[State], list[State]],
) -> dict[str, object]:
    pair_count = 0
    nonexpansion = 0
    distance_ratios: list[float] = []
    distance_deltas: list[int] = []
    post_distances: list[int] = []
    for left, right in unique_pair_iter(nodes, generator):
        if left not in succ or right not in succ:
            continue
        before = hamming_distance(left, right)
        after = hamming_distance(succ[left], succ[right])
        pair_count += 1
        if after <= before:
            nonexpansion += 1
        distance_ratios.append(after / max(before, 1))
        distance_deltas.append(after - before)
        post_distances.append(after)
    nonexpansion_ratio = nonexpansion / pair_count if pair_count else 0.0
    return {
        "mode": "statistical",
        "pass": nonexpansion_ratio >= PERTURBATION_THRESHOLDS[name],
        "pair_count": pair_count,
        "nonexpansion_ratio": nonexpansion_ratio,
        "mean_distance_ratio": mean(distance_ratios) if distance_ratios else 0.0,
        "mean_distance_delta": mean(distance_deltas) if distance_deltas else 0.0,
        "mean_post_distance": mean(post_distances) if post_distances else 0.0,
    }


def geodesic_like_flow_law(nodes: list[State], succ: dict[State, State], dist: dict[State, int], cycles: list[list[State]]) -> dict[str, object]:
    if not cycles:
        return {
            "mode": "statistical",
            "available": False,
            "pass": True,
            "reason": "no_cycle_components",
            "near_min_ratio": None,
            "exact_min_ratio": None,
            "mean_margin": None,
        }
    total = 0
    exact_min = 0
    near_min = 0
    margins: list[int] = []
    for src, dst in succ.items():
        neighbor_distances = [dist[neighbor] for neighbor in one_register_neighbors(src) if dist.get(neighbor, -1) >= 0]
        if not neighbor_distances or dist.get(dst, -1) < 0:
            continue
        best = min(neighbor_distances)
        current = dist[dst]
        total += 1
        if current == best:
            exact_min += 1
        if current <= best + 1:
            near_min += 1
        margins.append(current - best)
    near_min_ratio = near_min / total if total else 0.0
    return {
        "mode": "statistical",
        "available": True,
        "pass": near_min_ratio >= GEODESIC_NEAR_MIN_THRESHOLD,
        "exact_min_ratio": exact_min / total if total else 0.0,
        "near_min_ratio": near_min_ratio,
        "mean_margin": mean(margins) if margins else 0.0,
        "samples": total,
        "neighbor_filter": "cycle_reachable_only",
    }


def curvature_like_concentration_law(nodes: list[State], dist: dict[State, int], cycles: list[list[State]]) -> dict[str, object]:
    spreads = []
    for state in nodes:
        neighbor_distances = [dist[neighbor] for neighbor in one_register_neighbors(state) if dist.get(neighbor, -1) >= 0]
        if neighbor_distances:
            spreads.append(max(neighbor_distances) - min(neighbor_distances))
    mean_spread = mean(spreads) if spreads else 0.0
    if not cycles:
        return {
            "mode": "statistical",
            "available": False,
            "pass": abs(mean_spread) <= 1e-12,
            "reason": "no_cycle_components",
            "mean_neighbor_spread": mean_spread,
            "spread_gt2_ratio": 0.0,
        }
    return {
        "mode": "statistical",
        "available": True,
        "pass": mean_spread >= CURVATURE_MEAN_SPREAD_THRESHOLD,
        "mean_neighbor_spread": mean_spread,
        "spread_gt2_ratio": sum(value > 2 for value in spreads) / len(spreads) if spreads else 0.0,
        "neighbor_filter": "cycle_reachable_only",
    }


def defect_attraction_law(succ: dict[State, State]) -> dict[str, object]:
    deltas = [
        sum(abs(value) for value in dst[2:]) - sum(abs(value) for value in src[2:])
        for src, dst in succ.items()
    ]
    nonincrease_ratio = sum(value <= 0 for value in deltas) / len(deltas) if deltas else 0.0
    return {
        "mode": "statistical",
        "pass": nonincrease_ratio >= DEFECT_NONINCREASE_THRESHOLD,
        "nonincrease_ratio": nonincrease_ratio,
        "strict_drop_ratio": sum(value < 0 for value in deltas) / len(deltas) if deltas else 0.0,
        "mean_delta": mean(deltas) if deltas else 0.0,
    }


def _count_by_value(states: Iterable[State], idx: int) -> dict[str, int]:
    counts = {-1: 0, 0: 0, 1: 0}
    for state in states:
        counts[state[idx]] += 1
    return {
        "negative": counts[-1],
        "zero": counts[0],
        "positive": counts[1],
    }


def _source_class(state: State) -> str:
    left = state[SOURCE_REGISTER_INDEX["R1"]] != 0
    right = state[SOURCE_REGISTER_INDEX["R2"]] != 0
    if left and right:
        return "dual_active"
    if left:
        return "left_only"
    if right:
        return "right_only"
    return "neutral"


def _defect_load(state: State) -> int:
    return sum(abs(value) for value in state[2:])


def observable_surrogates(nodes: list[State], succ: dict[State, State], dist: dict[State, int]) -> dict[str, object]:
    deterministic_sources = list(succ.keys())
    cycle_reachable_sources = [state for state in deterministic_sources if dist[state] >= 0]

    shell_to_interior = 0
    boundary_to_interior = 0
    interior_to_noninterior = 0
    for src, dst in succ.items():
        if src[3] == 0 and dst[3] == 1:
            shell_to_interior += 1
        if src[3] == -1 and dst[3] == 1:
            boundary_to_interior += 1
        if src[3] == 1 and dst[3] != 1:
            interior_to_noninterior += 1

    latch_states = [state for state in deterministic_sources if state[4] != 0]
    aligned = 0
    for state in latch_states:
        if state[4] > 0 and state[0] != 0:
            aligned += 1
        elif state[4] < 0 and state[1] != 0:
            aligned += 1

    defect_by_source: dict[str, list[int]] = {
        "neutral": [],
        "left_only": [],
        "right_only": [],
        "dual_active": [],
    }
    for state in cycle_reachable_sources:
        defect_by_source[_source_class(state)].append(_defect_load(state))

    payload = {
        "region_mass": {
            "deterministic_sources": _count_by_value(deterministic_sources, 3),
            "cycle_reachable_sources": _count_by_value(cycle_reachable_sources, 3),
        },
        "action_phase_profile": {
            "deterministic_sources": _count_by_value(deterministic_sources, 5),
            "cycle_reachable_sources": _count_by_value(cycle_reachable_sources, 5),
        },
        "reentry_flow": {
            "shell_to_interior": shell_to_interior,
            "boundary_to_interior": boundary_to_interior,
            "interior_to_noninterior": interior_to_noninterior,
            "shell_to_interior_ratio": shell_to_interior / len(succ) if succ else 0.0,
            "boundary_to_interior_ratio": boundary_to_interior / len(succ) if succ else 0.0,
        },
        "source_latch_alignment": {
            "latched_source_count": len(latch_states),
            "aligned_count": aligned,
            "alignment_ratio": aligned / len(latch_states) if latch_states else 0.0,
        },
        "source_defect_coupling": {
            key: {
                "count": len(values),
                "mean_defect_load": mean(values) if values else 0.0,
            }
            for key, values in defect_by_source.items()
        },
    }
    if len(REGISTERS) >= 8:
        payload["boundary_return_profile"] = {
            "deterministic_sources": _count_by_value(deterministic_sources, 6),
            "cycle_reachable_sources": _count_by_value(cycle_reachable_sources, 6),
        }
        payload["transport_debt_profile"] = {
            "deterministic_sources": _count_by_value(deterministic_sources, 7),
            "cycle_reachable_sources": _count_by_value(cycle_reachable_sources, 7),
        }
    return payload


def all_states() -> list[State]:
    return [tuple(int(v) for v in vec) for vec in product((-1, 0, 1), repeat=len(REGISTERS))]


def deterministic_successor(state: State, transitions, matches_fn, apply_transition_fn) -> tuple[str, State] | None:
    for transition in transitions:
        if matches_fn(state, transition):
            return transition.name, apply_transition_fn(state, transition)
    return None


def deterministic_graph(transitions, matches_fn, apply_transition_fn) -> tuple[dict[State, State], dict[State, str], list[State]]:
    succ: dict[State, State] = {}
    edge_name: dict[State, str] = {}
    nodes = all_states()
    for state in nodes:
        nxt = deterministic_successor(state, transitions, matches_fn, apply_transition_fn)
        if nxt is None:
            continue
        name, target = nxt
        succ[state] = target
        edge_name[state] = name
    return succ, edge_name, nodes


def tarjan_scc(nodes: list[State], succ: dict[State, State]) -> list[list[State]]:
    index = 0
    stack: list[State] = []
    on_stack: set[State] = set()
    indices: dict[State, int] = {}
    lowlinks: dict[State, int] = {}
    components: list[list[State]] = []

    def strongconnect(node: State) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        nxt = succ.get(node)
        if nxt is not None:
            if nxt not in indices:
                strongconnect(nxt)
                lowlinks[node] = min(lowlinks[node], lowlinks[nxt])
            elif nxt in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[nxt])
        if lowlinks[node] == indices[node]:
            comp: list[State] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                comp.append(member)
                if member == node:
                    break
            components.append(sorted(comp))

    for node in sorted(nodes):
        if node not in indices:
            strongconnect(node)
    return components


def cycle_components(components: list[list[State]], succ: dict[State, State]) -> list[list[State]]:
    cycles: list[list[State]] = []
    for comp in components:
        if len(comp) > 1:
            cycles.append(comp)
            continue
        state = comp[0]
        if succ.get(state) == state:
            cycles.append(comp)
    return cycles


def distance_to_cycle(nodes: list[State], succ: dict[State, State], cycles: list[list[State]]) -> dict[State, int]:
    reverse_edges: dict[State, list[State]] = defaultdict(list)
    for src, dst in succ.items():
        reverse_edges[dst].append(src)
    dist: dict[State, int] = {state: 10**9 for state in nodes}
    queue: deque[State] = deque()
    for comp in cycles:
        for state in comp:
            dist[state] = 0
            queue.append(state)
    while queue:
        node = queue.popleft()
        for prev in reverse_edges.get(node, []):
            if dist[prev] > dist[node] + 1:
                dist[prev] = dist[node] + 1
                queue.append(prev)
    for state in nodes:
        if dist[state] >= 10**9:
            dist[state] = -1
    return dist


def evaluate_candidate(
    name: str,
    potential: Callable[[State], float],
    succ: dict[State, State],
) -> CandidateScore:
    total = 0
    nonincrease = 0
    strict = 0
    increases = 0
    for src, dst in succ.items():
        total += 1
        src_v = potential(src)
        dst_v = potential(dst)
        if dst_v <= src_v:
            nonincrease += 1
            if dst_v < src_v:
                strict += 1
        else:
            increases += 1
    if total == 0:
        return CandidateScore(name=name, nonincrease_ratio=0.0, strict_decrease_ratio=0.0, increase_ratio=0.0, increases=0, edges=0, details={})
    return CandidateScore(
        name=name,
        nonincrease_ratio=nonincrease / total,
        strict_decrease_ratio=strict / total,
        increase_ratio=increases / total,
        increases=increases,
        edges=total,
        details={},
    )


def search_weighted_potential(succ: dict[State, State]) -> CandidateScore:
    best: CandidateScore | None = None
    best_weights = None
    for weights in product((-2, -1, 0, 1, 2), repeat=len(REGISTERS)):
        if all(w == 0 for w in weights):
            continue
        def pot(state: State, w=weights) -> float:
            return float(sum(abs(state[i]) * w[i] for i in range(len(state))))
        score = evaluate_candidate("weighted_abs", pot, succ)
        if best is None:
            best = score
            best_weights = weights
            continue
        key = (score.nonincrease_ratio, score.strict_decrease_ratio, -score.increases)
        best_key = (best.nonincrease_ratio, best.strict_decrease_ratio, -best.increases)
        if key > best_key:
            best = score
            best_weights = weights
    assert best is not None and best_weights is not None
    return CandidateScore(
        name="weighted_abs_search",
        nonincrease_ratio=best.nonincrease_ratio,
        strict_decrease_ratio=best.strict_decrease_ratio,
        increase_ratio=best.increase_ratio,
        increases=best.increases,
        edges=best.edges,
        details={"weights": list(best_weights)},
    )


def pca_embedding(nodes: list[State]) -> dict[State, tuple[float, float]]:
    try:
        import numpy as np
    except ModuleNotFoundError:
        return {state: (float(state[0]), float(state[1])) for state in nodes}
    arr = np.array(nodes, dtype=float)
    centered = arr - np.mean(arr, axis=0, keepdims=True)
    _u, _s, vh = np.linalg.svd(centered, full_matrices=False)
    axes = vh[:2]
    emb = centered @ axes.T
    return {
        nodes[i]: (float(emb[i, 0]), float(emb[i, 1]))
        for i in range(len(nodes))
    }


def trace_from(start: State, succ: dict[State, State], max_steps: int) -> list[State]:
    current = start
    seen: set[State] = set()
    out = [current]
    for _ in range(max_steps):
        if current in seen:
            break
        seen.add(current)
        nxt = succ.get(current)
        if nxt is None:
            break
        out.append(nxt)
        current = nxt
    return out


def build_analysis_subset(
    carrier_family: str,
    nodes: list[State],
    succ: dict[State, State],
    sample_starts: list[State],
    max_states: int = 512,
) -> tuple[list[State], dict[State, State], str]:
    if carrier_family != "physics_local_8":
        return nodes, succ, "full_state_space"

    seen: set[State] = set()
    queue: deque[State] = deque()
    node_set = set(nodes)
    for start in sample_starts:
        if start in node_set and start not in seen:
            seen.add(start)
            queue.append(start)

    while queue and len(seen) < max_states:
        state = queue.popleft()
        nxt = succ.get(state)
        if nxt is not None and nxt not in seen:
            seen.add(nxt)
            queue.append(nxt)
            if len(seen) >= max_states:
                break
        for neighbor in one_register_neighbors(state):
            if neighbor in node_set and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
                if len(seen) >= max_states:
                    break

    changed = True
    while changed and len(seen) < max_states:
        changed = False
        for state in list(seen):
            nxt = succ.get(state)
            if nxt is not None and nxt not in seen:
                seen.add(nxt)
                changed = True
                if len(seen) >= max_states:
                    break

    subset_nodes = sorted(seen)
    subset_set = set(subset_nodes)
    subset_succ = {src: dst for src, dst in succ.items() if src in subset_set and dst in subset_set}
    return subset_nodes, subset_succ, "bounded_active_subset"


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze gravity-like invariants and produce visualization-ready physics artifacts.")
    parser.add_argument(
        "--template-set",
        default="physics8",
        choices=("physics2", "physics3", "physics4", "physics5", "physics6", "physics7", "physics8", "physics9", "physics10", "physics11", "physics12", "physics13", "physics14", "physics15", "physics16", "physics17", "physics18", "physics19", "physics20", "physics21", "carrier8_physics1"),
        help="Physics template set to analyze.",
    )
    parser.add_argument("--max-trace-steps", type=int, default=24, help="Max steps per sample trace.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: benchmarks/results/<today>-physics-invariants-<template>.json).",
    )
    args = parser.parse_args()

    output_path = (
        Path(args.output)
        if args.output
        else ROOT / "benchmarks" / "results" / f"{date.today().isoformat()}-physics-invariants-{args.template_set}.json"
    )

    carrier_family, runtime = load_runtime(args.template_set)
    transitions, transition_source_summary = runtime.transitions_from_templates(args.template_set)
    succ, edge_name, nodes = deterministic_graph(transitions, runtime.matches, runtime.apply_transition)

    candidates: list[CandidateScore] = []
    if len(REGISTERS) == 8:
        sample_starts = [
            (1, 0, 0, 1, 0, -1, 0, 0),
            (0, 0, 0, 1, 0, -1, 0, 0),
            (1, 1, 0, 1, -1, -1, 0, 1),
            (-1, -1, 0, 1, 0, -1, 1, -1),
        ]
    else:
        sample_starts = [
            (1, 0, 0, 1, 0, -1),
            (0, 0, 0, 1, 0, -1),
            (1, 1, 0, 1, -1, -1),
            (-1, -1, 0, 1, 0, -1),
        ]
    analysis_nodes, analysis_succ, analysis_scope = build_analysis_subset(
        carrier_family,
        nodes,
        succ,
        sample_starts,
    )
    analysis_edge_name = {src: edge_name[src] for src in analysis_succ}
    components = tarjan_scc(analysis_nodes, analysis_succ)
    cycles = cycle_components(components, analysis_succ)
    dist = distance_to_cycle(analysis_nodes, analysis_succ, cycles)

    candidates.append(evaluate_candidate("distance_to_cycle", lambda s: float(dist[s]), analysis_succ))
    candidates.append(evaluate_candidate("action_rank", lambda s: float(runtime.action_rank(s)), analysis_succ))
    candidates.append(evaluate_candidate("abs_l1", lambda s: float(sum(abs(v) for v in s)), analysis_succ))
    if len(REGISTERS) <= 6:
        weighted = search_weighted_potential(analysis_succ)
        candidates.append(weighted)
    candidates_sorted = sorted(
        candidates,
        key=lambda c: (c.nonincrease_ratio, c.strict_decrease_ratio, -c.increases),
        reverse=True,
    )
    best = candidates_sorted[0]

    emb2 = pca_embedding(analysis_nodes)
    traces = []
    for start in sample_starts:
        if start not in succ and start not in nodes:
            continue
        traj = trace_from(start, analysis_succ, args.max_trace_steps)
        traces.append(
            {
                "start": list(start),
                "path": [list(state) for state in traj],
                "path_xy": [list(emb2[state]) for state in traj],
                "transitions": [analysis_edge_name.get(traj[i], "halt") for i in range(len(traj) - 1)],
            }
        )

    exact_laws = {
        "source_charge_conservation": source_charge_laws(analysis_succ),
        "source_parity_sector_preservation": source_parity_laws(analysis_succ),
        "locality_radius_bound": locality_law(analysis_succ),
        "forward_cone_bound": forward_cone_law(analysis_nodes, analysis_succ),
        "cycle_distance_nonincrease": cycle_distance_law(analysis_succ, dist),
    }
    statistical_laws = {
        "perturbation_stability": {
            "mode": "statistical",
            "families": {
                "single_register_sign_flip": perturbation_family_score(
                    "single_register_sign_flip", analysis_nodes, analysis_succ, sign_flip_neighbors
                ),
                "single_register_zero_toggle": perturbation_family_score(
                    "single_register_zero_toggle", analysis_nodes, analysis_succ, zero_toggle_neighbors
                ),
                "paired_defect": perturbation_family_score(
                    "paired_defect", analysis_nodes, analysis_succ, paired_defect_neighbors
                ),
            },
        },
        "geodesic_like_flow": geodesic_like_flow_law(analysis_nodes, analysis_succ, dist, cycles),
        "curvature_like_concentration": curvature_like_concentration_law(analysis_nodes, dist, cycles),
        "defect_attraction": defect_attraction_law(analysis_succ),
    }

    payload = {
        "template_set": args.template_set,
        "carrier_family": carrier_family,
        "transition_source_summary": transition_source_summary,
        "state_space_size": len(nodes),
        "analysis_scope": analysis_scope,
        "analysis_state_count": len(analysis_nodes),
        "deterministic_edges": len(analysis_succ),
        "deterministic_edges_full": len(succ),
        "scc_count": len(components),
        "cycle_component_count": len(cycles),
        "physics_target_suite": {
            "version": TARGET_SUITE_VERSION,
            "exact_laws": exact_laws,
            "statistical_laws": statistical_laws,
        },
        "observable_surrogates": observable_surrogates(analysis_nodes, analysis_succ, dist),
        "candidate_invariants": [
            {
                "name": c.name,
                "nonincrease_ratio": c.nonincrease_ratio,
                "strict_decrease_ratio": c.strict_decrease_ratio,
                "increase_ratio": c.increase_ratio,
                "increases": c.increases,
                "edges": c.edges,
                "details": c.details,
            }
            for c in candidates_sorted
        ],
        "best_candidate": {
            "name": best.name,
            "nonincrease_ratio": best.nonincrease_ratio,
            "strict_decrease_ratio": best.strict_decrease_ratio,
            "increase_ratio": best.increase_ratio,
            "increases": best.increases,
            "edges": best.edges,
            "details": best.details,
        },
        "visualization": {
            "embedding": [
                {
                    "state": list(state),
                    "x": emb2[state][0],
                    "y": emb2[state][1],
                    "distance_to_cycle": dist[state],
                    "action_rank": runtime.action_rank(state),
                }
                for state in analysis_nodes
            ],
            "edges": [
                {
                    "source": list(src),
                    "target": list(dst),
                    "transition": analysis_edge_name[src],
                }
                for src, dst in analysis_succ.items()
            ],
            "sample_traces": traces,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(f"wrote {output_path}")
    print(
        f"best_candidate={best.name} "
        f"nonincrease={best.nonincrease_ratio:.4f} "
        f"strict={best.strict_decrease_ratio:.4f}"
    )


if __name__ == "__main__":
    main()
