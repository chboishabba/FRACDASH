#!/usr/bin/env python3
"""Render FRACDASH deterministic walks as a small directed state graph."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _short_state(state: list[int]) -> str:
    return "[" + ", ".join(str(v) for v in state) + "]"


def _walk_graph(phase2: dict[str, Any]) -> dict[str, Any]:
    walk = phase2.get("deterministic_walk")
    if not isinstance(walk, dict):
        raise ValueError("phase-2 artifact is missing deterministic_walk")
    path = walk.get("path")
    if not isinstance(path, list) or not path:
        raise ValueError("deterministic_walk.path is missing or empty")

    node_order: list[tuple[int, ...]] = []
    node_steps: dict[tuple[int, ...], list[int]] = {}
    edges: list[dict[str, Any]] = []
    edge_counts: Counter[tuple[tuple[int, ...], tuple[int, ...], str]] = Counter()

    for entry in path:
        state = tuple(int(v) for v in entry["state"])
        next_state = tuple(int(v) for v in entry["next_state"])
        transition = str(entry.get("transition", ""))
        step = int(entry.get("step", len(edges) + 1))

        for node, marker in ((state, step), (next_state, step + 1)):
            if node not in node_steps:
                node_order.append(node)
                node_steps[node] = []
            node_steps[node].append(marker)

        edge_key = (state, next_state, transition)
        edge_counts[edge_key] += 1
        edges.append(
            {
                "step": step,
                "state": state,
                "next_state": next_state,
                "transition": transition,
            }
        )

    cycle_start = walk.get("cycle_start")
    final_state = tuple(int(v) for v in walk.get("final_state", path[-1]["next_state"]))

    nodes = []
    for index, node in enumerate(node_order):
        theta = (2.0 * math.pi * index / max(1, len(node_order))) - (math.pi / 2.0)
        nodes.append(
            {
                "id": node,
                "label": _short_state(list(node)),
                "steps": sorted(node_steps[node]),
                "x": math.cos(theta),
                "y": math.sin(theta),
                "is_start": index == 0,
                "is_final": node == final_state,
                "is_cycle": isinstance(cycle_start, int) and cycle_start in node_steps[node],
            }
        )

    edge_summaries = []
    for (state, next_state, transition), count in edge_counts.items():
        step_labels = [edge["step"] for edge in edges if edge["state"] == state and edge["next_state"] == next_state and edge["transition"] == transition]
        edge_summaries.append(
            {
                "source": state,
                "target": next_state,
                "transition": transition,
                "count": count,
                "steps": step_labels,
            }
        )

    return {
        "template_set": phase2.get("template_set", "unknown"),
        "cycle_start": cycle_start,
        "steps": int(walk.get("steps", len(path))),
        "status": walk.get("status", "unknown"),
        "nodes": nodes,
        "edges": edge_summaries,
    }


def _draw_graph(graph: dict[str, Any], title: str) -> bytes:
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_title(title)
    ax.set_aspect("equal")
    ax.axis("off")

    max_edge_count = max((edge["count"] for edge in graph["edges"]), default=1)
    transition_names = sorted({edge["transition"] for edge in graph["edges"]})
    palette = plt.cm.get_cmap("tab10", max(1, len(transition_names)))
    transition_colors = {name: palette(idx) for idx, name in enumerate(transition_names)}
    node_lookup = {node["id"]: node for node in graph["nodes"]}

    for edge in graph["edges"]:
        source = node_lookup[edge["source"]]
        target = node_lookup[edge["target"]]
        color = transition_colors[edge["transition"]]
        width = 1.5 + (4.0 * edge["count"] / max_edge_count)
        rad = 0.18 if edge["source"] == edge["target"] else 0.08
        arrow = FancyArrowPatch(
            (source["x"], source["y"]),
            (target["x"], target["y"]),
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=width,
            color=color,
            alpha=0.85,
            shrinkA=14,
            shrinkB=14,
        )
        ax.add_patch(arrow)
        mid_x = (source["x"] + target["x"]) / 2.0
        mid_y = (source["y"] + target["y"]) / 2.0
        ax.text(
            mid_x,
            mid_y,
            f"{edge['transition']}\nsteps={edge['steps']}",
            fontsize=7,
            ha="center",
            va="center",
            bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "none", "pad": 1.5},
        )

    for node in graph["nodes"]:
        if node["is_start"]:
            face = "#bfdbfe"
        elif node["is_final"]:
            face = "#fde68a"
        elif node["is_cycle"]:
            face = "#fecaca"
        else:
            face = "#e5e7eb"
        ax.scatter([node["x"]], [node["y"]], s=1400, c=[face], edgecolors="#1f2937", linewidths=1.0, zorder=3)
        ax.text(
            node["x"],
            node["y"],
            node["label"] + "\nsteps=" + ",".join(str(v) for v in node["steps"]),
            ha="center",
            va="center",
            fontsize=8,
            zorder=4,
        )

    legend_lines = [
        f"template={graph['template_set']}",
        f"status={graph['status']}",
        f"steps={graph['steps']}",
        f"cycle_start={graph['cycle_start']}",
        "edge width = repeated use count",
        "edge color = transition family",
    ]
    ax.text(
        0.02,
        0.02,
        "\n".join(legend_lines),
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.9, "edgecolor": "#d1d5db"},
    )

    import io

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def render_html(graph: dict[str, Any], png_path: Path, title: str) -> str:
    node_rows = []
    for node in graph["nodes"]:
        node_rows.append(
            "<tr>"
            f"<td><code>{list(node['id'])}</code></td>"
            f"<td>{','.join(str(v) for v in node['steps'])}</td>"
            f"<td>{'yes' if node['is_start'] else 'no'}</td>"
            f"<td>{'yes' if node['is_final'] else 'no'}</td>"
            f"<td>{'yes' if node['is_cycle'] else 'no'}</td>"
            "</tr>"
        )
    edge_rows = []
    for edge in graph["edges"]:
        edge_rows.append(
            "<tr>"
            f"<td><code>{list(edge['source'])}</code></td>"
            f"<td><code>{list(edge['target'])}</code></td>"
            f"<td>{edge['transition']}</td>"
            f"<td>{edge['count']}</td>"
            f"<td>{','.join(str(v) for v in edge['steps'])}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin: 24px; color: #1f2937; background: #f8fafc; }}
    .panel {{ background: white; border: 1px solid #dbe4ee; border-radius: 8px; padding: 16px; margin-bottom: 18px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ border: 1px solid #dbe4ee; padding: 6px 8px; text-align: left; vertical-align: top; }}
    th {{ background: #eff6ff; }}
    code {{ white-space: pre-wrap; word-break: break-word; }}
    img {{ max-width: 100%; border: 1px solid #dbe4ee; border-radius: 8px; background: white; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="panel">
    <p>This view renders the saved deterministic walk as a directed state graph. It does not infer the full basin graph from absent data; edge width shows repeated use count inside the saved walk, and edge color shows transition family.</p>
    <p><img alt="Trace graph" src="{png_path.name}"></p>
  </div>
  <div class="panel">
    <h2>Nodes</h2>
    <table>
      <thead><tr><th>State</th><th>Steps Seen</th><th>Start</th><th>Final</th><th>Cycle Marker</th></tr></thead>
      <tbody>{''.join(node_rows)}</tbody>
    </table>
  </div>
  <div class="panel">
    <h2>Edges</h2>
    <table>
      <thead><tr><th>Source</th><th>Target</th><th>Transition</th><th>Count</th><th>Steps</th></tr></thead>
      <tbody>{''.join(edge_rows)}</tbody>
    </table>
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a deterministic-walk state graph from a FRACDASH phase-2 artifact.")
    parser.add_argument("phase2_artifact", type=Path, help="Phase-2 JSON artifact")
    parser.add_argument("--output-prefix", help="Optional output prefix for .trace-graph.html/.png")
    parser.add_argument("--title", help="Optional title override")
    args = parser.parse_args()

    phase2 = _load_json(args.phase2_artifact)
    graph = _walk_graph(phase2)
    prefix = Path(args.output_prefix) if args.output_prefix else args.phase2_artifact.with_suffix("")
    png_path = prefix.with_name(prefix.name + ".trace-graph.png")
    html_path = prefix.with_name(prefix.name + ".trace-graph.html")
    title = args.title or f"Trace Graph: {graph['template_set']}"
    png_bytes = _draw_graph(graph, title)
    png_path.write_bytes(png_bytes)
    html_path.write_text(render_html(graph, png_path, title), encoding="utf-8")
    print(json.dumps({"png": str(png_path), "html": str(html_path)}, indent=2))


if __name__ == "__main__":
    main()
