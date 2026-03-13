#!/usr/bin/env python3
"""Prototype wave-3 state carrier for richer AGDAS/Monster bridge work.

This script does not execute the bridge yet. Its purpose is to define and
validate a larger signed-ternary state layout that can plausibly host the
compressed Monster seam without collapsing to the near-terminal behavior seen
in the 4-register probe.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from itertools import product
from typing import Mapping


@dataclass(frozen=True)
class RegisterSpec:
    name: str
    negative: int
    zero: int
    positive: int
    role: str


REGISTERS: tuple[RegisterSpec, ...] = (
    RegisterSpec("R1", 47, 41, 43, "mask summary"),
    RegisterSpec("R2", 61, 53, 59, "candidate / choice summary"),
    RegisterSpec("R3", 73, 67, 71, "admissibility summary"),
    RegisterSpec("R4", 89, 79, 83, "window low trit"),
    RegisterSpec("R5", 103, 97, 101, "window high trit"),
    RegisterSpec("R6", 113, 107, 109, "kernel / polarity"),
)

STATE_TO_NAME = {-1: "negative", 0: "zero", 1: "positive"}
NAME_TO_STATE = {value: key for key, value in STATE_TO_NAME.items()}
PRIMES = {
    reg.name: {
        "negative": reg.negative,
        "zero": reg.zero,
        "positive": reg.positive,
    }
    for reg in REGISTERS
}


def encode_signed_state(state: Mapping[str, int]) -> int:
    value = 1
    for reg in REGISTERS:
        signed = state.get(reg.name, 0)
        if signed not in STATE_TO_NAME:
            raise ValueError(f"invalid signed value {signed} for {reg.name}")
        value *= PRIMES[reg.name][STATE_TO_NAME[signed]]
    return value


def decode_signed_state(value: int) -> dict[str, int]:
    remaining = value
    decoded: dict[str, int] = {}
    for reg in REGISTERS:
        matches: list[int] = []
        for signed, state_name in STATE_TO_NAME.items():
            prime = PRIMES[reg.name][state_name]
            if remaining % prime == 0:
                matches.append(signed)
        if len(matches) != 1:
            raise ValueError(f"state for {reg.name} is not uniquely decodable")
        signed = matches[0]
        prime = PRIMES[reg.name][STATE_TO_NAME[signed]]
        remaining //= prime
        decoded[reg.name] = signed
    if remaining != 1:
        raise ValueError("value contains unexpected primes")
    return decoded


def all_signed_vectors() -> list[tuple[int, ...]]:
    return list(product((-1, 0, 1), repeat=len(REGISTERS)))


def validate_round_trip() -> list[dict[str, object]]:
    failures: list[dict[str, object]] = []
    for vector in all_signed_vectors():
        state = {reg.name: vector[idx] for idx, reg in enumerate(REGISTERS)}
        encoded = encode_signed_state(state)
        decoded = decode_signed_state(encoded)
        if decoded != state:
            failures.append(
                {
                    "vector": vector,
                    "encoded": encoded,
                    "decoded": decoded,
                }
            )
    return failures


def sample_monster_states() -> list[dict[str, object]]:
    samples = [
        {
            "name": "monster_idle_p0",
            "state": {"R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0, "R6": 0},
        },
        {
            "name": "monster_accept_p0",
            "state": {"R1": 0, "R2": 1, "R3": 1, "R4": 0, "R5": 0, "R6": 0},
        },
        {
            "name": "monster_reject_p0",
            "state": {"R1": 0, "R2": -1, "R3": -1, "R4": 0, "R5": 0, "R6": 0},
        },
        {
            "name": "monster_accept_p1",
            "state": {"R1": 1, "R2": 0, "R3": 0, "R4": 1, "R5": 0, "R6": 0},
        },
        {
            "name": "monster_window_wrap",
            "state": {"R1": 1, "R2": 0, "R3": 0, "R4": -1, "R5": 1, "R6": 0},
        },
    ]
    encoded_samples: list[dict[str, object]] = []
    for item in samples:
        encoded = encode_signed_state(item["state"])
        encoded_samples.append(
            {
                "name": item["name"],
                "state": item["state"],
                "encoded": encoded,
                "decoded": decode_signed_state(encoded),
            }
        )
    return encoded_samples


def summary() -> dict[str, object]:
    failures = validate_round_trip()
    return {
        "register_count": len(REGISTERS),
        "state_space_size": 3 ** len(REGISTERS),
        "registers": [
            {
                "name": reg.name,
                "role": reg.role,
                "negative": reg.negative,
                "zero": reg.zero,
                "positive": reg.positive,
            }
            for reg in REGISTERS
        ],
        "round_trip": {
            "status": "ok" if not failures else "failed",
            "failure_count": len(failures),
            "failures": failures[:20],
        },
        "samples": sample_monster_states(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the prototype wave-3 AGDAS/Monster state carrier."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument("--check-only", action="store_true", help="Only report round-trip status.")
    args = parser.parse_args()

    failures = validate_round_trip()
    if args.check_only:
        print(
            json.dumps(
                {
                    "status": "ok" if not failures else "failed",
                    "failure_count": len(failures),
                    "state_space_size": 3 ** len(REGISTERS),
                },
                indent=2,
            )
        )
        return

    payload = summary()
    if args.json:
        print(json.dumps(payload, indent=2))
        return

    print("Wave-3 AGDAS state carrier")
    print(f"Registers: {len(REGISTERS)}")
    print(f"State space size: {3 ** len(REGISTERS)}")
    print(f"Round-trip status: {payload['round_trip']['status']}")
    print(f"Round-trip failures: {payload['round_trip']['failure_count']}")
    print("Register roles:")
    for item in payload["registers"]:
        print(
            f"- {item['name']}: {item['role']} "
            f"({item['negative']}, {item['zero']}, {item['positive']})"
        )
    print("Sample states:")
    for item in payload["samples"]:
        print(f"- {item['name']}: {item['state']} -> {item['encoded']}")


if __name__ == "__main__":
    main()
