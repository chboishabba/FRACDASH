#!/usr/bin/env python3
"""Normalize and compact dashi_agda perf summary artifacts."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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


def _bucket(value: int) -> str:
    if value < 25_000_000:
        return "xs"
    if value < 35_000_000:
        return "s"
    if value < 45_000_000:
        return "m"
    if value < 60_000_000:
        return "l"
    return "xl"


def normalize_summary(summary: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(summary, start=1):
        file_name = str(item["file"])
        module_name = _module_name(file_name)
        dashi_class, dashi_family = _dashi_semantics(module_name)
        cycles = int(item["cycles"])
        instructions = int(item["instructions"])
        cache_misses = int(item["cache-misses"])
        branch_misses = int(item["branch-misses"])
        total_misses = cache_misses + branch_misses
        rows.append(
            {
                "step": index,
                "file": file_name,
                "module": module_name,
                "src_sha256": str(item["src_sha256"]),
                "cycles": cycles,
                "instructions": instructions,
                "cache_misses": cache_misses,
                "branch_misses": branch_misses,
                "total_misses": total_misses,
                "cache_per_kilo_instr": round(cache_misses * 1000.0 / max(instructions, 1), 6),
                "branch_per_kilo_instr": round(branch_misses * 1000.0 / max(instructions, 1), 6),
                "cycles_bucket": _bucket(cycles),
                "instructions_bucket": _bucket(instructions),
                "miss_bucket": _bucket(total_misses * 100),
                "dashi_class": dashi_class,
                "dashi_family": dashi_family,
            }
        )
    return {
        "trace_kind": "dashi_perf_summary_normalized/v1",
        "source_kind": "dashi_agda_da51_summary",
        "rows": rows,
    }


def encode_compact(normalized: dict[str, Any]) -> dict[str, Any]:
    if normalized.get("trace_kind") != "dashi_perf_summary_normalized/v1":
        raise ValueError(f"unsupported trace_kind: {normalized.get('trace_kind')!r}")

    rows = []
    for row in normalized.get("rows", []):
        rows.append(
            {
                "step": int(row["step"]),
                "file": row["file"],
                "src_sha256": row["src_sha256"],
                "cycles": int(row["cycles"]),
                "instructions": int(row["instructions"]),
                "cache_misses": int(row["cache_misses"]),
                "branch_misses": int(row["branch_misses"]),
                "dashi_class": row["dashi_class"],
                "dashi_family": row["dashi_family"],
            }
        )
    return {
        "trace_kind": "dashi_perf_summary_compact/v1",
        "source_kind": normalized.get("source_kind"),
        "rows": rows,
    }


def decode_compact(compact: dict[str, Any]) -> dict[str, Any]:
    if compact.get("trace_kind") != "dashi_perf_summary_compact/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")

    rows = []
    for row in compact.get("rows", []):
        cycles = int(row["cycles"])
        instructions = int(row["instructions"])
        cache_misses = int(row["cache_misses"])
        branch_misses = int(row["branch_misses"])
        total_misses = cache_misses + branch_misses
        rows.append(
            {
                "step": int(row["step"]),
                "file": row["file"],
                "module": _module_name(str(row["file"])),
                "src_sha256": row["src_sha256"],
                "cycles": cycles,
                "instructions": instructions,
                "cache_misses": cache_misses,
                "branch_misses": branch_misses,
                "total_misses": total_misses,
                "cache_per_kilo_instr": round(cache_misses * 1000.0 / max(instructions, 1), 6),
                "branch_per_kilo_instr": round(branch_misses * 1000.0 / max(instructions, 1), 6),
                "cycles_bucket": _bucket(cycles),
                "instructions_bucket": _bucket(instructions),
                "miss_bucket": _bucket(total_misses * 100),
                "dashi_class": row["dashi_class"],
                "dashi_family": row["dashi_family"],
            }
        )
    return {
        "trace_kind": "dashi_perf_summary_normalized/v1",
        "source_kind": compact.get("source_kind"),
        "rows": rows,
    }


def encode_surface_motif(compact: dict[str, Any]) -> dict[str, Any]:
    if compact.get("trace_kind") != "dashi_perf_summary_compact/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")

    motifs: list[dict[str, Any]] = []
    motif_to_index: dict[tuple[str, str, str], int] = {}
    rows: list[dict[str, Any]] = []

    for row in compact.get("rows", []):
        motif_key = (
            _bucket(int(row["cycles"])),
            _bucket(int(row["instructions"])),
            _bucket((int(row["cache_misses"]) + int(row["branch_misses"])) * 100),
        )
        motif_index = motif_to_index.setdefault(motif_key, len(motifs))
        if motif_index == len(motifs):
            cycles_bucket, instructions_bucket, miss_bucket = motif_key
            motifs.append(
                {
                    "cycles_bucket": cycles_bucket,
                    "instructions_bucket": instructions_bucket,
                    "miss_bucket": miss_bucket,
                }
            )
        rows.append(
            {
                "step": int(row["step"]),
                "file": row["file"],
                "src_sha256": row["src_sha256"],
                "cycles": int(row["cycles"]),
                "instructions": int(row["instructions"]),
                "cache_misses": int(row["cache_misses"]),
                "branch_misses": int(row["branch_misses"]),
                "dashi_class": row["dashi_class"],
                "dashi_family": row["dashi_family"],
                "motif_idx": motif_index,
            }
        )

    return {
        "trace_kind": "dashi_perf_summary_surface_motif/v1",
        "source_kind": compact.get("source_kind"),
        "motifs": motifs,
        "rows": rows,
    }


def decode_surface_motif(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("trace_kind") != "dashi_perf_summary_surface_motif/v1":
        raise ValueError(f"unsupported trace_kind: {payload.get('trace_kind')!r}")
    return {
        "trace_kind": "dashi_perf_summary_compact/v1",
        "source_kind": payload.get("source_kind"),
        "rows": [
            {
                "step": int(row["step"]),
                "file": row["file"],
                "src_sha256": row["src_sha256"],
                "cycles": int(row["cycles"]),
                "instructions": int(row["instructions"]),
                "cache_misses": int(row["cache_misses"]),
                "branch_misses": int(row["branch_misses"]),
                "dashi_class": row["dashi_class"],
                "dashi_family": row["dashi_family"],
            }
            for row in payload.get("rows", [])
        ],
    }


def encode_semantic_motif(compact: dict[str, Any]) -> dict[str, Any]:
    if compact.get("trace_kind") != "dashi_perf_summary_compact/v1":
        raise ValueError(f"unsupported trace_kind: {compact.get('trace_kind')!r}")

    motifs: list[dict[str, Any]] = []
    motif_to_index: dict[tuple[str, str], int] = {}
    rows: list[dict[str, Any]] = []

    for row in compact.get("rows", []):
        motif_key = (str(row["dashi_class"]), str(row["dashi_family"]))
        motif_index = motif_to_index.setdefault(motif_key, len(motifs))
        if motif_index == len(motifs):
            dashi_class, dashi_family = motif_key
            motifs.append({"dashi_class": dashi_class, "dashi_family": dashi_family})
        rows.append(
            {
                "step": int(row["step"]),
                "file": row["file"],
                "src_sha256": row["src_sha256"],
                "cycles": int(row["cycles"]),
                "instructions": int(row["instructions"]),
                "cache_misses": int(row["cache_misses"]),
                "branch_misses": int(row["branch_misses"]),
                "motif_idx": motif_index,
            }
        )

    return {
        "trace_kind": "dashi_perf_summary_semantic_motif/v1",
        "source_kind": compact.get("source_kind"),
        "motifs": motifs,
        "rows": rows,
    }


def decode_semantic_motif(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("trace_kind") != "dashi_perf_summary_semantic_motif/v1":
        raise ValueError(f"unsupported trace_kind: {payload.get('trace_kind')!r}")

    motifs = payload.get("motifs", [])
    rows = []
    for row in payload.get("rows", []):
        motif = motifs[int(row["motif_idx"])]
        rows.append(
            {
                "step": int(row["step"]),
                "file": row["file"],
                "src_sha256": row["src_sha256"],
                "cycles": int(row["cycles"]),
                "instructions": int(row["instructions"]),
                "cache_misses": int(row["cache_misses"]),
                "branch_misses": int(row["branch_misses"]),
                "dashi_class": motif["dashi_class"],
                "dashi_family": motif["dashi_family"],
            }
        )
    return {
        "trace_kind": "dashi_perf_summary_compact/v1",
        "source_kind": payload.get("source_kind"),
        "rows": rows,
    }


def stats_compare(summary_path: Path, normalized_path: Path, compact_path: Path, surface_path: Path, semantic_path: Path) -> dict[str, Any]:
    summary = load_json(summary_path)
    normalized = normalize_summary(summary)
    write_json(normalized_path, normalized)
    compact = encode_compact(normalized)
    write_json(compact_path, compact)
    surface = encode_surface_motif(compact)
    write_json(surface_path, surface)
    semantic = encode_semantic_motif(compact)
    write_json(semantic_path, semantic)
    return {
        "raw": str(summary_path),
        "normalized": {"path": str(normalized_path), "bytes": normalized_path.stat().st_size, "rows": len(normalized["rows"])},
        "compact": {"path": str(compact_path), "bytes": compact_path.stat().st_size},
        "surface_motif": {"path": str(surface_path), "bytes": surface_path.stat().st_size, "motif_count": len(surface["motifs"])},
        "semantic_motif": {"path": str(semantic_path), "bytes": semantic_path.stat().st_size, "motif_count": len(semantic["motifs"])},
        "raw_bytes": summary_path.stat().st_size,
        "compact_gain_over_normalized": normalized_path.stat().st_size - compact_path.stat().st_size,
        "surface_motif_gain_over_compact": compact_path.stat().st_size - surface_path.stat().st_size,
        "semantic_motif_gain_over_compact": compact_path.stat().st_size - semantic_path.stat().st_size,
        "semantic_minus_surface_bytes": surface_path.stat().st_size - semantic_path.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize and compact dashi_agda perf summary artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser("normalize", help="Normalize dashi_agda summary.json into a richer analysis contract")
    normalize_parser.add_argument("input", type=Path)
    normalize_parser.add_argument("output", type=Path)

    compare_parser = subparsers.add_parser("stats-compare", help="Normalize and compare compact, surface motif, and semantic motif layers")
    compare_parser.add_argument("input", type=Path)
    compare_parser.add_argument("normalized_output", type=Path)
    compare_parser.add_argument("compact_output", type=Path)
    compare_parser.add_argument("surface_motif_output", type=Path)
    compare_parser.add_argument("semantic_motif_output", type=Path)

    args = parser.parse_args()

    if args.command == "normalize":
        write_json(args.output, normalize_summary(load_json(args.input)))
        return

    if args.command == "stats-compare":
        print(
            json.dumps(
                stats_compare(
                    args.input,
                    args.normalized_output,
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
