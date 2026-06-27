"""Load the local package source for tests (avoids stale installed wheel)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PKG_DIR = Path(__file__).resolve().parent.parent / "src" / "objectifiabilist_SHAKERF"


def _ensure_local_package() -> None:
    if getattr(_ensure_local_package, "_loaded", False):
        return
    init = _PKG_DIR / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        "objectifiabilist",
        init,
        submodule_search_locations=[str(_PKG_DIR)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load objectifiabilist from {_PKG_DIR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["objectifiabilist"] = module
    spec.loader.exec_module(module)
    _ensure_local_package._loaded = True  # type: ignore[attr-defined]


_ensure_local_package()
