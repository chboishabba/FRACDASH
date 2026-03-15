#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path
from typing import Any


def require_numpy() -> Any:
    try:
        import numpy as np
    except ModuleNotFoundError as exc:
        raise SystemExit("numpy is required for discriminator experiments; install python-numpy.") from exc
    return np


def load_dataset(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_derivation_view(dataset: dict[str, Any], derivation: str | None) -> tuple[str, dict[str, Any]]:
    derivations = dataset.get("derivations")
    if isinstance(derivations, dict) and derivations:
        selected = derivation or dataset.get("canonical_derivation")
        if not isinstance(selected, str) or selected not in derivations:
            selected = sorted(derivations.keys())[0]
        return selected, dict(derivations[selected])
    return "legacy", dataset


def pca_embedding(matrix: list[list[float]], dims: int = 4) -> tuple[Any, dict[str, Any]]:
    np = require_numpy()
    arr = np.array(matrix, dtype=float)
    centered = arr - np.mean(arr, axis=0, keepdims=True)
    _u, singular, vh = np.linalg.svd(centered, full_matrices=False)
    axes = vh[:dims]
    embedding = centered @ axes.T
    variances = singular**2
    total = float(np.sum(variances))
    explained = [float(v / total) if total > 0 else 0.0 for v in variances[:dims]]
    return embedding, {"dimensions": dims, "explained_variance_ratio": explained}


def undirected_edges(adjacency: list[dict[str, Any]]) -> list[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for edge in adjacency:
        src = int(edge["from"])
        dst = int(edge["to"])
        if src == dst:
            continue
        pair = (src, dst) if src < dst else (dst, src)
        edges.add(pair)
    return sorted(edges)


def all_pairs(node_count: int) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for left in range(node_count):
        for right in range(left + 1, node_count):
            pairs.append((left, right))
    return pairs


def root_length_test(embedding: Any, adjacency: list[dict[str, Any]]) -> dict[str, Any]:
    np = require_numpy()
    pairs = undirected_edges(adjacency)
    source = "adjacency_edges"
    if not pairs:
        pairs = all_pairs(int(embedding.shape[0]))
        source = "all_pairs_fallback"
    distances = [float(np.linalg.norm(embedding[a] - embedding[b])) for a, b in pairs]
    positive = [value for value in distances if value > 0]
    if len(positive) == 1:
        only = positive[0]
        return {
            "status": "ok",
            "distance_source": source,
            "edge_count": len(pairs),
            "distance_min": only,
            "distance_max": only,
            "distance_ratio": 1.0,
            "coefficient_of_variation": 0.0,
            "single_scale_signal": True,
            "two_scale_signal": False,
            "candidate_hint": "D4-like",
        }
    if len(positive) < 2:
        return {"status": "inconclusive", "reason": "insufficient positive edge distances"}
    dmin = min(positive)
    dmax = max(positive)
    ratio = dmax / dmin if dmin > 0 else math.inf
    mean = sum(positive) / len(positive)
    variance = sum((value - mean) ** 2 for value in positive) / len(positive)
    stddev = math.sqrt(variance)
    coeff_var = stddev / mean if mean > 0 else math.inf
    return {
        "status": "ok",
        "distance_source": source,
        "edge_count": len(pairs),
        "distance_min": dmin,
        "distance_max": dmax,
        "distance_ratio": ratio,
        "coefficient_of_variation": coeff_var,
        "single_scale_signal": ratio <= 1.35,
        "two_scale_signal": ratio > 1.35,
        "candidate_hint": "D4-like" if ratio <= 1.35 else "F4/B4-like",
    }


def nearest_permutation(points: Any, transformed: Any) -> tuple[list[int], bool]:
    np = require_numpy()
    n = int(points.shape[0])
    remaining = set(range(n))
    mapping: list[int] = [-1] * n
    for idx in range(n):
        best = None
        best_dist = None
        for cand in remaining:
            dist = float(np.linalg.norm(transformed[idx] - points[cand]))
            if best_dist is None or dist < best_dist:
                best = cand
                best_dist = dist
        if best is None:
            return mapping, False
        mapping[idx] = int(best)
        remaining.remove(best)
    return mapping, len(set(mapping)) == n


def adjacency_preservation_ratio(mapping: list[int], edges: list[tuple[int, int]]) -> float:
    edge_set = set(edges)
    if not edge_set:
        return 0.0
    mapped = {(min(mapping[a], mapping[b]), max(mapping[a], mapping[b])) for a, b in edges}
    kept = len(mapped.intersection(edge_set))
    return float(kept / len(edge_set))


def gram_error(points: Any, transformed: Any) -> float:
    np = require_numpy()
    original_gram = points @ points.T
    transformed_gram = transformed @ transformed.T
    return float(np.max(np.abs(original_gram - transformed_gram)))


def reflection_closure_test(embedding: Any, adjacency: list[dict[str, Any]]) -> dict[str, Any]:
    np = require_numpy()
    dims = int(embedding.shape[1])
    edges = undirected_edges(adjacency)
    axes_reports = []
    valid_axes = 0
    for axis in range(min(4, dims)):
        normal = np.zeros(dims)
        normal[axis] = 1.0
        transformed = embedding - 2.0 * np.outer(embedding @ normal, normal)
        mapping, bijective = nearest_permutation(embedding, transformed)
        preserved_ratio = adjacency_preservation_ratio(mapping, edges) if bijective else 0.0
        axis_report = {
            "axis": axis,
            "bijective_permutation": bool(bijective),
            "adjacency_preservation_ratio": preserved_ratio,
            "gram_error": gram_error(embedding, transformed),
            "mapping": mapping,
        }
        if bijective:
            valid_axes += 1
        axes_reports.append(axis_report)
    closure_score = sum(item["adjacency_preservation_ratio"] for item in axes_reports) / max(
        len(axes_reports), 1
    )
    return {
        "status": "ok",
        "axes": axes_reports,
        "valid_axis_count": valid_axes,
        "closure_score": closure_score,
        "weyl_action_candidate": valid_axes >= 4 and closure_score >= 0.85,
    }


def orbit_multiplicity_test(
    stability: list[int],
    closure: dict[str, Any],
) -> dict[str, Any]:
    count_by_value: dict[int, int] = {}
    for value in stability:
        count_by_value[value] = count_by_value.get(value, 0) + 1
    repeated = sorted(
        [{"stability": int(v), "count": int(c)} for v, c in count_by_value.items() if c > 1],
        key=lambda item: (-item["count"], -item["stability"]),
    )

    mappings = [axis.get("mapping") for axis in closure.get("axes", []) if axis.get("bijective_permutation")]
    orbit_sizes: list[int] = []
    if mappings:
        n = len(stability)
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for mapping in mappings:
            for src, dst in enumerate(mapping):
                union(src, int(dst))

        groups: dict[int, list[int]] = {}
        for idx in range(n):
            root = find(idx)
            groups.setdefault(root, []).append(idx)
        orbit_sizes = sorted((len(nodes) for nodes in groups.values()), reverse=True)

    return {
        "status": "ok",
        "repeated_stability_groups": repeated,
        "reflection_orbit_sizes": orbit_sizes,
        "supports_repeated_orbit_hypothesis": bool(repeated and orbit_sizes),
    }


def clifford_reflection_test(embedding: Any, adjacency: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        import clifford  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return {
            "status": "not_available",
            "reason": "python package 'clifford' is not installed; skipping Clifford versor check.",
        }

    _ = clifford
    closure = reflection_closure_test(embedding, adjacency)
    return {
        "status": "ok",
        "note": "Using Euclidean reflection mapping as a Clifford-capable proxy check.",
        "proxy_reflection_closure": closure,
    }


def chamber_sign(point: list[float]) -> str:
    bits = []
    for value in point[:4]:
        bits.append("+" if value >= 0 else "-")
    return "".join(bits)


def stability_gradient_chamber_test(
    embedding: Any,
    stability: list[int],
    adjacency: list[dict[str, Any]],
) -> dict[str, Any]:
    chamber_by_node = {idx: chamber_sign([float(v) for v in embedding[idx]]) for idx in range(len(stability))}
    within_total = 0
    within_monotone = 0
    cross_total = 0
    cross_monotone = 0

    for edge in adjacency:
        src = int(edge["from"])
        dst = int(edge["to"])
        if src == dst:
            continue
        same = chamber_by_node[src] == chamber_by_node[dst]
        monotone = stability[src] >= stability[dst]
        if same:
            within_total += 1
            within_monotone += 1 if monotone else 0
        else:
            cross_total += 1
            cross_monotone += 1 if monotone else 0

    within_ratio = float(within_monotone / within_total) if within_total else None
    cross_ratio = float(cross_monotone / cross_total) if cross_total else None
    return {
        "status": "ok",
        "within_chamber_edges": within_total,
        "cross_chamber_edges": cross_total,
        "within_monotone_ratio": within_ratio,
        "cross_monotone_ratio": cross_ratio,
        "supports_chamber_hypothesis": (
            within_ratio is not None
            and cross_ratio is not None
            and within_ratio > cross_ratio
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Rank-4 Discriminator Report",
        "",
        f"- Dataset: `{report['dataset_path']}`",
        f"- Dataset SHA: `{report.get('dataset_sha256', 'unknown')}`",
        "",
        "## Root-Length Test",
        f"- Status: `{report['root_length_test']['status']}`",
        f"- Hint: `{report['root_length_test'].get('candidate_hint', 'n/a')}`",
        "",
        "## Reflection Closure",
        f"- Weyl action candidate: `{report['reflection_closure_test'].get('weyl_action_candidate')}`",
        f"- Closure score: `{report['reflection_closure_test'].get('closure_score')}`",
        "",
        "## Orbit Multiplicity",
        f"- Supports repeated orbit hypothesis: `{report['orbit_multiplicity_test'].get('supports_repeated_orbit_hypothesis')}`",
        "",
        "## Clifford Reflection",
        f"- Status: `{report['clifford_reflection_test'].get('status')}`",
        "",
        "## Stability Chamber Gradient",
        f"- Supports chamber hypothesis: `{report['stability_gradient_chamber_test'].get('supports_chamber_hypothesis')}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run rank-4 discriminator experiments on canonical basin dataset.")
    parser.add_argument(
        "--dataset",
        default="benchmarks/results/rank4-dataset-latest.json",
        help="Canonical dataset path.",
    )
    parser.add_argument(
        "--derivation",
        default=None,
        help="Optional derivation key to analyze; defaults to canonical_derivation.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="JSON output path (default: benchmarks/results/<today>-rank4-discriminators.json).",
    )
    parser.add_argument(
        "--markdown-output",
        default=None,
        help="Markdown summary path (default: benchmarks/results/<today>-rank4-discriminators.md).",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON report to stdout.")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    output_path = (
        Path(args.output)
        if args.output
        else Path(f"benchmarks/results/{date.today().isoformat()}-rank4-discriminators.json")
    )
    markdown_path = (
        Path(args.markdown_output)
        if args.markdown_output
        else Path(f"benchmarks/results/{date.today().isoformat()}-rank4-discriminators.md")
    )

    dataset = load_dataset(dataset_path)
    derivation_name, derivation_payload = resolve_derivation_view(dataset, args.derivation)
    matrix = derivation_payload.get("matrix")
    stability = derivation_payload.get("stability")
    adjacency = derivation_payload.get("adjacency")
    if not isinstance(matrix, list) or not isinstance(stability, list):
        raise SystemExit("dataset missing matrix/stability")
    if not isinstance(adjacency, list):
        adjacency = []

    embedding, embedding_meta = pca_embedding(matrix, dims=4)
    root_lengths = root_length_test(embedding, adjacency)
    closure = reflection_closure_test(embedding, adjacency)
    orbit = orbit_multiplicity_test([int(v) for v in stability], closure)
    clifford = clifford_reflection_test(embedding, adjacency)
    chamber = stability_gradient_chamber_test(embedding, [int(v) for v in stability], adjacency)

    report: dict[str, Any] = {
        "dataset_path": str(dataset_path),
        "dataset_sha256": dataset.get("sha256"),
        "selected_derivation": derivation_name,
        "embedding": embedding_meta,
        "root_length_test": root_lengths,
        "reflection_closure_test": closure,
        "orbit_multiplicity_test": orbit,
        "clifford_reflection_test": clifford,
        "stability_gradient_chamber_test": chamber,
        "claim_status": {
            "identity_level_claims": "unproven",
            "rank4_structure": "observed experimentally",
            "root_system_identity": "conjectured",
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"wrote {output_path}")
        print(f"wrote {markdown_path}")


if __name__ == "__main__":
    main()
