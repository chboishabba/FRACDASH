#!/usr/bin/env python3
"""Probe named equation families against DASHI-style quantized local dynamics.

This is intentionally a decision-quality harness, not a claim of solver parity.
It compares:

1. A transparent NumPy reference discretization.
2. A DASHI-style balanced-ternary local update path.

The current use is to test whether the bridge-aligned signed local dynamics are
even plausible as a numerical path for a named family, or whether the actual
project win is better understood as proof-carrying / auditable execution.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import numpy as np


Family = Literal["wave", "heat"]


@dataclass(frozen=True)
class ProbeMetrics:
    family: str
    classification: str
    recommended_next_family: str
    decision: str
    grid_size: int
    steps: int
    dx: float
    dt: float
    threshold: float
    reference_runtime_seconds: float
    dashi_runtime_seconds: float
    runtime_ratio_dashi_over_reference: float
    normalized_l2_error: float
    normalized_linf_error: float
    correlation: float
    reference_energy_start: float
    reference_energy_end: float
    dashi_energy_start: float
    dashi_energy_end: float
    dashi_nonzero_fraction: float
    dashi_histogram: dict[str, int]
    dashi_method: str
    notes: list[str]


def periodic_laplacian(values: np.ndarray, dx: float) -> np.ndarray:
    return (np.roll(values, 1) - 2.0 * values + np.roll(values, -1)) / (dx * dx)


def quantize_ternary(values: np.ndarray, threshold: float) -> np.ndarray:
    out = np.zeros_like(values, dtype=np.int8)
    out[values > threshold] = 1
    out[values < -threshold] = -1
    return out


def decode_ternary(values: np.ndarray, amplitude_scale: float) -> np.ndarray:
    return values.astype(np.float64) * amplitude_scale


def initial_condition(family: Family, grid_size: int) -> tuple[np.ndarray, np.ndarray]:
    x = np.linspace(0.0, 1.0, grid_size, endpoint=False)
    gaussian = np.exp(-((x - 0.5) ** 2) / 0.01)
    gaussian /= np.max(np.abs(gaussian))
    if family == "heat":
        return gaussian.astype(np.float64), np.zeros(grid_size, dtype=np.float64)
    carrier = np.sin(2.0 * math.pi * x) * np.exp(-((x - 0.5) ** 2) / 0.08)
    carrier /= np.max(np.abs(carrier))
    return carrier.astype(np.float64), np.zeros(grid_size, dtype=np.float64)


def run_reference_heat(u0: np.ndarray, *, steps: int, dx: float, dt: float, diffusivity: float) -> np.ndarray:
    state = u0.copy()
    alpha = diffusivity * dt
    for _ in range(steps):
        state = state + alpha * periodic_laplacian(state, dx)
    return state


def run_reference_wave(
    u0: np.ndarray,
    v0: np.ndarray,
    *,
    steps: int,
    dx: float,
    dt: float,
    wave_speed: float,
) -> tuple[np.ndarray, np.ndarray]:
    u = u0.copy()
    v = v0.copy()
    c2 = wave_speed * wave_speed
    for _ in range(steps):
        v = v + dt * c2 * periodic_laplacian(u, dx)
        u = u + dt * v
    return u, v


def run_dashi_heat(
    u0: np.ndarray,
    *,
    steps: int,
    dx: float,
    dt: float,
    diffusivity: float,
    threshold: float,
) -> np.ndarray:
    amplitude_scale = float(np.max(np.abs(u0))) or 1.0
    q = quantize_ternary(u0 / amplitude_scale, threshold)
    alpha = diffusivity * dt / (dx * dx)
    for _ in range(steps):
        qf = q.astype(np.float64)
        qf = qf + alpha * (np.roll(qf, 1) - 2.0 * qf + np.roll(qf, -1))
        q = quantize_ternary(qf, threshold)
    return decode_ternary(q, amplitude_scale)


def run_dashi_wave(
    u0: np.ndarray,
    v0: np.ndarray,
    *,
    steps: int,
    threshold: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    amplitude_scale = float(np.max(np.abs(u0))) or 1.0
    velocity_scale = max(float(np.max(np.abs(v0))), 1.0)
    q_u = quantize_ternary(u0 / amplitude_scale, threshold)
    q_v = quantize_ternary(v0 / velocity_scale, threshold)
    q_u_start = q_u.copy()
    for _ in range(steps):
        lap = np.roll(q_u, 1) - 2 * q_u + np.roll(q_u, -1)
        q_v = np.clip(q_v + np.sign(lap).astype(np.int8), -1, 1).astype(np.int8)
        q_u = np.clip(q_u + np.sign(q_v).astype(np.int8), -1, 1).astype(np.int8)
    return (
        decode_ternary(q_u, amplitude_scale),
        decode_ternary(q_v, velocity_scale),
        q_u_start,
        q_u,
    )


def normalized_errors(reference: np.ndarray, candidate: np.ndarray) -> tuple[float, float]:
    denom = float(np.linalg.norm(reference)) or 1.0
    l2 = float(np.linalg.norm(reference - candidate) / denom)
    linf = float(np.max(np.abs(reference - candidate)) / (float(np.max(np.abs(reference))) or 1.0))
    return l2, linf


def safe_correlation(reference: np.ndarray, candidate: np.ndarray) -> float:
    ref_std = float(np.std(reference))
    cand_std = float(np.std(candidate))
    if ref_std <= 1e-12 or cand_std <= 1e-12:
        return 0.0
    return float(np.corrcoef(reference, candidate)[0, 1])


def heat_energy(u: np.ndarray) -> float:
    return float(np.sum(u * u))


def wave_energy(u: np.ndarray, v: np.ndarray, dx: float, wave_speed: float) -> float:
    grad = (np.roll(u, -1) - u) / dx
    return float(0.5 * np.sum(v * v + (wave_speed * grad) ** 2))


def classify_probe(
    family: Family,
    *,
    l2: float,
    linf: float,
    correlation: float,
) -> tuple[str, str, str, list[str]]:
    notes: list[str] = []
    if family == "wave":
        if correlation < 0.55 or l2 > 0.85:
            notes.append("wave probe looks structurally mismatched to the current dissipative/quantized local dynamics")
            return (
                "mismatch_requires_fallback",
                "heat",
                "fallback_to_heat",
                notes,
            )
        if correlation >= 0.80 and l2 <= 0.45:
            notes.append("wave probe shows a plausible solver-shaped fit worth deeper benchmarking")
            return (
                "candidate_solver_path",
                "wave",
                "continue_wave",
                notes,
            )
        notes.append("wave probe is only qualitatively similar; likely stronger as an interpretation target than a direct solver target")
        return (
            "qualitative_only",
            "heat",
            "deprioritize_wave_runtime_claim",
            notes,
        )

    if correlation >= 0.90 and l2 <= 0.35 and linf <= 0.50:
        notes.append("heat probe is aligned enough to justify a stricter runtime/accuracy comparison")
        return (
            "candidate_solver_path",
            "heat",
            "benchmark_heat_more_seriously",
            notes,
        )
    if correlation >= 0.75 and l2 <= 0.75:
        notes.append("heat probe is qualitatively aligned but not yet competitive as a same-accuracy solver path")
        return (
            "qualitative_only",
            "heat",
            "keep_heat_as_interpretation_and_baseline_probe",
            notes,
        )
    notes.append("heat probe does not yet support a strong same-equation solver claim")
    return (
        "proof_carrying_or_interpretive_only",
        "heat",
        "treat_current_value_as_auditability_not_speed",
        notes,
    )


def choose_stable_dt(family: Family, *, dx: float, diffusivity: float, wave_speed: float, user_dt: float | None) -> float:
    if user_dt is not None:
        return user_dt
    if family == "heat":
        return 0.20 * dx * dx / max(diffusivity, 1e-9)
    return 0.40 * dx / max(wave_speed, 1e-9)


def choose_default_threshold(family: Family, user_threshold: float | None) -> float:
    if user_threshold is not None:
        return user_threshold
    if family == "heat":
        return 0.50
    return 0.20


def run_probe(
    family: Family,
    *,
    grid_size: int,
    steps: int,
    dt: float | None,
    threshold: float | None,
    diffusivity: float,
    wave_speed: float,
) -> ProbeMetrics:
    dx = 1.0 / grid_size
    dt = choose_stable_dt(family, dx=dx, diffusivity=diffusivity, wave_speed=wave_speed, user_dt=dt)
    threshold = choose_default_threshold(family, threshold)
    u0, v0 = initial_condition(family, grid_size)

    ref_start = time.perf_counter()
    if family == "heat":
        u_ref = run_reference_heat(u0, steps=steps, dx=dx, dt=dt, diffusivity=diffusivity)
        reference_runtime = time.perf_counter() - ref_start
        dashi_start = time.perf_counter()
        u_dashi = run_dashi_heat(u0, steps=steps, dx=dx, dt=dt, diffusivity=diffusivity, threshold=threshold)
        dashi_runtime = time.perf_counter() - dashi_start
        l2, linf = normalized_errors(u_ref, u_dashi)
        corr = safe_correlation(u_ref, u_dashi)
        classification, next_family, decision, notes = classify_probe("heat", l2=l2, linf=linf, correlation=corr)
        notes.append("heat benchmark uses a quantized explicit diffusion step rather than the earlier saturating sign-of-laplacian update")
        q_final = quantize_ternary(u_dashi / ((float(np.max(np.abs(u0))) or 1.0)), threshold)
        return ProbeMetrics(
            family=family,
            classification=classification,
            recommended_next_family=next_family,
            decision=decision,
            grid_size=grid_size,
            steps=steps,
            dx=dx,
            dt=dt,
            threshold=threshold,
            reference_runtime_seconds=reference_runtime,
            dashi_runtime_seconds=dashi_runtime,
            runtime_ratio_dashi_over_reference=(dashi_runtime / reference_runtime) if reference_runtime > 0 else float("inf"),
            normalized_l2_error=l2,
            normalized_linf_error=linf,
            correlation=corr,
            reference_energy_start=heat_energy(u0),
            reference_energy_end=heat_energy(u_ref),
            dashi_energy_start=heat_energy(u0),
            dashi_energy_end=heat_energy(u_dashi),
            dashi_nonzero_fraction=float(np.count_nonzero(q_final)) / float(q_final.size),
            dashi_histogram={str(v): int(np.sum(q_final == v)) for v in (-1, 0, 1)},
            dashi_method="quantized_explicit_diffusion",
            notes=notes,
        )

    u_ref, v_ref = run_reference_wave(u0, v0, steps=steps, dx=dx, dt=dt, wave_speed=wave_speed)
    reference_runtime = time.perf_counter() - ref_start
    dashi_start = time.perf_counter()
    u_dashi, v_dashi, q_u_start, q_u_final = run_dashi_wave(u0, v0, steps=steps, threshold=threshold)
    dashi_runtime = time.perf_counter() - dashi_start
    l2, linf = normalized_errors(u_ref, u_dashi)
    corr = safe_correlation(u_ref, u_dashi)
    classification, next_family, decision, notes = classify_probe("wave", l2=l2, linf=linf, correlation=corr)
    notes.append("wave benchmark uses a transparent NumPy reference and a balanced-ternary position/velocity probe, not a theorem-grade matched solver")
    return ProbeMetrics(
        family=family,
        classification=classification,
        recommended_next_family=next_family,
        decision=decision,
        grid_size=grid_size,
        steps=steps,
        dx=dx,
        dt=dt,
        threshold=threshold,
        reference_runtime_seconds=reference_runtime,
        dashi_runtime_seconds=dashi_runtime,
        runtime_ratio_dashi_over_reference=(dashi_runtime / reference_runtime) if reference_runtime > 0 else float("inf"),
        normalized_l2_error=l2,
        normalized_linf_error=linf,
        correlation=corr,
        reference_energy_start=wave_energy(u0, v0, dx, wave_speed),
        reference_energy_end=wave_energy(u_ref, v_ref, dx, wave_speed),
        dashi_energy_start=wave_energy(decode_ternary(q_u_start, float(np.max(np.abs(u0))) or 1.0), np.zeros_like(v0), dx, wave_speed),
        dashi_energy_end=wave_energy(u_dashi, v_dashi, dx, wave_speed),
        dashi_nonzero_fraction=float(np.count_nonzero(q_u_final)) / float(q_u_final.size),
        dashi_histogram={str(v): int(np.sum(q_u_final == v)) for v in (-1, 0, 1)},
        dashi_method="quantized_position_velocity_probe",
        notes=notes,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe named-equation solver viability for DASHI-style quantized dynamics.")
    parser.add_argument("--family", choices=("wave", "heat"), default="wave")
    parser.add_argument("--grid-size", type=int, default=256)
    parser.add_argument("--steps", type=int, default=96)
    parser.add_argument("--dt", type=float)
    parser.add_argument("--threshold", type=float)
    parser.add_argument("--diffusivity", type=float, default=0.15)
    parser.add_argument("--wave-speed", type=float, default=1.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    metrics = run_probe(
        args.family,
        grid_size=args.grid_size,
        steps=args.steps,
        dt=args.dt,
        threshold=args.threshold,
        diffusivity=args.diffusivity,
        wave_speed=args.wave_speed,
    )
    payload = asdict(metrics)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
