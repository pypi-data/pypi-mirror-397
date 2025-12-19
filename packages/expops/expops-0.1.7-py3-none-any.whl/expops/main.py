"""ExpOps CLI wrapper.

Console scripts in `pyproject.toml` point here so the user-facing command is
`expops`, while the implementation remains in `mlops.main`.
"""

from __future__ import annotations

from mlops.main import main

__all__ = ["main"]


