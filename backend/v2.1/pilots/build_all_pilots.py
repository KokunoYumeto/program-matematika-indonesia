#!/usr/bin/env python3
"""Rebuild every additive v2.1 pilot from its frozen owner authorities."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load pilot builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load("pmi_v21_base_pilots", ROOT / "build_pilots.py")
d20 = load("pmi_v21_d20_pilot", ROOT / "build_d20_pilot.py")
manifests = {
    "A00": base.build_a00(),
    "B10": base.build_b10(),
    "D20": d20.build(),
}
print(json.dumps({"result": "pass", "pilots": {key: value["record_counts"] for key, value in manifests.items()}}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
