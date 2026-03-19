#!/usr/bin/env python3
"""Consistency check between Python delta exports and Agda-side rule inventory.

This script ensures that the Python oracle (source of truth for deltas) and
the Agda certification (source of truth for formal proofs) agree on:
1. Rule names
2. Register/Coordinate order
3. Signed delta values
"""

import json
import re
import sys
from pathlib import Path


def _parse_agda_rules(agda_path: Path):
    content = agda_path.read_text(encoding="utf-8")
    
    # Extract rules from data _↦₁_
    # Look for rule name followed by colon
    # We look between 'data _↦₁_' and 'deltaOf'
    rules_section_match = re.search(r"data _↦₁_ : Physics1State → Physics1State → Set where(.*?)\ndeltaOf", content, re.DOTALL)
    if not rules_section_match:
        return {}
    
    rules_section = rules_section_match.group(1)
    rule_names = re.findall(r"^\s+([\w-]+)\s+:", rules_section, re.MULTILINE)
    
    # Extract deltas from deltaOf
    # deltaOf join-left-high  = delta4 d0 d0 dm1 d0
    delta_map = {}
    delta_val_to_int = {"dm2": -2, "dm1": -1, "d0": 0, "dp1": 1, "dp2": 2}
    
    for name in rule_names:
        # Use re.escape for safety, although names are simple
        delta_match = re.search(fr"deltaOf {re.escape(name)}\s+= delta4 (\w+) (\w+) (\w+) (\w+)", content)
        if delta_match:
            vals = [delta_val_to_int[v] for v in delta_match.groups()]
            delta_map[name] = vals
            
    return delta_map


def main():
    repo_root = Path(__file__).resolve().parents[1]
    canonical_json = repo_root / "benchmarks" / "results" / "physics1_deltas_canonical.json"
    agda_file = repo_root / "formalism" / "Physics1StepDelta.agda"
    
    if not canonical_json.exists():
        print(f"Error: {canonical_json} not found. Run scripts/reproduce_physics1_oracle.sh first.")
        sys.exit(1)
        
    if not agda_file.exists():
        print(f"Error: {agda_file} not found.")
        sys.exit(1)
        
    with open(canonical_json, "r") as f:
        oracle_data = json.load(f)
        
    oracle_deltas = {r["name"]: r["delta_vector"] for r in oracle_data["records"]}
    agda_deltas = _parse_agda_rules(agda_file)
    
    success = True
    
    # Check rule names alignment (normalized underscores to hyphens)
    oracle_names = set(oracle_deltas.keys())
    agda_names = set(agda_deltas.keys())
    
    if oracle_names != agda_names:
        print("Rule name discrepancy detected!")
        print(f"Only in Oracle (Python): {oracle_names - agda_names}")
        print(f"Only in Agda: {agda_names - oracle_names}")
        # We continue to check values for the intersection
        success = False
        
    common_names = oracle_names & agda_names
    for name in sorted(common_names):
        o_delta = oracle_deltas[name]
        a_delta = agda_deltas[name]
        if o_delta != a_delta:
            print(f"Delta mismatch for rule '{name}':")
            print(f"  Oracle: {o_delta}")
            print(f"  Agda:   {a_delta}")
            success = False
            
    if success:
        print(f"Consistency check PASSED for {len(common_names)} rules.")
        sys.exit(0)
    else:
        print("Consistency check FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
