#!/usr/bin/env python3
"""Render a first zkperf waveform from extracted DA51 sample shards."""

from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path
from typing import Any

import cbor2
import numpy as np

from render_trace_waveform import write_trace_outputs


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"


def _unwrap_tag(obj: Any) -> Any:
    return obj.value if isinstance(obj, cbor2.CBORTag) else obj


def _pairs_dict(component: dict[str, Any]) -> dict[str, str]:
    pairs = component.get("pairs", [])
    return {str(key): str(value) for key, value in pairs}


def _parse_opt_int(raw: str | None) -> int:
    if raw is None or raw == "None":
        return 0
    if raw.startswith("Some(") and raw.endswith(")"):
        return int(raw[5:-1])
    return int(raw)


def _cpu_mode_signal(raw: str | None) -> int:
    if raw == "Kernel":
        return -1
    if raw == "User":
        return 1
    return 0


def _sample_trace(shard_dir: Path) -> dict[str, Any]:
    sample_paths = sorted(shard_dir.glob("sample_*.cbor"))
    if not sample_paths:
        raise ValueError(f"no sample_*.cbor files found in {shard_dir}")

    sample_rows: list[dict[str, Any]] = []
    timestamps: list[int] = []
    family_counts = {family: len(list(shard_dir.glob(f"{family}_*.cbor"))) for family in ("sample", "mmap", "other", "schema")}

    for sample_path in sample_paths:
        obj = _unwrap_tag(cbor2.loads(sample_path.read_bytes()))
        component = obj.get("component", {})
        pairs = _pairs_dict(component)
        timestamp = _parse_opt_int(pairs.get("timestamp"))
        timestamps.append(timestamp)
        sample_rows.append(
            {
                "shard_id": obj.get("id", sample_path.stem),
                "cid": obj.get("cid"),
                "event": pairs.get("_event", ""),
                "idx": int(pairs.get("_idx", "0")),
                "timestamp": timestamp,
                "period": _parse_opt_int(pairs.get("period")),
                "pid": _parse_opt_int(pairs.get("pid")),
                "tid": _parse_opt_int(pairs.get("tid")),
                "cpu_mode": pairs.get("cpu_mode", ""),
            }
        )

    rows: list[list[float]] = []
    annotations: list[dict[str, Any]] = []
    prev_timestamp = timestamps[0]
    for row in sample_rows:
        ts_gap = row["timestamp"] - prev_timestamp
        prev_timestamp = row["timestamp"]
        period = row["period"]
        matrix_row = [
            float(row["idx"]),
            math.log10(period + 1.0) if period else 0.0,
            math.log10(abs(ts_gap) + 1.0) if ts_gap else 0.0,
            float(row["pid"]),
            float(row["tid"]),
            float(_cpu_mode_signal(row["cpu_mode"])),
        ]
        rows.append(matrix_row)
        annotations.append(
            {
                "step": row["idx"],
                "transition": row["event"] or row["shard_id"],
                "changed_register_count": 1,
                "changed_registers": ["sample"],
                "changed_register_mask": [True, True, True, True, True, True],
                "delta": matrix_row,
                "l1_step_delta": float(sum(abs(v) for v in matrix_row)),
                "state": None,
                "next_state": matrix_row,
                "cid": row["cid"],
                "cpu_mode": row["cpu_mode"],
                "timestamp": row["timestamp"],
                "period": row["period"],
            }
        )

    trace = {
        "matrix": np.asarray(rows, dtype=float),
        "register_labels": ["idx", "log10(period+1)", "log10(ts_gap+1)", "pid", "tid", "cpu_mode"],
        "step_annotations": annotations,
        "transition_names": [row["event"] or row["shard_id"] for row in sample_rows],
        "transition_colors": [],
        "cycle_start": None,
        "max_abs": max(abs(v) for row in rows for v in row) if rows else 1.0,
        "metadata": {
            "template_set": f"zkperf_samples:{shard_dir.name}",
            "artifact": str(shard_dir),
            "register_count": 6,
            "walk_status": "sample_trace",
            "steps": len(rows),
            "cycle_start": None,
            "final_state": rows[-1] if rows else [],
            "best_candidate": None,
            "regime_usage_by_slice": None,
            "shard_family_counts": family_counts,
        },
    }
    return trace


def _default_prefix(shard_dir: Path, output_prefix: str | None) -> Path:
    if output_prefix:
        return Path(output_prefix)
    return RESULTS / f"{date.today().isoformat()}-zkperf-{shard_dir.name}"


def _render_html_with_family_counts(html_path: Path, family_counts: dict[str, int]) -> None:
    html = html_path.read_text(encoding="utf-8")
    block = (
        '<div class="panel"><h2>Shard Families</h2><ul>'
        + "".join(f"<li><strong>{k}:</strong> <code>{v}</code></li>" for k, v in family_counts.items())
        + "</ul></div>"
    )
    html = html.replace("</body>", block + "\n</body>")
    html_path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a first zkperf waveform from extracted sample shards.")
    parser.add_argument("shard_dir", type=Path, help="Directory emitted by zkperf-schema extract")
    parser.add_argument("--output-prefix", help="Optional output prefix for .html/.png/.json")
    parser.add_argument("--title", help="Optional title override")
    args = parser.parse_args()

    trace = _sample_trace(args.shard_dir)
    title = args.title or f"zkperf Sample Waveform: {args.shard_dir.name}"
    prefix = _default_prefix(args.shard_dir, args.output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = prefix.with_name(prefix.name + ".trace-waveform.json")
    png_path, html_path = write_trace_outputs([trace], prefix, title)
    _render_html_with_family_counts(html_path, trace["metadata"]["shard_family_counts"])
    json_path.write_text(
        json.dumps(
            {
                "trace_kind": "zkperf_sample_trace",
                "source_dir": str(args.shard_dir),
                "register_labels": trace["register_labels"],
                "matrix": trace["matrix"].tolist(),
                "metadata": trace["metadata"],
                "step_annotations": trace["step_annotations"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"json": str(json_path), "png": str(png_path), "html": str(html_path)}, indent=2))


if __name__ == "__main__":
    main()
