from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from mlops.core.workspace import resolve_relative_path


def export_kv_env(
    backend_cfg: dict[str, Any] | None,
    *,
    workspace_root: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> dict[str, str]:
    """Return environment variables required for the configured KV backend.

    This is used at process boundaries (chart subprocesses, cluster submissions, etc.).
    """
    if not isinstance(backend_cfg, dict):
        return {}

    env: dict[str, str] = {}
    typ = str(backend_cfg.get("type") or "").strip().lower()
    if not typ:
        return env

    if typ in {"memory", "inmemory", "in-memory", "mem"}:
        env["MLOPS_KV_BACKEND"] = "memory"
        return env

    if typ == "redis":
        env["MLOPS_KV_BACKEND"] = "redis"
        if backend_cfg.get("host") is not None:
            env["MLOPS_REDIS_HOST"] = str(backend_cfg.get("host"))
        if backend_cfg.get("port") is not None:
            env["MLOPS_REDIS_PORT"] = str(backend_cfg.get("port"))
        if backend_cfg.get("db") is not None:
            env["MLOPS_REDIS_DB"] = str(backend_cfg.get("db"))
        if backend_cfg.get("password") is not None:
            env["MLOPS_REDIS_PASSWORD"] = str(backend_cfg.get("password"))
        return env

    if typ == "gcp":
        env["MLOPS_KV_BACKEND"] = "gcp"
        if backend_cfg.get("gcp_project") is not None:
            env["GOOGLE_CLOUD_PROJECT"] = str(backend_cfg.get("gcp_project"))
        if backend_cfg.get("emulator_host") is not None:
            env["FIRESTORE_EMULATOR_HOST"] = str(backend_cfg.get("emulator_host"))

        creds = backend_cfg.get("credentials_json")
        if creds:
            try:
                p = resolve_relative_path(
                    str(creds),
                    project_root=project_root,
                    workspace_root=workspace_root,
                )
                env["GOOGLE_APPLICATION_CREDENTIALS"] = str(p)
            except Exception:
                env["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds)
        return env

    # Unknown backend type: do not emit anything.
    return env


def export_run_env(run_context: Any) -> dict[str, str]:
    """Return a baseline env mapping for a run-scoped context."""
    env: dict[str, str] = {}

    workspace_root = getattr(run_context, "workspace_root", None)
    project_root = getattr(run_context, "project_root", None)

    if workspace_root is not None:
        env["MLOPS_WORKSPACE_DIR"] = str(workspace_root)

    project_id = getattr(run_context, "project_id", None)
    if project_id:
        env["MLOPS_PROJECT_ID"] = str(project_id)

    run_id = getattr(run_context, "run_id", None)
    if run_id:
        env["MLOPS_RUN_ID"] = str(run_id)

    runtime_python = getattr(run_context, "runtime_python", None)
    if runtime_python:
        env["MLOPS_RUNTIME_PYTHON"] = str(runtime_python)

    reporting_python = getattr(run_context, "reporting_python", None)
    if reporting_python:
        env["MLOPS_REPORTING_PYTHON"] = str(reporting_python)

    reporting_cfg = getattr(run_context, "reporting_config", None)
    if isinstance(reporting_cfg, dict):
        try:
            env["MLOPS_REPORTING_CONFIG"] = json.dumps(reporting_cfg)
        except Exception:
            pass

    backend_cfg = getattr(run_context, "cache_backend", None)
    if isinstance(backend_cfg, dict):
        env.update(export_kv_env(backend_cfg, workspace_root=workspace_root, project_root=project_root))

    return env


__all__ = [
    "export_kv_env",
    "export_run_env",
]


