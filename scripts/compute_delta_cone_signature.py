#!/usr/bin/env python3
"""Compute a Δ-cone signature from a deterministic walk artifact.

Input expectation (minimal):
- JSON with key `deterministic_walk` containing either:
  * a list of states, or
  * an object with key `path` that is a list of states.

Each state is a list/tuple of ints (e.g., [-1,0,1,...]).

Cone test:
- Project states (optionally drop registers)
- Form deltas Δs = s_{t+1} - s_t
- Evaluate Q(Δs) = Σ_i w_i * (Δs_i)^2
- Report fraction with Q <= 0, min/max Q, and basic norms.

This script is intentionally simple and standalone; it does not guess
weights. If no weights are provided, it defaults to all -1 (strictly
contractive cone).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


def _load_states(path: Path) -> list[list[int]]:
    data = json.loads(path.read_text())
    dw = data.get("deterministic_walk", data.get("deterministic_walk", None))
    if isinstance(dw, dict):
        states = dw.get("path")
    else:
        states = dw
    if not isinstance(states, list):
        raise ValueError(f"No deterministic_walk/path found in {path}")
    return [list(map(int, s)) for s in states]


def _project(states: Iterable[Sequence[int]], drop: set[int]) -> list[list[int]]:
    out: list[list[int]] = []
    for s in states:
        out.append([v for idx, v in enumerate(s) if idx not in drop])
    return out


def _deltas(states: list[list[int]]) -> list[list[int]]:
    return [[b - a for a, b in zip(states[i], states[i + 1])] for i in range(len(states) - 1)]


def _q(delta: Sequence[int], weights: Sequence[float]) -> float:
    return sum(w * (d ** 2) for w, d in zip(weights, delta))


def _norm(delta: Sequence[int]) -> int:
    return sum(abs(d) for d in delta)


@dataclass
class Summary:
    cone_frac: float
    q_min: float
    q_max: float
    l1_min: int
    l1_max: int
    count: int


def summarize(deltas: list[list[int]], weights: list[float]) -> Summary:
    qs = [_q(d, weights) for d in deltas]
    l1s = [_norm(d) for d in deltas]
    cone_hits = sum(1 for q in qs if q <= 0)
    return Summary(
        cone_frac=cone_hits / len(qs) if qs else 0.0,
        q_min=min(qs) if qs else 0.0,
        q_max=max(qs) if qs else 0.0,
        l1_min=min(l1s) if l1s else 0,
        l1_max=max(l1s) if l1s else 0,
        count=len(qs),
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute Δ-cone signature from a deterministic walk artifact.")
    ap.add_argument("artifact", type=Path, help="JSON artifact with deterministic_walk/path.")
    ap.add_argument("--drop", type=str, default="", help="Comma-separated register indices to drop (0-based).")
    ap.add_argument(
        "--weights",
        type=str,
        default="",
        help="Comma-separated weights for Q. Defaults to all -1 after drop.",
    )
    args = ap.parse_args()

    states = _load_states(args.artifact)
    drop_idx = {int(x) for x in args.drop.split(",") if x.strip()} if args.drop else set()
    proj_states = _project(states, drop_idx)
    deltas = _deltas(proj_states)
    if not deltas:
        raise SystemExit("No deltas to analyze (need at least two states).")

    dim = len(deltas[0])
    if args.weights:
        weights = [float(x) for x in args.weights.split(",")]
        if len(weights) != dim:
            raise SystemExit(f"weights length {len(weights)} != delta dimension {dim}")
    else:
        weights = [-1.0] * dim  # strict contraction cone

    summary = summarize(deltas, weights)
    payload = {
        "artifact": str(args.artifact),
        "drop_indices": sorted(drop_idx),
        "weights": weights,
        "delta_dimension": dim,
        "cone_fraction_nonpositive": summary.cone_frac,
        "q_min": summary.q_min,
        "q_max": summary.q_max,
        "l1_min": summary.l1_min,
        "l1_max": summary.l1_max,
        "samples": summary.count,
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
