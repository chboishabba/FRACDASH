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


def representative_from_basin_id(basin_id: str) -> tuple[int, ...]:
    _, _, payload = basin_id.partition(":")
    return parse_state_tuple(payload)


def build_common_basin_payload(
    basin_members: dict[str, list[tuple[int, ...]]],
    state_to_basin: dict[tuple[int, ...], str],
    successor_map: dict[tuple[int, ...], tuple[int, ...] | None],
    *,
    top_k: int,
    register_limit: int,
    prime_labels: list[str],
    registers: list[dict[str, Any]],
    derivation_name: str,
) -> dict[str, Any]:
    top_basins = sorted(
        ((basin_id, len(members)) for basin_id, members in basin_members.items()),
        key=lambda item: (-item[1], item[0]),
    )[:top_k]
    selected_basin_ids = [item[0] for item in top_basins]
    selected_index = {basin_id: idx for idx, basin_id in enumerate(selected_basin_ids)}

    basins: list[dict[str, Any]] = []
    matrix_rows: list[list[float]] = []
    stability: list[int] = []
    for basin_id, member_count in top_basins:
        members = basin_members[basin_id]
        counts = [0.0] * (register_limit * len(STATE_ORDER))
        for state in members:
            for reg_idx in range(register_limit):
                state_name = STATE_NAME_BY_VALUE[int(state[reg_idx])]
                state_idx = STATE_ORDER.index(state_name)
                counts[reg_idx * len(STATE_ORDER) + state_idx] += 1.0
        normalized = [count / float(len(members)) for count in counts]
        matrix_rows.append(normalized)
        stability.append(member_count)
        representative = members[0] if basin_id.startswith("scc:") else representative_from_basin_id(basin_id)
        basins.append(
            {
                "id": basin_id,
                "size": member_count,
                "representative_state": list(representative),
                "sample_members": [list(state) for state in sorted(members)[:8]],
            }
        )

    adjacency_pairs: set[tuple[int, int]] = set()
    for source_state, source_basin in state_to_basin.items():
        if source_basin not in selected_index:
            continue
        target_state = successor_map.get(source_state)
        if target_state is None:
            continue
        target_basin = state_to_basin.get(target_state)
        if target_basin is None or target_basin not in selected_index:
            continue
        src = selected_index[source_basin]
        dst = selected_index[target_basin]
        if src != dst:
            adjacency_pairs.add((src, dst))

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
        },
    }


def derive_walk_partition(
    fixed_walks: dict[str, dict[str, Any]],
    successor_map: dict[tuple[int, ...], tuple[int, ...] | None],
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
        successor_map,
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
        successor_map,
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

    derivations: dict[str, dict[str, Any]] = {}
    if derivation_mode in {"walk_partition", "both"}:
        derivations["walk_partition"] = derive_walk_partition(
            fixed_walks,
            successor_map,
            top_k=top_k,
            register_limit=register_limit,
            prime_labels=prime_labels,
            registers=registers,
        )
    if derivation_mode in {"scc_condensation", "both"}:
        derivations["scc_condensation"] = derive_scc_condensation(
            states,
            successor_map,
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
        "notes": [
            "Derived deterministically from local artifacts; no external data fetch.",
            "Stability is basin degeneracy count.",
            "Canonical derivation is selected by best-of-two policy with configured tiebreak.",
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
