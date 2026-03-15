#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import defaultdict
from datetime import date
from itertools import product
from pathlib import Path
from typing import Any


STATE_NAME_BY_VALUE = {-1: "negative", 0: "zero", 1: "positive"}
STATE_ORDER = ("negative", "zero", "positive")
GATE_SHAPE_BASINS = 10
GATE_SHAPE_PRIMES = 15
GATE_CHAIN_HEIGHT = 4
GATE_EFFECTIVE_DIMENSION = 4


def parse_state_tuple(raw: str) -> tuple[int, ...]:
    value = ast.literal_eval(raw)
    if not isinstance(value, tuple):
        raise ValueError(f"state key is not a tuple: {raw}")
    parsed = tuple(int(item) for item in value)
    for item in parsed:
        if item not in (-1, 0, 1):
            raise ValueError(f"invalid ternary entry {item} in {raw}")
    return parsed


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def with_hash(payload: dict[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    out = dict(payload)
    out["sha256"] = hashlib.sha256(encoded).hexdigest()
    return out


def extract_prime_layout(state_artifact: dict[str, Any], register_limit: int) -> tuple[list[str], list[dict[str, Any]]]:
    registers_raw = state_artifact.get("registers")
    if not isinstance(registers_raw, list):
        raise ValueError("state artifact missing registers list")
    registers = registers_raw[:register_limit]
    if len(registers) != register_limit:
        raise ValueError(f"need at least {register_limit} registers in state artifact")
    prime_labels: list[str] = []
    for reg in registers:
        reg_name = str(reg["name"])
        for state_name in STATE_ORDER:
            prime = int(reg[state_name])
            prime_labels.append(f"{reg_name}:{state_name}:{prime}")
    return prime_labels, registers


def state_key(state: tuple[int, ...]) -> str:
    return str(state)


def build_transition_list(physics_artifact: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    transitions = physics_artifact.get("transitions")
    register_count = int(physics_artifact.get("register_count", 0))
    if not isinstance(transitions, list) or register_count <= 0:
        raise ValueError("physics artifact missing transition list/register_count")
    normalized: list[dict[str, Any]] = []
    for item in transitions:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "name": str(item.get("name", "unnamed_transition")),
                "condition": dict(item.get("condition", {})),
                "action": dict(item.get("action", {})),
            }
        )
    if not normalized:
        raise ValueError("no transitions found in physics artifact")
    return normalized, register_count


def _register_names(count: int) -> list[str]:
    return [f"R{idx + 1}" for idx in range(count)]


def _matches(state: tuple[int, ...], transition: dict[str, Any], register_count: int) -> bool:
    names = _register_names(register_count)
    for register, required in transition.get("condition", {}).items():
        if register not in names:
            return False
        idx = names.index(register)
        value = state[idx]
        if STATE_NAME_BY_VALUE[value] != required:
            return False
    return True


def _apply(state: tuple[int, ...], transition: dict[str, Any], register_count: int) -> tuple[int, ...]:
    names = _register_names(register_count)
    next_state = list(state)
    for register, target in transition.get("action", {}).items():
        if register not in names:
            continue
        idx = names.index(register)
        if target == "negative":
            next_state[idx] = -1
        elif target == "zero":
            next_state[idx] = 0
        elif target == "positive":
            next_state[idx] = 1
    return tuple(next_state)


def deterministic_successor(
    state: tuple[int, ...],
    transitions: list[dict[str, Any]],
    register_count: int,
) -> tuple[int, ...] | None:
    for transition in transitions:
        if _matches(state, transition, register_count):
            return _apply(state, transition, register_count)
    return None


def rebuild_fixed_walks(
    transitions: list[dict[str, Any]],
    register_count: int,
    max_steps: int,
) -> dict[str, dict[str, Any]]:
    walks: dict[str, dict[str, Any]] = {}
    for state in product((-1, 0, 1), repeat=register_count):
        start = tuple(int(v) for v in state)
        current = start
        seen: dict[tuple[int, ...], int] = {}
        path: list[dict[str, Any]] = []
        status = "timeout"
        cycle_start = None
        final_state = current
        for step in range(max_steps):
            if current in seen:
                status = "cycle"
                cycle_start = seen[current]
                final_state = current
                break
            seen[current] = step
            nxt = deterministic_successor(current, transitions, register_count)
            if nxt is None:
                status = "terminal"
                final_state = current
                break
            path.append(
                {
                    "step": step + 1,
                    "state": list(current),
                    "transition": str(next(t["name"] for t in transitions if _matches(current, t, register_count))),
                    "next_state": list(nxt),
                }
            )
            current = nxt
            final_state = current
        walks[state_key(start)] = {
            "status": status,
            "start": list(start),
            "final_state": list(final_state),
            "steps": len(path),
            "max_steps": max_steps,
            "cycle_start": cycle_start,
            "path": path,
        }
    return walks


def basin_key_for_outcome(outcome: dict[str, Any]) -> str:
    status = str(outcome.get("status", "timeout"))
    if status == "terminal":
        final_state = tuple(int(v) for v in outcome["final_state"])
        return f"terminal:{final_state}"
    if status == "cycle":
        cycle_start = outcome.get("cycle_start")
        path = outcome.get("path", [])
        if isinstance(cycle_start, int) and 0 <= cycle_start < len(path):
            cycle_entry = tuple(int(v) for v in path[cycle_start]["state"])
        else:
            cycle_entry = tuple(int(v) for v in outcome["final_state"])
        return f"cycle:{cycle_entry}"
    timeout_state = tuple(int(v) for v in outcome["final_state"])
    return f"timeout:{timeout_state}"


def state_to_godel_value(state: tuple[int, ...], register_specs: list[dict[str, Any]]) -> int:
    value = 1
    for idx, entry in enumerate(register_specs):
        signed = int(state[idx])
        if signed == -1:
            prime = int(entry["negative"])
        elif signed == 0:
            prime = int(entry["zero"])
        else:
            prime = int(entry["positive"])
        value *= prime
    return value


def q_sector_id(n_value: int) -> int:
    return ((n_value % 71) + (n_value % 59) + (n_value % 47)) % 10


def build_atomic_sector_edges(
    states: list[tuple[int, ...]],
    transitions: list[dict[str, Any]],
    register_count: int,
    register_specs: list[dict[str, Any]],
    edge_mode: str,
) -> tuple[set[tuple[int, int]], list[dict[str, Any]], dict[tuple[int, int], list[dict[str, Any]]]]:
    def parity_signature(state: tuple[int, ...]) -> int:
        return sum(abs(int(v)) for v in state) % 2

    def is_reflection_constrained(
        state: tuple[int, ...], next_state: tuple[int, ...], transition_name: str
    ) -> bool:
        # Proxy for explicit reflection closure when Clifford backend is unavailable:
        # accept only sign-flip-like or balanced exchange moves.
        delta = [int(next_state[i]) - int(state[i]) for i in range(len(state))]
        nonzero = [value for value in delta if value != 0]
        if not nonzero:
            return False
        if all(value in (-2, 2) for value in nonzero):
            return True
        if sorted(nonzero) == [-1, 1]:
            return True
        if "reflect" in transition_name.lower():
            return True
        return False

    edges: set[tuple[int, int]] = set()
    trace_samples: list[dict[str, Any]] = []
    edge_witnesses: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for state in states:
        n_before = state_to_godel_value(state, register_specs)
        sector_before = q_sector_id(n_before)
        for transition in transitions:
            if not _matches(state, transition, register_count):
                continue
            next_state = _apply(state, transition, register_count)
            transition_name = str(transition["name"])
            delta_l1 = sum(abs(int(next_state[i]) - int(state[i])) for i in range(len(state)))
            if edge_mode == "atomic_local" and delta_l1 != 2:
                continue
            if edge_mode == "parity_preserving":
                if delta_l1 != 2:
                    continue
                if parity_signature(state) != parity_signature(next_state):
                    continue
            if edge_mode == "reflection_constrained":
                if delta_l1 != 2:
                    continue
                if parity_signature(state) != parity_signature(next_state):
                    continue
                if not is_reflection_constrained(state, next_state, transition_name):
                    continue
            if edge_mode in {
                "reflection_rank4_projected_single_wall",
                "reflection_rank4_projected_min_support",
                "reflection_single_wall_min_support",
                "reflection_rank4_projected_single_wall_orbit_consistent",
            } and delta_l1 != 2:
                continue
            n_after = state_to_godel_value(next_state, register_specs)
            sector_after = q_sector_id(n_after)
            if sector_before != sector_after:
                edges.add((sector_before, sector_after))
                edge_witnesses[(sector_before, sector_after)].append(
                    {
                        "transition": transition_name,
                        "delta_signed": [int(next_state[i]) - int(state[i]) for i in range(len(state))],
                        "support": sum(1 for i in range(len(state)) if int(next_state[i]) != int(state[i])),
                        "delta_l1": delta_l1,
                        "state": list(state),
                        "next_state": list(next_state),
                        "godel_before": n_before,
                        "godel_after": n_after,
                    }
                )
                if len(trace_samples) < 24:
                    trace_samples.append(
                        {
                            "transition": transition_name,
                            "state": list(state),
                            "next_state": list(next_state),
                            "godel_before": n_before,
                            "godel_after": n_after,
                            "sector_before": sector_before,
                            "sector_after": sector_after,
                            "delta_l1": delta_l1,
                            "edge_mode": edge_mode,
                        }
                    )
    return edges, trace_samples, dict(edge_witnesses)


def maybe_numpy() -> Any | None:
    try:
        import numpy as np
    except ModuleNotFoundError:
        return None
    return np


def single_wall_ok(x4: Any, y4: Any, roots4: Any, eps: float) -> bool:
    wall_changes = 0
    for root in roots4:
        sx = 1 if float(x4 @ root) > eps else -1 if float(x4 @ root) < -eps else 0
        sy = 1 if float(y4 @ root) > eps else -1 if float(y4 @ root) < -eps else 0
        if sx != sy:
            wall_changes += 1
            if wall_changes > 1:
                return False
    return True


def rank4_projected_ok(
    x15: list[float],
    y15: list[float],
    x4: Any,
    y4: Any,
    roots4: Any,
    proj_thresh: float,
    align_thresh: float,
) -> bool:
    np = maybe_numpy()
    if np is None:
        return True
    d15 = np.array(y15, dtype=float) - np.array(x15, dtype=float)
    d4 = np.array(y4, dtype=float) - np.array(x4, dtype=float)
    n15 = float(np.linalg.norm(d15))
    n4 = float(np.linalg.norm(d4))
    if n15 <= 1e-12 or n4 <= 1e-12:
        return False
    if (n4 * n4) / (n15 * n15) < proj_thresh:
        return False
    best_align = 0.0
    for root in roots4:
        nr = float(np.linalg.norm(root))
        if nr <= 1e-12:
            continue
        align = abs(float(d4 @ root)) / (n4 * nr)
        best_align = max(best_align, align)
    return best_align >= align_thresh


def min_support_ok(witnesses: list[dict[str, Any]], support_max: int, l1_max: int) -> bool:
    for witness in witnesses:
        if int(witness.get("support", 999)) <= support_max and int(witness.get("delta_l1", 999)) <= l1_max:
            return True
    return False


def orbit_consistent_filter(
    edges: set[tuple[int, int]],
    stability: list[int],
) -> set[tuple[int, int]]:
    groups: dict[int, list[int]] = defaultdict(list)
    for idx, value in enumerate(stability):
        groups[int(value)].append(idx)
    groups = {value: members for value, members in groups.items() if len(members) > 1}
    if not groups:
        return edges

    out_by_src: dict[int, list[int]] = defaultdict(list)
    in_by_dst: dict[int, list[int]] = defaultdict(list)
    for src, dst in edges:
        out_by_src[src].append(dst)
        in_by_dst[dst].append(src)

    keep: set[tuple[int, int]] = set()
    for src, dst in edges:
        src_stability = stability[src]
        dst_stability = stability[dst]
        src_group = groups.get(src_stability, [src])
        dst_group = groups.get(dst_stability, [dst])
        src_ok = all(
            any(stability[neighbor] == dst_stability for neighbor in out_by_src.get(other_src, []))
            for other_src in src_group
        )
        dst_ok = all(
            any(stability[neighbor] == src_stability for neighbor in in_by_dst.get(other_dst, []))
            for other_dst in dst_group
        )
        if src_ok and dst_ok:
            keep.add((src, dst))
    return keep if keep else edges


def filter_sector_edges(
    adjacency_pairs: set[tuple[int, int]],
    matrix_rows: list[list[float]],
    stability: list[int],
    edge_witnesses: dict[tuple[int, int], list[dict[str, Any]]],
    edge_mode: str,
    *,
    proj_thresh: float,
    align_thresh: float,
    support_max: int,
    l1_max: int,
    wall_eps: float,
) -> set[tuple[int, int]]:
    if edge_mode not in {
        "reflection_rank4_projected_single_wall",
        "reflection_rank4_projected_min_support",
        "reflection_single_wall_min_support",
        "reflection_rank4_projected_single_wall_orbit_consistent",
    }:
        return adjacency_pairs

    np = maybe_numpy()
    if np is None:
        return adjacency_pairs
    arr = np.array(matrix_rows, dtype=float)
    centered = arr - np.mean(arr, axis=0, keepdims=True)
    _u, _s, vh = np.linalg.svd(centered, full_matrices=False)
    axes = vh[:4]
    emb = centered @ axes.T
    roots4 = np.eye(min(4, emb.shape[1]), dtype=float)

    filtered: set[tuple[int, int]] = set()
    for src, dst in adjacency_pairs:
        x15 = matrix_rows[src]
        y15 = matrix_rows[dst]
        x4 = emb[src]
        y4 = emb[dst]
        witnesses = edge_witnesses.get((src, dst), [])
        projected = rank4_projected_ok(x15, y15, x4, y4, roots4, proj_thresh, align_thresh)
        single_wall = single_wall_ok(x4, y4, roots4, wall_eps)
        min_support = min_support_ok(witnesses, support_max, l1_max)
        keep = False
        if edge_mode == "reflection_rank4_projected_single_wall":
            keep = projected and single_wall
        elif edge_mode == "reflection_rank4_projected_min_support":
            keep = projected and min_support
        elif edge_mode == "reflection_single_wall_min_support":
            keep = single_wall and min_support
        elif edge_mode == "reflection_rank4_projected_single_wall_orbit_consistent":
            keep = projected and single_wall
        if keep:
            filtered.add((src, dst))

    if edge_mode == "reflection_rank4_projected_single_wall_orbit_consistent":
        filtered = orbit_consistent_filter(filtered, stability)
    return filtered


def quotient_raw_basins_to_sectors(
    basin_members: dict[str, list[tuple[int, ...]]],
    register_specs: list[dict[str, Any]],
) -> tuple[dict[str, list[tuple[int, ...]]], dict[str, str], dict[str, Any]]:
    raw_to_sector: dict[str, str] = {}
    sector_members: dict[str, list[tuple[int, ...]]] = defaultdict(list)
    q_rows: list[dict[str, Any]] = []
    for raw_id, members in sorted(basin_members.items(), key=lambda item: item[0]):
        representative = sorted(members)[0]
        n_value = state_to_godel_value(representative, register_specs)
        sector = q_sector_id(n_value)
        sector_id = f"sector:{sector}"
        raw_to_sector[raw_id] = sector_id
        sector_members[sector_id].extend(members)
        q_rows.append(
            {
                "raw_basin_id": raw_id,
                "raw_basin_size": len(members),
                "representative_state": list(representative),
                "godel_value": n_value,
                "sector_id": sector_id,
            }
        )
    reduced = {sector: sorted(members) for sector, members in sorted(sector_members.items(), key=lambda item: item[0])}
    q_artifact = {
        "quotient_name": "rfc10006_sector_id",
        "formula": "q(N)=((N mod 71)+(N mod 59)+(N mod 47)) mod 10",
        "raw_basin_count": len(basin_members),
        "sector_count_nonempty": len(reduced),
        "rows": q_rows,
    }
    return reduced, raw_to_sector, q_artifact


def build_common_basin_payload(
    basin_members: dict[str, list[tuple[int, ...]]],
    state_to_basin: dict[tuple[int, ...], str],
    states: list[tuple[int, ...]],
    transitions: list[dict[str, Any]],
    register_count: int,
    register_specs: list[dict[str, Any]],
    edge_mode: str,
    edge_params: dict[str, Any],
    *,
    top_k: int,
    register_limit: int,
    prime_labels: list[str],
    registers: list[dict[str, Any]],
    derivation_name: str,
) -> dict[str, Any]:
    reduced_members, merge_map, q_map_artifact = quotient_raw_basins_to_sectors(basin_members, register_specs)
    reduced_state_to_basin: dict[tuple[int, ...], str] = {
        state: merge_map.get(raw_basin, raw_basin) for state, raw_basin in state_to_basin.items()
    }

    top_basins = sorted(((basin_id, len(members)) for basin_id, members in reduced_members.items()), key=lambda item: item[0])
    if len(top_basins) > top_k:
        top_basins = top_basins[:top_k]
    selected_basin_ids = [item[0] for item in top_basins]
    selected_index = {basin_id: idx for idx, basin_id in enumerate(selected_basin_ids)}

    basins: list[dict[str, Any]] = []
    matrix_rows: list[list[float]] = []
    stability: list[int] = []
    for basin_id, member_count in top_basins:
        members = reduced_members[basin_id]
        counts = [0.0] * (register_limit * len(STATE_ORDER))
        for state in members:
            for reg_idx in range(register_limit):
                state_name = STATE_NAME_BY_VALUE[int(state[reg_idx])]
                state_idx = STATE_ORDER.index(state_name)
                counts[reg_idx * len(STATE_ORDER) + state_idx] += 1.0
        normalized = [count / float(len(members)) for count in counts]
        matrix_rows.append(normalized)
        stability.append(member_count)
        representative = members[0]
        basins.append(
            {
                "id": basin_id,
                "size": member_count,
                "representative_state": list(representative),
                "sample_members": [list(state) for state in sorted(members)[:8]],
            }
        )

    sector_edges, transfer_samples, edge_witnesses = build_atomic_sector_edges(
        states,
        transitions,
        register_count,
        register_specs,
        edge_mode=edge_mode,
    )
    adjacency_pairs: set[tuple[int, int]] = set()
    for src_sector, dst_sector in sector_edges:
        src_id = f"sector:{src_sector}"
        dst_id = f"sector:{dst_sector}"
        if src_id in selected_index and dst_id in selected_index and src_id != dst_id:
            adjacency_pairs.add((selected_index[src_id], selected_index[dst_id]))
    adjacency_pairs = filter_sector_edges(
        adjacency_pairs,
        matrix_rows,
        stability,
        edge_witnesses,
        edge_mode,
        proj_thresh=float(edge_params.get("proj_thresh", 0.95)),
        align_thresh=float(edge_params.get("align_thresh", 0.90)),
        support_max=int(edge_params.get("support_max", 2)),
        l1_max=int(edge_params.get("l1_max", 4)),
        wall_eps=float(edge_params.get("wall_eps", 1e-8)),
    )

    adjacency = sorted(
        [
            {
                "from": src,
                "to": dst,
                "from_basin_id": selected_basin_ids[src],
                "to_basin_id": selected_basin_ids[dst],
            }
            for src, dst in adjacency_pairs
        ],
        key=lambda item: (item["from"], item["to"]),
    )

    return {
        "derivation_name": derivation_name,
        "shape": {"basins": len(basins), "primes": len(prime_labels)},
        "basins": basins,
        "prime_labels": prime_labels,
        "prime_layout_registers": [
            {
                "name": str(reg["name"]),
                "negative": int(reg["negative"]),
                "zero": int(reg["zero"]),
                "positive": int(reg["positive"]),
            }
            for reg in registers
        ],
        "matrix": matrix_rows,
        "stability": stability,
        "adjacency": adjacency,
        "selection_policy": {
            "top_k": top_k,
            "register_limit": register_limit,
            "stability_definition": "basin degeneracy count",
            "matrix_encoding": "per-basin average one-hot occupancy over selected register-state primes",
            "reduction": {
                "mode": "quotient",
                "raw_basin_count": len(basin_members),
                "target_count": top_k,
                "quotient_name": q_map_artifact["quotient_name"],
            },
            "edge_mode": edge_mode,
            "edge_params": {
                "proj_thresh": float(edge_params.get("proj_thresh", 0.95)),
                "align_thresh": float(edge_params.get("align_thresh", 0.90)),
                "support_max": int(edge_params.get("support_max", 2)),
                "l1_max": int(edge_params.get("l1_max", 4)),
                "wall_eps": float(edge_params.get("wall_eps", 1e-8)),
            },
        },
        "q_map_artifact": q_map_artifact,
        "atomic_transfer_samples": transfer_samples,
    }


def derive_walk_partition(
    fixed_walks: dict[str, dict[str, Any]],
    states: list[tuple[int, ...]],
    transitions: list[dict[str, Any]],
    register_count: int,
    register_specs: list[dict[str, Any]],
    edge_mode: str,
    edge_params: dict[str, Any],
    *,
    top_k: int,
    register_limit: int,
    prime_labels: list[str],
    registers: list[dict[str, Any]],
) -> dict[str, Any]:
    state_to_basin: dict[tuple[int, ...], str] = {}
    basin_members: dict[str, list[tuple[int, ...]]] = defaultdict(list)
    for state_key_raw, outcome in fixed_walks.items():
        state = parse_state_tuple(state_key_raw)
        basin_id = basin_key_for_outcome(outcome)
        state_to_basin[state] = basin_id
        basin_members[basin_id].append(state)
    return build_common_basin_payload(
        basin_members,
        state_to_basin,
        states,
        transitions,
        register_count,
        register_specs,
        edge_mode,
        edge_params,
        top_k=top_k,
        register_limit=register_limit,
        prime_labels=prime_labels,
        registers=registers,
        derivation_name="walk_partition",
    )


def tarjan_scc(nodes: list[tuple[int, ...]], successor_map: dict[tuple[int, ...], tuple[int, ...] | None]) -> list[list[tuple[int, ...]]]:
    index = 0
    stack: list[tuple[int, ...]] = []
    on_stack: set[tuple[int, ...]] = set()
    indices: dict[tuple[int, ...], int] = {}
    lowlinks: dict[tuple[int, ...], int] = {}
    components: list[list[tuple[int, ...]]] = []

    def strongconnect(node: tuple[int, ...]) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        succ = successor_map.get(node)
        if succ is not None:
            if succ not in indices:
                strongconnect(succ)
                lowlinks[node] = min(lowlinks[node], lowlinks[succ])
            elif succ in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[succ])

        if lowlinks[node] == indices[node]:
            component: list[tuple[int, ...]] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            components.append(sorted(component))

    for node in sorted(nodes):
        if node not in indices:
            strongconnect(node)
    return components


def derive_scc_condensation(
    nodes: list[tuple[int, ...]],
    successor_map: dict[tuple[int, ...], tuple[int, ...] | None],
    states: list[tuple[int, ...]],
    transitions: list[dict[str, Any]],
    register_count: int,
    register_specs: list[dict[str, Any]],
    edge_mode: str,
    edge_params: dict[str, Any],
    *,
    top_k: int,
    register_limit: int,
    prime_labels: list[str],
    registers: list[dict[str, Any]],
) -> dict[str, Any]:
    components = tarjan_scc(nodes, successor_map)
    node_to_component: dict[tuple[int, ...], int] = {}
    for comp_idx, component in enumerate(components):
        for node in component:
            node_to_component[node] = comp_idx

    component_out: dict[int, set[int]] = {idx: set() for idx in range(len(components))}
    for node in nodes:
        succ = successor_map.get(node)
        if succ is None:
            continue
        src = node_to_component[node]
        dst = node_to_component[succ]
        if src != dst:
            component_out[src].add(dst)

    sink_components = sorted(idx for idx, outgoing in component_out.items() if not outgoing)

    sink_for_component: dict[int, int] = {}

    def resolve_sink(component_idx: int) -> int:
        if component_idx in sink_for_component:
            return sink_for_component[component_idx]
        if component_idx in sink_components:
            sink_for_component[component_idx] = component_idx
            return component_idx
        outgoing = sorted(component_out[component_idx])
        if not outgoing:
            sink_for_component[component_idx] = component_idx
            return component_idx
        sink_for_component[component_idx] = resolve_sink(outgoing[0])
        return sink_for_component[component_idx]

    state_to_basin: dict[tuple[int, ...], str] = {}
    basin_members: dict[str, list[tuple[int, ...]]] = defaultdict(list)
    sink_rank = {sink: idx for idx, sink in enumerate(sorted(sink_components))}
    for node in nodes:
        component_idx = node_to_component[node]
        sink_idx = resolve_sink(component_idx)
        basin_id = f"scc:{sink_rank.get(sink_idx, sink_idx)}"
        state_to_basin[node] = basin_id
        basin_members[basin_id].append(node)

    return build_common_basin_payload(
        basin_members,
        state_to_basin,
        states,
        transitions,
        register_count,
        register_specs,
        edge_mode,
        edge_params,
        top_k=top_k,
        register_limit=register_limit,
        prime_labels=prime_labels,
        registers=registers,
        derivation_name="scc_condensation",
    )


def pca_effective_dimension(matrix: list[list[float]], threshold: float) -> int | None:
    try:
        import numpy as np
    except ModuleNotFoundError:
        return None
    arr = np.array(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] == 0 or arr.shape[1] == 0:
        return None
    centered = arr - np.mean(arr, axis=0, keepdims=True)
    _u, singular, _vh = np.linalg.svd(centered, full_matrices=False)
    variances = singular**2
    total = float(np.sum(variances))
    if total <= 0.0:
        return len(variances)
    cumulative = 0.0
    for idx, variance in enumerate(variances, start=1):
        cumulative += float(variance / total)
        if cumulative >= threshold:
            return idx
    return len(variances)


def chain_height_from_stability(stability: list[int], adjacency: list[dict[str, Any]]) -> int:
    edges: list[tuple[int, int]] = []
    for edge in adjacency:
        src = int(edge["from"])
        dst = int(edge["to"])
        if src < 0 or dst < 0 or src >= len(stability) or dst >= len(stability):
            continue
        if stability[src] > stability[dst]:
            edges.append((src, dst))
    graph: dict[int, list[int]] = {idx: [] for idx in range(len(stability))}
    for src, dst in edges:
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

    return max((dfs(node) for node in range(len(stability))), default=0)


def compute_metrics(payload: dict[str, Any], variance_threshold: float) -> dict[str, Any]:
    shape = payload["shape"]
    matrix = payload["matrix"]
    stability = [int(v) for v in payload["stability"]]
    adjacency = payload["adjacency"]
    effective_dim = pca_effective_dimension(matrix, variance_threshold)
    chain_height = chain_height_from_stability(stability, adjacency)
    shape_ok = int(shape["basins"]) == GATE_SHAPE_BASINS and int(shape["primes"]) == GATE_SHAPE_PRIMES
    lock_pass = (
        shape_ok
        and effective_dim == GATE_EFFECTIVE_DIMENSION
        and chain_height == GATE_CHAIN_HEIGHT
    )
    return {
        "variance_threshold": variance_threshold,
        "effective_dimension": effective_dim,
        "monotone_chain_height": chain_height,
        "shape_ok": shape_ok,
        "lock_gate_pass": lock_pass,
    }


def load_previous_canonical(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    try:
        payload = load_json(path)
    except Exception:
        return None
    candidate = payload.get("canonical_derivation")
    if isinstance(candidate, str) and candidate:
        return candidate
    return None


def choose_canonical(
    derivations: dict[str, dict[str, Any]],
    *,
    policy: str,
    tiebreak: str,
    previous_canonical: str | None,
) -> tuple[str, str, bool]:
    if len(derivations) == 1:
        only = next(iter(derivations.keys()))
        return only, "single-derivation", bool(derivations[only]["metrics"]["lock_gate_pass"])

    passers = sorted([name for name, payload in derivations.items() if payload["metrics"]["lock_gate_pass"]])
    if policy != "best-of-two":
        raise ValueError(f"unsupported policy {policy}")
    if len(passers) == 1:
        selected = passers[0]
        return selected, "gate-pass-unique", True
    if len(passers) == 2:
        if tiebreak == "keep-previous" and previous_canonical in passers:
            return previous_canonical, "tiebreak-keep-previous", True
        if tiebreak == "prefer-scc":
            return "scc_condensation", "tiebreak-prefer-scc", True
        if tiebreak == "prefer-walk":
            return "walk_partition", "tiebreak-prefer-walk", True
        return "scc_condensation", "tiebreak-bootstrap", True

    if previous_canonical in derivations:
        return previous_canonical, "no-gate-pass-keep-previous", False
    return "scc_condensation", "no-gate-pass-bootstrap-scc", False


def build_dataset(
    physics_artifact: dict[str, Any],
    state_artifact: dict[str, Any],
    *,
    derivation_mode: str,
    top_k: int,
    register_limit: int,
    fallback_max_steps: int,
    variance_threshold: float,
    canonical_policy: str,
    tiebreak: str,
    previous_canonical: str | None,
    edge_mode: str,
    edge_params: dict[str, Any],
) -> dict[str, Any]:
    transitions, register_count = build_transition_list(physics_artifact)
    states = [tuple(int(v) for v in state) for state in product((-1, 0, 1), repeat=register_count)]
    successor_map = {
        state: deterministic_successor(state, transitions, register_count)
        for state in states
    }
    fixed_walks = physics_artifact.get("fixed_prime_walks")
    fixed_walks_rebuilt = False
    if not isinstance(fixed_walks, dict):
        fixed_walks = rebuild_fixed_walks(transitions, register_count, fallback_max_steps)
        fixed_walks_rebuilt = True

    prime_labels, registers = extract_prime_layout(state_artifact, register_limit=register_limit)
    all_register_specs = state_artifact.get("registers")
    if not isinstance(all_register_specs, list) or len(all_register_specs) < register_count:
        raise ValueError("state artifact missing full register specs for q-map")

    derivations: dict[str, dict[str, Any]] = {}
    if derivation_mode in {"walk_partition", "both"}:
        derivations["walk_partition"] = derive_walk_partition(
            fixed_walks,
            states,
            transitions,
            register_count,
            all_register_specs,
            edge_mode,
            edge_params,
            top_k=top_k,
            register_limit=register_limit,
            prime_labels=prime_labels,
            registers=registers,
        )
    if derivation_mode in {"scc_condensation", "both"}:
        derivations["scc_condensation"] = derive_scc_condensation(
            states,
            successor_map,
            states,
            transitions,
            register_count,
            all_register_specs,
            edge_mode,
            edge_params,
            top_k=top_k,
            register_limit=register_limit,
            prime_labels=prime_labels,
            registers=registers,
        )

    if not derivations:
        raise ValueError("no derivations generated")

    for payload in derivations.values():
        payload["metrics"] = compute_metrics(payload, variance_threshold)
        payload["selection_policy"]["fixed_walks_rebuilt_from_transitions"] = fixed_walks_rebuilt
        payload["selection_policy"]["fallback_max_steps"] = fallback_max_steps

    canonical_derivation, canonical_reason, lock_pass = choose_canonical(
        derivations,
        policy=canonical_policy,
        tiebreak=tiebreak,
        previous_canonical=previous_canonical,
    )
    canonical_payload = derivations[canonical_derivation]
    q_map_summary = {
        name: {
            "quotient_name": payload.get("q_map_artifact", {}).get("quotient_name"),
            "raw_basin_count": payload.get("q_map_artifact", {}).get("raw_basin_count"),
            "sector_count_nonempty": payload.get("q_map_artifact", {}).get("sector_count_nonempty"),
        }
        for name, payload in derivations.items()
    }
    result = {
        "derivation_version": 2,
        "derivations": derivations,
        "canonical_derivation": canonical_derivation,
        "canonical_selection": {
            "policy": canonical_policy,
            "tiebreak": tiebreak,
            "reason": canonical_reason,
            "previous_canonical": previous_canonical,
            "lock_pass": lock_pass,
            "edge_mode": edge_mode,
        },
        "shape": canonical_payload["shape"],
        "basins": canonical_payload["basins"],
        "prime_labels": canonical_payload["prime_labels"],
        "prime_layout_registers": canonical_payload["prime_layout_registers"],
        "matrix": canonical_payload["matrix"],
        "stability": canonical_payload["stability"],
        "adjacency": canonical_payload["adjacency"],
        "selection_policy": canonical_payload["selection_policy"],
        "source_artifacts": {},
        "q_map_summary": q_map_summary,
        "notes": [
            "Derived deterministically from local artifacts; no external data fetch.",
            "Stability is basin degeneracy count.",
            "Canonical derivation is selected by best-of-two policy with configured tiebreak.",
            "The 10-basin model is built via deterministic quotient q(N)=((N mod 71)+(N mod 59)+(N mod 47)) mod 10.",
            f"Reduced edge relation uses mode: {edge_mode}.",
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Derive canonical rank-4 basin dataset from local FRACDASH artifacts."
    )
    parser.add_argument(
        "--physics-artifact",
        default="benchmarks/results/2026-03-14-agdas-physics8-phase2.json",
        help="Physics artifact containing transitions/fixed walks.",
    )
    parser.add_argument(
        "--state-artifact",
        default="benchmarks/results/2026-03-14-agdas-wave3-state.json",
        help="State artifact containing register prime definitions.",
    )
    parser.add_argument(
        "--derivation",
        choices=("walk_partition", "scc_condensation", "both"),
        default="both",
        help="Derivation mode (default: both).",
    )
    parser.add_argument("--top-k", type=int, default=10, help="Number of basins to keep (default: 10).")
    parser.add_argument(
        "--register-limit",
        type=int,
        default=5,
        help="Number of leading registers to include in prime matrix (default: 5 => 15 primes).",
    )
    parser.add_argument(
        "--fallback-max-steps",
        type=int,
        default=32,
        help="Step cap when fixed_prime_walks are rebuilt from transitions (default: 32).",
    )
    parser.add_argument(
        "--variance-threshold",
        type=float,
        default=0.997,
        help="Variance threshold for effective-dimension lock metric (default: 0.997).",
    )
    parser.add_argument(
        "--canonical-policy",
        choices=("best-of-two",),
        default="best-of-two",
        help="Canonical selection policy (default: best-of-two).",
    )
    parser.add_argument(
        "--tiebreak",
        choices=("keep-previous", "prefer-scc", "prefer-walk"),
        default="keep-previous",
        help="Tiebreak policy when both derivations pass lock gate.",
    )
    parser.add_argument(
        "--previous-canonical",
        default="benchmarks/results/rank4-dataset-latest.json",
        help="Path to previous canonical dataset used for keep-previous tiebreak.",
    )
    parser.add_argument(
        "--edge-mode",
        choices=(
            "all_atomic",
            "atomic_local",
            "parity_preserving",
            "reflection_constrained",
            "reflection_rank4_projected_single_wall",
            "reflection_rank4_projected_min_support",
            "reflection_single_wall_min_support",
            "reflection_rank4_projected_single_wall_orbit_consistent",
        ),
        default="reflection_single_wall_min_support",
        help="Reduced-edge construction mode for sector graph (default: reflection_single_wall_min_support).",
    )
    parser.add_argument("--proj-thresh", type=float, default=0.95, help="Projected-energy threshold.")
    parser.add_argument("--align-thresh", type=float, default=0.90, help="Projected root-alignment threshold.")
    parser.add_argument("--support-max", type=int, default=2, help="Max support size for witness delta.")
    parser.add_argument("--l1-max", type=int, default=4, help="Max L1 size for witness delta.")
    parser.add_argument("--wall-eps", type=float, default=1e-8, help="Tolerance for wall-sign checks.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path (default: benchmarks/results/<today>-rank4-dataset.json).",
    )
    parser.add_argument(
        "--latest",
        default="benchmarks/results/rank4-dataset-latest.json",
        help="Path for stable latest copy.",
    )
    parser.add_argument("--json", action="store_true", help="Print output payload to stdout.")
    args = parser.parse_args()

    physics_path = Path(args.physics_artifact)
    state_path = Path(args.state_artifact)
    previous_path = Path(args.previous_canonical) if args.previous_canonical else None
    output_path = (
        Path(args.output)
        if args.output
        else Path(f"benchmarks/results/{date.today().isoformat()}-rank4-dataset.json")
    )
    latest_path = Path(args.latest)

    physics_artifact = load_json(physics_path)
    state_artifact = load_json(state_path)
    previous_canonical = load_previous_canonical(previous_path)

    payload = build_dataset(
        physics_artifact,
        state_artifact,
        derivation_mode=args.derivation,
        top_k=max(1, args.top_k),
        register_limit=max(1, args.register_limit),
        fallback_max_steps=max(1, args.fallback_max_steps),
        variance_threshold=float(args.variance_threshold),
        canonical_policy=args.canonical_policy,
        tiebreak=args.tiebreak,
        previous_canonical=previous_canonical,
        edge_mode=args.edge_mode,
        edge_params={
            "proj_thresh": args.proj_thresh,
            "align_thresh": args.align_thresh,
            "support_max": args.support_max,
            "l1_max": args.l1_max,
            "wall_eps": args.wall_eps,
        },
    )
    payload["source_artifacts"] = {
        "physics_artifact": str(physics_path),
        "state_artifact": str(state_path),
    }
    payload = with_hash(payload)

    write_json(output_path, payload)
    write_json(latest_path, payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(f"wrote {output_path}")
    print(f"wrote {latest_path}")
    print(f"canonical_derivation: {payload['canonical_derivation']}")
    print(f"shape: {payload['shape']['basins']}x{payload['shape']['primes']}")
    print(f"lock_pass: {payload['canonical_selection']['lock_pass']}")
    print(f"sha256: {payload['sha256']}")


if __name__ == "__main__":
    main()
