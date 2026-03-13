#!/usr/bin/env python3
"""Execute wave-3 AGDAS/Monster bridge experiments over the 6-register carrier."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Sequence

from agdas_wave3_state import REGISTERS, decode_signed_state, encode_signed_state


@dataclass(frozen=True)
class Transition:
    name: str
    condition: Mapping[str, str]
    action: Mapping[str, str]
    description: str


STATE_TO_NAME = {-1: "negative", 0: "zero", 1: "positive"}


def _load_agdas_bridge_module():
    bridge_path = Path(__file__).resolve().parent / "agdas_bridge.py"
    module_name = "agdas_bridge_wave3_local"
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


def all_vectors() -> list[tuple[int, ...]]:
    from agdas_wave3_state import all_signed_vectors

    return all_signed_vectors()


def graph_for(transitions: Sequence[Transition]) -> dict[tuple[int, ...], list[tuple[Transition, tuple[int, ...]]]]:
    graph: dict[tuple[int, ...], list[tuple[Transition, tuple[int, ...]]]] = {}
    for vector in all_vectors():
        edges: list[tuple[Transition, tuple[int, ...]]] = []
        for transition in transitions:
            if matches(vector, transition):
                edges.append((transition, apply_transition(vector, transition)))
        graph[vector] = edges
    return graph


def deterministic_walk(
    start: tuple[int, ...],
    transitions: Sequence[Transition],
    max_steps: int,
) -> dict[str, object]:
    current = start
    seen: dict[tuple[int, ...], int] = {}
    path: list[dict[str, object]] = []
    for step in range(max_steps):
        if current in seen:
            return {
                "status": "cycle",
                "steps": step,
                "cycle_start": seen[current],
                "final_state": current,
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
                "status": "terminal",
                "steps": step,
                "cycle_start": None,
                "final_state": current,
                "path": path,
            }
        transition, nxt = next_edge
        path.append(
            {
                "step": step + 1,
                "state": current,
                "transition": transition.name,
                "next_state": nxt,
                "encoded": encode_signed_state({reg.name: current[idx] for idx, reg in enumerate(REGISTERS)}),
            }
        )
        current = nxt
    return {
        "status": "timeout",
        "steps": max_steps,
        "cycle_start": None,
        "final_state": current,
        "path": path,
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


def compare_wave2() -> dict[str, object]:
    path = Path(__file__).resolve().parents[1] / "benchmarks/results/2026-03-14-agdas-template-wave2-phase2.json"
    if not path.exists():
        return {"status": "missing", "path": str(path)}
    wave2 = json.loads(path.read_text())
    return {
        "status": "ok",
        "path": str(path),
        "wave2_full_space_profile": wave2.get("full_space_profile"),
        "wave2_fixed_prime_walk_summary": {
            key: wave2.get("fixed_prime_walk_summary", {}).get(key)
            for key in ("state_count", "terminal", "cycle", "timeout", "max_steps_observed")
        },
    }


def summary(template_set: str, max_steps: int) -> dict[str, object]:
    transitions, transition_source_summary = transitions_from_templates(template_set)
    graph = graph_for(transitions)
    start = (0, 1, 1, 0, 0, 0)
    walk = deterministic_walk(start, transitions, max_steps=max_steps)
    return {
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
        "deterministic_start": start,
        "deterministic_start_decoded": decode_signed_state(
            encode_signed_state({reg.name: start[idx] for idx, reg in enumerate(REGISTERS)})
        ),
        "deterministic_walk": walk,
        "wave2_comparison": compare_wave2(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run wave-3 AGDAS/Monster bridge experiments.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument("--template-set", default="wave3", choices=("wave3",), help="Template set to execute.")
    parser.add_argument("--max-steps", type=int, default=12, help="Deterministic walk step cap.")
    args = parser.parse_args()

    payload = summary(args.template_set, args.max_steps)
    if args.json:
        print(json.dumps(payload, indent=2))
        return

    print("Wave-3 AGDAS experiments")
    print(f"Transition set: {payload['transition_source_summary']['template_set']}")
    print(f"Transitions: {payload['transition_count']}")
    print(f"State space size: {payload['state_space_size']}")
    print(f"Full-space profile: {payload['full_space_profile']}")
    print(f"Deterministic walk status: {payload['deterministic_walk']['status']}")


if __name__ == "__main__":
    main()
