#!/usr/bin/env python3
import json
import statistics
import sys
from collections import defaultdict


def load_rows(path):
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def median(values):
    return statistics.median(values) if values else None


def parity_ok(rows, engines):
    grouped = defaultdict(list)
    for row in rows:
        if row["engine"] in engines and row["ok"]:
            key = (row["scenario"], row["repeat"])
            grouped[key].append(row)

    failures = []
    for key, bucket in grouped.items():
        present = {row["engine"] for row in bucket}
        if present != set(engines):
            failures.append((key, "missing_engines"))
            continue
        checksums = {row["checksum"] for row in bucket}
        hashes = {row["final_state_hash"] for row in bucket}
        steps = {row["logical_steps_reached"] for row in bucket}
        if len(checksums) != 1 or len(hashes) != 1 or len(steps) != 1:
            failures.append((key, "value_mismatch"))
    return failures


def invalid_runs(rows):
    return [
        {
            "scenario": row["scenario"],
            "engine": row["engine"],
            "repeat": row["repeat"],
            "logical_steps_target": row["logical_steps_target"],
            "logical_steps_reached": row["logical_steps_reached"],
            "checkpoint_policy": row["checkpoint_policy"],
        }
        for row in rows
        if not row["ok"]
    ]


def cycle_at_least_report(rows):
    report = []
    for row in rows:
        if row["engine"] == "cycle" and row["ok"]:
            report.append(
                {
                    "scenario": row["scenario"],
                    "repeat": row["repeat"],
                    "logical_steps_target": row["logical_steps_target"],
                    "logical_steps_reached": row["logical_steps_reached"],
                    "logical_steps_overshoot": row.get("logical_steps_overshoot"),
                }
            )
    return report


def summarize(rows):
    by_key = defaultdict(list)
    for row in rows:
        by_key[(row["scenario"], row["engine"])].append(row)

    lines = []
    for (scenario, engine), bucket in sorted(by_key.items()):
        times = [row["cpu_seconds"] for row in bucket if row["ok"] and row["cpu_seconds"] is not None]
        reached = [row["logical_steps_reached"] for row in bucket if row["ok"]]
        overshoots = [row.get("logical_steps_overshoot") for row in bucket if row["ok"] and row.get("logical_steps_overshoot") is not None]
        effective = []
        for row in bucket:
            if row["ok"] and row["cpu_seconds"] is not None and row["logical_steps_reached"] > 0:
                effective.append(row["cpu_seconds"] / row["logical_steps_reached"])
        lines.append(
            {
                "scenario": scenario,
                "engine": engine,
                "runs": len(bucket),
                "median_cpu_seconds": median(times),
                "logical_steps_reached": sorted(set(reached)),
                "median_logical_steps_overshoot": median(overshoots),
                "median_cpu_seconds_per_logical_step": median(effective),
            }
        )
    return lines


def choose_next_target(rows):
    if any(not row["ok"] for row in rows):
        return "benchmark scenario/contract cleanup"
    medians = {}
    by_key = defaultdict(list)
    for row in rows:
        by_key[(row["scenario"], row["engine"])].append(row)

    for key, bucket in by_key.items():
        times = [row["cpu_seconds"] for row in bucket if row["ok"] and row["cpu_seconds"] is not None]
        medians[key] = median(times)

    def compiled_beats_frac_opt(scenario):
        compiled = medians.get((scenario, "compiled"))
        frac_opt = medians.get((scenario, "frac-opt"))
        if compiled is None or frac_opt is None:
            return False
        return compiled < frac_opt

    def compiled_within_margin(scenario, margin=0.15):
        compiled = medians.get((scenario, "compiled"))
        frac_opt = medians.get((scenario, "frac-opt"))
        if compiled is None or frac_opt is None:
            return False
        return compiled <= frac_opt * (1.0 + margin)

    if compiled_beats_frac_opt("primegame_medium") and compiled_beats_frac_opt("primegame_large"):
        return "continue compiled-path tuning"
    if compiled_within_margin("primegame_medium") and compiled_within_margin("primegame_large"):
        return "continue compiled-path tuning"
    return "keep frac-opt baseline"


def main(path):
    rows = load_rows(path)
    failures = parity_ok(rows, ["reg", "frac-opt", "compiled"])
    invalid = invalid_runs(rows)
    cycle_report = cycle_at_least_report(rows)
    summary = summarize(rows)
    next_target = choose_next_target(rows)

    report = {
        "rows": len(rows),
        "parity_failures": failures,
        "invalid_runs": invalid,
        "cycle_checkpoint_policy": "at-least",
        "cycle_report": cycle_report,
        "summary": summary,
        "next_target": next_target,
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: summarize_cpu_matrix.py <jsonl-path>", file=sys.stderr)
        raise SystemExit(2)
    main(sys.argv[1])
