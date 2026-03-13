#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gpu.dashicore_bridge import import_summary
from gpu.fractran_layout import compile_program, load_demo_program, summarize_trace


SCENARIOS = {
    "mult_smoke": {"program": "mult", "init": 2, "take": 2},
    "primegame_small": {"program": "primegame", "init": 2, "take": 1000},
}


def read_compiled_baseline(scenario_name: str) -> dict[str, str]:
    bench = ROOT / "fractran" / "fractran-bench"
    if not bench.exists():
        raise FileNotFoundError(f"missing benchmark binary: {bench}")
    cmd = [
        str(bench),
        "--scenario",
        scenario_name,
        "--engine",
        "compiled",
        "--mode",
        "logical-steps",
        "--checkpoint-policy",
        "exact",
        "--repeats",
        "1",
    ]
    proc = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    data = {}
    for line in proc.stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def compare_scenario(scenario_name: str) -> dict[str, object]:
    scenario = SCENARIOS[scenario_name]
    fractions = load_demo_program(scenario["program"])
    layout = compile_program(scenario["program"], fractions)
    trace = layout.run_trace(scenario["init"], scenario["take"])
    summary = summarize_trace(layout, trace)
    baseline = read_compiled_baseline(scenario_name)

    comparison = {
        "logical_steps_reached_match": str(summary["logical_steps_reached"]) == baseline["logical_steps_reached"],
        "emitted_states_match": str(summary["emitted_states"]) == baseline["emitted_states"],
        "checksum_match": str(summary["checksum"]) == baseline["checksum"],
        "final_state_hash_match": summary["final_state_hash"] == baseline["final_state_hash"],
    }

    return {
        "scenario": scenario_name,
        "layout": layout.summary(),
        "python_summary": summary,
        "compiled_baseline": {
            "logical_steps_reached": baseline["logical_steps_reached"],
            "emitted_states": baseline["emitted_states"],
            "checksum": baseline["checksum"],
            "final_state_hash": baseline["final_state_hash"],
        },
        "comparison": comparison,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify the FRACDASH dense FRACTRAN GPU contract against the compiled CPU baseline."
    )
    parser.add_argument(
        "--scenario",
        action="append",
        choices=sorted(SCENARIOS),
        help="Scenario(s) to check. Defaults to all.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    scenarios = args.scenario or sorted(SCENARIOS)
    result = {
        "dashicore_import": import_summary(),
        "scenarios": [compare_scenario(name) for name in scenarios],
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    print("dashiCORE root:", result["dashicore_import"]["dashicore_root"])
    for scenario in result["scenarios"]:
        print(f"scenario={scenario['scenario']}")
        print("  layout:", scenario["layout"])
        print("  python_summary:", scenario["python_summary"])
        print("  compiled_baseline:", scenario["compiled_baseline"])
        print("  comparison:", scenario["comparison"])


if __name__ == "__main__":
    main()
