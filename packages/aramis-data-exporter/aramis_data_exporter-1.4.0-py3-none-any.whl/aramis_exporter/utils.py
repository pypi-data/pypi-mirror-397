"""Utility functions for Aramis Exporter."""
from dataclasses import fields, is_dataclass
from pathlib import Path


def safe_getattr(obj, path, default=None):
    current = obj
    for part in path.split("."):
        try:
            current = getattr(current, part)
        except Exception:
            return default
        if current is None:
            return default
    return current


def safe_asdict(obj):
    if obj is None:
        return None

    # Dataclass -> dict of field -> safe_asdict(value)
    if is_dataclass(obj):
        result = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            result[f.name] = safe_asdict(value)
        return result

    # Sequence types
    if isinstance(obj, (list, tuple, set)):
        t = type(obj)
        return t(safe_asdict(v) for v in obj)

    # Mapping types
    if isinstance(obj, dict):
        return {k: safe_asdict(v) for k, v in obj.items()}

    # Anything else: leave as-is (int, float, str, numpy arrays, etc.)
    return obj


def safe_path(base, fn=None):
    if base is None:
        return None

    base = Path(base)

    if fn is None:
        return base

    fn = Path(fn)

    if fn.is_absolute():
        fn = fn.relative_to(fn.anchor)

    p = (base / fn).resolve()
    base_resolved = base.resolve()

    if base_resolved not in p.parents and p != base_resolved:
        raise ValueError(f"Unsafe path: {p}")

    return p
