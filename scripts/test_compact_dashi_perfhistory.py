#!/usr/bin/env python3
"""Regression checks for compact_dashi_perfhistory.py."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "compact_dashi_perfhistory.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("compact_dashi_perfhistory", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


FIXTURE = [
    {
        "cycles": 34176685,
        "instructions": 35438949,
        "cache-misses": 194755,
        "branch-misses": 226177,
        "file": "ActionMonotonicity.agda",
        "src_sha256": "aaa",
    },
    {
        "cycles": 38424270,
        "instructions": 53583336,
        "cache-misses": 173104,
        "branch-misses": 267430,
        "file": "Contraction.agda",
        "src_sha256": "bbb",
    },
    {
        "cycles": 42527604,
        "instructions": 65799009,
        "cache-misses": 228228,
        "branch-misses": 252973,
        "file": "JFixedPoint.agda",
        "src_sha256": "ccc",
    },
    {
        "cycles": 33055068,
        "instructions": 34779718,
        "cache-misses": 144286,
        "branch-misses": 221276,
        "file": "DA51Trace.agda",
        "src_sha256": "ddd",
    },
]


class CompactDashiPerfHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.codec = _load_module()

    def test_compact_roundtrip_exact(self) -> None:
        normalized = self.codec.normalize_summary(FIXTURE)
        compact = self.codec.encode_compact(normalized)
        rebuilt = self.codec.decode_compact(compact)
        self.assertEqual(rebuilt, normalized)

    def test_surface_and_semantic_roundtrip_exact(self) -> None:
        normalized = self.codec.normalize_summary(FIXTURE)
        compact = self.codec.encode_compact(normalized)
        surface = self.codec.encode_surface_motif(compact)
        semantic = self.codec.encode_semantic_motif(compact)
        self.assertEqual(self.codec.decode_surface_motif(surface), compact)
        self.assertEqual(self.codec.decode_semantic_motif(semantic), compact)

    def test_compare_outputs_are_emitted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            input_path = temp / "summary.json"
            input_path.write_text(json.dumps(FIXTURE, indent=2) + "\n", encoding="utf-8")
            stats = self.codec.stats_compare(
                input_path,
                temp / "normalized.json",
                temp / "compact.json",
                temp / "surface.json",
                temp / "semantic.json",
            )
            self.assertEqual(stats["normalized"]["rows"], len(FIXTURE))
            self.assertGreater(stats["normalized"]["bytes"], 0)
            self.assertGreater(stats["compact"]["bytes"], 0)


if __name__ == "__main__":
    unittest.main()
