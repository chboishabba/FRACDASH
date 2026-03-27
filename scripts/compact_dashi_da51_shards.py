#!/usr/bin/env python3
"""Compact aggregate DA51 CBOR shards with exact byte reconstruction."""

from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

import cbor2

DA51_TAG = 0xDA51


def _slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    return "_".join(part for part in cleaned.split("_") if part) or "unknown"


def _module_name(file_name: str) -> str:
    return file_name[:-5] if file_name.endswith(".agda") else file_name


def _dashi_semantics(module_name: str) -> tuple[str, str]:
    lowered = module_name.lower()
    if "monster" in lowered:
        return ("monster", "dynamics")
    if "moonshine" in lowered:
        return ("moonshine", "dynamics")
    if "fixedpoint" in lowered or "fixpoint" in lowered:
        return ("fixed_point", "proof_surface")
    if "contraction" in lowered or "ultrametric" in lowered:
        return ("geometry", "proof_surface")
    if "trace" in lowered or "history" in lowered or "da51" in lowered:
        return ("trace", "witness")
    if lowered.startswith("layer"):
        return ("layer", "dynamics")
    if "test" in lowered or "harness" in lowered:
        return ("test_harness", "derived_test")
    if "action" in lowered or "logic" in lowered or "prime" in lowered:
        return ("structural", "proof_surface")
    return (f"module_{_slug(module_name)}", "structural")


def load_shards(directory: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.cbor")):
        raw_bytes = path.read_bytes()
        decoded = cbor2.loads(raw_bytes)
        payload = decoded.value if isinstance(decoded, cbor2.CBORTag) else decoded
        module_name = _module_name(str(payload["file"]))
        dashi_class, dashi_family = _dashi_semantics(module_name)
        rows.append(
            {
                "path_name": path.name,
                "raw_bytes": raw_bytes,
                "payload": payload,
                "module": module_name,
                "dashi_class": dashi_class,
                "dashi_family": dashi_family,
            }
        )
    return rows


def _fractran_program_key(fractran: dict[str, Any]) -> tuple[Any, ...]:
    if "reason" in fractran:
        return (
            "negative",
            tuple(fractran.get("ssp_primes", [])),
            bool(fractran.get("earns_moonshine", False)),
            fractran.get("reason"),
        )
    return (
        "positive",
        tuple(fractran.get("ssp_primes", [])),
        tuple(fractran.get("denominators", [])),
        tuple(fractran.get("fractions", [])),
        int(fractran.get("steps", 0)),
        bool(fractran.get("earns_moonshine", False)),
    )


def _encode_programs(rows: list[dict[str, Any]]) -> tuple[list[list[Any]], dict[tuple[Any, ...], int]]:
    motifs: list[list[Any]] = []
    key_to_index: dict[tuple[Any, ...], int] = {}
    for row in rows:
        key = _fractran_program_key(row["payload"]["fractran"])
        if key in key_to_index:
            continue
        key_to_index[key] = len(motifs)
        if key[0] == "negative":
            _, ssp_primes, earns_moonshine, reason = key
            motifs.append(["negative", list(ssp_primes), earns_moonshine, reason])
        else:
            _, ssp_primes, denominators, fractions, steps, earns_moonshine = key
            motifs.append(
                [
                    "positive",
                    list(ssp_primes),
                    list(denominators),
                    list(fractions),
                    steps,
                    earns_moonshine,
                ]
            )
    return motifs, key_to_index


def encode_surface(rows: list[dict[str, Any]]) -> bytes:
    programs, program_to_index = _encode_programs(rows)
    encoded_rows: list[list[Any]] = []
    for row in rows:
        payload = row["payload"]
        counters = payload["counters"]
        fractran = payload["fractran"]
        encoded_rows.append(
            [
                payload["file"],
                payload["sha256"],
                [
                    int(counters["cycles"]),
                    int(counters["instructions"]),
                    int(counters["cache-misses"]),
                    int(counters["branch-misses"]),
                ],
                payload["trace_sha256"],
                fractran.get("state"),
                list(fractran.get("trace", [])),
                program_to_index[_fractran_program_key(fractran)],
            ]
        )
    compact_payload = {
        "trace_kind": "dashi_da51_shard_surface/v1",
        "tag": DA51_TAG,
        "programs": programs,
        "rows": encoded_rows,
    }
    return cbor2.dumps(compact_payload)


def encode_semantic(rows: list[dict[str, Any]]) -> bytes:
    programs, program_to_index = _encode_programs(rows)
    motifs: list[list[Any]] = []
    motif_to_index: dict[tuple[str, str], int] = {}
    encoded_rows: list[list[Any]] = []
    for row in rows:
        payload = row["payload"]
        counters = payload["counters"]
        fractran = payload["fractran"]
        program_index = program_to_index[_fractran_program_key(fractran)]
        motif_key = (row["dashi_class"], row["dashi_family"])
        motif_index = motif_to_index.setdefault(motif_key, len(motifs))
        if motif_index == len(motifs):
            dashi_class, dashi_family = motif_key
            motifs.append([dashi_class, dashi_family])
        encoded_rows.append(
            [
                payload["file"],
                payload["sha256"],
                [
                    int(counters["cycles"]),
                    int(counters["instructions"]),
                    int(counters["cache-misses"]),
                    int(counters["branch-misses"]),
                ],
                payload["trace_sha256"],
                fractran.get("state"),
                list(fractran.get("trace", [])),
                program_index,
                motif_index,
            ]
        )
    compact_payload = {
        "trace_kind": "dashi_da51_shard_semantic/v1",
        "tag": DA51_TAG,
        "programs": programs,
        "semantic_motifs": motifs,
        "rows": encoded_rows,
    }
    return cbor2.dumps(compact_payload)


def _decode_program(program: list[Any], state: Any, trace: list[Any]) -> OrderedDict[str, Any]:
    fractran: OrderedDict[str, Any] = OrderedDict()
    tag = program[0]
    if tag == "negative":
        _, ssp_primes, earns_moonshine, reason = program
        fractran["ssp_primes"] = list(ssp_primes)
        fractran["state"] = state
        fractran["earns_moonshine"] = earns_moonshine
        fractran["reason"] = reason
        return fractran

    _, ssp_primes, denominators, fractions, steps, earns_moonshine = program
    fractran["ssp_primes"] = list(ssp_primes)
    fractran["state"] = state
    fractran["denominators"] = list(denominators)
    fractran["fractions"] = list(fractions)
    fractran["trace"] = list(trace)
    fractran["steps"] = int(steps)
    fractran["earns_moonshine"] = earns_moonshine
    return fractran


def _decode_rows(compact: dict[str, Any], semantic: bool) -> list[tuple[str, bytes]]:
    tag = int(compact["tag"])
    programs = compact["programs"]
    semantic_motifs = compact.get("semantic_motifs", [])
    decoded: list[tuple[str, bytes]] = []
    for row in compact["rows"]:
        if semantic:
            file_name, sha256, counters_array, trace_sha256, state, trace, program_index, _semantic_index = row
        else:
            file_name, sha256, counters_array, trace_sha256, state, trace, program_index = row
        if semantic:
            # semantic motifs are analysis metadata only; program recovery stays exact
            _ = semantic_motifs
        counters = OrderedDict(
            [
                ("cycles", int(counters_array[0])),
                ("instructions", int(counters_array[1])),
                ("cache-misses", int(counters_array[2])),
                ("branch-misses", int(counters_array[3])),
            ]
        )
        payload = OrderedDict(
            [
                ("file", file_name),
                ("sha256", sha256),
                ("counters", counters),
                ("trace_sha256", trace_sha256),
                ("fractran", _decode_program(programs[program_index], state, trace)),
            ]
        )
        file_bytes = cbor2.dumps(cbor2.CBORTag(tag, payload))
        decoded.append((str(file_name).replace(".agda", ".cbor"), file_bytes))
    return decoded


def decode_surface_bytes(blob: bytes) -> list[tuple[str, bytes]]:
    compact = cbor2.loads(blob)
    if compact.get("trace_kind") != "dashi_da51_shard_surface/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")
    return _decode_rows(compact, semantic=False)


def decode_semantic_bytes(blob: bytes) -> list[tuple[str, bytes]]:
    compact = cbor2.loads(blob)
    if compact.get("trace_kind") != "dashi_da51_shard_semantic/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")
    return _decode_rows(compact, semantic=True)


def write_bytes(path: Path, payload: bytes) -> None:
    path.write_bytes(payload)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def stats_compare(rows: list[dict[str, Any]], surface_blob: bytes, semantic_blob: bytes) -> dict[str, Any]:
    raw_total = sum(len(row["raw_bytes"]) for row in rows)
    compact_surface = cbor2.loads(surface_blob)
    compact_semantic = cbor2.loads(semantic_blob)
    program_count = len(compact_surface["programs"])
    semantic_count = len(compact_semantic["semantic_motifs"])
    return {
        "source_kind": "dashi_agda_da51_cbor_aggregate",
        "file_count": len(rows),
        "raw_total_bytes": raw_total,
        "surface": {
            "bytes": len(surface_blob),
            "program_motifs": program_count,
            "gain_over_raw": raw_total - len(surface_blob),
        },
        "semantic": {
            "bytes": len(semantic_blob),
            "program_motifs": len(compact_semantic["programs"]),
            "semantic_motifs": semantic_count,
            "gain_over_raw": raw_total - len(semantic_blob),
            "semantic_minus_surface_bytes": len(semantic_blob) - len(surface_blob),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("encode-surface", "encode-semantic"):
        sub = subparsers.add_parser(command)
        sub.add_argument("input_dir", type=Path)
        sub.add_argument("output", type=Path)

    for command in ("decode-surface-dir", "decode-semantic-dir"):
        sub = subparsers.add_parser(command)
        sub.add_argument("input", type=Path)
        sub.add_argument("output_dir", type=Path)

    stats = subparsers.add_parser("stats-compare")
    stats.add_argument("input_dir", type=Path)
    stats.add_argument("surface_output", type=Path)
    stats.add_argument("semantic_output", type=Path)
    stats.add_argument("stats_output", type=Path)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "encode-surface":
        rows = load_shards(args.input_dir)
        write_bytes(args.output, encode_surface(rows))
        return 0

    if args.command == "encode-semantic":
        rows = load_shards(args.input_dir)
        write_bytes(args.output, encode_semantic(rows))
        return 0

    if args.command == "decode-surface-dir":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for file_name, file_bytes in decode_surface_bytes(args.input.read_bytes()):
            (args.output_dir / file_name).write_bytes(file_bytes)
        return 0

    if args.command == "decode-semantic-dir":
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for file_name, file_bytes in decode_semantic_bytes(args.input.read_bytes()):
            (args.output_dir / file_name).write_bytes(file_bytes)
        return 0

    if args.command == "stats-compare":
        rows = load_shards(args.input_dir)
        surface_blob = encode_surface(rows)
        semantic_blob = encode_semantic(rows)
        write_bytes(args.surface_output, surface_blob)
        write_bytes(args.semantic_output, semantic_blob)
        write_json(args.stats_output, stats_compare(rows, surface_blob, semantic_blob))
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
