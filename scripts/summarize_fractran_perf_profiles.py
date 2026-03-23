#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary(cpu: dict[str, object], gpu: dict[str, object]) -> dict[str, object]:
    cpu_assessment = cpu["assessment"]
    gpu_assessment = gpu["assessment"]
    return {
        "cpu_decision": cpu_assessment["decision"],
        "gpu_decision": gpu_assessment["decision"],
        "obvious_now": [
            item
            for item in [
                "tighten GPU routing around warm-resident wins" if gpu_assessment["obvious_large_gpu_gain_region_exists"] else None,
                "profile-based GPU host/setup reduction" if gpu_assessment["cold_start_penalty_cases"] else None,
            ]
            if item is not None
        ],
        "possible_but_unproven": [
            "another compiled rule-selection optimization round",
            "CPU batched exponent-vector execution",
            "program-family-specific mask or threshold shortcuts",
        ],
        "not_worth_immediate_effort": [
            "new general exact-step CPU engine replacing compiled/frac-opt from scratch"
            if not cpu_assessment["obvious_large_cpu_gain_over_imported_baseline"]
            else "none-yet"
        ],
        "cpu_assessment": cpu_assessment,
        "gpu_assessment": gpu_assessment,
    }


def build_markdown(summary: dict[str, object]) -> str:
    cpu = summary["cpu_assessment"]
    gpu = summary["gpu_assessment"]
    lines = [
        "# FRACDASH CPU/GPU Profiling Decision",
        "",
        "## Bottom Line",
        "",
        f"- CPU: `{summary['cpu_decision']}`",
        f"- GPU: `{summary['gpu_decision']}`",
        "",
        "## Obvious Now",
    ]
    obvious = summary["obvious_now"] or ["No obvious immediate optimization target was detected."]
    lines.extend([f"- {item}" for item in obvious])
    lines.extend(
        [
            "",
            "## CPU Read",
            "",
            f"- `compiled` wins all sampled exact-step cases: `{cpu['compiled_wins_all_sampled_exact_cases']}`",
            f"- obvious large CPU gain over imported baseline: `{cpu['obvious_large_cpu_gain_over_imported_baseline']}`",
            "",
            "## GPU Read",
            "",
            f"- warm GPU-preferred cases: `{len(gpu['warm_gpu_preferred_cases'])}`",
            f"- cold-start penalty cases: `{len(gpu['cold_start_penalty_cases'])}`",
            "",
            "## Next Performance Focus",
            "",
            "- refine the warm-resident GPU routing boundary",
            "- reduce host/setup overhead on the GPU path before attempting deeper kernel changes",
            "- only return to CPU exact-step tuning if a new profiling run surfaces a fresh dominant hotspot or a new workload where `compiled` clearly loses",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize FRACDASH CPU/GPU profiling artifacts.")
    parser.add_argument("--cpu", type=Path, required=True, help="CPU profiling JSON artifact.")
    parser.add_argument("--gpu", type=Path, required=True, help="GPU profiling JSON artifact.")
    parser.add_argument("--json-output", type=Path, help="Write combined JSON summary to this path.")
    parser.add_argument("--md-output", type=Path, help="Write markdown summary to this path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args()

    summary = build_summary(load_json(args.cpu), load_json(args.gpu))
    markdown = build_markdown(summary)

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.md_output:
        args.md_output.parent.mkdir(parents=True, exist_ok=True)
        args.md_output.write_text(markdown, encoding="utf-8")

    if args.json or (not args.json_output and not args.md_output):
        print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
