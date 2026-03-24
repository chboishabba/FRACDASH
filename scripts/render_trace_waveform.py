#!/usr/bin/env python3
"""Render a deterministic-walk waveform from a saved phase-2 artifact."""

from __future__ import annotations

import argparse
import base64
import io
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap


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


def _output_prefix(input_path: Path, output_prefix: str | None) -> Path:
    if output_prefix:
        return Path(output_prefix)
    return input_path.with_suffix("")


def _hash_color(name: str) -> tuple[float, float, float, float]:
    # Stable categorical color from transition name without extra deps.
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


def _build_trace_model(phase2: dict[str, Any], invariants: dict[str, Any] | None) -> dict[str, Any]:
    walk = phase2.get("deterministic_walk")
    if not isinstance(walk, dict):
        raise ValueError("phase-2 artifact is missing deterministic_walk")
    path = walk.get("path")
    if not isinstance(path, list) or not path:
        raise ValueError("deterministic_walk.path is missing or empty")

    first_state = path[0].get("state")
    if not isinstance(first_state, list) or not first_state:
        raise ValueError("deterministic_walk.path[0].state is missing or empty")

    state_rows: list[list[float]] = [list(first_state)]
    step_annotations: list[dict[str, Any]] = []
    transition_names: list[str] = []
    transition_colors: list[tuple[float, float, float, float]] = []
    max_abs = max(abs(float(v)) for v in first_state)

    for entry in path:
        state = entry.get("state")
        next_state = entry.get("next_state")
        transition = str(entry.get("transition", ""))
        if not isinstance(state, list) or not isinstance(next_state, list):
            raise ValueError("deterministic_walk.path entries must contain state and next_state")
        changed = sum(1 for a, b in zip(state, next_state) if a != b)
        l1_delta = sum(abs(float(b) - float(a)) for a, b in zip(state, next_state))
        max_abs = max(max_abs, max(abs(float(v)) for v in state), max(abs(float(v)) for v in next_state))
        state_rows.append(list(next_state))
        step_annotations.append(
            {
                "step": int(entry.get("step", len(step_annotations) + 1)),
                "transition": transition,
                "changed_register_count": changed,
                "l1_step_delta": l1_delta,
                "state": state,
                "next_state": next_state,
            }
        )
        transition_names.append(transition)
        transition_colors.append(_hash_color(transition))

    register_count = len(first_state)
    register_labels = [f"R{i}" for i in range(1, register_count + 1)]
    matrix = np.asarray(state_rows, dtype=float)
    cycle_start = walk.get("cycle_start")
    final_state = walk.get("final_state", state_rows[-1])
    template_set = phase2.get("template_set") or _template_from_path(Path(str(phase2.get("_path", "")))) or "unknown"
    metadata = {
        "template_set": template_set,
        "artifact": str(phase2.get("_path", "")),
        "register_count": register_count,
        "walk_status": walk.get("status", "unknown"),
        "steps": int(walk.get("steps", len(path))),
        "cycle_start": cycle_start,
        "final_state": final_state,
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
        "matrix": matrix,
        "register_labels": register_labels,
        "step_annotations": step_annotations,
        "transition_names": transition_names,
        "transition_colors": transition_colors,
        "metadata": metadata,
        "cycle_start": cycle_start,
        "max_abs": max_abs or 1.0,
    }


def _render_png(trace: dict[str, Any], title: str) -> bytes:
    matrix = trace["matrix"]
    cycle_start = trace["cycle_start"]
    transition_names = trace["transition_names"]
    transition_colors = trace["transition_colors"]
    steps = trace["step_annotations"]
    metadata = trace["metadata"]
    max_abs = max(1.0, float(trace["max_abs"]))
    changed = [step["changed_register_count"] for step in steps] or [0]
    l1_delta = [step["l1_step_delta"] for step in steps] or [0.0]

    fig = plt.figure(figsize=(max(10, matrix.shape[1] * 1.2), max(6, matrix.shape[0] * 0.75)))
    grid = fig.add_gridspec(nrows=3, ncols=1, height_ratios=[8, 0.6, 0.8], hspace=0.25)
    ax_heat = fig.add_subplot(grid[0, 0])
    ax_transition = fig.add_subplot(grid[1, 0], sharex=ax_heat)
    ax_scalar = fig.add_subplot(grid[2, 0], sharex=ax_heat)

    im = ax_heat.imshow(matrix, aspect="auto", interpolation="nearest", cmap="coolwarm", vmin=-max_abs, vmax=max_abs)
    ax_heat.set_title(title)
    ax_heat.set_xlabel("Register")
    ax_heat.set_ylabel("Step")
    ax_heat.set_xticks(np.arange(matrix.shape[1]))
    ax_heat.set_xticklabels(trace["register_labels"])
    ax_heat.set_yticks(np.arange(matrix.shape[0]))
    ax_heat.set_yticklabels([str(i) for i in range(matrix.shape[0])])
    if cycle_start is not None:
        ax_heat.axhline(float(cycle_start) - 0.5, color="black", linestyle="--", linewidth=1.2)
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
    cbar.set_label("Register value")

    if transition_colors:
        transition_rgba = np.asarray([transition_colors], dtype=float)
        ax_transition.imshow(transition_rgba, aspect="auto", interpolation="nearest")
    else:
        ax_transition.imshow(np.zeros((1, 1, 4)), aspect="auto")
    ax_transition.set_yticks([])
    ax_transition.set_ylabel("Transition", rotation=0, ha="right", va="center")
    ax_transition.set_xticks(np.arange(len(transition_names)))
    ax_transition.set_xticklabels([str(step["step"]) for step in steps], rotation=0, fontsize=8)

    scalar_img = np.vstack([changed, l1_delta]).astype(float)
    ax_scalar.imshow(scalar_img, aspect="auto", interpolation="nearest", cmap=ListedColormap(["#e8f1fb", "#6baed6", "#08306b"]))
    ax_scalar.set_yticks([0, 1])
    ax_scalar.set_yticklabels(["changed", "l1"])
    ax_scalar.set_xticks(np.arange(len(transition_names)))
    ax_scalar.set_xticklabels([str(step["step"]) for step in steps], fontsize=8)
    ax_scalar.set_xlabel("Transition step")

    summary_lines = [
        f"template={metadata['template_set']}  status={metadata['walk_status']}  steps={metadata['steps']}  registers={metadata['register_count']}",
        f"cycle_start={metadata['cycle_start']}  best_candidate={metadata['best_candidate'] or '-'}",
    ]
    if metadata["regime_usage_by_slice"]:
        summary_lines.append(f"regime_usage={metadata['regime_usage_by_slice']}")
    fig.text(0.01, 0.01, "\n".join(summary_lines), fontsize=9, ha="left", va="bottom")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _html_table_rows(trace: dict[str, Any]) -> str:
    rows = []
    for step in trace["step_annotations"]:
        rows.append(
            "<tr>"
            f"<td>{step['step']}</td>"
            f"<td>{step['transition']}</td>"
            f"<td>{step['changed_register_count']}</td>"
            f"<td>{step['l1_step_delta']:.1f}</td>"
            f"<td><code>{step['state']}</code></td>"
            f"<td><code>{step['next_state']}</code></td>"
            "</tr>"
        )
    return "\n".join(rows)


def _render_html(trace: dict[str, Any], png_bytes: bytes, title: str) -> str:
    metadata = trace["metadata"]
    img_b64 = base64.b64encode(png_bytes).decode("ascii")
    meta_items = [
        ("Template", metadata["template_set"]),
        ("Walk Status", metadata["walk_status"]),
        ("Steps", metadata["steps"]),
        ("Registers", metadata["register_count"]),
        ("Cycle Start", metadata["cycle_start"]),
        ("Best Candidate", metadata["best_candidate"] or "-"),
        ("Final State", metadata["final_state"]),
    ]
    if metadata["regime_usage_by_slice"]:
        meta_items.append(("Regime Usage", metadata["regime_usage_by_slice"]))
    meta_html = "\n".join(f"<li><strong>{label}:</strong> <code>{value}</code></li>" for label, value in meta_items)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin: 24px; color: #1f2937; background: #f8fafc; }}
    h1 {{ margin-bottom: 0.3rem; }}
    .meta {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
    .panel {{ background: white; border: 1px solid #dbe4ee; border-radius: 8px; padding: 16px; }}
    img {{ max-width: 100%; border: 1px solid #dbe4ee; border-radius: 8px; background: white; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border: 1px solid #dbe4ee; padding: 6px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #eff6ff; }}
    code {{ white-space: pre-wrap; word-break: break-word; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="meta">
    <div class="panel">
      <h2>Summary</h2>
      <ul>
        {meta_html}
      </ul>
    </div>
    <div class="panel">
      <h2>Legend</h2>
      <p>Main panel: signed register values over time. Dashed horizontal line marks the cycle start when present.</p>
      <p>Middle strip: transition family by step. Bottom strip: changed-register count and L1 step delta.</p>
    </div>
  </div>
  <p><img alt="Trace waveform" src="data:image/png;base64,{img_b64}"></p>
  <div class="panel">
    <h2>Step Table</h2>
    <table>
      <thead>
        <tr>
          <th>Step</th>
          <th>Transition</th>
          <th>Changed</th>
          <th>L1 Delta</th>
          <th>State</th>
          <th>Next State</th>
        </tr>
      </thead>
      <tbody>
        {_html_table_rows(trace)}
      </tbody>
    </table>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a deterministic-walk waveform from a phase-2 artifact.")
    parser.add_argument("phase2_artifact", type=Path, help="Path to a phase-2 JSON artifact")
    parser.add_argument("--invariants", type=Path, help="Optional matching invariant artifact")
    parser.add_argument("--output-prefix", help="Optional output prefix for .html/.png")
    parser.add_argument("--title", help="Optional title override")
    args = parser.parse_args()

    phase2 = _load_json(args.phase2_artifact)
    phase2["_path"] = str(args.phase2_artifact)
    invariant_path = args.invariants or _auto_resolve_invariants(phase2)
    invariants = _load_json(invariant_path) if invariant_path else None

    trace = _build_trace_model(phase2, invariants)
    title = args.title or f"Trace Waveform: {trace['metadata']['template_set']}"
    prefix = _output_prefix(args.phase2_artifact, args.output_prefix)
    png_path = prefix.with_name(prefix.name + ".trace-waveform.png")
    html_path = prefix.with_name(prefix.name + ".trace-waveform.html")

    png_bytes = _render_png(trace, title)
    png_path.write_bytes(png_bytes)
    html_path.write_text(_render_html(trace, png_bytes, title), encoding="utf-8")

    print(json.dumps({"png": str(png_path), "html": str(html_path), "invariants": str(invariant_path) if invariant_path else None}, indent=2))


if __name__ == "__main__":
    main()
