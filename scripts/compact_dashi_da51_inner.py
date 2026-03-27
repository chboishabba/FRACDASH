#!/usr/bin/env python3
"""Compact the inner FRACTRAN payload of the DA51 shard corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import OrderedDict
from fractions import Fraction
from pathlib import Path
from typing import Any

import cbor2

from compact_dashi_da51_shards import DA51_TAG, load_shards

FIXED_NUMERATORS = (47, 59, 71)
FIXED_STEPS = 3


def _sha256_counters(counters: OrderedDict[str, int]) -> str:
    plain = dict(counters)
    return hashlib.sha256(json.dumps(plain, sort_keys=True).encode()).hexdigest()


def _rebuild_fractions(denominators: list[int]) -> list[str]:
    return [f"{num}/{den}" for num, den in zip(FIXED_NUMERATORS, denominators)]


def _run_trace(state: int, fractions: list[str], steps: int) -> list[int]:
    current = int(state)
    trace = [current]
    fracs = [Fraction(item) for item in fractions]
    for _ in range(steps):
        for frac in fracs:
            numerator = frac.numerator
            denominator = frac.denominator
            if current % denominator == 0:
                current = current // denominator * numerator
                trace.append(current)
                break
        else:
            break
    return trace


def _positive_program_key(payload: dict[str, Any]) -> tuple[Any, ...]:
    fractran = payload["fractran"]
    return (tuple(fractran["ssp_primes"]), tuple(fractran["denominators"]))


def _negative_key(payload: dict[str, Any]) -> tuple[Any, ...]:
    fractran = payload["fractran"]
    return (tuple(fractran["ssp_primes"]), fractran["reason"])


def encode_inner(rows: list[dict[str, Any]]) -> bytes:
    positive_programs: list[list[Any]] = []
    positive_index: dict[tuple[Any, ...], int] = {}
    negative_cases: list[list[Any]] = []
    negative_index: dict[tuple[Any, ...], int] = {}
    encoded_rows: list[list[Any]] = []

    for row in rows:
        payload = row["payload"]
        counters = payload["counters"]
        fractran = payload["fractran"]
        if "denominators" in fractran:
            key = _positive_program_key(payload)
            program_idx = positive_index.setdefault(key, len(positive_programs))
            if program_idx == len(positive_programs):
                ssp_primes, denominators = key
                positive_programs.append([list(ssp_primes), list(denominators)])
            encoded_rows.append(
                [
                    "positive",
                    payload["file"],
                    payload["sha256"],
                    [
                        int(counters["cycles"]),
                        int(counters["instructions"]),
                        int(counters["cache-misses"]),
                        int(counters["branch-misses"]),
                    ],
                    int(fractran["state"]),
                    program_idx,
                ]
            )
        else:
            key = _negative_key(payload)
            reason_idx = negative_index.setdefault(key, len(negative_cases))
            if reason_idx == len(negative_cases):
                ssp_primes, reason = key
                negative_cases.append([list(ssp_primes), reason])
            encoded_rows.append(
                [
                    "negative",
                    payload["file"],
                    payload["sha256"],
                    [
                        int(counters["cycles"]),
                        int(counters["instructions"]),
                        int(counters["cache-misses"]),
                        int(counters["branch-misses"]),
                    ],
                    reason_idx,
                ]
            )

    compact = {
        "trace_kind": "dashi_da51_inner/v1",
        "tag": DA51_TAG,
        "fixed_numerators": list(FIXED_NUMERATORS),
        "fixed_steps": FIXED_STEPS,
        "positive_programs": positive_programs,
        "negative_cases": negative_cases,
        "rows": encoded_rows,
    }
    return cbor2.dumps(compact)


def decode_inner_bytes(blob: bytes) -> list[tuple[str, bytes]]:
    compact = cbor2.loads(blob)
    if compact.get("trace_kind") != "dashi_da51_inner/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")
    tag = int(compact["tag"])
    fixed_steps = int(compact["fixed_steps"])
    positive_programs = compact["positive_programs"]
    negative_cases = compact["negative_cases"]
    decoded: list[tuple[str, bytes]] = []

    for row in compact["rows"]:
        kind = row[0]
        file_name = row[1]
        sha256 = row[2]
        counters_array = row[3]
        counters = OrderedDict(
            [
                ("cycles", int(counters_array[0])),
                ("instructions", int(counters_array[1])),
                ("cache-misses", int(counters_array[2])),
                ("branch-misses", int(counters_array[3])),
            ]
        )
        top = OrderedDict(
            [
                ("file", file_name),
                ("sha256", sha256),
                ("counters", counters),
                ("trace_sha256", _sha256_counters(counters)),
            ]
        )
        if kind == "positive":
            state = int(row[4])
            program = positive_programs[row[5]]
            ssp_primes = list(program[0])
            denominators = list(program[1])
            fractions = _rebuild_fractions(denominators)
            trace = _run_trace(state, fractions, fixed_steps)
            fractran = OrderedDict(
                [
                    ("ssp_primes", ssp_primes),
                    ("state", state),
                    ("denominators", denominators),
                    ("fractions", fractions),
                    ("trace", trace),
                    ("steps", fixed_steps),
                    ("earns_moonshine", True),
                ]
            )
        else:
            negative = negative_cases[row[4]]
            fractran = OrderedDict(
                [
                    ("ssp_primes", list(negative[0])),
                    ("state", None),
                    ("earns_moonshine", False),
                    ("reason", negative[1]),
                ]
            )
        top["fractran"] = fractran
        decoded.append((str(file_name).replace(".agda", ".cbor"), cbor2.dumps(cbor2.CBORTag(tag, top))))
    return decoded


def stats_compare(rows: list[dict[str, Any]], inner_blob: bytes, aggregate_surface_bytes: int) -> dict[str, Any]:
    compact = cbor2.loads(inner_blob)
    raw_total = sum(len(row["raw_bytes"]) for row in rows)
    return {
        "source_kind": "dashi_agda_da51_inner_payload",
        "file_count": len(rows),
        "raw_total_bytes": raw_total,
        "inner": {
            "bytes": len(inner_blob),
            "positive_programs": len(compact["positive_programs"]),
            "negative_cases": len(compact["negative_cases"]),
            "gain_over_raw": raw_total - len(inner_blob),
        },
        "aggregate_surface_reference": {
            "bytes": aggregate_surface_bytes,
            "inner_minus_aggregate_bytes": len(inner_blob) - aggregate_surface_bytes,
        },
    }


def write_bytes(path: Path, payload: bytes) -> None:
    path.write_bytes(payload)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode = subparsers.add_parser("encode")
    encode.add_argument("input_dir", type=Path)
    encode.add_argument("output", type=Path)

    decode = subparsers.add_parser("decode-dir")
    decode.add_argument("input", type=Path)
    decode.add_argument("output_dir", type=Path)

    stats = subparsers.add_parser("stats-compare")
    stats.add_argument("input_dir", type=Path)
    stats.add_argument("output", type=Path)
    stats.add_argument("stats_output", type=Path)
    stats.add_argument("aggregate_surface_bytes", type=int)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "encode":
        rows = load_shards(args.input_dir)
        write_bytes(args.output, encode_inner(rows))
        return 0

    if args.command == "decode-dir":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for file_name, file_bytes in decode_inner_bytes(args.input.read_bytes()):
            (args.output_dir / file_name).write_bytes(file_bytes)
        return 0

    if args.command == "stats-compare":
        rows = load_shards(args.input_dir)
        inner_blob = encode_inner(rows)
        write_bytes(args.output, inner_blob)
        write_json(args.stats_output, stats_compare(rows, inner_blob, args.aggregate_surface_bytes))
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
