#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHI_AGDA_ROOT = ROOT.parent / "dashi_agda"


@dataclass(frozen=True)
class SurfaceModule:
    path: str
    role: str
    lane: str
    required_patterns: tuple[str, ...]


WAVE_MODULES = (
    SurfaceModule(
        path="DASHI/Unifier.agda",
        role="top-level wave lift surface with unitary evolution placeholder",
        lane="wave",
        required_patterns=("record WaveLift", "U : ℝ →", "Hgen : Set"),
    ),
    SurfaceModule(
        path="DASHI/Quantum/Stone.agda",
        role="Stone group / continuity package for wave evolution",
        lane="wave",
        required_patterns=("record StoneGroup", "record StoneContinuity", "Stone-theorem"),
    ),
    SurfaceModule(
        path="DASHI/Physics/WaveLiftEvenSubalgebra.agda",
        role="wave-lift to even-subalgebra bridge prototype",
        lane="wave",
        required_patterns=("record WaveLift", "record LiftFactorsThroughEven", "waveLift⇒evenSubalgebra"),
    ),
    SurfaceModule(
        path="DASHI/Physics/Closure/Algebra/WaveRegime.agda",
        role="closure-heavy wave regime ladder",
        lane="wave",
        required_patterns=("module DASHI.Physics.Closure.Algebra.WaveRegime", "WaveObservableTransportGeometry", "Regime"),
    ),
)


DIFFUSION_MODULES = (
    SurfaceModule(
        path="DASHI/Physics/Closure/ContractionDiffusionPair.agda",
        role="contraction/diffusion conceptual pair",
        lane="diffusion",
        required_patterns=("record ContractionDiffusionPair", "updateKD", "updateDK"),
    ),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_module(module: SurfaceModule) -> dict[str, object]:
    full_path = DASHI_AGDA_ROOT / module.path
    if not full_path.exists():
        return {
            "path": str(full_path),
            "lane": module.lane,
            "role": module.role,
            "exists": False,
            "matched_patterns": [],
            "required_patterns": list(module.required_patterns),
            "pattern_pass": False,
        }
    text = read_text(full_path)
    matched = [pattern for pattern in module.required_patterns if pattern in text]
    return {
        "path": str(full_path),
        "lane": module.lane,
        "role": module.role,
        "exists": True,
        "matched_patterns": matched,
        "required_patterns": list(module.required_patterns),
        "pattern_pass": len(matched) == len(module.required_patterns),
    }


def classify_wave_surface(wave_modules: list[dict[str, object]]) -> dict[str, object]:
    found = [item for item in wave_modules if item["exists"]]
    all_patterns = all(bool(item["pattern_pass"]) for item in found) and bool(found)
    return {
        "wave_surface_present": bool(found),
        "wave_surface_pattern_complete": all_patterns,
        "interpretation": (
            "formal_wave_target_present"
            if bool(found)
            else "no_formal_wave_target_detected"
        ),
    }


def summary_payload() -> dict[str, object]:
    wave_modules = [check_module(module) for module in WAVE_MODULES]
    diffusion_modules = [check_module(module) for module in DIFFUSION_MODULES]
    wave_summary = classify_wave_surface(wave_modules)
    return {
        "date": date.today().isoformat(),
        "dashi_agda_root": str(DASHI_AGDA_ROOT),
        "wave_modules": wave_modules,
        "diffusion_modules": diffusion_modules,
        "wave_summary": wave_summary,
        "current_fracdash_decision": {
            "formal_lane": "wave remains active as an upstream semantic and bridge-alignment target",
            "solver_lane": "heat remains the least-bad executable runtime comparison family",
            "current_mainline": "proof-carrying / auditable execution",
        },
        "bridge_boundary": {
            "upstream": "wave/unitary semantics exist in ../dashi_agda",
            "local": "FRACDASH currently realizes a compressed, empirically dissipative executable subset",
            "claim": "no current FRACDASH artifact should be read as a successful executable wave solver",
        },
    }


def markdown_summary(payload: dict[str, object]) -> str:
    lines = [
        "# dashi_agda Wave Surface Check",
        "",
        f"- Date: `{payload['date']}`",
        f"- Upstream root: `{payload['dashi_agda_root']}`",
        f"- Wave surface present: `{payload['wave_summary']['wave_surface_present']}`",
        f"- Wave surface pattern-complete: `{payload['wave_summary']['wave_surface_pattern_complete']}`",
        "",
        "## Wave Modules",
        "",
    ]
    for item in payload["wave_modules"]:
        lines.append(
            f"- `{Path(item['path']).name}`: `{len(item['matched_patterns'])}/{len(item['required_patterns'])}` patterns, role `{item['role']}`"
        )
    lines.extend(
        [
            "",
            "## Diffusion Modules",
            "",
        ]
    )
    for item in payload["diffusion_modules"]:
        lines.append(
            f"- `{Path(item['path']).name}`: `{len(item['matched_patterns'])}/{len(item['required_patterns'])}` patterns, role `{item['role']}`"
        )
    lines.extend(
        [
            "",
            "## Current Read",
            "",
            "- `../dashi_agda` contains a real wave/unitary semantic lane.",
            "- FRACDASH does not yet realize that lane as a numerically good executable wave solver.",
            "- `wave` therefore remains a formal bridge target, while `heat` remains the least-bad current runtime comparison family.",
            "- The near-term mainline remains proof-carrying / auditable execution.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Record the upstream dashi_agda wave surface and the current FRACDASH boundary."
    )
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    parser.add_argument("--markdown", action="store_true", help="Print markdown summary.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON output path. Defaults to benchmarks/results/<today>-dashi-agda-wave-surface.json",
    )
    parser.add_argument(
        "--markdown-output",
        default=None,
        help="Optional markdown output path. Defaults to benchmarks/results/<today>-dashi-agda-wave-surface.md",
    )
    args = parser.parse_args()

    if not DASHI_AGDA_ROOT.exists():
        raise SystemExit(f"missing upstream root: {DASHI_AGDA_ROOT}")

    payload = summary_payload()
    output_path = (
        Path(args.output)
        if args.output
        else ROOT / "benchmarks/results" / f"{date.today().isoformat()}-dashi-agda-wave-surface.json"
    )
    markdown_path = (
        Path(args.markdown_output)
        if args.markdown_output
        else ROOT / "benchmarks/results" / f"{date.today().isoformat()}-dashi-agda-wave-surface.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown_summary(payload), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
        return
    if args.markdown:
        print(markdown_summary(payload), end="")
        return
    print(f"wrote {output_path}")
    print(f"wrote {markdown_path}")
    print(f"wave_surface_present={payload['wave_summary']['wave_surface_present']}")


if __name__ == "__main__":
    main()
