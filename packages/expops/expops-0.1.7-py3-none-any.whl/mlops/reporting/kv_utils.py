from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Tuple

from mlops.core.workspace import get_projects_root, get_workspace_root
from mlops.storage.factory import create_kv_store as _create_kv_store


def _load_backend_cfg_from_project_config(project_id: str) -> dict[str, Any]:
    root = get_workspace_root()
    cfg_path = get_projects_root(root) / project_id / "configs" / "project_config.yaml"
    if not cfg_path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except Exception:
        return {}
    try:
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
        cache_cfg = (((cfg.get("model") or {}).get("parameters") or {}).get("cache") or {})
        backend_cfg = (cache_cfg.get("backend") or {}) if isinstance(cache_cfg, dict) else {}
        return backend_cfg if isinstance(backend_cfg, dict) else {}
    except Exception:
        return {}


def _as_int(val: Any) -> Optional[int]:
    if val is None or val == "":
        return None
    try:
        return int(val)
    except Exception:
        return None


def create_kv_store(project_id: str) -> Optional[Any]:
    """Create a KV store instance for chart subprocesses.

    Priority:
    - `MLOPS_KV_BACKEND` (if set)
    - project config `projects/<id>/configs/project_config.yaml` (cache.backend)
    - environment-driven heuristics
    """
    backend_cfg = _load_backend_cfg_from_project_config(project_id)
    root = get_workspace_root()
    project_root = get_projects_root(root) / project_id
    return _create_kv_store(
        project_id,
        backend_cfg,
        env=os.environ,
        workspace_root=root,
        project_root=project_root,
    )


def resolve_kv_path_from_env_or_firestore(project_id: str, run_id: str, probe_path: str) -> Tuple[str, Optional[str]]:
    """Deprecated: kept for older chart scripts (probe IDs removed)."""
    try:
        from mlops.storage.path_utils import encode_probe_path  # type: ignore
    except Exception:
        encode_probe_path = lambda s: s  # type: ignore
    if run_id and probe_path:
        enc = encode_probe_path(probe_path)
        return f"metric/{run_id}/probes_by_path/{enc}", None
    if run_id:
        return f"runs/{run_id}", None
    return "", None


__all__ = [
    "create_kv_store",
    "resolve_kv_path_from_env_or_firestore",
]


