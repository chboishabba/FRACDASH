#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gpu.fractran_layout import compile_program, load_demo_program
from gpu.vulkan_fractran_step import VulkanFractranStepper, ensure_default_icd


SCENARIOS = {
    "primegame_small": {"program": "primegame", "init": 2},
    "mult_smoke": {"program": "mult", "init": 2},
    "paper_smoke": {"program": "paper", "init": 2},
}


def build_batch_states(layout, init_value: int, count: int) -> np.ndarray:
    states = []
    current_state = layout.encode_integer_state(init_value)
    current_value = init_value
    states.append(current_state.copy())
    while len(states) < count:
        stepped = layout.step(current_state, current_value)
        if stepped is None:
            break
        current_state, current_value = stepped
        states.append(current_state.copy())
    while len(states) < count:
        states.append(states[-1].copy())
    return np.stack(states, axis=0)


def time_cpu(layout, batch_in: np.ndarray, steps: int, repeats: int):
    runtimes = []
    final_state = None
    final_rules = None
    final_halted = None
    for _ in range(repeats):
        start = time.perf_counter()
        state, rules, halted = layout.run_steps_batch(batch_in, steps)
        elapsed = time.perf_counter() - start
        runtimes.append(elapsed)
        final_state, final_rules, final_halted = state, rules, halted
    return {
        "seconds": runtimes,
        "median_seconds": sorted(runtimes)[len(runtimes) // 2],
        "final_state_hash": batch_state_hash(layout, final_state),
        "selected_rule_histogram": histogram(final_rules),
        "halted_count": int(np.count_nonzero(final_halted)),
    }


def time_gpu(layout, batch_in: np.ndarray, steps: int, repeats: int):
    runtimes = []
    final_state = None
    final_rules = None
    final_halted = None
    with VulkanFractranStepper() as stepper:
        for _ in range(repeats):
            start = time.perf_counter()
            result = stepper.run_steps_batch(layout, batch_in, steps)
            elapsed = time.perf_counter() - start
            runtimes.append(elapsed)
            final_state, final_rules, final_halted = (
                result.next_exponents,
                result.selected_rules,
                result.halted,
            )
    return {
        "seconds": runtimes,
        "median_seconds": sorted(runtimes)[len(runtimes) // 2],
        "final_state_hash": batch_state_hash(layout, final_state),
        "selected_rule_histogram": histogram(final_rules),
        "halted_count": int(np.count_nonzero(final_halted)),
    }


def benchmark_case(scenario_name: str, batch_size: int, steps: int, repeats: int) -> dict[str, object]:
    scenario = SCENARIOS[scenario_name]
    fractions = load_demo_program(scenario["program"])
    layout = compile_program(scenario["program"], fractions)
    batch_in = build_batch_states(layout, scenario["init"], batch_size)

    cpu = time_cpu(layout, batch_in, steps, repeats)
    gpu = time_gpu(layout, batch_in, steps, repeats)

    parity = {
        "final_state_hash_match": cpu["final_state_hash"] == gpu["final_state_hash"],
        "selected_rule_histogram_match": cpu["selected_rule_histogram"] == gpu["selected_rule_histogram"],
        "halted_count_match": cpu["halted_count"] == gpu["halted_count"],
    }
    cpu_median = float(cpu["median_seconds"])
    gpu_median = float(gpu["median_seconds"])
    speedup = (cpu_median / gpu_median) if gpu_median > 0 else None
    routing = (
        "gpu"
        if speedup is not None and speedup > 1.2
        else "cpu"
        if speedup is not None and speedup < 0.9
        else "measure-more"
    )

    return {
        "scenario": scenario_name,
        "program": scenario["program"],
        "batch_size": batch_size,
        "steps": steps,
        "repeats": repeats,
        "icd": ensure_default_icd(),
        "cpu": cpu,
        "gpu": gpu,
        "parity": parity,
        "speedup_cpu_over_gpu": speedup,
        "routing_hint": routing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark dense CPU versus resident Vulkan FRACTRAN batching."
    )
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIOS),
        help="Scenario(s) to benchmark. Defaults to primegame_small.",
    )
    parser.add_argument(
        "--batch-size",
        action="append",
        type=int,
        help="Batch size(s) to benchmark. Defaults to 32,128,512.",
    )
    parser.add_argument(
        "--steps",
        action="append",
        type=int,
        help="Exact step count(s) to benchmark. Defaults to 8,32,128.",
    )
    parser.add_argument("--repeats", type=int, default=5, help="Timing repeats per case.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    scenarios = args.scenario or ["primegame_small"]
    batch_sizes = args.batch_size or [32, 128, 512]
    step_counts = args.steps or [8, 32, 128]
    cases = [
        benchmark_case(scenario_name, batch_size, steps, args.repeats)
        for scenario_name in scenarios
        for batch_size in batch_sizes
        for steps in step_counts
    ]
    routing_rule = derive_routing_rule(cases)
    summary = {
        "cases": cases,
        "gpu_preferred_cases": [
            {
                "scenario": case["scenario"],
                "batch_size": case["batch_size"],
                "steps": case["steps"],
            }
            for case in cases
            if case["routing_hint"] == "gpu"
        ],
        "routing_rule": routing_rule,
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    for case in cases:
        print(
            f"scenario={case['scenario']} batch={case['batch_size']} steps={case['steps']} "
            f"cpu_median={case['cpu']['median_seconds']:.6f}s gpu_median={case['gpu']['median_seconds']:.6f}s "
            f"speedup={case['speedup_cpu_over_gpu']:.3f} routing_hint={case['routing_hint']} parity={case['parity']}"
        )
    print("gpu_preferred_cases:", summary["gpu_preferred_cases"])
    print("routing_rule:", summary["routing_rule"])


def batch_state_hash(layout, states: np.ndarray) -> str:
    return ":".join(str(layout.state_hash(state)) for state in np.asarray(states))


def histogram(values: np.ndarray) -> dict[str, int]:
    arr = np.asarray(values)
    uniq, counts = np.unique(arr, return_counts=True)
    return {str(int(key)): int(count) for key, count in zip(uniq.tolist(), counts.tolist())}


def derive_routing_rule(cases: list[dict[str, object]]) -> dict[str, object]:
    gpu_cases = [case for case in cases if case["routing_hint"] == "gpu"]
    cpu_cases = [case for case in cases if case["routing_hint"] == "cpu"]
    rule = {
        "gpu_when": [],
        "cpu_when": [],
        "notes": [],
    }
    for case in gpu_cases:
        rule["gpu_when"].append(
            {
                "scenario": case["scenario"],
                "batch_size": case["batch_size"],
                "steps": case["steps"],
            }
        )
    for case in cpu_cases:
        rule["cpu_when"].append(
            {
                "scenario": case["scenario"],
                "batch_size": case["batch_size"],
                "steps": case["steps"],
            }
        )
    if gpu_cases:
        min_gpu_batch = min(int(case["batch_size"]) for case in gpu_cases)
        min_gpu_steps = min(int(case["steps"]) for case in gpu_cases)
        rule["notes"].append(
            f"Measured GPU-preferred region begins no later than batch_size={min_gpu_batch}, steps={min_gpu_steps} on at least one scenario."
        )
    if cpu_cases:
        max_cpu_batch = max(int(case["batch_size"]) for case in cpu_cases)
        max_cpu_steps = max(int(case["steps"]) for case in cpu_cases)
        rule["notes"].append(
            f"Measured CPU-preferred cases still exist up to batch_size={max_cpu_batch}, steps={max_cpu_steps} on at least one scenario."
        )
    return rule


if __name__ == "__main__":
    main()
