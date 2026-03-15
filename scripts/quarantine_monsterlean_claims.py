#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEAN_ROOT = ROOT / "monster" / "MonsterLean"
DEFAULT_JSON = ROOT / "benchmarks" / "results" / f"{date.today().isoformat()}-monsterlean-claim-status.json"
DEFAULT_MD = ROOT / "benchmarks" / "results" / f"{date.today().isoformat()}-monsterlean-claim-status.md"

RE_THEOREM = re.compile(r"^\s*(theorem|lemma)\s+", flags=re.MULTILINE)
RE_THEOREM_NAME = re.compile(r"^\s*(theorem|lemma)\s+([A-Za-z0-9_']+)", flags=re.MULTILINE)
RE_AXIOM = re.compile(r"^\s*axiom\s+", flags=re.MULTILINE)
RE_AXIOM_NAME = re.compile(r"^\s*axiom\s+([A-Za-z0-9_']+)", flags=re.MULTILINE)
RE_SORRY = re.compile(r"\bsorry\b")

DEFAULT_PRIORITIZED = (
    "MonsterWalk.lean",
    "MonsterWalkPrimes.lean",
    "MonsterWalkRings.lean",
    "BottPeriodicity.lean",
)


def classify(ax: int, so: int) -> str:
    if ax > 0:
        return "quarantined_axiom"
    if so > 0:
        return "quarantined_sorry"
    return "closed_for_local_claim_reuse"


def theorem_blocks_with_sorry(text: str) -> list[str]:
    matches = list(RE_THEOREM_NAME.finditer(text))
    if not matches:
        return []
    out: list[str] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        block = text[start:end]
        if RE_SORRY.search(block):
            out.append(match.group(2))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate file-by-file MonsterLean claim quarantine report.")
    parser.add_argument("--lean-root", default=str(DEFAULT_LEAN_ROOT), help="Path to MonsterLean directory.")
    parser.add_argument("--output-json", default=str(DEFAULT_JSON), help="Output JSON path.")
    parser.add_argument("--output-md", default=str(DEFAULT_MD), help="Output markdown path.")
    parser.add_argument(
        "--prioritized-files",
        default=",".join(DEFAULT_PRIORITIZED),
        help="Comma-separated prioritized Lean files (relative to --lean-root) for closure tracking.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    args = parser.parse_args()

    lean_root = Path(args.lean_root)
    prioritized_rel = [token.strip() for token in args.prioritized_files.split(",") if token.strip()]
    files = sorted(lean_root.rglob("*.lean"))
    modules = []
    closed = 0
    quarantined = 0
    modules_by_rel: dict[str, dict[str, object]] = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        theorem_count = len(RE_THEOREM.findall(text))
        axiom_count = len(RE_AXIOM.findall(text))
        sorry_count = len(RE_SORRY.findall(text))
        axiom_names = sorted(set(RE_AXIOM_NAME.findall(text)))
        sorry_theorems = sorted(set(theorem_blocks_with_sorry(text)))
        status = classify(axiom_count, sorry_count)
        if status == "closed_for_local_claim_reuse":
            closed += 1
        else:
            quarantined += 1
        module = {
            "file": str(path),
            "relative_file": str(path.relative_to(lean_root)),
            "theorem_or_lemma_count": theorem_count,
            "axiom_count": axiom_count,
            "sorry_count": sorry_count,
            "axiom_names": axiom_names,
            "sorry_theorems": sorry_theorems,
            "status": status,
        }
        modules.append(module)
        modules_by_rel[module["relative_file"]] = module

    prioritized = []
    prioritized_closed = 0
    prioritized_quarantined = 0
    for rel in prioritized_rel:
        module = modules_by_rel.get(rel)
        if module is None:
            prioritized.append(
                {
                    "relative_file": rel,
                    "present": False,
                    "status": "missing",
                    "blocking_claims": [],
                }
            )
            continue
        blocking_claims = [f"axiom:{name}" for name in module["axiom_names"]] + [
            f"sorry_theorem:{name}" for name in module["sorry_theorems"]
        ]
        status = str(module["status"])
        if status == "closed_for_local_claim_reuse":
            prioritized_closed += 1
        else:
            prioritized_quarantined += 1
        prioritized.append(
            {
                "relative_file": rel,
                "present": True,
                "status": status,
                "theorem_or_lemma_count": module["theorem_or_lemma_count"],
                "axiom_count": module["axiom_count"],
                "sorry_count": module["sorry_count"],
                "blocking_claims": blocking_claims,
            }
        )

    payload = {
        "lean_root": str(lean_root),
        "file_count": len(modules),
        "prioritized_files": prioritized_rel,
        "summary": {
            "closed_for_local_claim_reuse": closed,
            "quarantined": quarantined,
            "prioritized_closed_for_local_claim_reuse": prioritized_closed,
            "prioritized_quarantined": prioritized_quarantined,
        },
        "policy": {
            "closed_for_local_claim_reuse": "no axiom and no sorry in file",
            "quarantined": "contains axiom or sorry; theorem claims cannot be used as authoritative FRACDASH evidence",
        },
        "prioritized_closure_queue": prioritized,
        "modules": modules,
    }

    json_out = Path(args.output_json)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# MonsterLean Claim Status",
        "",
        f"- Lean root: `{lean_root}`",
        f"- File count: `{len(modules)}`",
        f"- Closed for local claim reuse: `{closed}`",
        f"- Quarantined: `{quarantined}`",
        "",
        "## Prioritized Closure Queue",
        "",
    ]
    if not prioritized:
        lines.append("- none")
    else:
        for item in prioritized:
            if not item["present"]:
                lines.append(f"- `{item['relative_file']}` (`missing`)")
                continue
            blockers = item["blocking_claims"]
            blocker_text = ", ".join(blockers) if blockers else "none"
            lines.append(
                f"- `{item['relative_file']}` (`status={item['status']}`, `axiom={item['axiom_count']}`, `sorry={item['sorry_count']}`, `blockers={blocker_text}`)"
            )
    lines.extend(
        [
            "",
        "## Quarantined Files",
        "",
        ]
    )
    q = [m for m in modules if m["status"] != "closed_for_local_claim_reuse"]
    if not q:
        lines.append("- none")
    else:
        for m in q:
            lines.append(
                f"- `{m['relative_file']}` (`axiom={m['axiom_count']}`, `sorry={m['sorry_count']}`, `theorem_or_lemma={m['theorem_or_lemma_count']}`)"
            )
    lines.extend(
        [
            "",
            "## Closed Files",
            "",
        ]
    )
    c = [m for m in modules if m["status"] == "closed_for_local_claim_reuse"]
    if not c:
        lines.append("- none")
    else:
        for m in c:
            lines.append(f"- `{m['relative_file']}`")

    md_out = Path(args.output_md)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"wrote {json_out}")
        print(f"wrote {md_out}")


if __name__ == "__main__":
    main()
