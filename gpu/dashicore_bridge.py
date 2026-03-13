from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from types import ModuleType


DEFAULT_DASHICORE_ROOT = Path(__file__).resolve().parents[2] / "dashiCORE"
ENV_DASHICORE_ROOT = "FRACDASH_DASHICORE_ROOT"

REUSED_MODULES = (
    "gpu_common_methods",
    "gpu_vulkan_dispatcher",
    "gpu_vulkan_backend",
    "gpu_vulkan_adapter",
    "gpu_vulkan_gemv",
)


def resolve_dashicore_root() -> Path:
    candidate = Path(os.environ.get(ENV_DASHICORE_ROOT, str(DEFAULT_DASHICORE_ROOT))).expanduser()
    root = candidate.resolve()
    if not root.exists():
        raise FileNotFoundError(f"dashiCORE root not found: {root}")
    if not (root / "dashi_core" / "__init__.py").exists():
        raise FileNotFoundError(f"dashiCORE package not found under: {root}")
    return root


def ensure_dashicore_on_sys_path() -> Path:
    root = resolve_dashicore_root()
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return root


def import_dashicore_module(name: str) -> ModuleType:
    if name not in REUSED_MODULES and not name.startswith("dashi_core"):
        raise ValueError(f"unsupported dashiCORE import: {name}")
    ensure_dashicore_on_sys_path()
    return importlib.import_module(name)


def module_path_map() -> dict[str, Path]:
    root = ensure_dashicore_on_sys_path()
    return {name: root / f"{name}.py" for name in REUSED_MODULES}


def resolve_shader_asset(name: str) -> Path:
    gpu_common_methods = import_dashicore_module("gpu_common_methods")
    return Path(gpu_common_methods.resolve_shader(name))


def resolve_spv_asset(name: str) -> Path:
    gpu_common_methods = import_dashicore_module("gpu_common_methods")
    return Path(gpu_common_methods.resolve_spv(name))


def import_summary() -> dict[str, object]:
    root = ensure_dashicore_on_sys_path()
    loaded = {}
    for name in REUSED_MODULES:
        module = import_dashicore_module(name)
        loaded[name] = {
            "file": str(Path(module.__file__).resolve()),
        }
    return {
        "dashicore_root": str(root),
        "modules": loaded,
        "shader_passthrough": str(resolve_shader_asset("carrier_passthrough")),
        "spv_passthrough": str(resolve_spv_asset("carrier_passthrough")),
    }
