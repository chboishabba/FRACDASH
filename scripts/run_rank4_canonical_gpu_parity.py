#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gpu.fractran_layout import CompiledFractranLayout, CompiledRuleLayout
from gpu.vulkan_fractran_step import VulkanFractranStepper, ensure_default_icd


SIGNED_TO_STATE = {-1: "negative", 0: "zero", 1: "positive"}


@dataclass(frozen=True)
class RegisterPrimeSpec:
    name: str
    negative: int
    zero: int
    positive: int

    def prime_for(self, signed_value: int) -> int:
        if signed_value == -1:
            return self.negative
        if signed_value == 0:
            return self.zero
        if signed_value == 1:
            return self.positive
        raise ValueError(f"invalid signed value {signed_value} for {self.name}")

    def prime_for_name(self, state_name: str) -> int:
        if state_name == "negative":
            return self.negative
        if state_name == "zero":
            return self.zero
        if state_name == "positive":
            return self.positive
        raise ValueError(f"invalid state name {state_name} for {self.name}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_register_specs(state_artifact: dict[str, Any]) -> list[RegisterPrimeSpec]:
    registers_raw = state_artifact.get("registers")
    if not isinstance(registers_raw, list):
        raise ValueError("state artifact missing registers list")
    specs: list[RegisterPrimeSpec] = []
    for reg in registers_raw:
        specs.append(
            RegisterPrimeSpec(
                name=str(reg["name"]),
                negative=int(reg["negative"]),
                zero=int(reg["zero"]),
                positive=int(reg["positive"]),
            )
        )
    if not specs:
        raise ValueError("no register specs found in state artifact")
    return specs


def selected_rule_for_state(layout: CompiledFractranLayout, state: np.ndarray) -> int:
    for index, rule in enumerate(layout.rules):
        if np.all(state >= rule.den_thresholds):
            return index
    return -1


def build_layout_from_transitions(
    transitions: list[dict[str, Any]],
    register_specs: list[RegisterPrimeSpec],
) -> CompiledFractranLayout:
    register_index = {reg.name: idx for idx, reg in enumerate(register_specs)}
    primes = sorted(
        {
            prime
            for reg in register_specs
            for prime in (reg.negative, reg.zero, reg.positive)
        }
    )
    prime_index = {prime: ix for ix, prime in enumerate(primes)}
    rules: list[CompiledRuleLayout] = []

    for transition in transitions:
        condition = dict(transition.get("condition", {}))
        action = dict(transition.get("action", {}))
        thresholds = np.zeros(len(primes), dtype=np.int32)
        delta = np.zeros(len(primes), dtype=np.int32)
        required_mask = 0
        numerator_value = 1
        denominator_value = 1

        for register, required_name in condition.items():
            reg_idx = register_index.get(register)
            if reg_idx is None:
                continue
            reg_spec = register_specs[reg_idx]
            old_prime = reg_spec.prime_for_name(str(required_name))
            new_name = str(action.get(register, required_name))
            new_prime = reg_spec.prime_for_name(new_name)

            old_ix = prime_index[old_prime]
            new_ix = prime_index[new_prime]
            thresholds[old_ix] += 1
            required_mask |= 1 << old_ix
            delta[old_ix] -= 1
            delta[new_ix] += 1
            denominator_value *= old_prime
            numerator_value *= new_prime

        rules.append(
            CompiledRuleLayout(
                numerator=Fraction(numerator_value, 1),
                denominator=Fraction(denominator_value, 1),
                den_thresholds=thresholds,
                delta=delta,
                required_mask=required_mask,
                numerator_value=numerator_value,
                denominator_value=denominator_value,
            )
        )

    return CompiledFractranLayout(
        name="rank4_canonical_physics",
        primes=np.array(primes, dtype=np.int32),
        rules=tuple(rules),
    )


def encode_state_vector(layout: CompiledFractranLayout, register_specs: list[RegisterPrimeSpec], signed_state: list[int]) -> np.ndarray:
    if len(signed_state) != len(register_specs):
        raise ValueError(f"state length {len(signed_state)} does not match registers {len(register_specs)}")
    prime_to_exp = {int(prime): 0 for prime in layout.primes.tolist()}
    for reg_spec, value in zip(register_specs, signed_state):
        prime_to_exp[reg_spec.prime_for(int(value))] = 1
    return np.array([prime_to_exp[int(prime)] for prime in layout.primes.tolist()], dtype=np.int32)


def canonical_basin_states(dataset: dict[str, Any], batch_size: int) -> tuple[str, list[list[int]]]:
    canonical_derivation = dataset.get("canonical_derivation")
    derivations = dataset.get("derivations")
    if isinstance(derivations, dict) and isinstance(canonical_derivation, str) and canonical_derivation in derivations:
        payload = derivations[canonical_derivation]
    else:
        canonical_derivation = "legacy"
        payload = dataset
    basins = payload.get("basins", [])
    if not isinstance(basins, list):
        raise ValueError("dataset missing basins list")
    states: list[list[int]] = []
    for basin in basins:
        rep = basin.get("representative_state")
        if isinstance(rep, list):
            states.append([int(v) for v in rep])
        if len(states) >= batch_size:
            break
    return canonical_derivation, states


def main() -> None:
    parser = argparse.ArgumentParser(description="Run lock-gated GPU parity on canonical basin representative states.")
    parser.add_argument(
        "--dataset",
        default="benchmarks/results/rank4-dataset-latest.json",
        help="Rank4 dataset artifact path.",
    )
    parser.add_argument(
        "--physics-artifact",
        default=None,
        help="Optional physics artifact override; defaults to dataset source_artifacts.physics_artifact.",
    )
    parser.add_argument(
        "--state-artifact",
        default=None,
        help="Optional state artifact override; defaults to dataset source_artifacts.state_artifact.",
    )
    parser.add_argument("--batch-size", type=int, default=10, help="Representative state batch size.")
    parser.add_argument("--force", action="store_true", help="Run even if canonical lock gate is not satisfied.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: benchmarks/results/<today>-rank4-canonical-gpu-parity.json).",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    output_path = (
        Path(args.output)
        if args.output
        else Path(f"benchmarks/results/{date.today().isoformat()}-rank4-canonical-gpu-parity.json")
    )
    dataset = load_json(dataset_path)
    lock_pass = bool(dataset.get("canonical_selection", {}).get("lock_pass", False))

    report: dict[str, Any] = {
        "dataset_path": str(dataset_path),
        "dataset_sha256": dataset.get("sha256"),
        "lock_gate_pass": lock_pass,
        "forced": bool(args.force),
    }

    if not lock_pass and not args.force:
        report["status"] = "skipped"
        report["reason"] = "canonical lock gate not satisfied"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"wrote {output_path}")
            print("status: skipped (canonical lock gate not satisfied)")
        return

    source_artifacts = dataset.get("source_artifacts", {})
    physics_path = Path(args.physics_artifact or source_artifacts.get("physics_artifact", ""))
    state_path = Path(args.state_artifact or source_artifacts.get("state_artifact", ""))
    if not physics_path.is_file() or not state_path.is_file():
        raise SystemExit("physics/state artifact paths are missing or invalid")

    physics_artifact = load_json(physics_path)
    state_artifact = load_json(state_path)
    transitions = physics_artifact.get("transitions")
    if not isinstance(transitions, list):
        raise SystemExit("physics artifact missing transitions list")
    register_specs = build_register_specs(state_artifact)
    layout = build_layout_from_transitions(transitions, register_specs)

    canonical_derivation, basin_states = canonical_basin_states(dataset, max(1, args.batch_size))
    usable_states = [state for state in basin_states if len(state) == len(register_specs)]
    if not usable_states:
        raise SystemExit("no basin representative states compatible with register spec")
    state_matrix = np.stack(
        [encode_state_vector(layout, register_specs, state) for state in usable_states],
        axis=0,
    )

    cpu_next = []
    cpu_rules = []
    cpu_halted = []
    for state in state_matrix:
        selected = selected_rule_for_state(layout, state)
        stepped = layout.step(state, layout.decode_integer_state(state))
        if stepped is None:
            cpu_next.append(state.copy())
            cpu_rules.append(-1)
            cpu_halted.append(True)
        else:
            next_state, _next_value = stepped
            cpu_next.append(next_state)
            cpu_rules.append(selected)
            cpu_halted.append(False)
    cpu_next_arr = np.stack(cpu_next, axis=0)
    cpu_rules_arr = np.asarray(cpu_rules, dtype=np.int32)
    cpu_halted_arr = np.asarray(cpu_halted, dtype=bool)

    with VulkanFractranStepper() as stepper:
        gpu_result = stepper.step_batch(layout, state_matrix)

    report.update(
        {
            "status": "ok",
            "canonical_derivation": canonical_derivation,
            "physics_artifact": str(physics_path),
            "state_artifact": str(state_path),
            "icd": ensure_default_icd(),
            "batch_size": int(state_matrix.shape[0]),
            "prime_count": int(layout.primes.shape[0]),
            "selected_basin_states": usable_states,
            "comparison": {
                "next_exponents_match": bool(np.array_equal(cpu_next_arr, gpu_result.next_exponents)),
                "selected_rules_match": bool(np.array_equal(cpu_rules_arr, gpu_result.selected_rules)),
                "halted_match": bool(np.array_equal(cpu_halted_arr, gpu_result.halted)),
            },
        }
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"wrote {output_path}")
        print(
            "comparison:"
            f" next={report['comparison']['next_exponents_match']},"
            f" rules={report['comparison']['selected_rules_match']},"
            f" halted={report['comparison']['halted_match']}"
        )


if __name__ == "__main__":
    main()
