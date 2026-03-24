#!/usr/bin/env python3
"""Render FRACDASH deterministic-walk waveforms as HTML and PNG artifacts."""

from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _template_from_path(path: Path) -> str | None:
    stem = path.stem
    marker = "-agdas-"
    if marker not in stem:
        return None
    tail = stem.split(marker, 1)[1]
    if tail.endswith("-phase2"):
        tail = tail[: -len("-phase2")]
    return tail.replace("-", "_")


def _auto_resolve_invariants(phase2: dict[str, Any]) -> Path | None:
    template = phase2.get("template_set") or _template_from_path(Path(str(phase2.get("_path", ""))))
    if not template:
        return None
    matches = sorted(RESULTS.glob(f"*-physics-invariants-{template}.json"))
    return matches[-1] if matches else None


def _hash_color(name: str) -> tuple[float, float, float, float]:
    code = sum((idx + 1) * ord(ch) for idx, ch in enumerate(name))
    hue = (code % 360) / 360.0
    sat = 0.55
    val = 0.90
    i = int(hue * 6.0)
    f = hue * 6.0 - i
    p = val * (1.0 - sat)
    q = val * (1.0 - f * sat)
    t = val * (1.0 - (1.0 - f) * sat)
    i %= 6
    rgb = (
        (val, t, p),
        (q, val, p),
        (p, val, t),
        (p, q, val),
        (t, p, val),
        (val, p, q),
    )[i]
    return (rgb[0], rgb[1], rgb[2], 1.0)


def _normalize_phase2_trace(phase2: dict[str, Any], invariants: dict[str, Any] | None) -> dict[str, Any]:
    walk = phase2.get("deterministic_walk")
    if not isinstance(walk, dict):
        raise ValueError("phase-2 artifact is missing deterministic_walk")
    path = walk.get("path")
    if not isinstance(path, list) or not path:
        raise ValueError("deterministic_walk.path is missing or empty")

    state_rows = walk.get("state_rows")
    register_labels = walk.get("register_labels")
    if isinstance(state_rows, list) and state_rows:
        rows = [[float(v) for v in row] for row in state_rows]
    else:
        first_state = path[0].get("state")
        if not isinstance(first_state, list) or not first_state:
            raise ValueError("deterministic_walk.path[0].state is missing or empty")
        rows = [[float(v) for v in first_state]]
        rows.extend([[float(v) for v in entry["next_state"]] for entry in path])
    if not isinstance(register_labels, list) or not register_labels:
        register_labels = [f"R{i}" for i in range(1, len(rows[0]) + 1)]

    step_annotations: list[dict[str, Any]] = []
    transition_names: list[str] = []
    transition_colors: list[tuple[float, float, float, float]] = []
    max_abs = max(abs(v) for row in rows for v in row) if rows else 1.0

    for idx, entry in enumerate(path, start=1):
        state = entry.get("state")
        next_state = entry.get("next_state")
        transition = str(entry.get("transition", ""))
        if not isinstance(state, list) or not isinstance(next_state, list):
            raise ValueError("deterministic_walk.path entries must contain state and next_state")
        delta = entry.get("delta")
        if not isinstance(delta, list):
            delta = [int(b - a) for a, b in zip(state, next_state)]
        changed_registers = entry.get("changed_registers")
        if not isinstance(changed_registers, list):
            changed_registers = [register_labels[i] for i, (a, b) in enumerate(zip(state, next_state)) if a != b]
        changed_count = entry.get("changed_register_count")
        if not isinstance(changed_count, int):
            changed_count = len(changed_registers)
        l1_delta = entry.get("l1_step_delta")
        if not isinstance(l1_delta, (int, float)):
            l1_delta = sum(abs(int(v)) for v in delta)
        step_annotations.append(
            {
                "step": int(entry.get("step", idx)),
                "transition": transition,
                "changed_register_count": changed_count,
                "changed_registers": changed_registers,
                "changed_register_mask": entry.get("changed_register_mask")
                or [label in changed_registers for label in register_labels],
                "delta": delta,
                "l1_step_delta": float(l1_delta),
                "state": state,
                "next_state": next_state,
                "action_rank_before": entry.get("action_rank_before"),
                "action_rank_after": entry.get("action_rank_after"),
                "state_counts_before": entry.get("state_counts_before"),
                "state_counts_after": entry.get("state_counts_after"),
            }
        )
        transition_names.append(transition)
        transition_colors.append(_hash_color(transition))

    template_set = phase2.get("template_set") or _template_from_path(Path(str(phase2.get("_path", "")))) or "unknown"
    metadata = {
        "template_set": template_set,
        "artifact": str(phase2.get("_path", "")),
        "register_count": len(register_labels),
        "walk_status": walk.get("status", "unknown"),
        "steps": int(walk.get("steps", len(path))),
        "cycle_start": walk.get("cycle_start"),
        "final_state": walk.get("final_state", rows[-1]),
        "best_candidate": None,
        "regime_usage_by_slice": None,
    }
    if invariants:
        best = invariants.get("best_candidate", {})
        if isinstance(best, dict):
            metadata["best_candidate"] = best.get("name")
        exec_status = invariants.get("execution_status", {})
        if isinstance(exec_status, dict):
            metadata["regime_usage_by_slice"] = exec_status.get("regime_usage_by_slice")

    return {
        "matrix": np.asarray(rows, dtype=float),
        "register_labels": register_labels,
        "step_annotations": step_annotations,
        "transition_names": transition_names,
        "transition_colors": transition_colors,
        "metadata": metadata,
        "cycle_start": metadata["cycle_start"],
        "max_abs": max_abs or 1.0,
    }


def render_trace_png(traces: list[dict[str, Any]], title: str) -> bytes:
    max_abs = max(max(1.0, float(trace["max_abs"])) for trace in traces)
    height_units = sum(max(3, trace["matrix"].shape[0] * 0.55) for trace in traces)
    fig = plt.figure(figsize=(max(10, max(trace["matrix"].shape[1] * 1.2 for trace in traces)), 2.0 + height_units))
    grid = fig.add_gridspec(nrows=len(traces) * 3, ncols=1, height_ratios=sum(([8, 0.6, 0.8] for _ in traces), []), hspace=0.45)
    fig.suptitle(title, fontsize=14)

    for index, trace in enumerate(traces):
        row = index * 3
        ax_heat = fig.add_subplot(grid[row, 0])
        ax_transition = fig.add_subplot(grid[row + 1, 0], sharex=ax_heat)
        ax_scalar = fig.add_subplot(grid[row + 2, 0], sharex=ax_heat)

        matrix = trace["matrix"]
        steps = trace["step_annotations"]
        transition_names = trace["transition_names"]
        transition_colors = trace["transition_colors"]
        metadata = trace["metadata"]
        cycle_start = trace["cycle_start"]
        changed = [step["changed_register_count"] for step in steps] or [0]
        l1_delta = [step["l1_step_delta"] for step in steps] or [0.0]

        im = ax_heat.imshow(matrix, aspect="auto", interpolation="nearest", cmap="coolwarm", vmin=-max_abs, vmax=max_abs)
        ax_heat.set_title(f"{metadata['template_set']} ({metadata['walk_status']})", loc="left", fontsize=11)
        ax_heat.set_ylabel("Step")
        ax_heat.set_xticks(np.arange(matrix.shape[1]))
        ax_heat.set_xticklabels(trace["register_labels"])
        ax_heat.set_yticks(np.arange(matrix.shape[0]))
        ax_heat.set_yticklabels([str(i) for i in range(matrix.shape[0])], fontsize=8)
        if cycle_start is not None:
            ax_heat.axhline(float(cycle_start) - 0.5, color="black", linestyle="--", linewidth=1.1)
            ax_heat.text(
                matrix.shape[1] - 0.4,
                float(cycle_start) - 0.7,
                f"cycle_start={cycle_start}",
                ha="right",
                va="bottom",
                fontsize=8,
                color="black",
                bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "none"},
            )
        cbar = fig.colorbar(im, ax=ax_heat, fraction=0.025, pad=0.02)
        cbar.set_label("Value")

        if transition_colors:
            ax_transition.imshow(np.asarray([transition_colors], dtype=float), aspect="auto", interpolation="nearest")
        else:
            ax_transition.imshow(np.zeros((1, 1, 4)), aspect="auto")
        ax_transition.set_yticks([])
        ax_transition.set_ylabel("Transition", rotation=0, ha="right", va="center")
        ax_transition.set_xticks(np.arange(len(transition_names)))
        ax_transition.set_xticklabels([str(step["step"]) for step in steps], fontsize=8)

        scalar_img = np.vstack([changed, l1_delta]).astype(float)
        ax_scalar.imshow(scalar_img, aspect="auto", interpolation="nearest", cmap="Blues")
        ax_scalar.set_yticks([0, 1])
        ax_scalar.set_yticklabels(["changed", "l1"], fontsize=8)
        ax_scalar.set_xticks(np.arange(len(transition_names)))
        ax_scalar.set_xticklabels([str(step["step"]) for step in steps], fontsize=8)
        ax_scalar.set_xlabel("Transition step")

        summary = [
            f"registers={metadata['register_count']}",
            f"steps={metadata['steps']}",
            f"best={metadata['best_candidate'] or '-'}",
        ]
        if metadata["regime_usage_by_slice"]:
            summary.append(f"regime={metadata['regime_usage_by_slice']}")
        ax_scalar.text(1.01, 0.5, "\n".join(summary), transform=ax_scalar.transAxes, va="center", fontsize=8)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _step_table(trace: dict[str, Any]) -> str:
    rows = []
    for step in trace["step_annotations"]:
        rows.append(
            "<tr>"
            f"<td>{step['step']}</td>"
            f"<td>{step['transition']}</td>"
            f"<td>{step['changed_register_count']}</td>"
            f"<td>{step['l1_step_delta']:.1f}</td>"
            f"<td><code>{step['changed_registers']}</code></td>"
            f"<td><code>{step['state']}</code></td>"
            f"<td><code>{step['next_state']}</code></td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_trace_html(traces: list[dict[str, Any]], png_bytes: bytes, title: str) -> str:
    img_b64 = base64.b64encode(png_bytes).decode("ascii")
    blocks = []
    for trace in traces:
        meta = trace["metadata"]
        items = [
            ("Template", meta["template_set"]),
            ("Walk Status", meta["walk_status"]),
            ("Steps", meta["steps"]),
            ("Registers", meta["register_count"]),
            ("Cycle Start", meta["cycle_start"]),
            ("Best Candidate", meta["best_candidate"] or "-"),
            ("Final State", meta["final_state"]),
        ]
        if meta["regime_usage_by_slice"]:
            items.append(("Regime Usage", meta["regime_usage_by_slice"]))
        meta_html = "\n".join(f"<li><strong>{k}:</strong> <code>{v}</code></li>" for k, v in items)
        blocks.append(
            f"""
            <div class="panel">
              <h2>{meta['template_set']}</h2>
              <ul>{meta_html}</ul>
              <table>
                <thead>
                  <tr>
                    <th>Step</th><th>Transition</th><th>Changed</th><th>L1 Delta</th><th>Changed Registers</th><th>State</th><th>Next State</th>
                  </tr>
                </thead>
                <tbody>
                  {_step_table(trace)}
                </tbody>
              </table>
            </div>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin: 24px; color: #1f2937; background: #f8fafc; }}
    h1 {{ margin-bottom: 0.3rem; }}
    .panel {{ background: white; border: 1px solid #dbe4ee; border-radius: 8px; padding: 16px; margin-bottom: 18px; }}
    img {{ max-width: 100%; border: 1px solid #dbe4ee; border-radius: 8px; background: white; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ border: 1px solid #dbe4ee; padding: 6px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #eff6ff; }}
    code {{ white-space: pre-wrap; word-break: break-word; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="panel">
    <p>Rows are time steps, columns are registers. Dashed lines mark cycle starts. Middle strips show transition families; bottom strips show changed-register count and L1 step delta.</p>
    <p><img alt="Trace waveform" src="data:image/png;base64,{img_b64}"></p>
  </div>
  {''.join(blocks)}
</body>
</html>
"""


def write_trace_outputs(traces: list[dict[str, Any]], prefix: Path, title: str) -> tuple[Path, Path]:
    png_path = prefix.with_name(prefix.name + ".trace-waveform.png")
    html_path = prefix.with_name(prefix.name + ".trace-waveform.html")
    png_bytes = render_trace_png(traces, title)
    png_path.write_bytes(png_bytes)
    html_path.write_text(render_trace_html(traces, png_bytes, title), encoding="utf-8")
    return png_path, html_path


def _default_prefix(paths: list[Path], output_prefix: str | None) -> Path:
    if output_prefix:
        return Path(output_prefix)
    first = paths[0].with_suffix("")
    if len(paths) == 1:
        return first
    return first.with_name(first.name + ".compare")


def _load_phase2_trace(path: Path, invariant_path: Path | None) -> tuple[dict[str, Any], Path | None]:
    phase2 = _load_json(path)
    phase2["_path"] = str(path)
    resolved_invariant = invariant_path or _auto_resolve_invariants(phase2)
    invariants = _load_json(resolved_invariant) if resolved_invariant else None
    return _normalize_phase2_trace(phase2, invariants), resolved_invariant


def main() -> None:
    parser = argparse.ArgumentParser(description="Render one or more FRACDASH deterministic-walk waveforms.")
    parser.add_argument("phase2_artifacts", type=Path, nargs="+", help="One or more phase-2 JSON artifacts")
    parser.add_argument("--invariants", type=Path, help="Optional invariant artifact for single-run mode")
    parser.add_argument("--output-prefix", help="Optional output prefix for .html/.png")
    parser.add_argument("--title", help="Optional title override")
    args = parser.parse_args()

    if args.invariants and len(args.phase2_artifacts) > 1:
        raise SystemExit("--invariants is only supported in single-run mode")

    traces: list[dict[str, Any]] = []
    invariant_paths: list[str | None] = []
    for idx, phase2_path in enumerate(args.phase2_artifacts):
        invariant_path = args.invariants if idx == 0 else None
        trace, resolved_invariant = _load_phase2_trace(phase2_path, invariant_path)
        traces.append(trace)
        invariant_paths.append(str(resolved_invariant) if resolved_invariant else None)

    title = args.title or (
        f"Trace Waveform Compare: {', '.join(trace['metadata']['template_set'] for trace in traces)}"
        if len(traces) > 1
        else f"Trace Waveform: {traces[0]['metadata']['template_set']}"
    )
    prefix = _default_prefix(args.phase2_artifacts, args.output_prefix)
    png_path, html_path = write_trace_outputs(traces, prefix, title)
    print(json.dumps({"png": str(png_path), "html": str(html_path), "invariants": invariant_paths}, indent=2))


if __name__ == "__main__":
    main()
