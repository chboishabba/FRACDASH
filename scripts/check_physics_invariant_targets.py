#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from physics_invariant_analysis import (
    CURVATURE_MEAN_SPREAD_THRESHOLD,
    DEFECT_NONINCREASE_THRESHOLD,
    FORWARD_CONE_MAX_SUCCESSOR_HAMMING,
    GEODESIC_NEAR_MIN_THRESHOLD,
    LOCALITY_MAX_CHANGED_REGISTERS,
    LOCALITY_MAX_L1_STEP_DELTA,
    PERTURBATION_THRESHOLDS,
    TARGET_SUITE_VERSION,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "benchmarks" / "results"
PHYSICS_IDS = tuple(f"physics{i}" for i in range(2, 9))
GEOMETRY_IDS = tuple(pid for pid in PHYSICS_IDS if pid != "physics4")
EPS = 1e-12


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    details: dict[str, object]


def _latest_by_template(pattern: str, regex: str) -> dict[str, Path]:
    rx = re.compile(regex)
    matched: dict[str, Path] = {}
    for path in sorted(RESULTS_DIR.glob(pattern)):
        m = rx.search(path.name)
        if m is None:
            continue
        template = m.group(1)
        prev = matched.get(template)
        if prev is None or path.name > prev.name:
            matched[template] = path
    return matched


def _load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _phase2_metrics(payload: dict[str, object]) -> dict[str, object]:
    full = payload.get("full_space_profile", {})
    fixed = payload.get("fixed_walk_summary", {})
    action = payload.get("action_monotonicity", {})
    tail = payload.get("long_tail_diagnosis", {})
    return {
        "edges": int(full.get("edges", 0)),
        "longest_chain": int(full.get("longest_chain", 0)),
        "cycles": int(fixed.get("cycle", 0)),
        "timeout": int(fixed.get("timeout", 0)),
        "action_increases": None if "increases" not in action else int(action.get("increases", 0)),
        "still_timeout": None if "still_timeout" not in tail else int(tail.get("still_timeout", 0)),
    }


def _invariant_metrics(payload: dict[str, object]) -> dict[str, object]:
    best = payload.get("best_candidate", {})
    return {
        "name": str(best.get("name", "")),
        "nonincrease_ratio": float(best.get("nonincrease_ratio", 0.0)),
        "strict_decrease_ratio": float(best.get("strict_decrease_ratio", 0.0)),
        "increase_ratio": float(best.get("increase_ratio", 0.0)),
        "increases": int(best.get("increases", 0)),
    }


def _target_suite_metrics(payload: dict[str, object]) -> dict[str, object]:
    suite = payload.get("physics_target_suite", {})
    exact = suite.get("exact_laws", {})
    statistical = suite.get("statistical_laws", {})
    perturbation = statistical.get("perturbation_stability", {})
    return {
        "version": suite.get("version", ""),
        "exact": exact,
        "statistical": statistical,
        "perturbation": perturbation.get("families", {}),
    }


def _check(cond: bool, name: str, **details: object) -> CheckResult:
    return CheckResult(name=name, passed=cond, details=details)


def _all_present(phase2: dict[str, Path], invariants: dict[str, Path]) -> list[CheckResult]:
    missing_phase2 = sorted(set(PHYSICS_IDS) - set(phase2))
    missing_invariants = sorted(set(PHYSICS_IDS) - set(invariants))
    return [
        _check(
            not missing_phase2 and not missing_invariants,
            "coverage.physics2_to_physics8",
            missing_phase2=missing_phase2,
            missing_invariants=missing_invariants,
        )
    ]


def _lyapunov_checks(invariants: dict[str, dict[str, object]]) -> list[CheckResult]:
    out: list[CheckResult] = []
    nonincrease = {k: v["nonincrease_ratio"] for k, v in invariants.items()}
    increases = {k: v["increases"] for k, v in invariants.items()}
    names = {k: v["name"] for k, v in invariants.items()}
    out.append(
        _check(
            all(abs(float(v) - 1.0) <= EPS for v in nonincrease.values()),
            "lyapunov.nonincrease",
            nonincrease_ratio=nonincrease,
        )
    )
    out.append(
        _check(
            all(int(v) == 0 for v in increases.values()),
            "lyapunov.zero_increase_edges",
            increase_edges=increases,
        )
    )
    expected_name_ok = True
    for key, name in names.items():
        if key == "physics4":
            if name not in {"weighted_abs_search", "distance_to_cycle"}:
                expected_name_ok = False
        elif name != "distance_to_cycle":
            expected_name_ok = False
    out.append(
        _check(
            expected_name_ok,
            "lyapunov.best_candidate_identity",
            best_candidate_name=names,
        )
    )
    return out


def _target_suite_checks(targets: dict[str, dict[str, object]]) -> list[CheckResult]:
    out: list[CheckResult] = []
    versions = {key: value["version"] for key, value in targets.items()}
    out.append(
        _check(
            all(version == TARGET_SUITE_VERSION for version in versions.values()),
            "target_suite.version",
            version=versions,
        )
    )

    source_charge = {
        key: value["exact"]["source_charge_conservation"]["changed_edges_by_register"]
        for key, value in targets.items()
    }
    out.append(
        _check(
            all(
                int(registers["R1"]) == 0 and int(registers["R2"]) == 0
                for registers in source_charge.values()
            ),
            "exact.source_charge_conservation",
            changed_edges_by_register=source_charge,
        )
    )

    source_parity = {
        key: value["exact"]["source_parity_sector_preservation"]["parity_breaks"]
        for key, value in targets.items()
    }
    out.append(
        _check(
            all(all(int(count) == 0 for count in parity_breaks.values()) for parity_breaks in source_parity.values()),
            "exact.source_parity_sector_preservation",
            parity_breaks=source_parity,
        )
    )

    locality = {
        key: {
            "max_changed_registers": int(value["exact"]["locality_radius_bound"]["max_changed_registers"]),
            "max_l1_step_delta": int(value["exact"]["locality_radius_bound"]["max_l1_step_delta"]),
        }
        for key, value in targets.items()
    }
    out.append(
        _check(
            all(
                item["max_changed_registers"] <= LOCALITY_MAX_CHANGED_REGISTERS
                and item["max_l1_step_delta"] <= LOCALITY_MAX_L1_STEP_DELTA
                for item in locality.values()
            ),
            "exact.locality_radius_bound",
            locality=locality,
        )
    )

    forward_cone = {
        key: int(value["exact"]["forward_cone_bound"]["max_successor_hamming"])
        for key, value in targets.items()
    }
    out.append(
        _check(
            all(value <= FORWARD_CONE_MAX_SUCCESSOR_HAMMING for value in forward_cone.values()),
            "exact.forward_cone_bound",
            max_successor_hamming=forward_cone,
        )
    )

    cycle_distance = {
        key: value["exact"]["cycle_distance_nonincrease"]
        for key, value in targets.items()
    }
    out.append(
        _check(
            all(
                abs(float(item["nonincrease_ratio"]) - 1.0) <= EPS and int(item["increases"]) == 0
                for item in cycle_distance.values()
            ),
            "exact.cycle_distance_nonincrease",
            cycle_distance=cycle_distance,
        )
    )

    perturbation_details = {
        key: {
            family: float(targets[key]["perturbation"][family]["nonexpansion_ratio"])
            for family in PERTURBATION_THRESHOLDS
        }
        for key in targets
    }
    out.append(
        _check(
            all(
                perturbation_details[key][family] >= threshold
                for key in targets
                for family, threshold in PERTURBATION_THRESHOLDS.items()
            ),
            "stat.perturbation_stability",
            nonexpansion_ratio=perturbation_details,
        )
    )

    geodesic = {
        key: targets[key]["statistical"]["geodesic_like_flow"]
        for key in GEOMETRY_IDS
    }
    out.append(
        _check(
            all(
                bool(item["available"]) and float(item["near_min_ratio"]) >= GEODESIC_NEAR_MIN_THRESHOLD
                for item in geodesic.values()
            ),
            "stat.geodesic_like_flow",
            geodesic_like_flow={
                key: {
                    "near_min_ratio": geodesic[key]["near_min_ratio"],
                    "exact_min_ratio": geodesic[key]["exact_min_ratio"],
                }
                for key in geodesic
            },
        )
    )

    curvature = {
        key: targets[key]["statistical"]["curvature_like_concentration"]
        for key in GEOMETRY_IDS
    }
    out.append(
        _check(
            all(
                bool(item["available"]) and float(item["mean_neighbor_spread"]) >= CURVATURE_MEAN_SPREAD_THRESHOLD
                for item in curvature.values()
            ),
            "stat.curvature_like_concentration",
            mean_neighbor_spread={
                key: curvature[key]["mean_neighbor_spread"]
                for key in curvature
            },
        )
    )

    physics4_curvature = targets["physics4"]["statistical"]["curvature_like_concentration"]
    out.append(
        _check(
            abs(float(physics4_curvature["mean_neighbor_spread"]) - 0.0) <= EPS,
            "physics4.flat_curvature_signature",
            mean_neighbor_spread=physics4_curvature["mean_neighbor_spread"],
        )
    )

    defect = {
        key: float(value["statistical"]["defect_attraction"]["nonincrease_ratio"])
        for key, value in targets.items()
    }
    out.append(
        _check(
            all(value >= DEFECT_NONINCREASE_THRESHOLD for value in defect.values()),
            "stat.defect_attraction",
            nonincrease_ratio=defect,
        )
    )
    return out


def _hybrid_checks(phase2: dict[str, dict[str, object]]) -> list[CheckResult]:
    p5 = phase2["physics5"]
    p6 = phase2["physics6"]
    p7 = phase2["physics7"]
    p8 = phase2["physics8"]
    out: list[CheckResult] = []
    out.append(
        _check(
            all(phase2[f"physics{i}"]["action_increases"] == 27 for i in (5, 6, 7, 8)),
            "hybrid.action_increase_cap",
            increases={f"physics{i}": phase2[f"physics{i}"]["action_increases"] for i in (5, 6, 7, 8)},
        )
    )
    out.append(
        _check(
            int(p5["edges"]) < int(p6["edges"]) < int(p7["edges"]) < int(p8["edges"]),
            "hybrid.edge_growth_strict",
            edges={f"physics{i}": phase2[f"physics{i}"]["edges"] for i in (5, 6, 7, 8)},
        )
    )
    out.append(
        _check(
            int(p5["cycles"]) < int(p6["cycles"]) < int(p7["cycles"]) < int(p8["cycles"]),
            "hybrid.cycle_growth_strict",
            cycles={f"physics{i}": phase2[f"physics{i}"]["cycles"] for i in (5, 6, 7, 8)},
        )
    )
    out.append(
        _check(
            int(p5["longest_chain"]) <= int(p6["longest_chain"]) <= int(p7["longest_chain"]) <= int(p8["longest_chain"])
            and int(p8["longest_chain"]) >= 13,
            "hybrid.longest_chain_progression",
            longest_chain={f"physics{i}": phase2[f"physics{i}"]["longest_chain"] for i in (5, 6, 7, 8)},
        )
    )
    out.append(
        _check(
            all(int(phase2[f"physics{i}"]["still_timeout"]) == 0 for i in (6, 7, 8)),
            "hybrid.long_tail_resolved",
            still_timeout={f"physics{i}": phase2[f"physics{i}"]["still_timeout"] for i in (6, 7, 8)},
        )
    )
    return out


def _physics4_signature_checks(phase2: dict[str, dict[str, object]]) -> list[CheckResult]:
    p4 = phase2["physics4"]
    p5 = phase2["physics5"]
    return [
        _check(
            int(p4["cycles"]) == 0 and int(p4["edges"]) < int(p5["edges"]),
            "physics4.overconstrained_signature",
            physics4_cycles=p4["cycles"],
            physics4_edges=p4["edges"],
            physics5_edges=p5["edges"],
        )
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Check canonical physics invariant target relationships.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON report path (default: benchmarks/results/<today>-physics-invariant-target-check.json).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report to stdout.")
    args = parser.parse_args()

    output_path = (
        Path(args.output)
        if args.output
        else RESULTS_DIR / f"{date.today().isoformat()}-physics-invariant-target-check.json"
    )

    phase2_paths = _latest_by_template("*-agdas-physics*-phase2.json", r"(physics[2-8])(?!\d)")
    invariant_paths = _latest_by_template("*-physics-invariants-physics*.json", r"(physics[2-8])(?!\d)")

    checks: list[CheckResult] = []
    checks.extend(_all_present(phase2_paths, invariant_paths))

    phase2_metrics: dict[str, dict[str, object]] = {}
    invariant_metrics: dict[str, dict[str, object]] = {}
    target_suite_metrics: dict[str, dict[str, object]] = {}
    if not checks[0].passed:
        report = {
            "passed": False,
            "checks": [c.__dict__ for c in checks],
            "phase2_artifacts": {k: str(v) for k, v in phase2_paths.items()},
            "invariant_artifacts": {k: str(v) for k, v in invariant_paths.items()},
        }
        output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"wrote {output_path}")
            print("passed=False (missing artifact coverage)")
        raise SystemExit(1)

    for key in PHYSICS_IDS:
        phase2_metrics[key] = _phase2_metrics(_load_json(phase2_paths[key]))
        payload = _load_json(invariant_paths[key])
        invariant_metrics[key] = _invariant_metrics(payload)
        target_suite_metrics[key] = _target_suite_metrics(payload)

    checks.extend(_target_suite_checks(target_suite_metrics))
    checks.extend(_lyapunov_checks(invariant_metrics))
    checks.extend(_hybrid_checks(phase2_metrics))
    checks.extend(_physics4_signature_checks(phase2_metrics))

    passed = all(c.passed for c in checks)
    report = {
        "passed": passed,
        "checks": [c.__dict__ for c in checks],
        "phase2_artifacts": {k: str(v) for k, v in phase2_paths.items()},
        "invariant_artifacts": {k: str(v) for k, v in invariant_paths.items()},
        "phase2_metrics": phase2_metrics,
        "invariant_metrics": invariant_metrics,
        "target_suite_metrics": target_suite_metrics,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"wrote {output_path}")
        print(f"passed={passed}")
        for item in checks:
            print(f"- {item.name}: {'PASS' if item.passed else 'FAIL'}")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
