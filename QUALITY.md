# FRACDASH Quality Management System

Aligned with ISO 9001:2015 principles and implemented as Standard Operating Procedures (SOPS).

## 1. Document Control (ISO 9001 §7.5)

- All project intent lives in version-controlled markdown (`COMPACTIFIED_CONTEXT.md`, `AGENTS.md`, `spec.md`).
- Material changes are recorded in `CHANGELOG.md` before merge.
- Experiment artifacts carry datestamped filenames under `benchmarks/results/`.
- The Nix flake lockfile (`flake.lock`) pins all toolchain versions for reproducibility.

## 2. Quality Gates (ISO 9001 §8.6)

Five numbered gates run on every push and PR:

| Gate | What | Enforced by |
|------|------|-------------|
| QG-1 | Nix flake evaluation | `nix flake check` |
| QG-2 | Lint (flake8 + shellcheck) | `make lint` |
| QG-3 | Compile check (py_compile) | `make check` |
| QG-4 | Physics invariant targets | `make test` |
| QG-5 | Artifact reproducibility | `toy_dashi_transitions.py` |

QG-4 is advisory until all upstream artifacts are committed.

## 3. Change Management (ISO 9001 §6.3)

- Pre-commit hook (`.githooks/pre-commit`) enforces QG-1 through QG-3 locally.
- Enable: `git config core.hooksPath .githooks`
- CI (`.github/workflows/ci.yml`) enforces all five gates on the remote.
- Docs-before-code: update intent docs before implementation changes.

## 4. Nonconformity and Corrective Action (ISO 9001 §10.2)

- CI failures block merge.
- Physics invariant regressions are tracked via `check_physics_invariant_targets.py --json`.
- Timing regressions are caught by `scripts/check_timing_regression.py`.
- Each claim is tagged: `implemented`, `observed experimentally`, or `conjectured`.

## 5. Traceability (ISO 9001 §8.5.2)

- Every experiment artifact records its generation date, script entrypoint, and parameters.
- Bridge instances carry execution-status and regime-class tags (`formalism/BridgeInstances.agda`).
- Benchmark JSONL files are append-only; new runs get new datestamped filenames.

## 6. Continuous Improvement (ISO 9001 §10.3)

- `TODO.md` tracks the active task queue.
- `ROADMAP.md` tracks the phased implementation path.
- Physics baseline deltas (e.g. `physics22-baseline-delta.md`) record what each refinement gained or lost.

## Quick Start

```sh
# Enter the pinned dev environment
nix develop

# Run the full local quality gate
make check

# Enable the pre-commit hook
git config core.hooksPath .githooks
```
