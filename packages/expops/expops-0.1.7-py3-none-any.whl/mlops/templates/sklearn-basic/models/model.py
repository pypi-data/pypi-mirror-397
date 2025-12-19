from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from mlops.core import get_current_context, log_metric, process


def _load_xy(csv_path: str | Path):
    df = pd.read_csv(Path(csv_path))
    y = df.pop("label").values
    x = df.values
    return x, y


def _workspace_root() -> Path | None:
    """Workspace root (where `projects/` lives), if provided via env."""
    raw = os.environ.get("MLOPS_WORKSPACE_DIR")
    if not raw:
        return None
    try:
        return Path(raw).expanduser().resolve()
    except Exception:
        return Path(raw)


def _project_id() -> str | None:
    """Project id from runtime context/env (best-effort)."""
    try:
        ctx = get_current_context()
        pid = getattr(ctx, "project_id", None) if ctx else None
        if pid:
            return str(pid)
    except Exception:
        pass
    try:
        pid_env = os.environ.get("MLOPS_PROJECT_ID")
        return str(pid_env) if pid_env else None
    except Exception:
        return None


def _training_csv_path() -> Path:
    ws = _workspace_root()
    pid = _project_id()
    if ws and pid:
        cand = ws / "projects" / pid / "data" / "train.csv"
        if cand.exists():
            return cand
    return Path(__file__).resolve().parents[1] / "data" / "train.csv"


def _validation_csv_path() -> Path:
    return _training_csv_path()


@process(description="Train a tiny classifier")
def train_model(data):
    train_path = _training_csv_path()
    if not train_path.exists():
        raise FileNotFoundError(
            f"Training CSV not found at {train_path}. "
            "Expected the template dataset at projects/<project_id>/data/train.csv."
        )
    x, y = _load_xy(train_path)
    model = LogisticRegression(max_iter=200)
    model.fit(x, y)

    train_acc = float(accuracy_score(y, model.predict(x)))
    log_metric("accuracy", train_acc, step=1)

    return {"model": model, "train_accuracy": train_acc}


@process(description="Evaluate the model")
def evaluate_model(data):
    model = (data or {}).get("train_model", {}).get("model")
    if model is None:
        raise ValueError("Missing upstream model. Expected data['train_model']['model'].")

    val_path = _validation_csv_path()
    if not val_path.exists():
        raise FileNotFoundError(
            f"Validation CSV not found at {val_path}. "
            "Expected the template dataset at projects/<project_id>/data/train.csv."
        )
    x, y = _load_xy(val_path)
    eval_acc = float(accuracy_score(y, model.predict(x)))
    log_metric("accuracy", eval_acc, step=1)

    return {"evaluation_accuracy": eval_acc}

