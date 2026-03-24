#!/usr/bin/env python3
"""Run exploratory physics-local experiments over the 8-register carrier."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Sequence

from agdas_physics8_state import REGISTERS, decode_signed_state, encode_signed_state


@dataclass(frozen=True)
class Transition:
    name: str
    condition: Mapping[str, str]
    action: Mapping[str, str]
    description: str


STATE_TO_NAME = {-1: "negative", 0: "zero", 1: "positive"}


def _load_agdas_bridge_module():
    bridge_path = Path(__file__).resolve().parent / "agdas_bridge.py"
    module_name = "agdas_bridge_physics8_local"
    spec = importlib.util.spec_from_file_location(module_name, bridge_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load agdas bridge module from {bridge_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def transitions_from_templates(template_set: str) -> tuple[tuple[Transition, ...], dict[str, object]]:
    bridge = _load_agdas_bridge_module()
    template_rules = bridge._template_rules(template_set)

    def provenance_for_template_set(name: str) -> list[str]:
        base = [
            "UFTC_Lattice.agda",
            "Contraction.agda",
            "MaassRestoration.agda",
            "MonsterState.agda",
            "Monster/Step.agda",
            "MonsterSpec.agda",
            "Ontology/Hecke/Scan.agda",
            "DASHI/Physics/LiftToFullState.agda",
        ]
        closure = [
            "DASHI/Physics/Closure/CanonicalStageC.agda",
            "DASHI/Physics/Closure/MinimalCrediblePhysicsClosure.agda",
            "DASHI/Physics/Closure/MDLFejérAxiomsShift.agda",
            "DASHI/Physics/Closure/ShiftSeamCertificates.agda",
            "DASHI/Physics/Closure/ObservablePredictionPackage.agda",
        ]
        if name.startswith("carrier8_") or name.startswith("physics"):
            return base + closure
        return base

    transitions = tuple(
        Transition(
            name=rule.name,
            condition=dict(rule.condition),
            action=dict(rule.action),
            description=rule.description,
        )
        for rule in template_rules
    )
    return transitions, {
        "source": "agdas_templates",
        "template_set": template_set,
        "template_count": len(template_rules),
        "template_modules": sorted({rule.module for rule in template_rules}),
        "carrier_family": "physics_local_8",
        "provenance_modules": provenance_for_template_set(template_set),
    }


def state_names(vector: tuple[int, ...]) -> dict[str, str]:
    return {reg.name: STATE_TO_NAME[vector[idx]] for idx, reg in enumerate(REGISTERS)}


def matches(vector: tuple[int, ...], transition: Transition) -> bool:
    names = state_names(vector)
    return all(names[reg] == state for reg, state in transition.condition.items())


def apply_transition(vector: tuple[int, ...], transition: Transition) -> tuple[int, ...]:
    names = state_names(vector)
    for reg, state in transition.action.items():
        names[reg] = state
    return tuple(
        -1 if names[reg.name] == "negative" else 0 if names[reg.name] == "zero" else 1
        for reg in REGISTERS
    )


def action_rank(vector: tuple[int, ...]) -> int:
    value = vector[5]
    if value == -1:
        return 2
    if value == 1:
        return 1
    return 0


def _state_counts(vector: tuple[int, ...]) -> dict[str, int]:
    counts = {"negative": 0, "zero": 0, "positive": 0}
    for value in vector:
        counts[STATE_TO_NAME[value]] += 1
    return counts


def all_vectors() -> list[tuple[int, ...]]:
    from agdas_physics8_state import all_signed_vectors

    return all_signed_vectors()


def graph_for(transitions: Sequence[Transition]) -> dict[tuple[int, ...], list[tuple[Transition, tuple[int, ...]]]]:
    graph: dict[tuple[int, ...], list[tuple[Transition, tuple[int, ...]]]] = {}
    for vector in all_vectors():
        for transition in transitions:
            if matches(vector, transition):
                graph[vector] = [(transition, apply_transition(vector, transition))]
                break
        else:
            graph[vector] = []
    return graph


def deterministic_walk(start: tuple[int, ...], transitions: Sequence[Transition], max_steps: int) -> dict[str, object]:
    current = start
    seen: dict[tuple[int, ...], int] = {}
    path: list[dict[str, object]] = []
    state_rows: list[list[int]] = [list(start)]
    transition_names: list[str] = []
    for step in range(max_steps):
        if current in seen:
            return {
                "trace_schema_version": 2,
                "status": "cycle",
                "steps": step,
                "cycle_start": seen[current],
                "final_state": current,
                "register_labels": [reg.name for reg in REGISTERS],
                "state_rows": state_rows,
                "transition_names": transition_names,
                "path": path,
            }
        seen[current] = step
        next_edge: tuple[Transition, tuple[int, ...]] | None = None
        for transition in transitions:
            if matches(current, transition):
                next_edge = (transition, apply_transition(current, transition))
                break
        if next_edge is None:
            return {
                "trace_schema_version": 2,
                "status": "terminal",
                "steps": step,
                "cycle_start": None,
                "final_state": current,
                "register_labels": [reg.name for reg in REGISTERS],
                "state_rows": state_rows,
                "transition_names": transition_names,
                "path": path,
            }
        transition, nxt = next_edge
        delta = [int(b - a) for a, b in zip(current, nxt)]
        changed_registers = [REGISTERS[idx].name for idx, (a, b) in enumerate(zip(current, nxt)) if a != b]
        transition_names.append(transition.name)
        path.append(
            {
                "step": step + 1,
                "state": list(current),
                "transition": transition.name,
                "next_state": list(nxt),
                "delta": delta,
                "changed_registers": changed_registers,
                "changed_register_mask": [name in changed_registers for name in (reg.name for reg in REGISTERS)],
                "changed_register_count": len(changed_registers),
                "l1_step_delta": sum(abs(value) for value in delta),
                "action_rank_before": action_rank(current),
                "action_rank_after": action_rank(nxt),
                "state_counts_before": _state_counts(current),
                "state_counts_after": _state_counts(nxt),
            }
        )
        state_rows.append(list(nxt))
        current = nxt
    return {
        "trace_schema_version": 2,
        "status": "timeout",
        "steps": max_steps,
        "cycle_start": None,
        "final_state": current,
        "register_labels": [reg.name for reg in REGISTERS],
        "state_rows": state_rows,
        "transition_names": transition_names,
        "path": path,
    }


def fixed_walk_summary(transitions: Sequence[Transition], max_steps: int) -> dict[str, object]:
    terminal = 0
    cycle = 0
    timeout = 0
    max_steps_observed = 0
    longest_paths: list[tuple[str, int, str]] = []
    timeout_states: list[str] = []
    for vector in all_vectors():
        result = deterministic_walk(vector, transitions, max_steps)
        max_steps_observed = max(max_steps_observed, int(result["steps"]))
        status = str(result["status"])
        if status == "terminal":
            terminal += 1
        elif status == "cycle":
            cycle += 1
        else:
            timeout += 1
            timeout_states.append(str(vector))
        longest_paths.append((str(vector), int(result["steps"]), status))
    longest_paths.sort(key=lambda item: (-item[1], item[0]))
    return {
        "state_count": len(all_vectors()),
        "terminal": terminal,
        "cycle": cycle,
        "timeout": timeout,
        "max_steps_observed": max_steps_observed,
        "longest_paths": longest_paths[:10],
        "timeout_states": timeout_states[:20],
    }


def action_monotonicity_summary(
    graph: Mapping[tuple[int, ...], list[tuple[Transition, tuple[int, ...]]]]
) -> dict[str, object]:
    decreases = 0
    preserves = 0
    increases = 0
    for source, edges in graph.items():
        for _transition, target in edges:
            before = action_rank(source)
            after = action_rank(target)
            if after < before:
                decreases += 1
            elif after == before:
                preserves += 1
            else:
                increases += 1
    total = decreases + preserves + increases
    return {
        "total_edges": total,
        "decreases": decreases,
        "preserves": preserves,
        "increases": increases,
    }


def longest_chain_profile(graph: Mapping[tuple[int, ...], list[tuple[Transition, tuple[int, ...]]]]) -> dict[str, object]:
    @lru_cache(maxsize=None)
    def depth(node: tuple[int, ...], visiting: frozenset[tuple[int, ...]] = frozenset()) -> int:
        if node in visiting:
            return 0
        edges = graph[node]
        if not edges:
            return 0
        return 1 + max(depth(next_node, visiting | {node}) for _, next_node in edges)

    lengths = {node: depth(node) for node in graph}
    histogram: dict[str, int] = {}
    for value in lengths.values():
        histogram[str(value)] = histogram.get(str(value), 0) + 1
    max_len = max(lengths.values(), default=0)
    return {
        "nodes": len(graph),
        "edges": sum(len(edges) for edges in graph.values()),
        "terminal_states": sum(1 for edges in graph.values() if not edges),
        "longest_chain": max_len,
        "chain_length_histogram": histogram,
        "max_chain_start_states": [str(node) for node, value in lengths.items() if value == max_len][:10],
    }


def memory_profile(states: Sequence[tuple[int, ...]], idx: int) -> dict[str, int]:
    counts = {"negative": 0, "zero": 0, "positive": 0}
    for state in states:
        if state[idx] < 0:
            counts["negative"] += 1
        elif state[idx] == 0:
            counts["zero"] += 1
        else:
            counts["positive"] += 1
    return counts


def compare_artifact(filename: str, label: str) -> dict[str, object]:
    path = Path(__file__).resolve().parents[1] / f"benchmarks/results/{filename}"
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    obj = json.loads(path.read_text())
    walk_summary = obj.get("fixed_walk_summary") or obj.get("fixed_prime_walk_summary", {})
    return {
        "status": "ok",
        "path": str(path),
        f"{label}_full_space_profile": obj.get("full_space_profile"),
        f"{label}_fixed_walk_summary": {
            key: walk_summary.get(key)
            for key in ("state_count", "terminal", "cycle", "timeout", "max_steps_observed")
        },
    }


def summary(template_set: str, max_steps: int) -> dict[str, object]:
    transitions, transition_source_summary = transitions_from_templates(template_set)
    graph = graph_for(transitions)
    start = (1, 0, 0, 1, 0, -1, 0, 0)
    walk = deterministic_walk(start, transitions, max_steps)
    walk_summary = fixed_walk_summary(transitions, max_steps)
    all_states_list = all_vectors()
    deterministic_sources = [state for state, edges in graph.items() if edges]
    return {
        "template_set": template_set,
        "register_count": len(REGISTERS),
        "state_space_size": 3 ** len(REGISTERS),
        "transition_source": "agdas_templates",
        "transition_source_summary": transition_source_summary,
        "transition_count": len(transitions),
        "transitions": [
            {
                "name": item.name,
                "condition": item.condition,
                "action": item.action,
                "description": item.description,
            }
            for item in transitions
        ],
        "full_space_profile": longest_chain_profile(graph),
        "action_monotonicity": action_monotonicity_summary(graph),
        "fixed_walk_summary": walk_summary,
        "deterministic_start": start,
        "deterministic_start_decoded": decode_signed_state(
            encode_signed_state({reg.name: start[idx] for idx, reg in enumerate(REGISTERS)})
        ),
        "deterministic_walk": walk,
        "memory_observables": {
            "boundary_return_profile": {
                "all_states": memory_profile(all_states_list, 6),
                "deterministic_sources": memory_profile(deterministic_sources, 6),
            },
            "transport_debt_profile": {
                "all_states": memory_profile(all_states_list, 7),
                "deterministic_sources": memory_profile(deterministic_sources, 7),
            },
        },
        "physics20_comparison": compare_artifact("2026-03-15-agdas-physics20-phase2.json", "physics20"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run 8-register physics-local bridge experiments.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument(
        "--template-set",
        default="carrier8_physics1",
        choices=("carrier8_physics1", "carrier8_physics2", "carrier8_physics3", "carrier8_physics4", "carrier8_physics5", "carrier8_physics6", "carrier8_physics7", "carrier8_physics8"),
        help="Template set to execute.",
    )
    parser.add_argument("--max-steps", type=int, default=12, help="Deterministic walk step cap.")
    args = parser.parse_args()

    payload = summary(args.template_set, args.max_steps)
    if args.json:
        print(json.dumps(payload, indent=2))
        return

    print("Physics-local 8-register experiments")
    print(f"Transition set: {payload['transition_source_summary']['template_set']}")
    print(f"Transitions: {payload['transition_count']}")
    print(f"State space size: {payload['state_space_size']}")
    print(f"Full-space profile: {payload['full_space_profile']}")
    print(f"Deterministic walk status: {payload['deterministic_walk']['status']}")


if __name__ == "__main__":
    main()
