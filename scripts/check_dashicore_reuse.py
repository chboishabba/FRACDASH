#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gpu.dashicore_bridge import import_dashicore_module, import_summary


def run_passthrough_smoke() -> dict[str, object]:
    adapter_mod = import_dashicore_module("gpu_vulkan_adapter")
    carrier_mod = import_dashicore_module("dashi_core.carrier")

    summary = import_summary()
    shader_path = Path(summary["shader_passthrough"])
    spv_path = Path(summary["spv_passthrough"])

    carrier = carrier_mod.Carrier.from_signed(np.array([1, 0, -1, 1], dtype=np.int8))
    config = adapter_mod.VulkanKernelConfig(
        shader_path=shader_path,
        spv_path=spv_path,
        compile_on_init=False,
        compile_on_dispatch=False,
    )
    adapter = adapter_mod.VulkanBackendAdapter(config=config, allow_fallback=True, dispatcher=None)
    kernel = adapter_mod.VulkanCarrierKernel(adapter)
    out = kernel.apply(carrier)

    return {
        "input_signed": carrier.to_signed().tolist(),
        "output_signed": out.to_signed().tolist(),
        "support_preserved": bool(np.array_equal(out.support, carrier.support)),
        "sign_preserved": bool(np.array_equal(out.sign, carrier.sign)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify FRACDASH can import reusable dashiCORE Vulkan helpers by reference."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    args = parser.parse_args()

    summary = import_summary()
    summary["passthrough_smoke"] = run_passthrough_smoke()

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return

    print("dashiCORE root:", summary["dashicore_root"])
    print("Reusable module files:")
    for name, meta in summary["modules"].items():
        print(f"  - {name}: {meta['file']}")
    print("Shader passthrough:", summary["shader_passthrough"])
    print("SPIR-V passthrough:", summary["spv_passthrough"])
    smoke = summary["passthrough_smoke"]
    print("Passthrough smoke:")
    print("  - input signed:", smoke["input_signed"])
    print("  - output signed:", smoke["output_signed"])
    print("  - support preserved:", smoke["support_preserved"])
    print("  - sign preserved:", smoke["sign_preserved"])


if __name__ == "__main__":
    main()
