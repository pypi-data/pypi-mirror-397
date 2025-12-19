"""ExpOps distribution package.

The project historically used the internal Python package name `mlops`. The
`expops` package provides thin wrappers so user-facing imports and module
execution can follow the distribution name.
"""

from __future__ import annotations

try:
    from mlops._version import version as __version__  # type: ignore
except Exception:
    __version__ = "0.0.0"

__all__ = ["__version__"]


