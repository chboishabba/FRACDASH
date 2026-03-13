#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


def load_rows(path: Path) -> list[dict[str, object]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def summarize_timing(rows: list[dict[str, object]], engines: set[str]) -> dict[tuple[str, str], float]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        engine = row.get("engine")
        if engine not in engines:
            continue
        if not row.get("ok", False):
            continue
        cpu_seconds = row.get("cpu_seconds")
        if cpu_seconds is None:
            continue
        grouped[(row["scenario"], engine)].append(float(cpu_seconds))
    return {
        key: median(values)
        for key, values in grouped.items()
        if (m := median(values)) is not None
    }


def check_regression(
    baseline_stats: dict[tuple[str, str], float],
    current_stats: dict[tuple[str, str], float],
    tolerance: float,
    min_baseline_seconds: float,
) -> tuple[bool, list[dict[str, object]], list[dict[str, object]]]:
    failures = []
    skipped = []
    for key in sorted(current_stats):
        scenario, engine = key
        if key not in baseline_stats:
            failures.append(
                {
                    "scenario": scenario,
                    "engine": engine,
                    "status": "missing-baseline",
                    "message": "no baseline metric for this (scenario, engine).",
                }
            )
            continue

        base = baseline_stats[key]
        curr = current_stats[key]
        if base < min_baseline_seconds:
            skipped.append(
                {
                    "scenario": scenario,
                    "engine": engine,
                    "status": "low-baseline",
                    "message": "baseline is too short; skipping this timing check.",
                    "baseline_median": base,
                    "current_median": curr,
                    "min_baseline_seconds": min_baseline_seconds,
                }
            )
            continue
        if base <= 0:
            failures.append(
                {
                    "scenario": scenario,
                    "engine": engine,
                    "status": "invalid-baseline",
                    "message": "baseline timing is zero or negative.",
                    "baseline_median": base,
                    "current_median": curr,
                }
            )
            continue

        slowdown = (curr - base) / base
        if slowdown > tolerance:
            failures.append(
                {
                    "scenario": scenario,
                    "engine": engine,
                    "status": "regression",
                    "baseline_median": base,
                    "current_median": curr,
                    "slowdown_ratio": slowdown,
                    "tolerance": tolerance,
                    "message": f"timing regression: {(slowdown * 100):.2f}% slower than baseline.",
                }
            )

    for key in sorted(baseline_stats):
        if key not in current_stats:
            scenario, engine = key
            failures.append(
                {
                    "scenario": scenario,
                    "engine": engine,
                    "status": "missing-current",
                    "message": "no current metric for this (scenario, engine).",
                }
            )

    return not failures, failures, skipped


def require_repeat_depth(rows: list[dict[str, object]], engines: set[str], min_repeats: int) -> list[dict[str, object]]:
    if min_repeats <= 0:
        return []

    counts: dict[tuple[str, str], int] = defaultdict(int)
    for row in rows:
        if not row.get("ok", False):
            continue
        engine = row.get("engine")
        if engine not in engines:
            continue
        scenario = row.get("scenario")
        counts[(scenario, engine)] += 1

    return [
        {
            "scenario": scenario,
            "engine": engine,
            "status": "low-repetition",
            "message": f"{count} ok repeats; expected at least {min_repeats}.",
            "count": count,
            "required_min": min_repeats,
        }
        for (scenario, engine), count in counts.items()
        if count < min_repeats
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run timing regression check for CPU matrix baselines.")
    parser.add_argument("--baseline", required=True, help="Baseline JSONL from the prior known-good run.")
    parser.add_argument(
        "--current",
        required=True,
        help="Current JSONL run to validate.",
    )
    parser.add_argument(
        "--engine",
        action="append",
        default=None,
        help="Engine(s) to include in regression check. Repeatable; defaults to compiled, frac-opt, reg.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.20,
        help="Max allowed slowdown ratio (default: 0.20 for 20%%).",
    )
    parser.add_argument(
        "--min-repeats",
        type=int,
        default=3,
        help="Warn if any tracked (scenario, engine) has fewer than this many valid repeats.",
    )
    parser.add_argument(
        "--min-baseline-seconds",
        type=float,
        default=0.0001,
        help="Skip timing comparisons when baseline median is below this value (default: 0.0001).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    current_path = Path(args.current)
    if args.engine is None or len(args.engine) == 0:
        engines = {"compiled", "frac-opt", "reg"}
    else:
        engines = set(args.engine)

    baseline_rows = load_rows(baseline_path)
    current_rows = load_rows(current_path)

    baseline_stats = summarize_timing(baseline_rows, engines)
    current_stats = summarize_timing(current_rows, engines)

    passed, failures, skipped = check_regression(
        baseline_stats,
        current_stats,
        tolerance=args.tolerance,
        min_baseline_seconds=args.min_baseline_seconds,
    )
    repetitions = require_repeat_depth(current_rows, engines, args.min_repeats)
    failures.extend(repetitions)

    invalid = [
        {
            "scenario": row["scenario"],
            "engine": row["engine"],
            "repeat": row["repeat"],
            "error": row["error"],
        }
        for row in current_rows
        if not row.get("ok", False)
    ]

    report = {
        "baseline_path": str(baseline_path),
        "current_path": str(current_path),
        "engines": sorted(engines),
        "tolerance": args.tolerance,
        "min_repeats": args.min_repeats,
        "regressions": failures,
        "invalid_runs": invalid,
        "baseline_medians": {
            f"{scenario}:{engine}": value for (scenario, engine), value in baseline_stats.items()
        },
        "current_medians": {
            f"{scenario}:{engine}": value for (scenario, engine), value in current_stats.items()
        },
        "passed": passed and not failures and not repetitions and not invalid,
        "low_baseline_skips": skipped,
    }

    if not args.json:
        print(f"baseline: {baseline_path}")
        print(f"current:  {current_path}")
        print(f"engines:  {', '.join(sorted(engines))}")
        print(f"passed:   {report['passed']}")
        if skipped:
            print(f"low_baseline_skips: {len(skipped)}")
            for item in skipped:
                print(f"  {item}")
        if invalid:
            print(f"invalid_runs: {len(invalid)}")
            for item in invalid[:5]:
                print(f"  invalid: {item}")
        if failures:
            print(f"regressions: {len(failures)}")
            for item in failures[:10]:
                print(f"  {item}")
        if not report["passed"]:
            raise SystemExit(1)
        return

    print(json.dumps(report, indent=2))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
