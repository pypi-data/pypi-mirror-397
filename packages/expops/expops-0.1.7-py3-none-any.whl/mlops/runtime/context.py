from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class RunContext:
    """Typed, run-scoped context passed through orchestration/execution boundaries.

    This is intentionally small in Phase 2: it centralizes the identity (project/run)
    and key resolved paths/config snapshots so components don't rely on implicit
    global state or environment variables.
    """

    workspace_root: Path
    project_id: str
    project_root: Path
    run_id: str

    runtime_python: Optional[str] = None
    reporting_python: Optional[str] = None

    cache_backend: Dict[str, Any] = field(default_factory=dict)
    cache_config: Dict[str, Any] = field(default_factory=dict)
    reporting_config: Dict[str, Any] = field(default_factory=dict)


__all__ = [
    "RunContext",
]


