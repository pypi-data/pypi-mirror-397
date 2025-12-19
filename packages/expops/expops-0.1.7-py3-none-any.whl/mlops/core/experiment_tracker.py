from __future__ import annotations

from typing import Any, Dict, Optional, Protocol


class ExperimentTracker(Protocol):
    """
    Minimal interface for an experiment tracker.

    The platform uses this for optional experiment tracking (params/metrics/artifacts/tags)
    alongside the built-in KV-store metric logging in `mlops.core.step_system`.
    """

    def start_run(
        self,
        run_name: Optional[str] = None,
        run_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Start a new run (returns context manager or run handle)."""
        ...

    def end_run(self, status: Optional[str] = "FINISHED") -> None:
        """End the current active run."""
        ...


class NoOpExperimentTracker(ExperimentTracker):
    """
    Default tracker: prints a few lifecycle messages but intentionally ignores metrics
    to avoid noisy logs. Safe fallback when no experiment tracking backend is configured.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config if config else {}
        self.run_active = False
        self.current_run_id = None
        print(f"[NoOpTracker] Initialized with config: {self.config}")

    def start_run(
        self,
        run_name: Optional[str] = None,
        run_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
    ) -> "NoOpExperimentTracker":
        import uuid

        if self.run_active:
            print(
                f"[NoOpTracker] Warning: A run (ID: {self.current_run_id}) is already active. "
                f"Starting a new nested run is not fully supported by NoOpTracker; state will be overridden."
            )

        self.current_run_id = run_id if run_id else str(uuid.uuid4())
        self.run_active = True

        run_display_name = run_name if run_name else "default_run"
        print(f"[NoOpTracker] Started run. Name: '{run_display_name}', ID: '{self.current_run_id}'")
        if tags:
            # Intentionally ignore tags in the NoOp tracker.
            pass
        return self  # Return self to allow use as a context manager

    def end_run(self, status: Optional[str] = "FINISHED") -> None:
        if self.run_active:
            print(f"[NoOpTracker][RunID: {self.current_run_id}] Ended run with status: {status}")
            self.run_active = False
            self.current_run_id = None
        else:
            print("[NoOpTracker] No active run to end.")

    def __enter__(self):
        if not self.run_active:
            self.start_run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = "FAILED" if exc_type else "FINISHED"
        self.end_run(status=status)


