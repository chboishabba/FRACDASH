#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gpu.fractran_layout import compile_program, load_demo_program
from gpu.vulkan_fractran_step import VulkanFractranStepper, ensure_default_icd


SCENARIOS = {
    "mult_smoke": {"program": "mult", "init": 2},
    "primegame_small": {"program": "primegame", "init": 2},
}


def compare_one_step(scenario_name: str) -> dict[str, object]:
    scenario = SCENARIOS[scenario_name]
    fractions = load_demo_program(scenario["program"])
    layout = compile_program(scenario["program"], fractions)
    init_state = layout.encode_integer_state(scenario["init"])
    cpu_step = layout.step(init_state, scenario["init"])
    if cpu_step is None:
        raise RuntimeError(f"CPU contract halted unexpectedly for {scenario_name}")

    with VulkanFractranStepper() as stepper:
        gpu_step = stepper.step(layout, init_state)

    next_cpu_state, next_cpu_value = cpu_step
    return {
        "scenario": scenario_name,
        "icd": ensure_default_icd(),
        "initial_exponents": init_state.tolist(),
        "cpu": {
            "next_exponents": next_cpu_state.tolist(),
            "next_value": int(next_cpu_value),
            "selected_rule": int(np.argmax([np.all(init_state >= rule.den_thresholds) for rule in layout.rules])),
        },
        "gpu": {
            "next_exponents": gpu_step.next_exponents.tolist(),
            "selected_rule": gpu_step.selected_rule,
            "halted": gpu_step.halted,
        },
        "comparison": {
            "next_exponents_match": bool(np.array_equal(next_cpu_state, gpu_step.next_exponents)),
            "selected_rule_match": int(np.argmax([np.all(init_state >= rule.den_thresholds) for rule in layout.rules]))
            == gpu_step.selected_rule,
            "halted_match": gpu_step.halted is False,
        },
    }


def selected_rule_for_state(layout, init_state: np.ndarray) -> int:
    for ix, rule in enumerate(layout.rules):
        if np.all(init_state >= rule.den_thresholds):
            return ix
    return -1


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


def compare_batch(scenario_name: str, batch_size: int = 4) -> dict[str, object]:
    scenario = SCENARIOS[scenario_name]
    fractions = load_demo_program(scenario["program"])
    layout = compile_program(scenario["program"], fractions)
    batch_in = build_batch_states(layout, scenario["init"], batch_size)

    cpu_next = []
    cpu_rules = []
    cpu_halted = []
    for state in batch_in:
        selected_rule = selected_rule_for_state(layout, state)
        stepped = layout.step(state, layout.decode_integer_state(state))
        if stepped is None:
            cpu_next.append(state.copy())
            cpu_rules.append(-1)
            cpu_halted.append(True)
        else:
            next_state, _ = stepped
            cpu_next.append(next_state)
            cpu_rules.append(selected_rule)
            cpu_halted.append(False)

    with VulkanFractranStepper() as stepper:
        gpu_batch = stepper.step_batch(layout, batch_in)

    cpu_next_arr = np.stack(cpu_next, axis=0)
    cpu_rules_arr = np.asarray(cpu_rules, dtype=np.int32)
    cpu_halted_arr = np.asarray(cpu_halted, dtype=bool)

    return {
        "scenario": scenario_name,
        "icd": ensure_default_icd(),
        "batch_size": batch_size,
        "initial_exponents": batch_in.tolist(),
        "cpu": {
            "next_exponents": cpu_next_arr.tolist(),
            "selected_rules": cpu_rules_arr.tolist(),
            "halted": cpu_halted_arr.tolist(),
        },
        "gpu": {
            "next_exponents": gpu_batch.next_exponents.tolist(),
            "selected_rules": gpu_batch.selected_rules.tolist(),
            "halted": gpu_batch.halted.tolist(),
        },
        "comparison": {
            "next_exponents_match": bool(np.array_equal(cpu_next_arr, gpu_batch.next_exponents)),
            "selected_rules_match": bool(np.array_equal(cpu_rules_arr, gpu_batch.selected_rules)),
            "halted_match": bool(np.array_equal(cpu_halted_arr, gpu_batch.halted)),
        },
    }


def compare_multi_step(scenario_name: str, batch_size: int = 4, steps: int = 3) -> dict[str, object]:
    scenario = SCENARIOS[scenario_name]
    fractions = load_demo_program(scenario["program"])
    layout = compile_program(scenario["program"], fractions)
    batch_in = build_batch_states(layout, scenario["init"], batch_size)

    cpu_current = batch_in.copy()
    cpu_rules_arr = np.full(batch_size, -1, dtype=np.int32)
    cpu_halted_arr = np.zeros(batch_size, dtype=bool)
    for _ in range(steps):
        next_states = []
        next_rules = []
        next_halted = []
        for state in cpu_current:
            selected_rule = selected_rule_for_state(layout, state)
            stepped = layout.step(state, layout.decode_integer_state(state))
            if stepped is None:
                next_states.append(state.copy())
                next_rules.append(-1)
                next_halted.append(True)
            else:
                next_state, _ = stepped
                next_states.append(next_state)
                next_rules.append(selected_rule)
                next_halted.append(False)
        cpu_current = np.stack(next_states, axis=0)
        cpu_rules_arr = np.asarray(next_rules, dtype=np.int32)
        cpu_halted_arr = np.asarray(next_halted, dtype=bool)

    with VulkanFractranStepper() as stepper:
        gpu_result = stepper.run_steps_batch(layout, batch_in, steps)

    return {
        "scenario": scenario_name,
        "icd": ensure_default_icd(),
        "batch_size": batch_size,
        "steps": steps,
        "initial_exponents": batch_in.tolist(),
        "cpu": {
            "final_exponents": cpu_current.tolist(),
            "selected_rules": cpu_rules_arr.tolist(),
            "halted": cpu_halted_arr.tolist(),
        },
        "gpu": {
            "final_exponents": gpu_result.next_exponents.tolist(),
            "selected_rules": gpu_result.selected_rules.tolist(),
            "halted": gpu_result.halted.tolist(),
        },
        "comparison": {
            "final_exponents_match": bool(np.array_equal(cpu_current, gpu_result.next_exponents)),
            "selected_rules_match": bool(np.array_equal(cpu_rules_arr, gpu_result.selected_rules)),
            "halted_match": bool(np.array_equal(cpu_halted_arr, gpu_result.halted)),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run one exact FRACTRAN step on Vulkan and compare it to the dense CPU contract."
    )
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIOS),
        help="Scenario(s) to check. Defaults to all.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size for the batched smoke.")
    parser.add_argument("--multi-steps", type=int, default=3, help="Step count for the resident multi-step smoke.")
    args = parser.parse_args()

    scenarios = args.scenario or sorted(SCENARIOS)
    result = {
        "one_step": [compare_one_step(name) for name in scenarios],
        "batched": [compare_batch(name, batch_size=args.batch_size) for name in scenarios],
        "multi_step": [
            compare_multi_step(name, batch_size=args.batch_size, steps=args.multi_steps) for name in scenarios
        ],
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    print("one_step:")
    for scenario in result["one_step"]:
        print(f"scenario={scenario['scenario']}")
        print("  icd:", scenario["icd"])
        print("  cpu:", scenario["cpu"])
        print("  gpu:", scenario["gpu"])
        print("  comparison:", scenario["comparison"])
    print("batched:")
    for scenario in result["batched"]:
        print(f"scenario={scenario['scenario']}")
        print("  icd:", scenario["icd"])
        print("  cpu:", scenario["cpu"])
        print("  gpu:", scenario["gpu"])
        print("  comparison:", scenario["comparison"])
    print("multi_step:")
    for scenario in result["multi_step"]:
        print(f"scenario={scenario['scenario']}")
        print("  icd:", scenario["icd"])
        print("  cpu:", scenario["cpu"])
        print("  gpu:", scenario["gpu"])
        print("  comparison:", scenario["comparison"])


if __name__ == "__main__":
    main()
