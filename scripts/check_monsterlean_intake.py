#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEAN_ROOT = ROOT / "monster" / "MonsterLean"
DEFAULT_OUTPUT = ROOT / "benchmarks" / "results" / f"{date.today().isoformat()}-monsterlean-intake.json"

KEYWORD_PATTERNS = {
    "def": re.compile(r"^\s*def\s+", flags=re.MULTILINE),
    "structure": re.compile(r"^\s*structure\s+", flags=re.MULTILINE),
    "inductive": re.compile(r"^\s*inductive\s+", flags=re.MULTILINE),
    "theorem": re.compile(r"^\s*theorem\s+", flags=re.MULTILINE),
    "lemma": re.compile(r"^\s*lemma\s+", flags=re.MULTILINE),
    "axiom": re.compile(r"^\s*axiom\s+", flags=re.MULTILINE),
    "sorry": re.compile(r"\bsorry\b"),
}

PRIME15_LITERAL = "[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71]"


@dataclass(frozen=True)
class ModuleSummary:
    file: str
    exists: bool
    counts: dict[str, int]
    has_prime15_literal: bool
    classification: str


def classify(counts: dict[str, int]) -> str:
    if counts["axiom"] > 0:
        return "conjectural_axiom_present"
    if counts["sorry"] > 0:
        return "incomplete_sorry_present"
    if counts["theorem"] > 0:
        return "proof_claims_without_obvious_placeholders"
    return "definition_only_or_no_theorems"


def summarize_module(path: Path) -> ModuleSummary:
    if not path.exists():
        return ModuleSummary(
            file=str(path),
            exists=False,
            counts={key: 0 for key in KEYWORD_PATTERNS},
            has_prime15_literal=False,
            classification="missing",
        )

    text = path.read_text(encoding="utf-8")
    counts = {key: len(pattern.findall(text)) for key, pattern in KEYWORD_PATTERNS.items()}
    has_prime15 = PRIME15_LITERAL in text
    return ModuleSummary(
        file=str(path),
        exists=True,
        counts=counts,
        has_prime15_literal=has_prime15,
        classification=classify(counts),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory and classify selected MonsterLean modules.")
    parser.add_argument(
        "--lean-root",
        default=str(DEFAULT_LEAN_ROOT),
        help="Root directory containing MonsterLean .lean files.",
    )
    parser.add_argument(
        "--module",
        action="append",
        default=[],
        help="Relative .lean file path under --lean-root. Repeatable.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output JSON path.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    args = parser.parse_args()

    lean_root = Path(args.lean_root)
    modules = args.module or [
        "MonsterWalkPrimes.lean",
        "MonsterWalk.lean",
        "MonsterWalkRings.lean",
        "ComplexityLattice.lean",
    ]

    summaries = [summarize_module(lean_root / rel) for rel in modules]
    blocked = [item.file for item in summaries if item.classification in {"conjectural_axiom_present", "incomplete_sorry_present"}]
    reusable = [item.file for item in summaries if item.classification == "definition_only_or_no_theorems"]

    payload = {
        "lean_root": str(lean_root),
        "module_count": len(summaries),
        "modules": [
            {
                "file": item.file,
                "exists": item.exists,
                "counts": item.counts,
                "has_prime15_literal": item.has_prime15_literal,
                "classification": item.classification,
            }
            for item in summaries
        ],
        "summary": {
            "blocked_for_claim_reuse": blocked,
            "reusable_definition_only": reusable,
            "intake_policy": "treat theorem claims with axiom/sorry as non-authoritative until reproduced in FRACDASH artifacts",
        },
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
