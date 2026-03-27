#!/usr/bin/env python3
"""Regression checks for aggregate DA51 shard compaction."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from compact_dashi_da51_shards import (
    decode_semantic_bytes,
    decode_surface_bytes,
    encode_semantic,
    encode_surface,
    load_shards,
    stats_compare,
)


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "dashi_agda" / "da51_shards"


class CompactDashiDa51ShardsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = load_shards(INPUT_DIR)

    def test_surface_roundtrip_restores_exact_bytes(self) -> None:
        blob = encode_surface(self.rows)
        decoded = dict(decode_surface_bytes(blob))
        for row in self.rows:
            self.assertEqual(decoded[row["path_name"]], row["raw_bytes"])

    def test_semantic_roundtrip_restores_exact_bytes(self) -> None:
        blob = encode_semantic(self.rows)
        decoded = dict(decode_semantic_bytes(blob))
        for row in self.rows:
            self.assertEqual(decoded[row["path_name"]], row["raw_bytes"])

    def test_surface_beats_raw_total_and_semantic_stays_below_raw(self) -> None:
        surface_blob = encode_surface(self.rows)
        semantic_blob = encode_semantic(self.rows)
        stats = stats_compare(self.rows, surface_blob, semantic_blob)
        self.assertGreater(stats["surface"]["gain_over_raw"], 0)
        self.assertGreater(stats["semantic"]["gain_over_raw"], 0)


if __name__ == "__main__":
    unittest.main()
