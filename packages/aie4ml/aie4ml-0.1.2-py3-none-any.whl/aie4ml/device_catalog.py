# Copyright 2025 D. Danopoulos, aie4ml
# SPDX-License-Identifier: Apache-2.0

"""Helpers for loading the AIE device catalog."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

_DEVICE_CATALOG: Dict[str, Any] | None = None


def load_device_catalog() -> Dict[str, Any]:
    """Return the cached device catalog loaded from aie_devices.json."""
    global _DEVICE_CATALOG
    if _DEVICE_CATALOG is None:
        catalog_path = Path(__file__).with_name('aie_devices.json')
        if catalog_path.exists():
            with open(catalog_path, 'r') as handle:
                _DEVICE_CATALOG = json.load(handle)
        else:
            _DEVICE_CATALOG = {}
    return _DEVICE_CATALOG
