"""Shared helpers for AIE backend passes."""

from __future__ import annotations

from typing import Any


def sanitize_identifier(name: str, prefix: str = 'id') -> str:
    """Return a C/C++ friendly identifier derived from ``name``."""

    if not name:
        return prefix

    filtered = ''.join(ch if (ch.isalnum() or ch == '_') else '_' for ch in str(name))
    filtered = filtered.lstrip('_') or '_'
    if filtered[0].isdigit():
        filtered = f'{prefix}_{filtered}'
    return filtered


def lookup_layer(model: Any, name: str):
    """Return the hls4ml layer instance with the given name, or None if missing."""
    try:
        return model.get_layer(name)
    except AttributeError:
        for layer in model.get_layers():
            if getattr(layer, 'name', None) == name:
                return layer
    return None
