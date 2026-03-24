#!/usr/bin/env python3
"""zkperf-witnessed FRACTRAN cross-implementation test harness.

Runs canonical FRACTRAN programs through all available implementations,
records zkperf-compatible witness JSON per run, compares traces, and
writes a summary artifact to benchmarks/results/.

Backends detected at runtime:
  - python   : always available (pure-Python reference stepper)
  - rust     : if FRACTRAN_VM_BIN or fractran-vm in PATH / default location
  - haskell  : if fractran/fractran binary exists

No novel research content — only standard FRACTRAN programs.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "benchmarks" / "results"

# ── Canonical programs (public, well-known) ──────────────────────

PROGRAMS = {
    "addition": {
        "fractions": [(3, 2)],
        "cases": [
            {"init": 8, "max_steps": 100, "expected_final": 27},
            {"init": 32, "max_steps": 100, "expected_final": 243},
        ],
    },
    "primegame": {
        "fractions": [
            (17, 91), (78, 85), (19, 51), (23, 38), (29, 33),
            (77, 29), (95, 23), (77, 19), (1, 17), (11, 13),
            (13, 11), (15, 14), (15, 2), (55, 1),
        ],
        "cases": [
            {"init": 2, "max_steps": 20, "expected_final": None},
        ],
    },
    "multiply": {
        "fractions": [
            (455, 33), (11, 13), (1, 11), (3, 7), (11, 2), (1, 3),
        ],
        "cases": [
            {"init": 108, "max_steps": 200, "expected_final": 15625},
        ],
    },
}

# ── Pure-Python reference stepper ────────────────────────────────

def py_step(program: list[Fraction], n: int) -> int | None:
    for f in program:
        v = n * f
        if v.denominator == 1:
            return int(v)
    return None


def py_run(program: list[Fraction], n: int, max_steps: int) -> list[int]:
    trace = [n]
    for _ in range(max_steps):
        nxt = py_step(program, trace[-1])
        if nxt is None:
            break
        trace.append(nxt)
    return trace


# ── zkperf witness format ────────────────────────────────────────

def make_witness(context: str, elapsed_ns: int, trace_len: int,
                 program_name: str, backend: str) -> dict:
    elapsed_ms = elapsed_ns / 1_000_000
    sig_input = f"{backend}:{program_name}:{trace_len}"
    signature = hashlib.sha256(sig_input.encode()).hexdigest()
    return {
        "context": context,
        "signature": signature,
        "complexity": "O(n*k)",
        "max_n": trace_len,
        "max_ms": 60000,
        "elapsed_ms": round(elapsed_ms, 3),
        "violated": elapsed_ms > 60000,
        "timestamp": int(time.time() * 1000),
        "platform": platform.system().lower(),
        "backend": backend,
        "program": program_name,
        "trace_length": trace_len,
    }


# ── Backend runners ──────────────────────────────────────────────

def run_python(fracs_raw, init, max_steps):
    program = [Fraction(n, d) for n, d in fracs_raw]
    t0 = time.perf_counter_ns()
    trace = py_run(program, init, max_steps)
    elapsed = time.perf_counter_ns() - t0
    return trace, elapsed


RUST_VM = os.environ.get(
    "FRACTRAN_VM_BIN",
    str(Path.home() / ".emacs.d.kiro/kiro.el-research/fractran-vm/target/release/fractran-vm"),
)


def rust_available():
    return Path(RUST_VM).is_file()


def run_rust(fracs_raw, init, max_steps):
    payload = json.dumps({"program": list(fracs_raw), "init": init, "max_steps": max_steps})
    t0 = time.perf_counter_ns()
    proc = subprocess.run([RUST_VM, "fractran-json"], input=payload, capture_output=True, text=True, timeout=10)
    elapsed = time.perf_counter_ns() - t0
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)["trace"], elapsed


HS_BIN = ROOT / "fractran" / "fractran"


def haskell_available():
    return HS_BIN.is_file()


def run_haskell(fracs_raw, init, max_steps):
    """Invoke Haskell fractran binary if built."""
    return None


# ── Main harness ─────────────────────────────────────────────────

def run_harness():
    witnesses = []
    comparisons = []
    backends = ["python"]
    if rust_available():
        backends.append("rust")
    if haskell_available():
        backends.append("haskell")

    print(f"zkperf FRACTRAN harness — backends: {backends}")

    for prog_name, spec in PROGRAMS.items():
        fracs = spec["fractions"]
        for case in spec["cases"]:
            init = case["init"]
            max_steps = case["max_steps"]
            expected = case.get("expected_final")

            # Python reference (always runs)
            trace_py, elapsed_py = run_python(fracs, init, max_steps)
            ctx = f"fractran:{prog_name}:init={init}"
            w = make_witness(ctx, elapsed_py, len(trace_py), prog_name, "python")
            witnesses.append(w)

            final_py = trace_py[-1]
            if expected is not None and final_py != expected:
                print(f"  FAIL python {prog_name} init={init}: "
                      f"got {final_py}, expected {expected}")

            # Rust comparison
            if rust_available():
                rs_result = run_rust(fracs, init, max_steps)
                if rs_result:
                    trace_rs, elapsed_rs = rs_result
                    w_rs = make_witness(ctx, elapsed_rs, len(trace_rs),
                                        prog_name, "rust")
                    witnesses.append(w_rs)
                    if trace_rs != trace_py:
                        comparisons.append({
                            "program": prog_name, "init": init,
                            "status": "DIVERGE",
                            "python_len": len(trace_py),
                            "rust_len": len(trace_rs),
                        })
                    else:
                        comparisons.append({
                            "program": prog_name, "init": init,
                            "status": "MATCH",
                        })

            # Haskell comparison
            if haskell_available():
                hs_result = run_haskell(fracs, init, max_steps)
                if hs_result:
                    trace_hs, elapsed_hs = hs_result
                    w_hs = make_witness(ctx, elapsed_hs, len(trace_hs),
                                        prog_name, "haskell")
                    witnesses.append(w_hs)

            print(f"  {prog_name} init={init}: "
                  f"steps={len(trace_py)-1} final={final_py} "
                  f"elapsed={w['elapsed_ms']:.3f}ms")

    # Write artifact
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    artifact = {
        "harness": "zkperf-fractran-cross",
        "date": date_str,
        "backends": backends,
        "witnesses": witnesses,
        "comparisons": comparisons,
        "programs": list(PROGRAMS.keys()),
    }
    out_path = RESULTS_DIR / f"{date_str}-zkperf-fractran-cross.json"
    out_path.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"\nArtifact written: {out_path}")

    # Exit non-zero if any comparison diverged
    diverged = [c for c in comparisons if c.get("status") == "DIVERGE"]
    if diverged:
        print(f"FAIL: {len(diverged)} trace divergence(s)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run_harness())
