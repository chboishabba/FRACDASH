#!/usr/bin/env python3
"""Load a source/attractor basis for projection.

This is deliberately simple: it reads a JSON with a matrix under `basis`
or a plain list-of-lists. Used by Δ-cone projection to align execution
space to source space (ERDFA/CFT).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


def load_basis(path: Path) -> List[List[float]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict) and "basis" in data:
        mat = data["basis"]
    else:
        mat = data
    if not isinstance(mat, list) or not mat:
        raise ValueError(f"invalid basis in {path}")
    rows = []
    for row in mat:
        if not isinstance(row, list):
            raise ValueError(f"basis row not list: {row}")
        rows.append([float(x) for x in row])
    return rows


def project(vec: list[float], basis: List[List[float]]) -> list[float]:
    # basis is list of rows; project vec into basis rows (dot product)
    return [sum(v * b for v, b in zip(vec, row)) for row in basis]


__all__ = ["load_basis", "project"]
