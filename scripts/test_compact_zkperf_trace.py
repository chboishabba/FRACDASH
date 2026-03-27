#!/usr/bin/env python3
"""Regression checks for the compact zkperf trace codec."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "compact_zkperf_trace.py"
FIXTURE = ROOT / "benchmarks" / "results" / "2026-03-25-zkperf-zkperf-da51-python.trace-waveform.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("compact_zkperf_trace", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CompactZkperfTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.codec = _load_module()
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_roundtrip_exact(self) -> None:
        compact = self.codec.encode_trace(self.fixture)
        rebuilt = self.codec.decode_trace(compact)
        self.assertIn("dashi_class", compact["rows"][0])
        self.assertIn("dashi_family", compact["rows"][0])
        self.assertEqual(rebuilt, self.fixture)

    def test_compact_payload_is_smaller(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "source.json"
            compact_path = Path(temp_dir) / "compact.json"
            roundtrip_path = Path(temp_dir) / "roundtrip.json"
            source_path.write_text(json.dumps(self.fixture, indent=2) + "\n", encoding="utf-8")
            stats = self.codec.compression_stats(source_path, compact_path, roundtrip_path)
            self.assertTrue(stats["roundtrip_equal"])
            self.assertLess(stats["compact_bytes"], stats["source_bytes"])

    def test_motif_roundtrip_exact(self) -> None:
        compact = self.codec.encode_trace(self.fixture)
        motif = self.codec.encode_motif(compact)
        rebuilt = self.codec.decode_motif(motif)
        self.assertEqual(rebuilt, compact)

    def test_motif_payload_is_smaller_than_compact(self) -> None:
        compact = self.codec.encode_trace(self.fixture)
        with tempfile.TemporaryDirectory() as temp_dir:
            compact_path = Path(temp_dir) / "compact.json"
            motif_path = Path(temp_dir) / "motif.json"
            roundtrip_path = Path(temp_dir) / "compact-roundtrip.json"
            compact_path.write_text(json.dumps(compact, indent=2) + "\n", encoding="utf-8")
            stats = self.codec.motif_compression_stats(compact_path, motif_path, roundtrip_path)
            self.assertTrue(stats["roundtrip_equal"])
            self.assertLess(stats["motif_bytes"], stats["source_bytes"])

    def test_semantic_motif_roundtrip_exact(self) -> None:
        compact = self.codec.encode_trace(self.fixture)
        motif = self.codec.encode_semantic_motif(compact)
        rebuilt = self.codec.decode_semantic_motif(motif)
        self.assertEqual(rebuilt, compact)

    def test_semantic_motif_payload_is_smaller_than_compact(self) -> None:
        compact = self.codec.encode_trace(self.fixture)
        with tempfile.TemporaryDirectory() as temp_dir:
            compact_path = Path(temp_dir) / "compact.json"
            semantic_path = Path(temp_dir) / "semantic-motif.json"
            roundtrip_path = Path(temp_dir) / "semantic-roundtrip.json"
            compact_path.write_text(json.dumps(compact, indent=2) + "\n", encoding="utf-8")
            stats = self.codec.semantic_motif_compression_stats(compact_path, semantic_path, roundtrip_path)
            self.assertTrue(stats["roundtrip_equal"])
            self.assertLess(stats["semantic_motif_bytes"], stats["source_bytes"])


if __name__ == "__main__":
    unittest.main()
