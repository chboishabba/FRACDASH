#!/usr/bin/env python3
"""Render FRACDASH walk waveforms and rank-4 branch-density views."""

from __future__ import annotations

import argparse
import base64
import io
import json
from itertools import product
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "benchmarks" / "results"
STATE_NAME_BY_VALUE = {-1: "negative", 0: "zero", 1: "positive"}
STATE_ORDER = ("negative", "zero", "positive")


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


def _default_prefix(paths: list[Path], output_prefix: str | None, suffix: str = "") -> Path:
    if output_prefix:
        return Path(output_prefix)
    first = paths[0].with_suffix("")
    if len(paths) == 1:
        base = first
    else:
        base = first.with_name(first.name + ".compare")
    return base.with_name(base.name + suffix) if suffix else base


def _load_phase2_trace(path: Path, invariant_path: Path | None) -> tuple[dict[str, Any], Path | None]:
    phase2 = _load_json(path)
    phase2["_path"] = str(path)
    resolved_invariant = invariant_path or _auto_resolve_invariants(phase2)
    invariants = _load_json(resolved_invariant) if resolved_invariant else None
    return _normalize_phase2_trace(phase2, invariants), resolved_invariant


def _register_names(count: int) -> list[str]:
    return [f"R{idx + 1}" for idx in range(count)]


def _matches(state: tuple[int, ...], transition: dict[str, Any], register_count: int) -> bool:
    names = _register_names(register_count)
    for register, required in transition.get("condition", {}).items():
        if register not in names:
            return False
        idx = names.index(register)
        value = state[idx]
        if STATE_NAME_BY_VALUE[value] != required:
            return False
    return True


def _apply(state: tuple[int, ...], transition: dict[str, Any], register_count: int) -> tuple[int, ...]:
    names = _register_names(register_count)
    next_state = list(state)
    for register, target in transition.get("action", {}).items():
        if register not in names:
            continue
        idx = names.index(register)
        next_state[idx] = {"negative": -1, "zero": 0, "positive": 1}[target]
    return tuple(next_state)


def _build_transition_list(physics_artifact: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    transitions = physics_artifact.get("transitions")
    register_count = int(physics_artifact.get("register_count", 0))
    if not isinstance(transitions, list) or register_count <= 0:
        raise ValueError("physics artifact missing transition list/register_count")
    normalized: list[dict[str, Any]] = []
    for item in transitions:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "name": str(item.get("name", "unnamed_transition")),
                "condition": dict(item.get("condition", {})),
                "action": dict(item.get("action", {})),
            }
        )
    if not normalized:
        raise ValueError("no transitions found in physics artifact")
    return normalized, register_count


def _deterministic_successor(
    state: tuple[int, ...], transitions: list[dict[str, Any]], register_count: int
) -> tuple[tuple[int, ...] | None, str | None]:
    for transition in transitions:
        if _matches(state, transition, register_count):
            return _apply(state, transition, register_count), transition["name"]
    return None, None


def _state_to_godel_value(state: tuple[int, ...], register_specs: list[dict[str, Any]]) -> int:
    value = 1
    for idx, entry in enumerate(register_specs):
        signed = int(state[idx])
        if signed == -1:
            prime = int(entry["negative"])
        elif signed == 0:
            prime = int(entry["zero"])
        else:
            prime = int(entry["positive"])
        value *= prime
    return value


def _q_sector_id(n_value: int) -> int:
    return ((n_value % 71) + (n_value % 59) + (n_value % 47)) % 10


def _project_state(state: tuple[int, ...], width: int) -> tuple[int, ...]:
    return tuple(int(v) for v in state[:width])


def _load_rank4_graph(rank4_path: Path) -> dict[str, Any]:
    rank4 = _load_json(rank4_path)
    canonical_name = rank4.get("canonical_derivation")
    derivations = rank4.get("derivations")
    if isinstance(derivations, dict) and isinstance(canonical_name, str) and canonical_name in derivations:
        canonical = derivations[canonical_name]
    else:
        canonical = rank4
    source = rank4.get("source_artifacts", {})
    physics_ref = source.get("physics_artifact")
    if not isinstance(physics_ref, str):
        raise ValueError("rank4 dataset missing source_artifacts.physics_artifact")
    physics_path = ROOT / physics_ref
    physics_artifact = _load_json(physics_path)
    register_specs = canonical.get("prime_layout_registers") or rank4.get("prime_layout_registers")
    if not isinstance(register_specs, list) or not register_specs:
        raise ValueError("rank4 dataset missing prime_layout_registers")
    transitions, register_count = _build_transition_list(physics_artifact)
    return {
        "dataset": rank4,
        "canonical": canonical,
        "physics_artifact": physics_artifact,
        "register_specs": register_specs,
        "register_count": register_count,
        "transitions": transitions,
        "canonical_name": canonical_name or "legacy",
    }


def _build_branch_density_payload(
    rank4_path: Path, phase2_path: Path | None, density_mode: str, panels: str
) -> dict[str, Any]:
    graph = _load_rank4_graph(rank4_path)
    canonical = graph["canonical"]
    register_specs = graph["register_specs"]
    project_width = len(register_specs)
    transitions = graph["transitions"]
    register_count = int(graph["register_count"])
    full_states = [tuple(int(v) for v in state) for state in product((-1, 0, 1), repeat=register_count)]
    projected_states = [tuple(int(v) for v in state) for state in product((-1, 0, 1), repeat=project_width)]

    sector_by_proj = {_project_state(state, project_width): _q_sector_id(_state_to_godel_value(_project_state(state, project_width), register_specs)) for state in projected_states}
    ordered_states = sorted(projected_states, key=lambda s: (sector_by_proj[s], s))
    x_index = {state: idx for idx, state in enumerate(ordered_states)}

    out_counts = {state: 0 for state in ordered_states}
    in_counts = {state: 0 for state in ordered_states}
    cross_counts = {state: 0 for state in ordered_states}
    transfer_counts = {state: 0 for state in ordered_states}

    for state in full_states:
        src_proj = _project_state(state, project_width)
        nxt, _name = _deterministic_successor(state, transitions, register_count)
        if nxt is None:
            continue
        dst_proj = _project_state(nxt, project_width)
        out_counts[src_proj] += 1
        in_counts[dst_proj] += 1
        transfer_counts[src_proj] += 1
        if sector_by_proj[src_proj] != sector_by_proj[dst_proj]:
            cross_counts[src_proj] += 1

    if density_mode == "visit":
        base_graph_score = {state: 0.0 for state in ordered_states}
    elif density_mode == "hybrid":
        base_graph_score = {
            state: float(0.5 * (out_counts[state] + in_counts[state]) + 1.5 * cross_counts[state]) for state in ordered_states
        }
    else:
        base_graph_score = {
            state: float(out_counts[state] + in_counts[state] + 2 * cross_counts[state]) for state in ordered_states
        }

    structural_matrix = np.full((10, len(ordered_states)), np.nan, dtype=float)
    for state in ordered_states:
        structural_matrix[sector_by_proj[state], x_index[state]] = base_graph_score[state]

    walk_matrix: np.ndarray | None = None
    walk_steps: list[dict[str, Any]] = []
    walk_notes: list[str] = []
    if phase2_path is not None:
        phase2 = _load_json(phase2_path)
        phase2["_path"] = str(phase2_path)
        trace, _resolved_invariant = _load_phase2_trace(phase2_path, None)
        walk = phase2.get("deterministic_walk", {})
        path = walk.get("path", [])
        if not isinstance(path, list) or not path:
            raise ValueError("phase2 artifact missing deterministic_walk.path")
        if len(path[0].get("state", [])) < project_width:
            raise ValueError("phase2 artifact does not have enough registers for rank4 projection")
        walk_rows = len(path) + 1
        walk_matrix = np.zeros((walk_rows, len(ordered_states)), dtype=float)
        states = [tuple(int(v) for v in path[0]["state"])]
        states.extend(tuple(int(v) for v in step["next_state"]) for step in path)
        visit_counts = {state: 0 for state in ordered_states}
        for row_idx, state in enumerate(states):
            proj = _project_state(state, project_width)
            if proj not in x_index:
                continue
            visit_counts[proj] += 1
            if density_mode == "visit":
                value = float(visit_counts[proj])
            elif density_mode == "hybrid":
                value = float(1.0 + base_graph_score[proj])
            else:
                value = 1.0
            walk_matrix[row_idx, x_index[proj]] = value
        walk_steps = trace["step_annotations"]
        walk_notes.append(f"walk_template={trace['metadata']['template_set']}")
        walk_notes.append(f"walk_cycle_start={trace['metadata']['cycle_start']}")
    elif panels in {"time", "both"}:
        raise ValueError("--phase2-artifact is required when panels include time")

    sector_sizes = {sector: sum(1 for state in ordered_states if sector_by_proj[state] == sector) for sector in range(10)}
    separators = []
    cursor = 0
    for sector in range(10):
        cursor += sector_sizes[sector]
        separators.append(cursor - 0.5)

    hot_states = sorted(
        ordered_states,
        key=lambda state: (base_graph_score[state], cross_counts[state], in_counts[state], out_counts[state], state),
        reverse=True,
    )[:12]

    q_rows = canonical.get("q_map_artifact", {}).get("rows", [])
    metadata = {
        "rank4_dataset": str(rank4_path),
        "canonical_derivation": graph["canonical_name"],
        "physics_artifact": graph["dataset"].get("source_artifacts", {}).get("physics_artifact"),
        "project_width": project_width,
        "register_count": register_count,
        "raw_projected_states": len(ordered_states),
        "raw_basin_count": canonical.get("q_map_artifact", {}).get("raw_basin_count"),
        "sector_count": canonical.get("shape", {}).get("basins"),
        "chain_height": canonical.get("metrics", {}).get("monotone_chain_height"),
        "effective_dimension": canonical.get("metrics", {}).get("effective_dimension"),
        "stability_values": canonical.get("stability"),
        "q_rows": len(q_rows),
        "density_mode": density_mode,
        "phase2_artifact": str(phase2_path) if phase2_path else None,
    }

    return {
        "metadata": metadata,
        "ordered_states": ordered_states,
        "sector_by_state": sector_by_proj,
        "structural_matrix": structural_matrix,
        "walk_matrix": walk_matrix,
        "walk_steps": walk_steps,
        "walk_notes": walk_notes,
        "separators": separators,
        "state_scores": {
            "out": out_counts,
            "in": in_counts,
            "cross": cross_counts,
            "transfer": transfer_counts,
            "graph": base_graph_score,
        },
        "hot_states": hot_states,
    }


def render_branch_density_png(payload: dict[str, Any], title: str, panels: str) -> bytes:
    show_structural = panels in {"stability", "both"}
    show_time = panels in {"time", "both"} and payload["walk_matrix"] is not None
    panel_count = int(show_structural) + int(show_time)
    fig = plt.figure(figsize=(max(14, payload["structural_matrix"].shape[1] * 0.16), 4.0 + 3.4 * panel_count))
    grid = fig.add_gridspec(panel_count, 1, hspace=0.35)
    fig.suptitle(title, fontsize=14)

    row = 0
    if show_structural:
        ax = fig.add_subplot(grid[row, 0])
        row += 1
        matrix = payload["structural_matrix"]
        masked = np.ma.masked_invalid(matrix)
        im = ax.imshow(masked, aspect="auto", interpolation="nearest", cmap="magma")
        ax.set_ylabel("Sector")
        ax.set_yticks(np.arange(10))
        ax.set_yticklabels([f"S{i}" for i in range(10)], fontsize=8)
        ax.set_xticks([])
        ax.set_title("Structural branch density by projected raw state", loc="left", fontsize=11)
        for sep in payload["separators"][:-1]:
            ax.axvline(sep, color="white", linewidth=0.35, alpha=0.8)
        cbar = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
        cbar.set_label("Graph branch score")

    if show_time:
        ax = fig.add_subplot(grid[row, 0])
        matrix = payload["walk_matrix"]
        im = ax.imshow(matrix, aspect="auto", interpolation="nearest", cmap="viridis")
        ax.set_ylabel("Walk Step")
        ax.set_yticks(np.arange(matrix.shape[0]))
        ax.set_yticklabels([str(i) for i in range(matrix.shape[0])], fontsize=8)
        ax.set_xticks([])
        ax.set_title("Walk-time activation on the same projected raw-state axis", loc="left", fontsize=11)
        for sep in payload["separators"][:-1]:
            ax.axvline(sep, color="white", linewidth=0.35, alpha=0.8)
        cbar = fig.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
        cbar.set_label("Traversal activation")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def render_branch_density_html(payload: dict[str, Any], png_bytes: bytes, title: str, panels: str) -> str:
    img_b64 = base64.b64encode(png_bytes).decode("ascii")
    meta = payload["metadata"]
    hot_rows = []
    for state in payload["hot_states"]:
        hot_rows.append(
            "<tr>"
            f"<td><code>{state}</code></td>"
            f"<td>{payload['sector_by_state'][state]}</td>"
            f"<td>{payload['state_scores']['graph'][state]:.1f}</td>"
            f"<td>{payload['state_scores']['cross'][state]}</td>"
            f"<td>{payload['state_scores']['in'][state]}</td>"
            f"<td>{payload['state_scores']['out'][state]}</td>"
            "</tr>"
        )
    notes_html = "".join(f"<li><code>{note}</code></li>" for note in payload["walk_notes"])
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
    ul {{ margin: 0.5rem 0; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="panel">
    <p>This is the graph-facing spectrogram view. The structural panel shows graph branch activity over the projected raw-state axis; the optional traversal panel shows a walk projected onto the same axis. It is experimental evidence for the basin/topology discussion, not a proof of the 10-basin or chain-height-4 claims.</p>
    <p><img alt="Branch density spectrogram" src="data:image/png;base64,{img_b64}"></p>
  </div>
  <div class="panel">
    <h2>Metadata</h2>
    <ul>
      <li><strong>Rank-4 dataset:</strong> <code>{meta['rank4_dataset']}</code></li>
      <li><strong>Canonical derivation:</strong> <code>{meta['canonical_derivation']}</code></li>
      <li><strong>Physics artifact:</strong> <code>{meta['physics_artifact']}</code></li>
      <li><strong>Projected raw-state width:</strong> <code>{meta['project_width']}</code></li>
      <li><strong>Projected columns:</strong> <code>{meta['raw_projected_states']}</code></li>
      <li><strong>Raw basin count:</strong> <code>{meta['raw_basin_count']}</code></li>
      <li><strong>Sector count:</strong> <code>{meta['sector_count']}</code></li>
      <li><strong>Chain height:</strong> <code>{meta['chain_height']}</code></li>
      <li><strong>Effective dimension:</strong> <code>{meta['effective_dimension']}</code></li>
      <li><strong>Density mode:</strong> <code>{meta['density_mode']}</code></li>
      <li><strong>Panels:</strong> <code>{panels}</code></li>
      <li><strong>Walk artifact:</strong> <code>{meta['phase2_artifact'] or '-'}</code></li>
    </ul>
    <p>Sector separators on the x-axis are induced by the canonical quotient `q(N)`, applied to the projected raw-state coordinates used by the rank-4 dataset.</p>
  </div>
  <div class="panel">
    <h2>Hot Projected States</h2>
    <table>
      <thead>
        <tr>
          <th>Projected State</th><th>Sector</th><th>Graph Score</th><th>Cross-Sector</th><th>In</th><th>Out</th>
        </tr>
      </thead>
      <tbody>
        {''.join(hot_rows)}
      </tbody>
    </table>
  </div>
  <div class="panel">
    <h2>Walk Notes</h2>
    <ul>{notes_html or '<li><code>no walk-time panel</code></li>'}</ul>
  </div>
</body>
</html>
"""


def write_branch_density_outputs(payload: dict[str, Any], prefix: Path, title: str, panels: str) -> tuple[Path, Path]:
    png_path = prefix.with_name(prefix.name + ".branch-density.png")
    html_path = prefix.with_name(prefix.name + ".branch-density.html")
    png_bytes = render_branch_density_png(payload, title, panels)
    png_path.write_bytes(png_bytes)
    html_path.write_text(render_branch_density_html(payload, png_bytes, title, panels), encoding="utf-8")
    return png_path, html_path


def _print_paths(png_path: Path, html_path: Path, extra: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"png": str(png_path), "html": str(html_path)}
    if extra:
        payload.update(extra)
    print(json.dumps(payload, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Render FRACDASH walk waveforms and rank-4 branch-density views.")
    parser.add_argument("phase2_artifacts", type=Path, nargs="*", help="One or more phase-2 JSON artifacts for waveform mode")
    parser.add_argument("--mode", choices=("waveform", "branch-density"), default="waveform")
    parser.add_argument("--invariants", type=Path, help="Optional invariant artifact for single-run waveform mode")
    parser.add_argument("--output-prefix", help="Optional output prefix for rendered artifacts")
    parser.add_argument("--title", help="Optional title override")
    parser.add_argument("--rank4-dataset", type=Path, help="Canonical rank-4 dataset JSON for branch-density mode")
    parser.add_argument("--phase2-artifact", type=Path, help="Optional phase-2 walk artifact for branch-density mode")
    parser.add_argument("--density-mode", choices=("graph", "visit", "hybrid"), default="graph")
    parser.add_argument("--panels", choices=("stability", "time", "both"), default="both")
    args = parser.parse_args()

    if args.mode == "waveform":
        if not args.phase2_artifacts:
            raise SystemExit("waveform mode requires one or more phase-2 artifacts")
        if args.invariants and len(args.phase2_artifacts) > 1:
            raise SystemExit("--invariants is only supported in single-run waveform mode")
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
        _print_paths(png_path, html_path, {"invariants": invariant_paths})
        return

    if args.rank4_dataset is None:
        raise SystemExit("branch-density mode requires --rank4-dataset")
    payload = _build_branch_density_payload(args.rank4_dataset, args.phase2_artifact, args.density_mode, args.panels)
    title = args.title or "Branch Density Spectrogram"
    prefix = (
        Path(args.output_prefix)
        if args.output_prefix
        else args.rank4_dataset.with_suffix("").with_name(args.rank4_dataset.with_suffix("").name + ".branch-density-view")
    )
    png_path, html_path = write_branch_density_outputs(payload, prefix, title, args.panels)
    _print_paths(
        png_path,
        html_path,
        {
            "rank4_dataset": str(args.rank4_dataset),
            "phase2_artifact": str(args.phase2_artifact) if args.phase2_artifact else None,
            "density_mode": args.density_mode,
            "panels": args.panels,
        },
    )


if __name__ == "__main__":
    main()
