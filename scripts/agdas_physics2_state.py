#!/usr/bin/env python3
"""Dedicated 6-register carrier for the widened physics2 bridge layer."""

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
    RegisterSpec("R1", 127, 131, 137, "left/source severity code"),
    RegisterSpec("R2", 139, 149, 151, "right/source severity code"),
    RegisterSpec("R3", 157, 163, 167, "effective joined severity"),
    RegisterSpec("R4", 173, 179, 181, "region flag"),
    RegisterSpec("R5", 191, 193, 197, "signature/scan latch"),
    RegisterSpec("R6", 199, 211, 223, "action/energy phase"),
)

STATE_TO_NAME = {-1: "negative", 0: "zero", 1: "positive"}
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
            failures.append({"vector": vector, "encoded": encoded, "decoded": decoded})
    return failures


def sample_states() -> list[dict[str, object]]:
    samples = [
        {
            "name": "physics2_idle",
            "state": {"R1": 0, "R2": 0, "R3": 0, "R4": 1, "R5": 0, "R6": -1},
        },
        {
            "name": "physics2_left_mid",
            "state": {"R1": 1, "R2": 0, "R3": 0, "R4": 1, "R5": 0, "R6": -1},
        },
        {
            "name": "physics2_right_high",
            "state": {"R1": 0, "R2": -1, "R3": 0, "R4": 1, "R5": 0, "R6": -1},
        },
        {
            "name": "physics2_boundary",
            "state": {"R1": 1, "R2": 0, "R3": 0, "R4": -1, "R5": 1, "R6": 0},
        },
    ]
    results: list[dict[str, object]] = []
    for item in samples:
        encoded = encode_signed_state(item["state"])
        results.append(
            {
                "name": item["name"],
                "state": item["state"],
                "encoded": encoded,
                "decoded": decode_signed_state(encoded),
            }
        )
    return results


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
        "samples": sample_states(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the physics2 state carrier.")
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    parser.add_argument("--check-only", action="store_true", help="Only emit round-trip status.")
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

    print("Physics2 state carrier")
    print(f"Registers: {len(REGISTERS)}")
    print(f"State space size: {payload['state_space_size']}")
    print(f"Round-trip status: {payload['round_trip']['status']}")
    print(f"Round-trip failures: {payload['round_trip']['failure_count']}")


if __name__ == "__main__":
    main()
