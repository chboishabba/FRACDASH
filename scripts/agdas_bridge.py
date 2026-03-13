#!/usr/bin/env python3
"""Typed AGDAS to FRACTRAN bridge extractor.

The bridge has a practical goal: expose a small, executable FRACTRAN-facing
transition surface derived from selected AGDA semantics for Phase 2 verifier work.

There are two routes:

- the primary route is FRACDASH-side template transitions,
- the optional route is parsing compact transition-like declarations from AGDA-adjacent text.

The parser is intentionally conservative and explicit:

- it emits only rules it can parse into concrete register/state pairs,
- it carries provenance (module, line number, source text),
- and it keeps conservative fallbacks for manual review when no typed rule
  can be extracted from a candidate block.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import re
from fractions import Fraction
from typing import Any, Iterable


AGDAS_FILENAME = "all_dashi_agdas.txt"
DEFAULT_SIGNED_STATE_PRIMES = {
    "R1": {"negative": 5, "zero": 2, "positive": 3},
    "R2": {"negative": 13, "zero": 7, "positive": 11},
    "R3": {"negative": 23, "zero": 17, "positive": 19},
    "R4": {"negative": 37, "zero": 29, "positive": 31},
}
DEFAULT_STATE_SYMBOLS = {
    "negative": "-1",
    "zero": "0",
    "positive": "+1",
}


@dataclass(frozen=True)
class TransitionRule:
    name: str
    module: str
    path: str
    line: int
    condition: dict[str, str]
    action: dict[str, str]
    source_text: str
    raw_condition: str
    raw_action: str

    @property
    def transition_signature(self) -> tuple[str, str]:
        cond = ",".join(f"{register}:{value}" for register, value in sorted(self.condition.items()))
        act = ",".join(f"{register}:{value}" for register, value in sorted(self.action.items()))
        return (cond, act)


@dataclass(frozen=True)
class BridgeScan:
    modules: list[str]
    transition_lines: list[str]
    parsed_rules: list[TransitionRule]
    malformed_rules: list[dict[str, Any]]
    total_lines: int
    path: str
    files: list[str]
    scan_signature: str


@dataclass(frozen=True)
class TemplateRule:
    name: str
    template_set: str
    module: str
    condition: dict[str, str]
    action: dict[str, str]
    description: str


def _default_agdas_path() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    sibling_root = repo_root.parent / "dashi_agda"
    if sibling_root.exists():
        return sibling_root
    return repo_root / AGDAS_FILENAME


def _template_rules(template_set: str = "wave1") -> list[TemplateRule]:
    wave1 = [
        TemplateRule(
            name="tri_rotate_low_to_mid",
            template_set="wave1",
            module="Base369.rotateTri",
            condition={"R1": "negative"},
            action={"R1": "zero"},
            description="Map tri-low -> tri-mid on R1.",
        ),
        TemplateRule(
            name="tri_rotate_mid_to_high",
            template_set="wave1",
            module="Base369.rotateTri",
            condition={"R1": "zero"},
            action={"R1": "positive"},
            description="Map tri-mid -> tri-high on R1.",
        ),
        TemplateRule(
            name="tri_rotate_high_to_low",
            template_set="wave1",
            module="Base369.rotateTri",
            condition={"R1": "positive"},
            action={"R1": "negative"},
            description="Map tri-high -> tri-low on R1.",
        ),
        TemplateRule(
            name="stage_seed_to_counter",
            template_set="wave1",
            module="LogicTlurey.next",
            condition={"R1": "negative", "R2": "zero"},
            action={"R1": "zero", "R2": "zero"},
            description="Stage seed -> counter using R1 for tri state and R2 as overflow flag.",
        ),
        TemplateRule(
            name="stage_counter_to_resonance",
            template_set="wave1",
            module="LogicTlurey.next",
            condition={"R1": "zero", "R2": "zero"},
            action={"R1": "positive", "R2": "zero"},
            description="Stage counter -> resonance.",
        ),
        TemplateRule(
            name="stage_resonance_to_overflow",
            template_set="wave1",
            module="LogicTlurey.next",
            condition={"R1": "positive", "R2": "zero"},
            action={"R1": "negative", "R2": "positive"},
            description="Stage resonance -> overflow (overflow flag set).",
        ),
        TemplateRule(
            name="stage_overflow_to_seed",
            template_set="wave1",
            module="LogicTlurey.next",
            condition={"R1": "negative", "R2": "positive"},
            action={"R1": "negative", "R2": "zero"},
            description="Stage overflow -> seed (overflow flag cleared).",
        ),
        TemplateRule(
            name="kernel_involution_neg_to_pos",
            template_set="wave1",
            module="Kernel.Algebra.ι",
            condition={"R3": "negative"},
            action={"R3": "positive"},
            description="Kernel involution on R3: neg -> pos.",
        ),
        TemplateRule(
            name="kernel_involution_pos_to_neg",
            template_set="wave1",
            module="Kernel.Algebra.ι",
            condition={"R3": "positive"},
            action={"R3": "negative"},
            description="Kernel involution on R3: pos -> neg.",
        ),
        TemplateRule(
            name="kernel_involution_zero_fixed",
            template_set="wave1",
            module="Kernel.Algebra.ι",
            condition={"R3": "zero"},
            action={"R3": "zero"},
            description="Kernel involution on R3: zero fixed.",
        ),
    ]
    wave2 = [
        TemplateRule(
            name="monster_step_accept_p0",
            template_set="wave2",
            module="Monster.Step.step",
            condition={"R1": "zero", "R2": "positive", "R4": "zero"},
            action={"R1": "positive", "R2": "zero", "R4": "positive"},
            description="Compressed Monster step: accepted candidate, advance window phase 0 -> 1.",
        ),
        TemplateRule(
            name="monster_step_accept_p1",
            template_set="wave2",
            module="Monster.Step.step",
            condition={"R1": "zero", "R2": "positive", "R4": "positive"},
            action={"R1": "positive", "R2": "zero", "R4": "negative"},
            description="Compressed Monster step: accepted candidate, advance window phase 1 -> 2.",
        ),
        TemplateRule(
            name="monster_step_accept_p2",
            template_set="wave2",
            module="Monster.Step.step",
            condition={"R1": "zero", "R2": "positive", "R4": "negative"},
            action={"R1": "positive", "R2": "zero", "R4": "zero"},
            description="Compressed Monster step: accepted candidate, advance window phase 2 -> 0.",
        ),
        TemplateRule(
            name="monster_step_reject_p0",
            template_set="wave2",
            module="Monster.Step.step",
            condition={"R1": "zero", "R2": "negative", "R4": "zero"},
            action={"R1": "zero", "R2": "zero", "R4": "positive"},
            description="Compressed Monster step: rejected candidate, fallback/current mask kept, phase 0 -> 1.",
        ),
        TemplateRule(
            name="monster_step_reject_p1",
            template_set="wave2",
            module="Monster.Step.step",
            condition={"R1": "zero", "R2": "negative", "R4": "positive"},
            action={"R1": "zero", "R2": "zero", "R4": "negative"},
            description="Compressed Monster step: rejected candidate, fallback/current mask kept, phase 1 -> 2.",
        ),
        TemplateRule(
            name="monster_step_reject_p2",
            template_set="wave2",
            module="Monster.Step.step",
            condition={"R1": "zero", "R2": "negative", "R4": "negative"},
            action={"R1": "zero", "R2": "zero", "R4": "zero"},
            description="Compressed Monster step: rejected candidate, fallback/current mask kept, phase 2 -> 0.",
        ),
    ]
    physics1 = [
        TemplateRule(
            name="physics_join_from_left_high",
            template_set="physics1",
            module="UFTC_Lattice.C_XOR",
            condition={"R1": "negative", "R3": "zero"},
            action={"R1": "negative", "R3": "negative"},
            description="Materialize high effective severity from the left code.",
        ),
        TemplateRule(
            name="physics_join_from_right_high",
            template_set="physics1",
            module="UFTC_Lattice.C_XOR",
            condition={"R2": "negative", "R3": "zero"},
            action={"R2": "negative", "R3": "negative"},
            description="Materialize high effective severity from the right code.",
        ),
        TemplateRule(
            name="physics_join_from_left_mid",
            template_set="physics1",
            module="UFTC_Lattice.C_XOR",
            condition={"R1": "positive", "R3": "zero"},
            action={"R1": "positive", "R3": "positive"},
            description="Materialize mid effective severity from the left code.",
        ),
        TemplateRule(
            name="physics_join_from_right_mid",
            template_set="physics1",
            module="UFTC_Lattice.C_XOR",
            condition={"R2": "positive", "R3": "zero"},
            action={"R2": "positive", "R3": "positive"},
            description="Materialize mid effective severity from the right code.",
        ),
        TemplateRule(
            name="physics_contract_high",
            template_set="physics1",
            module="Contraction.StrictContraction",
            condition={"R3": "negative", "R4": "positive"},
            action={"R3": "positive", "R4": "positive"},
            description="Interior contraction lowers high severity to mid.",
        ),
        TemplateRule(
            name="physics_contract_mid",
            template_set="physics1",
            module="Contraction.StrictContraction",
            condition={"R3": "positive", "R4": "positive"},
            action={"R3": "zero", "R4": "negative"},
            description="Interior contraction lowers mid severity to zero and reaches boundary.",
        ),
        TemplateRule(
            name="physics_boundary_reset",
            template_set="physics1",
            module="UFTC_Lattice.ConeInteriorPreserved",
            condition={"R4": "negative"},
            action={"R4": "positive"},
            description="Boundary reset re-arms the local interior for another relaxation pass.",
        ),
    ]
    physics2 = [
        TemplateRule(
            name="physics2_scan_left_high",
            template_set="physics2",
            module="DASHI.Algebra.PhysicsSignature.scan",
            condition={"R1": "negative", "R5": "zero"},
            action={"R1": "negative", "R5": "positive"},
            description="Latch left-dominant scan from a high left source.",
        ),
        TemplateRule(
            name="physics2_scan_left_mid",
            template_set="physics2",
            module="DASHI.Algebra.PhysicsSignature.scan",
            condition={"R1": "positive", "R5": "zero"},
            action={"R1": "positive", "R5": "positive"},
            description="Latch left-dominant scan from a mid left source.",
        ),
        TemplateRule(
            name="physics2_scan_right_high",
            template_set="physics2",
            module="DASHI.Algebra.PhysicsSignature.scan",
            condition={"R2": "negative", "R5": "zero"},
            action={"R2": "negative", "R5": "negative"},
            description="Latch right-dominant scan from a high right source.",
        ),
        TemplateRule(
            name="physics2_scan_right_mid",
            template_set="physics2",
            module="DASHI.Algebra.PhysicsSignature.scan",
            condition={"R2": "positive", "R5": "zero"},
            action={"R2": "positive", "R5": "negative"},
            description="Latch right-dominant scan from a mid right source.",
        ),
        TemplateRule(
            name="physics2_join_left_high",
            template_set="physics2",
            module="UFTC_Lattice.C_XOR",
            condition={"R1": "negative", "R3": "zero", "R5": "positive", "R6": "negative"},
            action={"R1": "negative", "R3": "negative", "R5": "positive", "R6": "negative"},
            description="Materialize high severity from a latched left source.",
        ),
        TemplateRule(
            name="physics2_join_right_high",
            template_set="physics2",
            module="UFTC_Lattice.C_XOR",
            condition={"R2": "negative", "R3": "zero", "R5": "negative", "R6": "negative"},
            action={"R2": "negative", "R3": "negative", "R5": "negative", "R6": "negative"},
            description="Materialize high severity from a latched right source.",
        ),
        TemplateRule(
            name="physics2_join_left_mid",
            template_set="physics2",
            module="UFTC_Lattice.C_XOR",
            condition={"R1": "positive", "R3": "zero", "R5": "positive", "R6": "negative"},
            action={"R1": "positive", "R3": "positive", "R5": "positive", "R6": "positive"},
            description="Materialize mid severity from a latched left source and advance the action phase.",
        ),
        TemplateRule(
            name="physics2_join_right_mid",
            template_set="physics2",
            module="UFTC_Lattice.C_XOR",
            condition={"R2": "positive", "R3": "zero", "R5": "negative", "R6": "negative"},
            action={"R2": "positive", "R3": "positive", "R5": "negative", "R6": "positive"},
            description="Materialize mid severity from a latched right source and advance the action phase.",
        ),
        TemplateRule(
            name="physics2_contract_high",
            template_set="physics2",
            module="Contraction.StrictContraction",
            condition={"R3": "negative", "R4": "positive", "R6": "negative"},
            action={"R3": "positive", "R4": "positive", "R6": "positive"},
            description="Interior contraction lowers high severity to mid.",
        ),
        TemplateRule(
            name="physics2_contract_mid",
            template_set="physics2",
            module="Contraction.StrictContraction",
            condition={"R3": "positive", "R4": "positive", "R6": "positive"},
            action={"R3": "zero", "R4": "negative", "R6": "zero"},
            description="Interior contraction lowers mid severity to zero and drops to the boundary.",
        ),
        TemplateRule(
            name="physics2_boundary_rearm",
            template_set="physics2",
            module="UFTC_Lattice.ConeInteriorPreserved",
            condition={"R4": "negative"},
            action={"R4": "positive", "R5": "zero", "R6": "negative"},
            description="Boundary reset clears the scan latch and re-arms the interior/action phase.",
        ),
    ]
    phase_cycle = [
        (("zero", "zero"), ("positive", "zero"), "00->10"),
        (("positive", "zero"), ("negative", "zero"), "10->20"),
        (("negative", "zero"), ("zero", "positive"), "20->01"),
        (("zero", "positive"), ("positive", "positive"), "01->11"),
        (("positive", "positive"), ("negative", "positive"), "11->21"),
        (("negative", "positive"), ("zero", "negative"), "21->02"),
        (("zero", "negative"), ("positive", "negative"), "02->12"),
        (("positive", "negative"), ("negative", "negative"), "12->22"),
        (("negative", "negative"), ("zero", "zero"), "22->00"),
    ]
    wave3: list[TemplateRule] = []
    for (r4, r5), (next_r4, next_r5), phase_name in phase_cycle:
        wave3.append(
            TemplateRule(
                name=f"monster_wave3_accept_{phase_name}",
                template_set="wave3",
                module="Monster.Step.step",
                condition={"R1": "zero", "R2": "positive", "R3": "positive", "R4": r4, "R5": r5},
                action={"R1": "positive", "R2": "zero", "R3": "zero", "R4": next_r4, "R5": next_r5},
                description=(
                    "Wave-3 Monster step: accepted candidate, promote mask summary, "
                    f"advance window phase {phase_name}."
                ),
            )
        )
        wave3.append(
            TemplateRule(
                name=f"monster_wave3_reject_{phase_name}",
                template_set="wave3",
                module="Monster.Step.step",
                condition={"R1": "zero", "R2": "negative", "R3": "negative", "R4": r4, "R5": r5},
                action={"R1": "negative", "R2": "zero", "R3": "zero", "R4": next_r4, "R5": next_r5},
                description=(
                    "Wave-3 Monster step: rejected candidate, mark reduced/fallback mask, "
                    f"advance window phase {phase_name}."
                ),
            )
        )
    if template_set == "wave1":
        return wave1
    if template_set == "wave2":
        return wave2
    if template_set == "physics1":
        return physics1
    if template_set == "physics2":
        return physics2
    if template_set == "wave3":
        return wave3
    if template_set == "all":
        return wave1 + wave2 + physics1 + physics2 + wave3
    raise ValueError(f"unknown template set: {template_set}")


def _normalize_state_value(raw: str) -> str | None:
    token = raw.strip().lower()
    if token in DEFAULT_STATE_SYMBOLS:
        return token
    if token in ("-1", "−1", "neg", "negative"):
        return "negative"
    if token in ("0", "zero", "z", "neutral"):
        return "zero"
    if token in ("1", "+1", "pos", "positive"):
        return "positive"
    return None


def _parse_binding_clause(clause: str) -> tuple[dict[str, str], list[str]]:
    bindings: dict[str, str] = {}
    unknown: list[str] = []
    normalized = clause.replace(";", ",").replace(" and ", ",").replace(" and\n", ",").replace("\n", " ")
    # match forms: R1=+1 / R2:+1 / R3 0
    for match in re.finditer(r"\b([Rr]\d+)\b\s*[=:]?\s*([^\s,]+)", normalized):
        register = match.group(1).upper()
        state = _normalize_state_value(match.group(2))
        if state is None:
            unknown.append(match.group(0).strip())
            continue
        if register not in DEFAULT_SIGNED_STATE_PRIMES:
            unknown.append(match.group(0).strip())
            continue
        bindings[register] = state
    return bindings, unknown


def _parse_rule_body(body: str) -> tuple[str, str] | None:
    tokens = body.strip()
    arrow_match = re.search(r"\s*(?:=>|->)\s*", tokens)
    if arrow_match:
        condition = tokens[:arrow_match.start()].strip()
        action = tokens[arrow_match.end():].strip()
        if condition.lower().startswith("if "):
            condition = condition[3:].strip()
        return condition, action

    then_match = re.search(r"\s+then\s+", tokens, flags=re.IGNORECASE)
    if then_match and condition_is_like(tokens):
        left = tokens[: then_match.start()].strip()
        right = tokens[then_match.end():].strip()
        if left.lower().startswith("if "):
            left = left[3:].strip()
        return left, right
    return None


def condition_is_like(text: str) -> bool:
    normalized = re.sub(r"[;,]", " ", text.lower())
    return "r" in normalized and any(
        state in normalized for state in ("+1", "-1", "0", "negative", "positive", "zero")
    )


def _extract_rule_from_comment(
    line: str,
    line_no: int,
    module: str,
    path: Path,
) -> TransitionRule | None | str:
    marker_match = re.match(
        r"^\s*--\s*(?:agdas|agd|dashi)\s*(?:transition|rule)\b(.*)$",
        line,
        flags=re.IGNORECASE,
    )
    if not marker_match:
        return None

    rest = marker_match.group(1).strip()
    if not rest:
        return "empty_rule_marker"

    # name may be provided as `name:` before condition/action body
    rule_name = f"{module}-line-{line_no}"
    body = rest
    name_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.+)$", rest)
    if name_match:
        rule_name = name_match.group(1)
        body = name_match.group(2)

    split_body = _parse_rule_body(body)
    if split_body is None:
        return "unparsed_rule_body"
    raw_condition, raw_action = split_body
    condition, bad_condition_tokens = _parse_binding_clause(raw_condition)
    action, bad_action_tokens = _parse_binding_clause(raw_action)
    if bad_condition_tokens or bad_action_tokens or not condition or not action:
        return "unparseable_bindings"

    return TransitionRule(
        name=rule_name,
        module=module,
        path=str(path),
        line=line_no,
        condition=condition,
        action=action,
        source_text=line.strip(),
        raw_condition=raw_condition,
        raw_action=raw_action,
    )


def _rule_fraction(rule: TransitionRule) -> Fraction:
    numerator = 1
    denominator = 1
    for register, state in rule.condition.items():
        denominator *= int(DEFAULT_SIGNED_STATE_PRIMES[register][state])
    for register, state in rule.action.items():
        numerator *= int(DEFAULT_SIGNED_STATE_PRIMES[register][state])
    return Fraction(numerator, denominator)


def _dedupe_rules(rules: list[TransitionRule]) -> list[TransitionRule]:
    seen: set[tuple[str, str, str, str]] = set()
    deduped: list[TransitionRule] = []
    for rule in rules:
        key = (rule.path, rule.module, *rule.transition_signature, rule.name)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rule)
    return deduped


def _collect_agdas_files(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted([p for p in path.rglob("*.agda") if p.is_file()])
    return [path]


def _iter_agdas_lines(paths: Iterable[Path]) -> Iterable[tuple[Path, int, str]]:
    for path in paths:
        text = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(text, start=1):
            yield path, index, line


def scan_agdas(path: Path) -> BridgeScan:
    module_re = re.compile(r"^\s*module\s+([A-Za-z_][A-Za-z0-9_.'-]*)")
    modules: list[str] = []
    transition_lines: list[str] = []
    parsed_rules: list[TransitionRule] = []
    malformed_rules: list[dict[str, Any]] = []
    current_module = "<top>"
    module_count = 0
    files = _collect_agdas_files(path)
    total_lines = 0

    for file_path, index, line in _iter_agdas_lines(files):
        total_lines += 1
        stripped = line.strip()
        module_match = module_re.match(stripped)
        if module_match:
            current_module = module_match.group(1)
            modules.append(current_module)
            module_count += 1

        if "agdas" not in stripped.lower() and "dashi" not in stripped.lower():
            if "rule" not in stripped.lower() and "transition" not in stripped.lower():
                continue

        extracted = _extract_rule_from_comment(line, index, current_module, file_path)
        if isinstance(extracted, TransitionRule):
            parsed_rules.append(extracted)
            transition_lines.append(f"{file_path}:{index}")
            continue
        if extracted == "empty_rule_marker":
            malformed_rules.append(
                {
                    "file": str(file_path),
                    "line": index,
                    "status": "empty_rule_marker",
                    "text": line.strip(),
                }
            )
        elif extracted == "unparsed_rule_body":
            malformed_rules.append(
                {
                    "file": str(file_path),
                    "line": index,
                    "status": "unparsed_rule_body",
                    "text": line.strip(),
                }
            )
        elif extracted == "unparseable_bindings":
            malformed_rules.append(
                {
                    "file": str(file_path),
                    "line": index,
                    "status": "unparseable_bindings",
                    "text": line.strip(),
                }
            )

    parsed_rules = _dedupe_rules(parsed_rules)
    signature = f"{total_lines}|{len(modules)}|{len(parsed_rules)}|{len(malformed_rules)}|{module_count}"
    return BridgeScan(
        modules=modules,
        transition_lines=transition_lines,
        parsed_rules=parsed_rules,
        malformed_rules=malformed_rules,
        total_lines=total_lines,
        path=str(path),
        files=[str(p) for p in files],
        scan_signature=signature,
    )


def _template_records(template_set: str = "wave1") -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for rule in _template_rules(template_set):
        records.append(
            {
                "name": rule.name,
                "template_set": rule.template_set,
                "module": rule.module,
                "condition": rule.condition,
                "action": rule.action,
                "description": rule.description,
            }
        )
    return records


def summarize_scan(scan: BridgeScan, include_templates: bool = False, template_set: str = "wave1") -> dict[str, object]:
    parsed_rule_records: list[dict[str, object]] = []
    for rule in scan.parsed_rules:
        transition_text = f"{rule.module}:{rule.name}"
        record: dict[str, object] = {
            "module": rule.module,
            "path": rule.path,
            "line": rule.line,
            "name": rule.name,
            "condition": rule.condition,
            "action": rule.action,
            "source_text": rule.source_text,
            "raw_condition": rule.raw_condition,
            "raw_action": rule.raw_action,
            "signature": transition_text,
        }
        parsed_rule_records.append(record)

    canonical_fractran = []
    for rule in scan.parsed_rules:
        try:
            frac = _rule_fraction(rule)
        except KeyError:
            continue
        canonical_fractran.append(
            {
                "name": rule.name,
                "module": rule.module,
                "path": rule.path,
                "line": rule.line,
                "fraction": f"{frac.numerator}/{frac.denominator}",
                "condition": rule.condition,
                "action": rule.action,
                "signed_fraction": str(frac),
            }
        )

    payload = {
        "path": scan.path,
        "files": scan.files,
        "total_lines": scan.total_lines,
        "module_count": len(scan.modules),
        "modules_preview": scan.modules[:20],
        "scan_signature": scan.scan_signature,
        "transition_count": len(scan.parsed_rules),
        "transition_lines": scan.transition_lines,
        "transitions": parsed_rule_records,
        "malformed_rules": scan.malformed_rules,
        "malformed_rule_count": len(scan.malformed_rules),
        "fractran": canonical_fractran,
    }
    if include_templates:
        payload["template_transitions"] = _template_records(template_set)
        payload["template_set"] = template_set
    return payload


def parse_and_emit_json(path: Path, include_templates: bool = False, template_set: str = "wave1") -> dict[str, object]:
    scan = scan_agdas(path)
    return summarize_scan(scan, include_templates=include_templates, template_set=template_set)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect, parse, and emit AGDAS transition candidates as a typed bridge artifact."
    )
    parser.add_argument(
        "--agdas-path",
        default=str(_default_agdas_path()),
        help="Path to the AGDAS source file or directory.",
    )
    parser.add_argument(
        "--emit-fractran",
        action="store_true",
        help="Only emit FRACTRAN-ready typed rules (fails if no parseable rules).",
    )
    parser.add_argument(
        "--emit-templates",
        action="store_true",
        help="Emit the built-in template transition list.",
    )
    parser.add_argument(
        "--template-set",
        default="wave1",
        choices=("wave1", "wave2", "wave3", "physics1", "physics2", "all"),
        help="Which FRACDASH-side template transition set to use.",
    )
    parser.add_argument(
        "--require-rules",
        action="store_true",
        help="Exit non-zero when no typed AGDAS rules are parsed.",
    )
    parser.add_argument(
        "--include-templates",
        action="store_true",
        help="Include the built-in template transitions in JSON output.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit scan summary as JSON.",
    )
    args = parser.parse_args()

    path = Path(args.agdas_path)
    if not path.exists():
        raise SystemExit(f"AGDAS source not found: {path}")

    scan = scan_agdas(path)
    if args.json:
        payload = summarize_scan(scan, include_templates=args.include_templates, template_set=args.template_set)
        if args.emit_fractran:
            payload["emit_mode"] = "fractran"
        if args.emit_templates:
            payload["emit_mode"] = "templates"
        print(json.dumps(payload, indent=2))
        if (args.emit_fractran or args.require_rules) and not scan.parsed_rules:
            raise SystemExit(1)
        return
    if args.emit_templates:
        print("# AGDAS -> FRACTRAN template transition list")
        for item in _template_records(args.template_set):
            print(
                f"- {item['name']}: {item['condition']} -> {item['action']} "
                f"[{item['module']}; set={item['template_set']}]"
            )
        return
    if args.emit_fractran:
        if not scan.parsed_rules:
            raise SystemExit("No parsed AGDAS transition candidates were found.")
        print("# AGDAS -> FRACTRAN typed transition extract")
        for frac in summarize_scan(scan)["fractran"]:
            print(f"- {frac['name']}: {frac['fraction']} ({frac['condition']} -> {frac['action']})")
        return

    print(f"AGDAS source: {scan.path}")
    print(f"Total lines: {scan.total_lines}")
    print(f"Files scanned: {len(scan.files)}")
    print(f"Modules discovered: {len(scan.modules)}")
    for module in scan.modules:
        print(f"- {module}")
    print(f"Parsed transition lines: {len(scan.transition_lines)}")
    print(f"Parsed transitions: {len(scan.parsed_rules)}")
    print(f"Malformed transition marker lines: {len(scan.malformed_rules)}")
    print(f"scan_signature: {scan.scan_signature}")
    for rule in scan.parsed_rules[:25]:
        print(
            f"- {rule.module}:{rule.name} @ {rule.line}: "
            f"{rule.raw_condition} -> {rule.raw_action}"
        )
    if scan.malformed_rules:
        print("Malformed markers:")
        for item in scan.malformed_rules[:10]:
            print(f"- line {item['line']}: {item['status']}")


if __name__ == "__main__":
    main()
