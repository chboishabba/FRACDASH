#!/usr/bin/env python3
"""Regression checks for the DA51 inner-payload codec."""

from __future__ import annotations

import unittest
from pathlib import Path

from compact_dashi_da51_inner import decode_inner_bytes, encode_inner, stats_compare
from compact_dashi_da51_shards import encode_surface, load_shards


ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "dashi_agda" / "da51_shards"


class CompactDashiDa51InnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = load_shards(INPUT_DIR)

    def test_roundtrip_restores_exact_bytes(self) -> None:
        blob = encode_inner(self.rows)
        decoded = dict(decode_inner_bytes(blob))
        for row in self.rows:
            self.assertEqual(decoded[row["path_name"]], row["raw_bytes"])

    def test_inner_beats_raw_total(self) -> None:
        blob = encode_inner(self.rows)
        aggregate_surface = encode_surface(self.rows)
        stats = stats_compare(self.rows, blob, len(aggregate_surface))
        self.assertGreater(stats["inner"]["gain_over_raw"], 0)

    def test_inner_beats_current_aggregate_surface_codec(self) -> None:
        blob = encode_inner(self.rows)
        aggregate_surface = encode_surface(self.rows)
        self.assertLess(len(blob), len(aggregate_surface))


if __name__ == "__main__":
    unittest.main()
