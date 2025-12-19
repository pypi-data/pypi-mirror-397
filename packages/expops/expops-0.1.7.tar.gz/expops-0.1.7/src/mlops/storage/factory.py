from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional


def _as_int(val: Any) -> Optional[int]:
    if val is None or val == "":
        return None
    try:
        return int(val)
    except Exception:
        return None


def _norm_backend_type(value: Any) -> str:
    try:
        s = str(value or "").strip().lower()
    except Exception:
        return ""
    aliases = {
        "mem": "memory",
        "inmem": "memory",
        "in-memory": "memory",
        "inmemory": "memory",
        "firestore": "gcp",
    }
    return aliases.get(s, s)


def _resolve_relative_path(
    raw: Any,
    *,
    workspace_root: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> Optional[Path]:
    if not raw:
        return None
    try:
        p = Path(str(raw))
    except Exception:
        return None
    if p.is_absolute():
        return p
    candidates: list[Path] = []
    if project_root is not None:
        candidates.append(project_root / p)
    if workspace_root is not None:
        candidates.append(workspace_root / p)
    candidates.append(Path.cwd() / p)
    for c in candidates:
        try:
            if c.exists():
                return c.resolve()
        except Exception:
            continue
    # Fall back to the most likely base for debugging purposes.
    return (candidates[0] if candidates else p)


def _maybe_apply_gcp_env(backend_cfg: dict[str, Any], *, workspace_root: Optional[Path], project_root: Optional[Path]) -> None:
    """Best-effort: export GCP env vars from backend config if present.

    This mirrors existing behavior across the codebase and ensures that Firestore/GCS
    SDKs can locate credentials when chart subprocesses or web server runs separately.
    """
    try:
        import os

        creds_rel = backend_cfg.get("credentials_json")
        if creds_rel and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            p = _resolve_relative_path(creds_rel, workspace_root=workspace_root, project_root=project_root)
            if p is not None:
                os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(p))

        gcp_project = backend_cfg.get("gcp_project") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if gcp_project and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
            os.environ.setdefault("GOOGLE_CLOUD_PROJECT", str(gcp_project))

        emulator_host = backend_cfg.get("emulator_host")
        if emulator_host and not os.environ.get("FIRESTORE_EMULATOR_HOST"):
            os.environ.setdefault("FIRESTORE_EMULATOR_HOST", str(emulator_host))
    except Exception:
        return


def create_kv_store(
    project_id: str,
    backend_cfg: Optional[dict[str, Any]] = None,
    *,
    env: Optional[Mapping[str, str]] = None,
    workspace_root: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> Any:
    """Create a KV store instance (Redis, GCP Firestore/PubSub, or in-memory).

    Precedence:
    - `MLOPS_KV_BACKEND` env override (if set)
    - `backend_cfg['type']` from config
    - safe fallback: in-memory
    """
    from mlops.storage.adapters.memory_store import InMemoryStore

    cfg = backend_cfg if isinstance(backend_cfg, dict) else {}

    def _env_get(key: str) -> Optional[str]:
        try:
            if env is not None:
                v = env.get(key)
                return str(v) if v is not None else None
        except Exception:
            pass
        try:
            import os

            return os.environ.get(key)
        except Exception:
            return None

    backend_type = _norm_backend_type(_env_get("MLOPS_KV_BACKEND") or cfg.get("type") or "")
    if not backend_type:
        backend_type = "memory"

    if backend_type == "memory":
        return InMemoryStore(project_id)

    if backend_type == "redis":
        try:
            from mlops.storage.adapters.redis_store import RedisStore

            host = _env_get("MLOPS_REDIS_HOST") or cfg.get("host")
            port = _as_int(_env_get("MLOPS_REDIS_PORT") or cfg.get("port"))
            db = _as_int(_env_get("MLOPS_REDIS_DB") or cfg.get("db"))
            password = _env_get("MLOPS_REDIS_PASSWORD") or cfg.get("password")
            return RedisStore(project_id=project_id, host=host, port=port, db=db, password=password)
        except Exception:
            return InMemoryStore(project_id)

    if backend_type == "gcp":
        try:
            from mlops.storage.adapters.gcp_kv_store import GCPStore

            _maybe_apply_gcp_env(cfg, workspace_root=workspace_root, project_root=project_root)
            gcp_project = cfg.get("gcp_project") or _env_get("GOOGLE_CLOUD_PROJECT")
            emulator_host = cfg.get("emulator_host") or _env_get("FIRESTORE_EMULATOR_HOST")
            topic_name = cfg.get("topic_name")
            return GCPStore(project_id=project_id, gcp_project=gcp_project, topic_name=topic_name, emulator_host=emulator_host)
        except Exception:
            return InMemoryStore(project_id)

    # Unknown type: fall back safely.
    return InMemoryStore(project_id)


def create_object_store(
    cache_cfg: Optional[dict[str, Any]] = None,
    *,
    env: Optional[Mapping[str, str]] = None,
) -> Any:
    """Create an object store instance for cache artifacts (currently GCS only)."""
    cfg = cache_cfg if isinstance(cache_cfg, dict) else {}
    store_cfg = cfg.get("object_store") if isinstance(cfg.get("object_store"), dict) else {}
    store_type = _norm_backend_type(store_cfg.get("type") or "")

    def _env_get(key: str) -> Optional[str]:
        try:
            if env is not None:
                v = env.get(key)
                return str(v) if v is not None else None
        except Exception:
            pass
        try:
            import os

            return os.environ.get(key)
        except Exception:
            return None

    if store_type == "gcs":
        bucket = store_cfg.get("bucket") or _env_get("MLOPS_GCS_BUCKET")
        prefix = store_cfg.get("prefix") or _env_get("MLOPS_GCS_PREFIX")
        if not bucket:
            return None
        try:
            from mlops.storage.adapters.gcs_object_store import GCSObjectStore

            return GCSObjectStore(bucket=str(bucket), prefix=str(prefix) if prefix else None)
        except Exception:
            return None

    return None


__all__ = [
    "create_kv_store",
    "create_object_store",
]


