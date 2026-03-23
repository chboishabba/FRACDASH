#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
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
    "hamming_smoke": {"program": "hamming", "init": 2},
}


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


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


def batch_state_hash(layout, states: np.ndarray) -> str:
    return ":".join(str(layout.state_hash(state)) for state in np.asarray(states))


def histogram(values: np.ndarray) -> dict[str, int]:
    arr = np.asarray(values)
    uniq, counts = np.unique(arr, return_counts=True)
    return {str(int(key)): int(count) for key, count in zip(uniq.tolist(), counts.tolist())}


def time_cpu(layout, batch_in: np.ndarray, steps: int, repeats: int) -> dict[str, object]:
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
    med = median(runtimes)
    return {
        "seconds": runtimes,
        "median_seconds": med,
        "final_state_hash": batch_state_hash(layout, final_state),
        "selected_rule_histogram": histogram(final_rules),
        "halted_count": int(np.count_nonzero(final_halted)),
    }


def time_gpu_cold(layout, batch_in: np.ndarray, steps: int) -> dict[str, object]:
    start = time.perf_counter()
    with VulkanFractranStepper() as stepper:
        init_end = time.perf_counter()
        result = stepper.run_steps_batch_profiled(layout, batch_in, steps)
        final_end = time.perf_counter()
    return {
        "init_seconds": init_end - start,
        "run_phase_seconds": result.phase_seconds,
        "total_seconds": final_end - start,
        "final_state_hash": batch_state_hash(layout, result.next_exponents),
        "selected_rule_histogram": histogram(result.selected_rules),
        "halted_count": int(np.count_nonzero(result.halted)),
    }


def time_gpu_warm(layout, batch_in: np.ndarray, steps: int, repeats: int) -> dict[str, object]:
    total_seconds = []
    phase_samples: dict[str, list[float]] = {}
    final_result = None
    with VulkanFractranStepper() as stepper:
        for _ in range(repeats):
            profiled = stepper.run_steps_batch_profiled(layout, batch_in, steps)
            total_seconds.append(float(profiled.phase_seconds["total"]))
            for key, value in profiled.phase_seconds.items():
                phase_samples.setdefault(key, []).append(float(value))
            final_result = profiled
    assert final_result is not None
    return {
        "seconds": total_seconds,
        "median_seconds": median(total_seconds),
        "median_phase_seconds": {key: median(values) for key, values in sorted(phase_samples.items())},
        "final_state_hash": batch_state_hash(layout, final_result.next_exponents),
        "selected_rule_histogram": histogram(final_result.selected_rules),
        "halted_count": int(np.count_nonzero(final_result.halted)),
    }


def benchmark_case(scenario_name: str, batch_size: int, steps: int, repeats: int) -> dict[str, object]:
    scenario = SCENARIOS[scenario_name]
    compile_start = time.perf_counter()
    fractions = load_demo_program(scenario["program"])
    layout = compile_program(scenario["program"], fractions)
    compile_seconds = time.perf_counter() - compile_start

    batch_start = time.perf_counter()
    batch_in = build_batch_states(layout, scenario["init"], batch_size)
    batch_build_seconds = time.perf_counter() - batch_start

    cpu = time_cpu(layout, batch_in, steps, repeats)
    cold = time_gpu_cold(layout, batch_in, steps)
    warm = time_gpu_warm(layout, batch_in, steps, repeats)

    parity = {
        "cold_final_state_hash_match": cpu["final_state_hash"] == cold["final_state_hash"],
        "cold_rule_histogram_match": cpu["selected_rule_histogram"] == cold["selected_rule_histogram"],
        "cold_halted_count_match": cpu["halted_count"] == cold["halted_count"],
        "warm_final_state_hash_match": cpu["final_state_hash"] == warm["final_state_hash"],
        "warm_rule_histogram_match": cpu["selected_rule_histogram"] == warm["selected_rule_histogram"],
        "warm_halted_count_match": cpu["halted_count"] == warm["halted_count"],
    }

    cpu_median = float(cpu["median_seconds"])
    cold_total = float(cold["total_seconds"])
    warm_median = float(warm["median_seconds"])
    return {
        "scenario": scenario_name,
        "program": scenario["program"],
        "batch_size": batch_size,
        "steps": steps,
        "repeats": repeats,
        "icd": ensure_default_icd(),
        "compile_seconds": compile_seconds,
        "batch_build_seconds": batch_build_seconds,
        "cpu": cpu,
        "gpu_cold": cold,
        "gpu_warm": warm,
        "parity": parity,
        "speedup_cpu_over_gpu_cold": (cpu_median / cold_total) if cold_total > 0 else None,
        "speedup_cpu_over_gpu_warm": (cpu_median / warm_median) if warm_median > 0 else None,
    }


def derive_assessment(cases: list[dict[str, object]]) -> dict[str, object]:
    warm_gpu_cases = []
    cold_penalty_cases = []
    for case in cases:
        warm = case["speedup_cpu_over_gpu_warm"]
        cold = case["speedup_cpu_over_gpu_cold"]
        if warm is not None and warm > 1.2:
            warm_gpu_cases.append(
                {
                    "scenario": case["scenario"],
                    "batch_size": case["batch_size"],
                    "steps": case["steps"],
                    "warm_speedup_cpu_over_gpu": warm,
                }
            )
        if warm is not None and cold is not None and warm > 1.2 and cold <= 1.1:
            cold_penalty_cases.append(
                {
                    "scenario": case["scenario"],
                    "batch_size": case["batch_size"],
                    "steps": case["steps"],
                    "cold_speedup_cpu_over_gpu": cold,
                    "warm_speedup_cpu_over_gpu": warm,
                }
            )
    return {
        "warm_gpu_preferred_cases": warm_gpu_cases,
        "cold_start_penalty_cases": cold_penalty_cases,
        "obvious_large_gpu_gain_region_exists": bool(warm_gpu_cases),
        "decision": (
            "warm-resident-gpu-win-is-real"
            if warm_gpu_cases
            else "no-obvious-gpu-win-on-current-cases"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile the FRACDASH GPU path before optimization.")
    parser.add_argument("--scenario", action="append", choices=sorted(SCENARIOS), help="Scenario(s) to profile.")
    parser.add_argument("--batch-size", action="append", type=int, help="Batch size(s) to profile.")
    parser.add_argument("--steps", action="append", type=int, help="Step count(s) to profile.")
    parser.add_argument("--repeats", type=int, default=5, help="Warm CPU/GPU repeats.")
    parser.add_argument("--output", type=Path, help="Write JSON artifact to this path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args()

    scenarios = args.scenario or ["primegame_small", "mult_smoke", "paper_smoke", "hamming_smoke"]
    batch_sizes = args.batch_size or [4, 16, 32, 64, 128]
    steps_list = args.steps or [4, 8, 16]

    cases = [
        benchmark_case(scenario_name, batch_size, steps, args.repeats)
        for scenario_name in scenarios
        for batch_size in batch_sizes
        for steps in steps_list
    ]

    report = {
        "cases": cases,
        "assessment": derive_assessment(cases),
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
