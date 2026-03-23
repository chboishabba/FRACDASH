#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHI_AGDA_ROOT = ROOT.parent / "dashi_agda"


@dataclass(frozen=True)
class UpstreamModule:
    path: str
    role: str
    required_patterns: tuple[str, ...]
    local_counterparts: tuple[str, ...]


UPSTREAM_MODULES = (
    UpstreamModule(
        path="UFTC_Lattice.agda",
        role="severity lattice and monotone local code propagation",
        required_patterns=("Severity : Set", "C_XOR", "record ConeInteriorPreserved"),
        local_counterparts=("scripts/agdas_bridge.py", "AGDAS_BRIDGE_MAPPING.md"),
    ),
    UpstreamModule(
        path="Contraction.agda",
        role="contraction and unique fixed-point contract",
        required_patterns=("record Contractive", "contraction", "record StrictContraction", "unique :"),
        local_counterparts=("scripts/agdas_bridge.py", "formalism/PhysicsBridgeRefreshSketch.agda"),
    ),
    UpstreamModule(
        path="MaassRestoration.agda",
        role="stability restoration seam",
        required_patterns=("module MaassRestoration", "Stability contracts"),
        local_counterparts=("formalism/PhysicsBridgeRefreshSketch.agda",),
    ),
    UpstreamModule(
        path="MonsterState.agda",
        role="canonical state/mask/admissibility seam",
        required_patterns=("record State", "admissible"),
        local_counterparts=("scripts/agdas_bridge.py", "scripts/agdas_wave3_state.py"),
    ),
    UpstreamModule(
        path="Monster/Step.agda",
        role="canonical step/update seam",
        required_patterns=("choose", "step :"),
        local_counterparts=("scripts/agdas_bridge.py",),
    ),
    UpstreamModule(
        path="MonsterSpec.agda",
        role="spec step plus encode/decode contract",
        required_patterns=("stepSpec", "encode", "decode"),
        local_counterparts=("scripts/agdas_bridge.py", "scripts/toy_dashi_transitions.py"),
    ),
    UpstreamModule(
        path="Ontology/Hecke/Scan.agda",
        role="scan/compatibility/signature seam",
        required_patterns=("scan :", "Sig15", "Compat"),
        local_counterparts=("scripts/agdas_bridge.py", "AGDAS_BRIDGE_MAPPING.md"),
    ),
    UpstreamModule(
        path="DASHI/Physics/LiftToFullState.agda",
        role="lift seam from compressed state into full physics state",
        required_patterns=("module DASHI.Physics.LiftToFullState",),
        local_counterparts=("scripts/agdas_physics8_state.py",),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/CanonicalPhysicsPathPostulateAudit.agda",
        role="canonical no-essential-postulates audit surface",
        required_patterns=("record KnownLimitsQFTFieldAudit", "noEssentialPostulatesOnCanonicalPhysicsPath", "canonicalNoEssentialPostulatesOnCanonicalPhysicsPath"),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md",),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/PhysicsClosureValidationSummary.agda",
        role="repo-facing Stage C validation summary surface",
        required_patterns=("module DASHI.Physics.Closure.PhysicsClosureValidationSummary", "MinimalCrediblePhysicsClosureValidation", "KnownLimitsQFTBridgeTheorem", "ObservableCollapse", "FejerOverChiSquared", "SnapThresholdLaw"),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md", "PHYSICS_INVARIANT_TARGETS.md"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/MinimalCrediblePhysicsClosure.agda",
        role="minimum-credible closure adapter: full closure + observables with matching signature + authoritative execution/family witnesses",
        required_patterns=(
            "module DASHI.Physics.Closure.MinimalCrediblePhysicsClosure",
            "record MinimalCrediblePhysicsClosure",
            "authoritativeExecutionAdmissibilityWitness",
            "authoritativeFamilyClassificationWitness",
        ),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md", "scripts/physics_invariant_analysis.py"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/PhysicsClosureCoreWitness.agda",
        role="core closure witness bundle now including dynamics, execution admissibility, and family classification witnesses",
        required_patterns=(
            "module DASHI.Physics.Closure.PhysicsClosureCoreWitness",
            "record PhysicsClosureCoreWitness",
            "executionAdmissibilityWitness",
            "familyClassificationWitness",
        ),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md", "formalism/BridgeInstances.agda"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/PhysicsClosureFullInstance.agda",
        role="canonical full-instance wiring that supplies the current trace execution admissibility and family classification witnesses",
        required_patterns=(
            "module DASHI.Physics.Closure.PhysicsClosureFullInstance",
            "currentTraceExecutionAdmissibility",
            "currentFamilyClassification",
        ),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md",),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/CanonicalStageC.agda",
        role="authoritative Stage C closure surface with gauge/constraint bridge imports",
        required_patterns=("module DASHI.Physics.Closure.CanonicalStageC", "Canonical Stage C entrypoint"),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md", "AGDAS_BRIDGE_MAPPING.md", "scripts/agdas_bridge.py", "scripts/physics_invariant_analysis.py"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/PhysicsClosureTheoremChecklist.agda",
        role="theorem checklist linking contraction → quadratic → signature → Clifford → spin/Dirac → closure",
        required_patterns=("module DASHI.Physics.Closure.PhysicsClosureTheoremChecklist", "record PhysicsClosureTheoremChecklist"),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md", "scripts/agdas_bridge.py"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/MDLFejerAxiomsShift.agda",
        role="MDL/Fejér monotonicity axioms for shift energy",
        required_patterns=("module DASHI.Physics.Closure.MDLFejerAxiomsShift", "record MDLFejerAxiomsShift"),
        local_counterparts=("PHYSICS_INVARIANT_TARGETS.md", "scripts/physics_invariant_analysis.py"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/ShiftSeamCertificates.agda",
        role="closest-point / Fejér / defect-collapse seam certificates for shift",
        required_patterns=("module DASHI.Physics.Closure.ShiftSeamCertificates", "record ShiftSeams"),
        local_counterparts=("PHYSICS_INVARIANT_TARGETS.md", "scripts/physics_invariant_analysis.py"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/ObservablePredictionPackage.agda",
        role="observable boundary for current 4D shift framework: proved / excluded / forward claims",
        required_patterns=("module DASHI.Physics.Closure.ObservablePredictionPackage", "record ObservablePredictionPackage"),
        local_counterparts=("PHYSICS_INVARIANT_TARGETS.md", "AGDAS_FORMALISM_INTAKE.md"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/KnownLimitsQFTBridgeTheorem.agda",
        role="known-limits QFT bridge theorem bundle with canonical wave-even witnesses",
        required_patterns=("module DASHI.Physics.Closure.KnownLimitsQFTBridgeTheorem", "known-limits QFT bridge"),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md", "PHYSICS_INVARIANT_TARGETS.md"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/ExecutionAdmissibilityWitness.agda",
        role="shared witness vocabulary for execution admissibility and family classification",
        required_patterns=(
            "module DASHI.Physics.Closure.ExecutionAdmissibilityWitness",
            "SomeExecutionAdmissibilityWitness",
            "SomeFamilyClassificationWitness",
        ),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md", "formalism/GenericMacroBridge.agda"),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/ExecutionAdmissibilityCurrentTraceWitness.agda",
        role="current-trace execution admissibility witness used by the authoritative minimal closure",
        required_patterns=(
            "module DASHI.Physics.Closure.ExecutionAdmissibilityCurrentTraceWitness",
            "currentTraceExecutionAdmissibility",
        ),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md",),
    ),
    UpstreamModule(
        path="DASHI/Physics/Closure/ExecutionAdmissibilityCurrentFamilyWitness.agda",
        role="current-family classification witness paired with the authoritative minimal closure",
        required_patterns=(
            "module DASHI.Physics.Closure.ExecutionAdmissibilityCurrentFamilyWitness",
            "currentFamilyClassification",
        ),
        local_counterparts=("AGDAS_FORMALISM_INTAKE.md", "formalism/BridgeInstances.agda"),
    ),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def module_status(module: UpstreamModule) -> dict[str, object]:
    full_path = DASHI_AGDA_ROOT / module.path
    exists = full_path.exists()
    if not exists:
        return {
            "path": str(full_path),
            "exists": False,
            "role": module.role,
            "required_patterns": list(module.required_patterns),
            "matched_patterns": [],
            "local_counterparts": list(module.local_counterparts),
            "coverage_status": "missing_upstream_module",
        }
    text = read_text(full_path)
    matched = [pattern for pattern in module.required_patterns if pattern in text]
    if not module.local_counterparts:
        coverage_status = "no_local_counterpart_documented"
    else:
        coverage_status = "documented_local_subset"
    return {
        "path": str(full_path),
        "exists": True,
        "role": module.role,
        "required_patterns": list(module.required_patterns),
        "matched_patterns": matched,
        "local_counterparts": list(module.local_counterparts),
        "coverage_status": coverage_status,
        "pattern_pass": len(matched) == len(module.required_patterns),
    }


def parse_checklist() -> dict[str, object]:
    path = DASHI_AGDA_ROOT / "Docs/PhysicsClosureImplementationChecklist.md"
    text = read_text(path)
    done = len(re.findall(r"^\d+\.\s+\[x\]", text, flags=re.MULTILINE))
    pending = len(re.findall(r"^\d+\.\s+\[ \]", text, flags=re.MULTILINE))
    return {
        "path": str(path),
        "top_level_done": done,
        "top_level_pending": pending,
    }


def parse_minimal_closure_doc() -> dict[str, object]:
    path = DASHI_AGDA_ROOT / "Docs/MinimalCrediblePhysicsClosure.md"
    text = read_text(path)
    return {
        "path": str(path),
        "mentions_minimal_credible": "minimal credible physics closure" in text.lower(),
        "mentions_known_open_gaps": "Still genuinely open:" in text,
        "mentions_qft_recovery_limit": "full gauge/matter recovery as theorem rather than derivation program" in text,
    }


def local_counterpart_status() -> dict[str, object]:
    local_paths = (
        "AGDAS_BRIDGE_MAPPING.md",
        "AGDAS_FORMALISM_INTAKE.md",
        "scripts/agdas_bridge.py",
        "scripts/agdas_physics_experiments.py",
        "scripts/agdas_physics8_state.py",
        "scripts/agdas_physics8_experiments.py",
        "scripts/toy_dashi_transitions.py",
        "PHYSICS_INVARIANT_TARGETS.md",
        "formalism/GenericMacroBridge.agda",
        "formalism/BridgeInstances.agda",
    )
    statuses = {}
    for rel in local_paths:
        path = ROOT / rel
        statuses[rel] = path.exists()
    return {
        "paths": statuses,
        "all_present": all(statuses.values()),
    }


def summary_payload() -> dict[str, object]:
    modules = [module_status(module) for module in UPSTREAM_MODULES]
    all_exist = all(item["exists"] for item in modules)
    all_patterns = all(bool(item.get("pattern_pass")) for item in modules if item["exists"])
    return {
        "date": date.today().isoformat(),
        "dashi_agda_root": str(DASHI_AGDA_ROOT),
        "formalism_decision": {
            "source_of_truth": "../dashi_agda",
            "local_repo_status": "compressed_executable_subset",
            "bridge_rule": "upstream formal closure is authoritative; FRACDASH claims stay bounded to extracted executable coverage",
        },
        "upstream_modules": modules,
        "checklist": parse_checklist(),
        "minimal_credible_closure_doc": parse_minimal_closure_doc(),
        "local_counterparts": local_counterpart_status(),
        "summary": {
            "all_upstream_modules_present": all_exist,
            "all_required_patterns_present": all_patterns,
            "authoritative_formalism_detected": all_exist and all_patterns,
        },
    }


def markdown_summary(payload: dict[str, object]) -> str:
    lines = [
        "# dashi_agda Formalism Check",
        "",
        f"- Date: `{payload['date']}`",
        f"- Upstream root: `{payload['dashi_agda_root']}`",
        f"- Authoritative formalism detected: `{payload['summary']['authoritative_formalism_detected']}`",
        f"- Local repo status: `{payload['formalism_decision']['local_repo_status']}`",
        "",
        "## Upstream Modules",
        "",
    ]
    for item in payload["upstream_modules"]:
        lines.append(f"- `{Path(item['path']).name}`: `{item['coverage_status']}`, patterns `{len(item['matched_patterns'])}/{len(item['required_patterns'])}`")
    lines.extend(
        [
            "",
            "## Checklist",
            "",
            f"- Top-level completed items: `{payload['checklist']['top_level_done']}`",
            f"- Top-level pending items: `{payload['checklist']['top_level_pending']}`",
            "",
            "## Interpretation",
            "",
            "- `../dashi_agda` contains a concrete closure/audit surface that FRACDASH should treat as authoritative semantics.",
            "- FRACDASH still executes a compressed subset and should not present the full closure as locally implemented.",
            "- The current authoritative minimal-credible closure now includes execution-admissibility and family-classification witness surfaces; FRACDASH should treat those as upstream truth even where local executable coverage is only partial.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the upstream dashi_agda formalism and record a bridge-intake artifact.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    parser.add_argument("--markdown", action="store_true", help="Print markdown summary.")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional JSON output path. Defaults to benchmarks/results/<today>-dashi-agda-formalism-check.json",
    )
    parser.add_argument(
        "--markdown-output",
        default=None,
        help="Optional markdown output path. Defaults to benchmarks/results/<today>-dashi-agda-formalism-check.md",
    )
    args = parser.parse_args()

    if not DASHI_AGDA_ROOT.exists():
        raise SystemExit(f"missing upstream root: {DASHI_AGDA_ROOT}")

    payload = summary_payload()
    output_path = Path(args.output) if args.output else ROOT / "benchmarks/results" / f"{date.today().isoformat()}-dashi-agda-formalism-check.json"
    markdown_path = Path(args.markdown_output) if args.markdown_output else ROOT / "benchmarks/results" / f"{date.today().isoformat()}-dashi-agda-formalism-check.md"
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
    print(f"authoritative_formalism_detected={payload['summary']['authoritative_formalism_detected']}")


if __name__ == "__main__":
    main()
