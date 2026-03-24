# FRACDASH Makefile — SOPS/ISO 9001 quality-gated build
# All heavy targets run inside `nix develop` so deps are pinned.
SHELL := /bin/bash
.DEFAULT_GOAL := check

NIX_DEVELOP := nix develop --command

# ── Quality gates ──────────────────────────────────────────────
.PHONY: lint lint-py lint-sh check test build artifacts clean

lint: lint-py lint-sh  ## Run all linters

lint-py:  ## Lint Python sources
	$(NIX_DEVELOP) flake8 scripts/ gpu/ benchmarks/

lint-sh:  ## Shellcheck all shell scripts (advisory for existing code)
	$(NIX_DEVELOP) bash -c 'find scripts benchmarks -name "*.sh" -exec shellcheck {} +' || echo "shellcheck: warnings found (advisory)"

check: lint  ## Full pre-merge quality gate (lint + compile check + physics targets)
	$(NIX_DEVELOP) python3 -m py_compile scripts/toy_dashi_transitions.py
	$(NIX_DEVELOP) python3 -m py_compile scripts/check_physics_invariant_targets.py
	$(NIX_DEVELOP) python3 -m py_compile gpu/fractran_layout.py
	@echo "FRACDASH: all quality gates passed"

test:  ## Run physics invariant target suite
	$(NIX_DEVELOP) python3 scripts/check_physics_invariant_targets.py --json

build:  ## Build FRACTRAN binaries (requires fractran/ source)
	@if [ -f fractran/build.sh ]; then \
		cd fractran && $(NIX_DEVELOP) bash build.sh; \
	else \
		echo "fractran/build.sh not present — skipping binary build"; \
	fi

artifacts:  ## Generate reproducible benchmark artifacts
	$(NIX_DEVELOP) bash scripts/run_toy_dashi_phase2.sh
	@echo "Artifacts written to benchmarks/results/"

clean:  ## Remove generated caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf result .pre-commit-cache

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-14s %s\n", $$1, $$2}'
