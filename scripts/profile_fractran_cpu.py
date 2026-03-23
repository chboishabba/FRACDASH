#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRACTRAN_DIR = ROOT / "fractran"
BENCH_BIN = FRACTRAN_DIR / "fractran-bench"

DEFAULT_EXACT_ENGINES = ("compiled", "frac-opt", "reg")
DEFAULT_SCENARIOS = ("mult_smoke", "primegame_small", "primegame_medium", "primegame_large")

RTS_TOTAL_RE = re.compile(r"^\s*Total\s+time\s+([0-9.]+)s", re.MULTILINE)
RTS_MUT_RE = re.compile(r"^\s*MUT\s+time\s+([0-9.]+)s", re.MULTILINE)
RTS_GC_RE = re.compile(r"^\s*GC\s+time\s+([0-9.]+)s", re.MULTILINE)
RTS_ALLOC_RE = re.compile(r"^\s*([\d,]+)\s+bytes allocated in the heap", re.MULTILINE)
PROF_ROW_RE = re.compile(
    r"^(?P<cost_centre>\S.*?)\s{2,}(?P<module>\S+)\s{2,}(?P<src>\S.*?)\s+(?P<time>[0-9.]+)\s+(?P<alloc>[0-9.]+)\s*$"
)


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def load_rows(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def summarize_timings(rows: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    grouped: dict[tuple[str, str], list[float]] = {}
    logical_steps: dict[tuple[str, str], int] = {}
    for row in rows:
        if not row.get("ok", False):
            continue
        key = (str(row["scenario"]), str(row["engine"]))
        grouped.setdefault(key, []).append(float(row["cpu_seconds"]))
        logical_steps[key] = int(row["logical_steps_reached"])
    summary: dict[str, dict[str, object]] = {}
    for (scenario, engine), times in sorted(grouped.items()):
        med = median(times)
        steps = logical_steps[(scenario, engine)]
        summary[f"{scenario}:{engine}"] = {
            "scenario": scenario,
            "engine": engine,
            "median_cpu_seconds": med,
            "logical_steps_reached": steps,
            "median_cpu_seconds_per_logical_step": (med / steps) if med and steps else None,
            "runs": len(times),
        }
    return summary


def parse_rts(stderr_text: str) -> dict[str, float | int | None]:
    def extract_float(pattern: re.Pattern[str]) -> float | None:
        match = pattern.search(stderr_text)
        return float(match.group(1)) if match else None

    alloc_match = RTS_ALLOC_RE.search(stderr_text)
    return {
        "total_time_seconds": extract_float(RTS_TOTAL_RE),
        "mut_time_seconds": extract_float(RTS_MUT_RE),
        "gc_time_seconds": extract_float(RTS_GC_RE),
        "bytes_allocated": int(alloc_match.group(1).replace(",", "")) if alloc_match else None,
    }


def parse_prof(prof_text: str) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    capture = False
    for line in prof_text.splitlines():
        if line.startswith("COST CENTRE"):
            capture = True
            continue
        if not capture:
            continue
        if not line.strip():
            if rows:
                break
            continue
        match = PROF_ROW_RE.match(line.rstrip())
        if not match:
            continue
        rows.append(
            {
                "cost_centre": match.group("cost_centre").strip(),
                "module": match.group("module").strip(),
                "src": match.group("src").strip(),
                "time_percent": float(match.group("time")),
                "alloc_percent": float(match.group("alloc")),
            }
        )
    rows.sort(key=lambda row: (-float(row["time_percent"]), -float(row["alloc_percent"])))
    return {
        "top_by_time": rows[:10],
        "top_by_alloc": sorted(rows, key=lambda row: (-float(row["alloc_percent"]), -float(row["time_percent"])))[:10],
    }


def scenario_mode(scenario: str) -> str:
    return "exact" if scenario != "cycle" else "at-least"


def run_bench_rows(scenarios: list[str], engines: list[str], repeats: int) -> list[dict[str, object]]:
    with tempfile.NamedTemporaryFile(prefix="fractran-cpu-profile-", suffix=".jsonl", delete=False) as handle:
        out_path = Path(handle.name)
    try:
        for scenario in scenarios:
            for engine in engines:
                checkpoint_policy = "at-least" if engine == "cycle" else "exact"
                run(
                    [
                        str(BENCH_BIN),
                        "--scenario",
                        scenario,
                        "--engine",
                        engine,
                        "--mode",
                        "logical-steps",
                        "--checkpoint-policy",
                        checkpoint_policy,
                        "--repeats",
                        str(repeats),
                        "--output",
                        str(out_path),
                    ],
                    FRACTRAN_DIR,
                )
        return load_rows(out_path)
    finally:
        out_path.unlink(missing_ok=True)


def profile_engine_case(scenario: str, engine: str) -> dict[str, object]:
    checkpoint_policy = "at-least" if engine == "cycle" else "exact"
    prof_path = FRACTRAN_DIR / "fractran-bench.prof"
    prof_path.unlink(missing_ok=True)
    result = subprocess.run(
        [
            str(BENCH_BIN),
            "--scenario",
            scenario,
            "--engine",
            engine,
            "--mode",
            "logical-steps",
            "--checkpoint-policy",
            checkpoint_policy,
            "--repeats",
            "1",
            "+RTS",
            "-p",
            "-s",
            "-RTS",
        ],
        cwd=FRACTRAN_DIR,
        text=True,
        capture_output=True,
        check=True,
    )
    prof_text = prof_path.read_text(encoding="utf-8") if prof_path.exists() else ""
    return {
        "scenario": scenario,
        "engine": engine,
        "rts": parse_rts(result.stderr),
        "profile": parse_prof(prof_text),
    }


def derive_cpu_assessment(timing_summary: dict[str, dict[str, object]], profile_cases: list[dict[str, object]]) -> dict[str, object]:
    comparisons = []
    exact_scenarios = sorted({entry["scenario"] for entry in timing_summary.values() if entry["engine"] == "compiled"})
    compiled_wins_all = True
    for scenario in exact_scenarios:
        compiled = timing_summary.get(f"{scenario}:compiled")
        frac_opt = timing_summary.get(f"{scenario}:frac-opt")
        if not compiled or not frac_opt:
            continue
        compiled_med = float(compiled["median_cpu_seconds"])
        frac_opt_med = float(frac_opt["median_cpu_seconds"])
        ratio = compiled_med / frac_opt_med if frac_opt_med > 0 else None
        comparisons.append(
            {
                "scenario": scenario,
                "compiled_over_frac_opt": ratio,
                "compiled_faster": ratio is not None and ratio < 1.0,
            }
        )
        if ratio is None or ratio >= 1.0:
            compiled_wins_all = False

    compiled_profiles = [case for case in profile_cases if case["engine"] == "compiled"]
    top_hotspots = []
    for case in compiled_profiles:
        top = case["profile"]["top_by_time"][:3]
        top_hotspots.append({"scenario": case["scenario"], "hotspots": top})

    return {
        "compiled_vs_frac_opt": comparisons,
        "compiled_wins_all_sampled_exact_cases": compiled_wins_all,
        "obvious_large_cpu_gain_over_imported_baseline": not compiled_wins_all,
        "top_compiled_hotspots": top_hotspots,
        "decision": (
            "no-obvious-large-exact-step-cpu-win"
            if compiled_wins_all
            else "cpu-baseline-still-has-obvious-gap"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile the FRACDASH CPU FRACTRAN paths before optimization.")
    parser.add_argument("--scenario", action="append", choices=DEFAULT_SCENARIOS, help="Scenario(s) to profile.")
    parser.add_argument(
        "--engine",
        action="append",
        choices=DEFAULT_EXACT_ENGINES,
        help="Exact-step engine(s) to time/profile. Defaults to compiled, frac-opt, reg.",
    )
    parser.add_argument("--include-cycle", action="store_true", help="Also profile the cycle engine separately.")
    parser.add_argument("--repeats", type=int, default=5, help="Timing repeats for the exact-step matrix.")
    parser.add_argument("--output", type=Path, help="Write JSON artifact to this path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args()

    scenarios = list(args.scenario or DEFAULT_SCENARIOS)
    exact_engines = list(args.engine or DEFAULT_EXACT_ENGINES)

    run(["./build.sh"], FRACTRAN_DIR)
    timing_rows = run_bench_rows(scenarios, exact_engines + (["cycle"] if args.include_cycle else []), args.repeats)
    timing_summary = summarize_timings(timing_rows)

    run(["./build.sh", "--profile"], FRACTRAN_DIR)
    profile_cases = [profile_engine_case(scenario, engine) for scenario in scenarios for engine in exact_engines]
    cycle_profiles = [profile_engine_case(scenario, "cycle") for scenario in scenarios] if args.include_cycle else []
    run(["./build.sh"], FRACTRAN_DIR)

    report = {
        "scenarios": scenarios,
        "exact_engines": exact_engines,
        "include_cycle": args.include_cycle,
        "timing_summary": timing_summary,
        "profile_cases": profile_cases,
        "cycle_profiles": cycle_profiles,
        "assessment": derive_cpu_assessment(timing_summary, profile_cases),
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json or not args.output:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
