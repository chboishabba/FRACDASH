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
        raise SystemExit("numpy is required for PCA diagnostics; install python-numpy.") from exc
    return np


def load_dataset(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pca_summary(matrix: list[list[float]], variance_threshold: float) -> dict[str, Any]:
    np = require_numpy()
    arr = np.array(matrix, dtype=float)
    if arr.ndim != 2 or arr.shape[0] == 0 or arr.shape[1] == 0:
        raise ValueError("matrix must be a non-empty 2D array")
    centered = arr - np.mean(arr, axis=0, keepdims=True)
    _u, singular, _vh = np.linalg.svd(centered, full_matrices=False)
    variances = singular**2
    total = float(np.sum(variances))
    explained = [float(v / total) if total > 0 else 0.0 for v in variances]
    cumulative: list[float] = []
    running = 0.0
    for value in explained:
        running += value
        cumulative.append(running)
    effective_dim = len(cumulative)
    for idx, cum in enumerate(cumulative, start=1):
        if cum >= variance_threshold:
            effective_dim = idx
            break
    return {
        "matrix_shape": [int(arr.shape[0]), int(arr.shape[1])],
        "variance_threshold": variance_threshold,
        "singular_values": [float(v) for v in singular],
        "explained_variance_ratio": explained,
        "cumulative_variance_ratio": cumulative,
        "effective_dimension": int(effective_dim),
    }


def build_monotone_edges(adjacency: list[dict[str, Any]], stability: list[int]) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for edge in adjacency:
        src = int(edge["from"])
        dst = int(edge["to"])
        if src < 0 or src >= len(stability) or dst < 0 or dst >= len(stability):
            continue
        if stability[src] > stability[dst]:
            edges.append((src, dst))
    return edges


def longest_chain_height(node_count: int, edges: list[tuple[int, int]]) -> int:
    adjacency: dict[int, list[int]] = {node: [] for node in range(node_count)}
    for src, dst in edges:
        adjacency[src].append(dst)
    memo: dict[int, int] = {}

    def dfs(node: int) -> int:
        if node in memo:
            return memo[node]
        best = 1
        for child in adjacency.get(node, []):
            best = max(best, 1 + dfs(child))
        memo[node] = best
        return best

    return max((dfs(node) for node in range(node_count)), default=0)


def chain_summary(basins: list[dict[str, Any]], stability: list[int], adjacency: list[dict[str, Any]]) -> dict[str, Any]:
    descending_edges = build_monotone_edges(adjacency, stability)
    chain_height = longest_chain_height(len(basins), descending_edges)
    distinct_stability = sorted(set(stability), reverse=True)
    return {
        "node_count": len(basins),
        "edge_count": len(adjacency),
        "descending_edge_count": len(descending_edges),
        "stability_values": [int(v) for v in stability],
        "stability_distinct_values": [int(v) for v in distinct_stability],
        "longest_monotone_chain_height": int(chain_height),
    }


def finite_matrix(matrix: list[list[float]]) -> bool:
    for row in matrix:
        for value in row:
            if not math.isfinite(float(value)):
                return False
    return True


def stable_checks(payload: dict[str, Any], pca: dict[str, Any], chain: dict[str, Any]) -> dict[str, Any]:
    matrix = payload["matrix"]
    stability = payload["stability"]
    basins = payload["basins"]
    adjacency = payload["adjacency"]
    shape = payload["shape"]

    shape_ok = int(shape["basins"]) == 10 and int(shape["primes"]) == 15
    matrix_rows_ok = len(matrix) == int(shape["basins"]) and all(len(row) == int(shape["primes"]) for row in matrix)
    finite_ok = finite_matrix(matrix)
    stability_ok = len(stability) == len(basins)
    adjacency_ok = all(
        0 <= int(edge["from"]) < len(basins) and 0 <= int(edge["to"]) < len(basins) for edge in adjacency
    )
    pca_ok = pca["effective_dimension"] > 0 and pca["effective_dimension"] <= len(pca["explained_variance_ratio"])
    chain_ok = chain["longest_monotone_chain_height"] >= 1

    checks = {
        "shape_10x15": shape_ok,
        "matrix_shape_consistent": matrix_rows_ok,
        "matrix_finite": finite_ok,
        "stability_length_consistent": stability_ok,
        "adjacency_indices_valid": adjacency_ok,
        "pca_computable": pca_ok,
        "chain_computable": chain_ok,
    }
    return {
        "checks": checks,
        "all_pass": all(checks.values()),
    }


def lock_gate(payload: dict[str, Any], pca: dict[str, Any], chain: dict[str, Any]) -> dict[str, Any]:
    shape = payload["shape"]
    shape_ok = int(shape["basins"]) == 10 and int(shape["primes"]) == 15
    gate = {
        "shape_10x15": shape_ok,
        "effective_dimension_is_4": pca["effective_dimension"] == 4,
        "chain_height_is_4": chain["longest_monotone_chain_height"] == 4,
    }
    return {
        "checks": gate,
        "pass": all(gate.values()),
    }


def collect_derivations(dataset: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if isinstance(dataset.get("derivations"), dict):
        return dict(dataset["derivations"])
    # Backward compatibility with pre-v2 artifact format.
    return {
        "legacy": {
            "shape": dataset.get("shape", {"basins": 0, "primes": 0}),
            "matrix": dataset.get("matrix", []),
            "stability": dataset.get("stability", []),
            "basins": dataset.get("basins", []),
            "adjacency": dataset.get("adjacency", []),
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run rank-4 diagnostics across derivations in canonical dataset.")
    parser.add_argument(
        "--dataset",
        default="benchmarks/results/rank4-dataset-latest.json",
        help="Canonical dataset JSON path.",
    )
    parser.add_argument(
        "--variance-threshold",
        type=float,
        default=0.997,
        help="Cumulative variance threshold for effective dimension (default: 0.997).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output report path (default: benchmarks/results/<today>-rank4-diagnostics.json).",
    )
    parser.add_argument(
        "--strict-stable",
        action="store_true",
        help="Exit non-zero if stable structural checks fail for any derivation.",
    )
    parser.add_argument(
        "--strict-lock",
        action="store_true",
        help="Exit non-zero unless canonical derivation passes lock gate (shape+rank4+chain4).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Backward-compatible alias for --strict-lock.",
    )
    parser.add_argument("--json", action="store_true", help="Print full report JSON.")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    report_path = (
        Path(args.output)
        if args.output
        else Path(f"benchmarks/results/{date.today().isoformat()}-rank4-diagnostics.json")
    )
    dataset = load_dataset(dataset_path)

    derivations = collect_derivations(dataset)
    canonical = dataset.get("canonical_derivation")
    if not isinstance(canonical, str) or canonical not in derivations:
        canonical = sorted(derivations.keys())[0]

    per_derivation: dict[str, dict[str, Any]] = {}
    stable_failures: list[str] = []
    for name, payload in sorted(derivations.items()):
        matrix = payload.get("matrix")
        stability = payload.get("stability")
        basins = payload.get("basins")
        adjacency = payload.get("adjacency")
        if not isinstance(matrix, list) or not isinstance(stability, list) or not isinstance(basins, list):
            raise SystemExit(f"derivation {name} missing matrix/stability/basins")
        if not isinstance(adjacency, list):
            adjacency = []

        pca = pca_summary(matrix, variance_threshold=args.variance_threshold)
        chain = chain_summary(basins, [int(v) for v in stability], adjacency)
        stable = stable_checks(payload, pca, chain)
        lock = lock_gate(payload, pca, chain)
        if not stable["all_pass"]:
            stable_failures.append(name)
        per_derivation[name] = {
            "shape": payload.get("shape"),
            "pca": pca,
            "chain": chain,
            "stable": stable,
            "lock_gate": lock,
            "observations": {
                "rank4_observed": pca["effective_dimension"] == 4,
                "chain4_observed": chain["longest_monotone_chain_height"] == 4,
                "both_rank4_signals": pca["effective_dimension"] == 4 and chain["longest_monotone_chain_height"] == 4,
            },
        }

    canonical_summary = per_derivation[canonical]
    comparison = {
        name: {
            "effective_dimension": data["pca"]["effective_dimension"],
            "chain_height": data["chain"]["longest_monotone_chain_height"],
            "lock_gate_pass": data["lock_gate"]["pass"],
            "stable_pass": data["stable"]["all_pass"],
        }
        for name, data in per_derivation.items()
    }
    strict_lock = bool(args.strict_lock or args.strict)
    report: dict[str, Any] = {
        "dataset_path": str(dataset_path),
        "dataset_sha256": dataset.get("sha256"),
        "canonical_derivation": canonical,
        "canonical_selection": dataset.get("canonical_selection", {}),
        "status_mode": {
            "strict_stable": bool(args.strict_stable),
            "strict_lock": strict_lock,
        },
        "derivations": per_derivation,
        "comparison": comparison,
        "independence_check": {
            "pca_inputs": ["matrix"],
            "chain_inputs": ["stability", "adjacency"],
            "input_overlap": [],
            "valid": True,
        },
        "summary": {
            "canonical_lock_gate_pass": canonical_summary["lock_gate"]["pass"],
            "all_derivations_stable": len(stable_failures) == 0,
            "stable_failures": stable_failures,
        },
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"wrote {report_path}")
        print(
            "canonical:"
            f" {canonical},"
            f" effective_dimension={canonical_summary['pca']['effective_dimension']},"
            f" chain_height={canonical_summary['chain']['longest_monotone_chain_height']},"
            f" lock_gate={canonical_summary['lock_gate']['pass']}"
        )

    failed = False
    if args.strict_stable and stable_failures:
        failed = True
    if strict_lock and not canonical_summary["lock_gate"]["pass"]:
        failed = True
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
