#!/usr/bin/env python3
"""Schema-aware codecs for normalized zkperf waveform traces."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


REGISTER_LABELS = [
    "idx",
    "log10(period+1)",
    "log10(ts_gap+1)",
    "pid",
    "tid",
    "cpu_mode",
]

CPU_MODE_SIGNAL = {
    "Kernel": -1.0,
    "User": 1.0,
}


def _slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    return "_".join(part for part in cleaned.split("_") if part) or "unknown"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _as_int(value: Any) -> int:
    if isinstance(value, bool):
        raise TypeError(f"unexpected bool where int was required: {value!r}")
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return int(value)


def _matrix_row(step: int, period: int, ts_gap: int, pid: int, tid: int, cpu_mode: str) -> list[float]:
    return [
        float(step),
        math.log10(period + 1.0) if period else 0.0,
        math.log10(abs(ts_gap) + 1.0) if ts_gap else 0.0,
        float(pid),
        float(tid),
        CPU_MODE_SIGNAL.get(cpu_mode, 0.0),
    ]


def _classify_dashi(transition: str, cpu_mode: str) -> tuple[str, str]:
    normalized = transition.strip()
    if normalized.startswith("cycles:"):
        return ("cycle_probe", "perf_history")
    if "cache" in normalized.lower():
        return ("cache_probe", "memory_observation")
    if "branch" in normalized.lower():
        return ("branch_probe", "control_flow")
    if cpu_mode == "Kernel":
        return ("kernel_sample", "execution_boundary")
    if cpu_mode == "User":
        return ("user_sample", "execution_flow")
    base = _slug(normalized or "sample")
    return (f"event_{base}", "sample_trace")


def encode_trace(trace: dict[str, Any]) -> dict[str, Any]:
    if trace.get("trace_kind") != "zkperf_sample_trace":
        raise ValueError(f"unsupported trace_kind: {trace.get('trace_kind')!r}")

    metadata = trace.get("metadata", {})
    rows: list[dict[str, Any]] = []
    events: list[str] = []
    event_to_index: dict[str, int] = {}

    for annotation in trace.get("step_annotations", []):
        transition = str(annotation.get("transition", ""))
        event_index = event_to_index.setdefault(transition, len(events))
        if event_index == len(events):
            events.append(transition)
        dashi_class, dashi_family = _classify_dashi(transition, str(annotation["cpu_mode"]))
        rows.append(
            {
                "step": _as_int(annotation["step"]),
                "event_idx": event_index,
                "timestamp": _as_int(annotation["timestamp"]),
                "period": _as_int(annotation["period"]),
                "pid": _as_int(annotation["next_state"][3]),
                "tid": _as_int(annotation["next_state"][4]),
                "cpu_mode": str(annotation["cpu_mode"]),
                "cid": annotation["cid"],
                "dashi_class": dashi_class,
                "dashi_family": dashi_family,
            }
        )

    return {
        "trace_kind": "zkperf_sample_trace_compact/v1",
        "source_dir": trace.get("source_dir"),
        "artifact": metadata.get("artifact"),
        "template_set": metadata.get("template_set"),
        "shard_family_counts": metadata.get("shard_family_counts", {}),
        "events": events,
        "rows": rows,
    }


def decode_trace(compact: dict[str, Any]) -> dict[str, Any]:
    if compact.get("trace_kind") != "zkperf_sample_trace_compact/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")

    events = list(compact.get("events", []))
    rows = compact.get("rows", [])

    matrix: list[list[float]] = []
    annotations: list[dict[str, Any]] = []
    transition_names: list[str] = []
    prev_timestamp: int | None = None

    for row in rows:
        step = _as_int(row["step"])
        timestamp = _as_int(row["timestamp"])
        period = _as_int(row["period"])
        pid = _as_int(row["pid"])
        tid = _as_int(row["tid"])
        cpu_mode = str(row["cpu_mode"])
        ts_gap = 0 if prev_timestamp is None else timestamp - prev_timestamp
        prev_timestamp = timestamp
        transition = events[_as_int(row["event_idx"])]
        matrix_row = _matrix_row(step, period, ts_gap, pid, tid, cpu_mode)
        matrix.append(matrix_row)
        transition_names.append(transition)
        annotations.append(
            {
                "step": step,
                "transition": transition,
                "changed_register_count": 1,
                "changed_registers": ["sample"],
                "changed_register_mask": [True, True, True, True, True, True],
                "delta": matrix_row,
                "l1_step_delta": float(sum(abs(value) for value in matrix_row)),
                "state": None,
                "next_state": matrix_row,
                "cid": row["cid"],
                "cpu_mode": cpu_mode,
                "timestamp": timestamp,
                "period": period,
            }
        )

    return {
        "trace_kind": "zkperf_sample_trace",
        "source_dir": compact.get("source_dir"),
        "register_labels": REGISTER_LABELS,
        "matrix": matrix,
        "metadata": {
            "template_set": compact.get("template_set"),
            "artifact": compact.get("artifact"),
            "register_count": 6,
            "walk_status": "sample_trace",
            "steps": len(matrix),
            "cycle_start": None,
            "final_state": matrix[-1] if matrix else [],
            "best_candidate": None,
            "regime_usage_by_slice": None,
            "shard_family_counts": compact.get("shard_family_counts", {}),
        },
        "step_annotations": annotations,
    }


def encode_motif(compact: dict[str, Any]) -> dict[str, Any]:
    if compact.get("trace_kind") != "zkperf_sample_trace_compact/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")

    motifs: list[dict[str, Any]] = []
    motif_to_index: dict[tuple[int, int, int, str, str, str], int] = {}
    rows: list[dict[str, Any]] = []

    for row in compact.get("rows", []):
        motif_key = (
            _as_int(row["event_idx"]),
            _as_int(row["pid"]),
            _as_int(row["tid"]),
            str(row["cpu_mode"]),
            str(row["dashi_class"]),
            str(row["dashi_family"]),
        )
        motif_index = motif_to_index.setdefault(motif_key, len(motifs))
        if motif_index == len(motifs):
            event_idx, pid, tid, cpu_mode, dashi_class, dashi_family = motif_key
            motifs.append(
                {
                    "event_idx": event_idx,
                    "pid": pid,
                    "tid": tid,
                    "cpu_mode": cpu_mode,
                    "dashi_class": dashi_class,
                    "dashi_family": dashi_family,
                }
            )
        rows.append(
            {
                "step": _as_int(row["step"]),
                "timestamp": _as_int(row["timestamp"]),
                "period": _as_int(row["period"]),
                "cid": row["cid"],
                "motif_idx": motif_index,
            }
        )

    return {
        "trace_kind": "zkperf_sample_trace_motif/v1",
        "source_dir": compact.get("source_dir"),
        "artifact": compact.get("artifact"),
        "template_set": compact.get("template_set"),
        "shard_family_counts": compact.get("shard_family_counts", {}),
        "events": compact.get("events", []),
        "motifs": motifs,
        "rows": rows,
    }


def decode_motif(motif_payload: dict[str, Any]) -> dict[str, Any]:
    if motif_payload.get("trace_kind") != "zkperf_sample_trace_motif/v1":
        raise ValueError(f"unsupported trace_kind: {motif_payload.get('trace_kind')!r}")

    motifs = motif_payload.get("motifs", [])
    rows: list[dict[str, Any]] = []

    for row in motif_payload.get("rows", []):
        motif = motifs[_as_int(row["motif_idx"])]
        rows.append(
            {
                "step": _as_int(row["step"]),
                "event_idx": _as_int(motif["event_idx"]),
                "timestamp": _as_int(row["timestamp"]),
                "period": _as_int(row["period"]),
                "pid": _as_int(motif["pid"]),
                "tid": _as_int(motif["tid"]),
                "cpu_mode": str(motif["cpu_mode"]),
                "cid": row["cid"],
                "dashi_class": str(motif["dashi_class"]),
                "dashi_family": str(motif["dashi_family"]),
            }
        )

    return {
        "trace_kind": "zkperf_sample_trace_compact/v1",
        "source_dir": motif_payload.get("source_dir"),
        "artifact": motif_payload.get("artifact"),
        "template_set": motif_payload.get("template_set"),
        "shard_family_counts": motif_payload.get("shard_family_counts", {}),
        "events": motif_payload.get("events", []),
        "rows": rows,
    }


def encode_semantic_motif(compact: dict[str, Any]) -> dict[str, Any]:
    if compact.get("trace_kind") != "zkperf_sample_trace_compact/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")

    motifs: list[dict[str, Any]] = []
    motif_to_index: dict[tuple[int, int, int, str, str], int] = {}
    rows: list[dict[str, Any]] = []

    for row in compact.get("rows", []):
        motif_key = (
            _as_int(row["event_idx"]),
            _as_int(row["pid"]),
            _as_int(row["tid"]),
            str(row["dashi_class"]),
            str(row["dashi_family"]),
        )
        motif_index = motif_to_index.setdefault(motif_key, len(motifs))
        if motif_index == len(motifs):
            event_idx, pid, tid, dashi_class, dashi_family = motif_key
            motifs.append(
                {
                    "event_idx": event_idx,
                    "pid": pid,
                    "tid": tid,
                    "dashi_class": dashi_class,
                    "dashi_family": dashi_family,
                }
            )
        rows.append(
            {
                "step": _as_int(row["step"]),
                "timestamp": _as_int(row["timestamp"]),
                "period": _as_int(row["period"]),
                "cpu_mode": str(row["cpu_mode"]),
                "cid": row["cid"],
                "motif_idx": motif_index,
            }
        )

    return {
        "trace_kind": "zkperf_sample_trace_semantic_motif/v1",
        "source_dir": compact.get("source_dir"),
        "artifact": compact.get("artifact"),
        "template_set": compact.get("template_set"),
        "shard_family_counts": compact.get("shard_family_counts", {}),
        "events": compact.get("events", []),
        "motifs": motifs,
        "rows": rows,
    }


def decode_semantic_motif(motif_payload: dict[str, Any]) -> dict[str, Any]:
    if motif_payload.get("trace_kind") != "zkperf_sample_trace_semantic_motif/v1":
        raise ValueError(f"unsupported trace_kind: {motif_payload.get('trace_kind')!r}")

    motifs = motif_payload.get("motifs", [])
    rows: list[dict[str, Any]] = []

    for row in motif_payload.get("rows", []):
        motif = motifs[_as_int(row["motif_idx"])]
        rows.append(
            {
                "step": _as_int(row["step"]),
                "event_idx": _as_int(motif["event_idx"]),
                "timestamp": _as_int(row["timestamp"]),
                "period": _as_int(row["period"]),
                "pid": _as_int(motif["pid"]),
                "tid": _as_int(motif["tid"]),
                "cpu_mode": str(row["cpu_mode"]),
                "cid": row["cid"],
                "dashi_class": str(motif["dashi_class"]),
                "dashi_family": str(motif["dashi_family"]),
            }
        )

    return {
        "trace_kind": "zkperf_sample_trace_compact/v1",
        "source_dir": motif_payload.get("source_dir"),
        "artifact": motif_payload.get("artifact"),
        "template_set": motif_payload.get("template_set"),
        "shard_family_counts": motif_payload.get("shard_family_counts", {}),
        "events": motif_payload.get("events", []),
        "rows": rows,
    }


def compression_stats(source_path: Path, compact_path: Path, roundtrip_path: Path | None = None) -> dict[str, Any]:
    source = load_json(source_path)
    compact = encode_trace(source)
    write_json(compact_path, compact)
    roundtrip = decode_trace(compact)
    if roundtrip_path is not None:
        write_json(roundtrip_path, roundtrip)
    source_bytes = source_path.stat().st_size
    compact_bytes = compact_path.stat().st_size
    return {
        "source": str(source_path),
        "compact": str(compact_path),
        "roundtrip": str(roundtrip_path) if roundtrip_path is not None else None,
        "source_bytes": source_bytes,
        "compact_bytes": compact_bytes,
        "saved_bytes": source_bytes - compact_bytes,
        "reduction_ratio": 0.0 if source_bytes == 0 else (source_bytes - compact_bytes) / source_bytes,
        "row_count": len(compact.get("rows", [])),
        "event_count": len(compact.get("events", [])),
        "roundtrip_equal": roundtrip == source,
    }


def motif_compression_stats(source_path: Path, motif_path: Path, roundtrip_path: Path | None = None) -> dict[str, Any]:
    source = load_json(source_path)
    motif_payload = encode_motif(source)
    write_json(motif_path, motif_payload)
    roundtrip = decode_motif(motif_payload)
    if roundtrip_path is not None:
        write_json(roundtrip_path, roundtrip)
    source_bytes = source_path.stat().st_size
    motif_bytes = motif_path.stat().st_size
    return {
        "source": str(source_path),
        "motif": str(motif_path),
        "roundtrip": str(roundtrip_path) if roundtrip_path is not None else None,
        "source_bytes": source_bytes,
        "motif_bytes": motif_bytes,
        "saved_bytes": source_bytes - motif_bytes,
        "reduction_ratio": 0.0 if source_bytes == 0 else (source_bytes - motif_bytes) / source_bytes,
        "row_count": len(motif_payload.get("rows", [])),
        "event_count": len(motif_payload.get("events", [])),
        "motif_count": len(motif_payload.get("motifs", [])),
        "roundtrip_equal": roundtrip == source,
    }


def semantic_motif_compression_stats(
    source_path: Path,
    motif_path: Path,
    roundtrip_path: Path | None = None,
) -> dict[str, Any]:
    source = load_json(source_path)
    motif_payload = encode_semantic_motif(source)
    write_json(motif_path, motif_payload)
    roundtrip = decode_semantic_motif(motif_payload)
    if roundtrip_path is not None:
        write_json(roundtrip_path, roundtrip)
    source_bytes = source_path.stat().st_size
    motif_bytes = motif_path.stat().st_size
    return {
        "source": str(source_path),
        "semantic_motif": str(motif_path),
        "roundtrip": str(roundtrip_path) if roundtrip_path is not None else None,
        "source_bytes": source_bytes,
        "semantic_motif_bytes": motif_bytes,
        "saved_bytes": source_bytes - motif_bytes,
        "reduction_ratio": 0.0 if source_bytes == 0 else (source_bytes - motif_bytes) / source_bytes,
        "row_count": len(motif_payload.get("rows", [])),
        "event_count": len(motif_payload.get("events", [])),
        "motif_count": len(motif_payload.get("motifs", [])),
        "roundtrip_equal": roundtrip == source,
    }


def compare_compression_stats(raw_path: Path, compact_path: Path, surface_motif_path: Path, semantic_motif_path: Path) -> dict[str, Any]:
    raw = load_json(raw_path)
    compact = encode_trace(raw)
    write_json(compact_path, compact)
    surface = encode_motif(compact)
    write_json(surface_motif_path, surface)
    semantic = encode_semantic_motif(compact)
    write_json(semantic_motif_path, semantic)
    raw_bytes = raw_path.stat().st_size
    compact_bytes = compact_path.stat().st_size
    surface_bytes = surface_motif_path.stat().st_size
    semantic_bytes = semantic_motif_path.stat().st_size
    return {
        "raw": str(raw_path),
        "compact": {"path": str(compact_path), "bytes": compact_bytes},
        "surface_motif": {"path": str(surface_motif_path), "bytes": surface_bytes, "motif_count": len(surface.get("motifs", []))},
        "semantic_motif": {"path": str(semantic_motif_path), "bytes": semantic_bytes, "motif_count": len(semantic.get("motifs", []))},
        "raw_bytes": raw_bytes,
        "compact_gain": raw_bytes - compact_bytes,
        "surface_motif_gain_over_compact": compact_bytes - surface_bytes,
        "semantic_motif_gain_over_compact": compact_bytes - semantic_bytes,
        "semantic_minus_surface_bytes": surface_bytes - semantic_bytes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Encode or decode compact zkperf waveform traces.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="Encode normalized waveform JSON into compact JSON")
    encode_parser.add_argument("input", type=Path)
    encode_parser.add_argument("output", type=Path)

    decode_parser = subparsers.add_parser("decode", help="Decode compact JSON back into normalized waveform JSON")
    decode_parser.add_argument("input", type=Path)
    decode_parser.add_argument("output", type=Path)

    stats_parser = subparsers.add_parser("stats", help="Encode a trace and report size + round-trip stats")
    stats_parser.add_argument("input", type=Path)
    stats_parser.add_argument("compact_output", type=Path)
    stats_parser.add_argument("--roundtrip-output", type=Path)

    motif_encode_parser = subparsers.add_parser("encode-motif", help="Encode compact JSON into motif JSON")
    motif_encode_parser.add_argument("input", type=Path)
    motif_encode_parser.add_argument("output", type=Path)

    motif_decode_parser = subparsers.add_parser("decode-motif", help="Decode motif JSON back into compact JSON")
    motif_decode_parser.add_argument("input", type=Path)
    motif_decode_parser.add_argument("output", type=Path)

    motif_stats_parser = subparsers.add_parser(
        "stats-motif",
        help="Encode a compact trace into motif form and report size + round-trip stats",
    )
    motif_stats_parser.add_argument("input", type=Path)
    motif_stats_parser.add_argument("motif_output", type=Path)
    motif_stats_parser.add_argument("--roundtrip-output", type=Path)

    semantic_motif_encode_parser = subparsers.add_parser(
        "encode-semantic-motif",
        help="Encode compact JSON into semantic-motif JSON",
    )
    semantic_motif_encode_parser.add_argument("input", type=Path)
    semantic_motif_encode_parser.add_argument("output", type=Path)

    semantic_motif_decode_parser = subparsers.add_parser(
        "decode-semantic-motif",
        help="Decode semantic-motif JSON back into compact JSON",
    )
    semantic_motif_decode_parser.add_argument("input", type=Path)
    semantic_motif_decode_parser.add_argument("output", type=Path)

    semantic_motif_stats_parser = subparsers.add_parser(
        "stats-semantic-motif",
        help="Encode a compact trace into semantic-motif form and report size + round-trip stats",
    )
    semantic_motif_stats_parser.add_argument("input", type=Path)
    semantic_motif_stats_parser.add_argument("semantic_motif_output", type=Path)
    semantic_motif_stats_parser.add_argument("--roundtrip-output", type=Path)

    compare_parser = subparsers.add_parser(
        "stats-compare",
        help="Compare raw->compact, raw->compact->surface-motif, and raw->compact->semantic-motif",
    )
    compare_parser.add_argument("input", type=Path)
    compare_parser.add_argument("compact_output", type=Path)
    compare_parser.add_argument("surface_motif_output", type=Path)
    compare_parser.add_argument("semantic_motif_output", type=Path)

    args = parser.parse_args()

    if args.command == "encode":
        write_json(args.output, encode_trace(load_json(args.input)))
        return

    if args.command == "decode":
        write_json(args.output, decode_trace(load_json(args.input)))
        return

    if args.command == "stats":
        print(json.dumps(compression_stats(args.input, args.compact_output, args.roundtrip_output), indent=2))
        return

    if args.command == "encode-motif":
        write_json(args.output, encode_motif(load_json(args.input)))
        return

    if args.command == "decode-motif":
        write_json(args.output, decode_motif(load_json(args.input)))
        return

    if args.command == "stats-motif":
        print(json.dumps(motif_compression_stats(args.input, args.motif_output, args.roundtrip_output), indent=2))
        return

    if args.command == "encode-semantic-motif":
        write_json(args.output, encode_semantic_motif(load_json(args.input)))
        return

    if args.command == "decode-semantic-motif":
        write_json(args.output, decode_semantic_motif(load_json(args.input)))
        return

    if args.command == "stats-semantic-motif":
        print(
            json.dumps(
                semantic_motif_compression_stats(
                    args.input,
                    args.semantic_motif_output,
                    args.roundtrip_output,
                ),
                indent=2,
            )
        )
        return

    if args.command == "stats-compare":
        print(
            json.dumps(
                compare_compression_stats(
                    args.input,
                    args.compact_output,
                    args.surface_motif_output,
                    args.semantic_motif_output,
                ),
                indent=2,
            )
        )
        return

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    main()
