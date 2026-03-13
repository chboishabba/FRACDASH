from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np


DEFAULT_DEMO_PATH = Path(__file__).resolve().parents[1] / "fractran" / "src" / "Demo.hs"
HASH_SEED = 1469598103934665603
HASH_MULT = 1099511628211
HASH_PRIME_SCALE = 1000003


@dataclass(frozen=True)
class CompiledRuleLayout:
    numerator: Fraction
    denominator: Fraction
    den_thresholds: np.ndarray
    delta: np.ndarray
    required_mask: int
    numerator_value: int
    denominator_value: int


@dataclass(frozen=True)
class CompiledFractranLayout:
    name: str
    primes: np.ndarray
    rules: tuple[CompiledRuleLayout, ...]

    def encode_integer_state(self, value: int) -> np.ndarray:
        factors = factor_integer(value)
        return np.array([factors.get(int(prime), 0) for prime in self.primes], dtype=np.int32)

    def decode_integer_state(self, exponents: np.ndarray) -> int:
        total = 1
        for prime, exponent in zip(self.primes.tolist(), exponents.tolist()):
            if exponent:
                total *= int(prime) ** int(exponent)
        return total

    def state_hash(self, exponents: np.ndarray) -> int:
        acc = HASH_SEED
        for ix, exponent in enumerate(exponents.tolist()):
            if exponent == 0:
                continue
            prime = int(self.primes[ix])
            acc = (acc * HASH_MULT) + (prime * HASH_PRIME_SCALE) + int(exponent)
        return acc

    def step(self, exponents: np.ndarray, current_value: int) -> tuple[np.ndarray, int] | None:
        for rule in self.rules:
            if np.all(exponents >= rule.den_thresholds):
                next_exponents = exponents + rule.delta
                next_value = (current_value * rule.numerator_value) // rule.denominator_value
                return next_exponents, next_value
        return None

    def run_trace(self, init_value: int, logical_steps: int) -> list[tuple[np.ndarray, int]]:
        state = self.encode_integer_state(init_value)
        current_value = int(init_value)
        states: list[tuple[np.ndarray, int]] = []
        for _ in range(logical_steps):
            stepped = self.step(state, current_value)
            if stepped is None:
                break
            state, current_value = stepped
            states.append((state.copy(), current_value))
        return states

    def run_steps_batch(
        self, states: np.ndarray, steps: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        state_matrix = np.asarray(states, dtype=np.int32, order="C")
        if state_matrix.ndim == 1:
            state_matrix = state_matrix.reshape(1, -1)
        if state_matrix.ndim != 2:
            raise ValueError("states must be a 1D or 2D exponent array")
        if state_matrix.shape[1] != self.primes.shape[0]:
            raise ValueError("state prime dimension does not match compiled layout")
        if steps < 0:
            raise ValueError("steps must be non-negative")

        current = state_matrix.copy()
        selected_rules = np.full(current.shape[0], -1, dtype=np.int32)
        halted = np.zeros(current.shape[0], dtype=bool)
        for _ in range(steps):
            next_states = []
            next_rules = []
            next_halted = []
            for state in current:
                selected_rule = -1
                for ix, rule in enumerate(self.rules):
                    if np.all(state >= rule.den_thresholds):
                        selected_rule = ix
                        break
                if selected_rule < 0:
                    next_states.append(state.copy())
                    next_rules.append(-1)
                    next_halted.append(True)
                else:
                    rule = self.rules[selected_rule]
                    next_states.append((state + rule.delta).astype(np.int32, copy=False))
                    next_rules.append(selected_rule)
                    next_halted.append(False)
            current = np.stack(next_states, axis=0)
            selected_rules = np.asarray(next_rules, dtype=np.int32)
            halted = np.asarray(next_halted, dtype=bool)
        return current, selected_rules, halted

    def gpu_buffers(self) -> dict[str, np.ndarray]:
        den_thresholds = np.stack([rule.den_thresholds for rule in self.rules]).astype(np.int32, copy=False)
        deltas = np.stack([rule.delta for rule in self.rules]).astype(np.int32, copy=False)
        required_masks = np.array([rule.required_mask for rule in self.rules], dtype=np.uint32)
        numerator_values = np.array([rule.numerator_value for rule in self.rules], dtype=object)
        denominator_values = np.array([rule.denominator_value for rule in self.rules], dtype=object)
        return {
            "primes": self.primes.astype(np.int32, copy=False),
            "den_thresholds": den_thresholds,
            "deltas": deltas,
            "required_masks": required_masks,
            "numerator_values": numerator_values,
            "denominator_values": denominator_values,
        }

    def summary(self) -> dict[str, object]:
        buffers = self.gpu_buffers()
        return {
            "name": self.name,
            "prime_count": int(self.primes.shape[0]),
            "rule_count": len(self.rules),
            "buffer_shapes": {name: list(buffer.shape) for name, buffer in buffers.items()},
            "state_dtype": "int32",
            "required_mask_dtype": "uint32",
        }


def load_demo_program(name: str, demo_path: Path = DEFAULT_DEMO_PATH) -> list[Fraction]:
    source = demo_path.read_text()
    if name == "mult":
        match = re.search(r"^mult\s*=\s*map\s*\(uncurry\s*\(%\)\)\s*\[(.+)\]\s*$", source, re.MULTILINE)
        if match is None:
            raise ValueError("could not locate mult in Demo.hs")
        tuples = re.findall(r"\(([^,]+),\s*([^)]+)\)", match.group(1))
        return [Fraction(_eval_int_expr(num), _eval_int_expr(den)) for num, den in tuples]

    match = re.search(rf"^{re.escape(name)}\s*=\s*\[(.+)\]\s*$", source, re.MULTILINE)
    if match is None:
        raise ValueError(f"could not locate {name} in Demo.hs")
    terms = [term.strip() for term in match.group(1).split(",") if term.strip()]
    return [_parse_fraction_term(term) for term in terms]


def compile_program(name: str, fractions: list[Fraction]) -> CompiledFractranLayout:
    factor_maps = [(_fraction_factor_map(frac.numerator), _fraction_factor_map(frac.denominator)) for frac in fractions]
    primes = sorted({prime for num, den in factor_maps for prime in (*num.keys(), *den.keys())})
    prime_index = {prime: ix for ix, prime in enumerate(primes)}

    rules = []
    for frac, (num_map, den_map) in zip(fractions, factor_maps):
        thresholds = np.zeros(len(primes), dtype=np.int32)
        delta = np.zeros(len(primes), dtype=np.int32)
        required_mask = 0
        for prime, power in den_map.items():
            ix = prime_index[prime]
            thresholds[ix] = int(power)
            if power > 0:
                required_mask |= 1 << ix
        for prime in primes:
            ix = prime_index[prime]
            delta[ix] = int(num_map.get(prime, 0) - den_map.get(prime, 0))
        rules.append(
            CompiledRuleLayout(
                numerator=Fraction(frac.numerator, 1),
                denominator=Fraction(frac.denominator, 1),
                den_thresholds=thresholds,
                delta=delta,
                required_mask=required_mask,
                numerator_value=int(frac.numerator),
                denominator_value=int(frac.denominator),
            )
        )

    return CompiledFractranLayout(
        name=name,
        primes=np.array(primes, dtype=np.int32),
        rules=tuple(rules),
    )


def summarize_trace(layout: CompiledFractranLayout, trace: list[tuple[np.ndarray, int]]) -> dict[str, object]:
    if not trace:
        return {
            "logical_steps_reached": 0,
            "emitted_states": 0,
            "checksum": None,
            "final_state_hash": None,
        }

    checksum = sum(value for _, value in trace)
    final_hash = layout.state_hash(trace[-1][0])
    return {
        "logical_steps_reached": len(trace),
        "emitted_states": len(trace),
        "checksum": checksum,
        "final_state_hash": str(final_hash),
    }


def factor_integer(value: int) -> dict[int, int]:
    n = int(value)
    factors: dict[int, int] = {}
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            n //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def _fraction_factor_map(value: int) -> dict[int, int]:
    return factor_integer(int(value))


def _parse_fraction_term(term: str) -> Fraction:
    if "%" not in term:
        return Fraction(_eval_int_expr(term), 1)
    numerator_expr, denominator_expr = _split_top_level_fraction(term)
    return Fraction(_eval_int_expr(numerator_expr), _eval_int_expr(denominator_expr))


def _split_top_level_fraction(term: str) -> tuple[str, str]:
    depth = 0
    for ix, char in enumerate(term):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "%" and depth == 0:
            return term[:ix], term[ix + 1 :]
    raise ValueError(f"invalid fraction term: {term}")


def _eval_int_expr(expr: str) -> int:
    parsed = ast.parse(expr.replace("^", "**"), mode="eval")
    return int(_eval_ast(parsed.body))


def _eval_ast(node: ast.AST) -> int:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return int(node.value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        return _eval_ast(node.left) * _eval_ast(node.right)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        return _eval_ast(node.left) ** _eval_ast(node.right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_ast(node.operand)
    raise ValueError(f"unsupported Demo.hs integer expression: {ast.dump(node)}")
