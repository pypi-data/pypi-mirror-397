from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib
import json
import yaml
import subprocess
from datetime import datetime
import numpy as np
import os
import random

from ..core.experiment_tracker import ExperimentTracker, NoOpExperimentTracker
from ..environment.factory import create_environment_manager
from ..environment.base import EnvironmentManager
from mlops.environment.venv_manager import VenvEnvironmentManager

class ReproducibilityManager:
    """Lightweight reproducibility manager for custom models."""
    
    def __init__(self, config_path: str, tracker_instance: Optional[ExperimentTracker] = None, 
                 project_path: Optional[Path] = None):
        self.config_path = Path(config_path)
        self.project_path = project_path
        self.config = self._load_config()
        self.environment_manager: Optional[EnvironmentManager] = None
        self.reporting_environment_manager: Optional[EnvironmentManager] = None
        
        if tracker_instance:
            self.tracker = tracker_instance
        else:
            self.tracker = self._setup_tracker()
        
        print(f"[ReproducibilityManager] Initialized with tracker: {type(self.tracker).__name__}")
        if self.project_path:
            print(f"[ReproducibilityManager] Using project path: {self.project_path}")

    @property
    def environment_name(self) -> Optional[str]:
        """Get the name of the current environment."""
        return self.environment_manager.get_environment_name() if self.environment_manager else None

    @property
    def python_interpreter(self) -> Optional[str]:
        """Get the Python interpreter path for the current environment."""
        return self.environment_manager.get_python_interpreter() if self.environment_manager else None

    def _setup_tracker(self) -> ExperimentTracker:
        """Set up the experiment tracker based on configuration."""
        tracker_config = self.config.get("reproducibility", {}).get("experiment_tracking", {})
        tracker_name = str(tracker_config.get("backend", "noop") or "noop").strip().lower()
        tracker_params = tracker_config.get("parameters", {})
        if not isinstance(tracker_params, dict):
            tracker_params = {}

        # External experiment tracking backends are optional; default to NoOp.
        if tracker_name not in {"noop"}:
            print(f"Warning: Tracker '{tracker_name}' not available. Falling back to NoOpExperimentTracker.")

        return NoOpExperimentTracker(config=tracker_params)

    def ensure_reproducibility_setup(self) -> None:
        """Set up reproducibility across common ML libraries (minimal).

        - Seed Python's random and NumPy RNGs
        - Best-effort seed for PyTorch and TensorFlow if installed
        - Apply environment flags that encourage deterministic behavior
        """
        random_seed_config = self.config.get("reproducibility", {}).get("random_seed")

        if not isinstance(random_seed_config, int):
            random_seed_config = 42
            if self.config.get("reproducibility", {}).get("random_seed") is None:
                print(f"[ReproducibilityManager] random_seed not specified, using default {random_seed_config}.")
            else:
                print(
                    f"[ReproducibilityManager] Invalid random_seed "
                    f"'{self.config.get('reproducibility', {}).get('random_seed')}', "
                    f"using default {random_seed_config}."
                )

        seed = int(random_seed_config)

        # Core Python and NumPy
        try:
            random.seed(seed)
        except Exception as e:
            print(f"[ReproducibilityManager] Failed to seed Python random: {e}")
        try:
            np.random.seed(seed)
            print(f"[ReproducibilityManager] Global seeds set (python, numpy): {seed}")
        except Exception as e:
            print(f"[ReproducibilityManager] Failed to seed NumPy: {e}")

        # Best-effort environment flags for deterministic operations in DL frameworks
        try:
            os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
            os.environ.setdefault("TF_CUDNN_DETERMINISTIC", "1")
            os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":16:8")
        except Exception:
            pass

        # Framework-specific seeding
        self._seed_pytorch_if_available(seed)
        self._seed_tensorflow_if_available(seed)

        # Export base seed and task-level seeding toggle for workers/subprocesses
        try:
            os.environ.setdefault("MLOPS_RANDOM_SEED", str(seed))
        except Exception:
            pass
        try:
            tl_seed_cfg = self.config.get("reproducibility", {}).get("task_level_seeding")
            enabled = True if tl_seed_cfg is None else bool(tl_seed_cfg)
            os.environ.setdefault("MLOPS_TASK_LEVEL_SEEDING", "1" if enabled else "0")
        except Exception:
            pass

        print(f"[ReproducibilityManager] Reproducibility setup completed with seed {seed}.")

    def _seed_pytorch_if_available(self, seed: int) -> None:
        try:
            import torch
            try:
                torch.manual_seed(seed)
            except Exception:
                pass
            try:
                if torch.cuda.is_available():
                    torch.cuda.manual_seed_all(seed)
                # Ensure deterministic behavior when possible
                try:
                    torch.use_deterministic_algorithms(True)  # type: ignore[attr-defined]
                except Exception:
                    pass
                try:
                    import torch.backends.cudnn as cudnn  # type: ignore
                    cudnn.deterministic = True
                    cudnn.benchmark = False
                except Exception:
                    pass
            except Exception:
                pass
            print("[ReproducibilityManager] PyTorch seed applied.")
        except Exception:
            # PyTorch not installed or failed to import; ignore silently
            pass

    def _seed_tensorflow_if_available(self, seed: int) -> None:
        try:
            import tensorflow as tf
            try:
                tf.random.set_seed(seed)
                print("[ReproducibilityManager] TensorFlow seed applied.")
            except Exception:
                pass
        except Exception:
            pass



    def _load_config(self) -> Dict[str, Any]:
        """Load and parse the configuration file."""
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def setup_environment(self) -> None:
        """Set up the environment based on configuration."""
        print("[ReproducibilityManager] Starting environment setup...")
        
        self.environment_manager = create_environment_manager(self.config)
        
        try:
            self.environment_manager.setup_environment()
        except RuntimeError as e:
            print(f"[ReproducibilityManager] Environment setup failed: {e}")
            raise 
        
        print(f"[ReproducibilityManager] Environment '{self.environment_manager.get_environment_name()}' setup completed.")
        print(f"[ReproducibilityManager] Environment type: {self.environment_manager.get_environment_type()}")
        print(f"[ReproducibilityManager] Python interpreter: {self.environment_manager.get_python_interpreter()}")

        try:
            env_cfg = self.config.get("environment", {}) or {}
            reporting_cfg = None
            venv_cfg = env_cfg.get("venv") if isinstance(env_cfg, dict) else None
            if isinstance(venv_cfg, dict) and isinstance(venv_cfg.get("reporting"), dict):
                reporting_cfg = dict(venv_cfg.get("reporting") or {})
                # Default name if not provided -> derive from training venv name
                if not reporting_cfg.get("name"):
                    train_name = venv_cfg.get("name")
                    if train_name:
                        reporting_cfg["name"] = f"{train_name}-reporting"
                    else:
                        proj_name = self.project_path.name if self.project_path else "reporting"
                        reporting_cfg["name"] = f"{proj_name}-reporting"
                self.reporting_environment_manager = VenvEnvironmentManager(reporting_cfg)
                self.reporting_environment_manager.setup_environment()
                print(f"[ReproducibilityManager] Reporting environment '{self.reporting_environment_manager.get_environment_name()}' setup completed.")
                print(f"[ReproducibilityManager] Reporting Python interpreter: {self.reporting_environment_manager.get_python_interpreter()}")
                try:
                    rep_py = self.reporting_environment_manager.get_python_interpreter()
                    import_check = subprocess.run(
                        [rep_py, "-c", "import mlops"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if import_check.returncode != 0:
                        # Prefer installing from local source checkout when available (dev workflow),
                        # otherwise install from index. Fall back to unpinned install when the
                        # current version isn't published (e.g., local .dev versions).
                        try:
                            from mlops.core.workspace import infer_source_root
                            src_root = infer_source_root()
                        except Exception:
                            src_root = None
                        if src_root and ((src_root / "pyproject.toml").exists() or (src_root / "setup.py").exists()):
                            subprocess.run(
                                [rep_py, "-m", "pip", "install", "--no-deps", "-e", str(src_root)],
                                check=False,
                            )
                        else:
                            try:
                                from importlib.metadata import version  # type: ignore

                                v = version("expops")
                                res = subprocess.run(
                                    [rep_py, "-m", "pip", "install", "--no-deps", f"expops=={v}"],
                                    check=False,
                                )
                                if getattr(res, "returncode", 1) != 0:
                                    subprocess.run(
                                        [rep_py, "-m", "pip", "install", "--no-deps", "expops"],
                                        check=False,
                                    )
                            except Exception:
                                subprocess.run(
                                    [rep_py, "-m", "pip", "install", "--no-deps", "expops"],
                                    check=False,
                                )
                except Exception as _e:
                    print(f"[ReproducibilityManager] Warning: failed to ensure platform is importable in reporting env: {_e}")
        except Exception as e:
            print(f"[ReproducibilityManager] Reporting environment setup skipped or failed: {e}")

    def apply_cloud_env_from_config(self, model_section: Dict[str, Any]) -> None:
        """Apply cloud-related environment variables from the YAML config.

        Sets GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT, and FIRESTORE_EMULATOR_HOST
        if present under model.parameters.cache.backend. Only applies when configured.
        """
        try:
            base_dir = self.project_path or Path.cwd()
            params = (model_section or {}).get("parameters", {}) or {}
            cache_cfg = params.get("cache", {}) or {}
            backend_cfg = cache_cfg.get("backend", {}) or {}

            creds_rel = backend_cfg.get("credentials_json")
            if creds_rel:
                candidates = [
                    (base_dir / creds_rel).resolve(),
                    (Path.cwd() / creds_rel).resolve(),
                ]
                chosen = next((p for p in candidates if p.exists()), None)
                if chosen is not None:
                    current = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
                    if not current or not Path(current).expanduser().exists():
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(chosen)
                else:
                    print(
                        f"[ReproducibilityManager] GCP credentials not found at: "
                        + ", ".join(str(p) for p in candidates)
                    )

            gcp_project = backend_cfg.get("gcp_project")
            if gcp_project:
                os.environ.setdefault("GOOGLE_CLOUD_PROJECT", str(gcp_project))

            emulator_host = backend_cfg.get("emulator_host")
            if emulator_host:
                os.environ.setdefault("FIRESTORE_EMULATOR_HOST", str(emulator_host))
        except Exception as e:
            print(f"[ReproducibilityManager] Failed to apply cloud env: {e}")

    def _pip_install(self, python_exec: str, packages: List[str]) -> None:
        if not packages or not python_exec:
            return
        try:
            # Pre-upgrade pip tooling
            try:
                subprocess.run([python_exec, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=False)
            except Exception:
                pass
            timeout_env = os.getenv("MLOPS_PIP_TIMEOUT", "")
            try:
                timeout_s = int(timeout_env) if timeout_env.strip().isdigit() else 1200
            except Exception:
                timeout_s = 1200
            try:
                subprocess.run([python_exec, "-m", "pip", "install", *packages], check=True, timeout=timeout_s)
            except subprocess.TimeoutExpired:
                print(f"[ReproducibilityManager] pip install timed out for: {', '.join(packages)}. Retrying without timeout...")
                subprocess.run([python_exec, "-m", "pip", "install", *packages], check=True)
        except Exception as e:
            print(f"[ReproducibilityManager] pip install failed for {packages} into {python_exec}: {e}")

    def ensure_cloud_dependencies(self, model_section: Dict[str, Any]) -> None:
        """Ensure cloud libs are present based on configured backend/object store.

        - google-cloud-storage when object_store.type == 'gcs'
        - google-cloud-firestore and google-cloud-pubsub when backend.type == 'gcp'
        - redis when backend.type == 'redis'
        Installs into training/runtime interpreter and reporting interpreter if available.
        """
        params = (model_section or {}).get("parameters", {}) or {}
        cache_cfg = params.get("cache", {}) or {}
        backend_cfg = cache_cfg.get("backend", {}) or {}
        store_cfg = cache_cfg.get("object_store", {}) or {}

        backend_type = backend_cfg.get("type")
        need_storage = (store_cfg.get("type") == "gcs")
        need_firestore = (backend_type == "gcp")
        need_redis = (backend_type == "redis")

        to_install: List[str] = []
        if need_storage:
            try:
                __import__("google.cloud.storage")
            except Exception:
                to_install.append("google-cloud-storage>=2.10.0")
        if need_firestore:
            try:
                __import__("google.cloud.firestore")
            except Exception:
                to_install.append("google-cloud-firestore>=2.11.0")
            try:
                __import__("google.cloud.pubsub")
            except Exception:
                to_install.append("google-cloud-pubsub>=2.13.0")
        if need_redis:
            try:
                __import__("redis")
            except Exception:
                to_install.append("redis>=5.0.0")

        # Deduplicate
        seen = set()
        final = [p for p in to_install if not (p in seen or seen.add(p))]
        if final and self.python_interpreter:
            self._pip_install(self.python_interpreter, final)

        # Reporting env
        reporting_packages: List[str] = []
        if need_firestore:
            reporting_packages += ["google-cloud-firestore>=2.11.0", "google-cloud-pubsub>=2.13.0"]
        if need_storage:
            reporting_packages += ["google-cloud-storage>=2.10.0"]
        seen_r = set()
        reporting_final = [p for p in reporting_packages if not (p in seen_r or seen_r.add(p))]
        if reporting_final and self.reporting_python_interpreter:
            self._pip_install(self.reporting_python_interpreter, reporting_final)

    def verify_environment(self) -> bool:
        """Verify that the environment is properly configured."""
        if not self.environment_manager:
            print("[ReproducibilityManager] Environment manager not initialized.")
            return False
        
        return self.environment_manager.verify_environment()

    @property
    def reporting_python_interpreter(self) -> Optional[str]:
        """Get Python interpreter for the reporting environment, if configured."""
        return self.reporting_environment_manager.get_python_interpreter() if self.reporting_environment_manager else None

    def compute_data_hash(self, data_path: str) -> str:
        """Compute a hash of the input data (file or directory)."""
        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"Data path {data_path} not found for hashing.")

        if path.is_dir():
            hasher = hashlib.sha256()
            for item in sorted(os.listdir(path)):
                item_path = path / item
                hasher.update(item.encode())
                if item_path.is_file():
                    with open(item_path, 'rb') as f:
                        hasher.update(f.read())
            return hasher.hexdigest()
        else:
            with open(data_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
    
    def log_run_info(self, run_id: str, custom_params: Optional[Dict[str, Any]] = None) -> None:
        """Log run parameters and metadata."""
        if not self.tracker or not self.config.get("reproducibility", {}).get("experiment_tracking", {}).get("enabled", False):
            return
        
        if custom_params:
            fn = getattr(self.tracker, "log_params", None)
            if callable(fn):
                try:
                    fn(custom_params)
                except Exception:
                    pass
    
        model_params = self.config.get("model", {}).get("parameters", {})
        if model_params:
            fn = getattr(self.tracker, "log_params", None)
            if callable(fn):
                try:
                    fn(model_params)
                except Exception:
                    pass
        
        if self.config.get("reproducibility", {}).get("version_control", {}).get("enabled", False):
            try:
                git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
                fn = getattr(self.tracker, "log_param", None)
                if callable(fn):
                    fn("git_commit", git_commit)
                
                git_branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
                fn = getattr(self.tracker, "log_param", None)
                if callable(fn):
                    fn("git_branch", git_branch)
            except Exception as e:
                print(f"Could not log Git information: {e}")
        
        try:
            python_version = subprocess.check_output(["python", "--version"], text=True).strip()
            fn = getattr(self.tracker, "log_param", None)
            if callable(fn):
                fn("python_version", python_version)
        except Exception:
            pass
            
        set_tag = getattr(self.tracker, "set_tag", None)
        if callable(set_tag):
            try:
                set_tag("run_id", run_id)
                set_tag("pipeline_name", self.config.get("metadata", {}).get("name", "unknown_pipeline"))
                set_tag("creation_timestamp", datetime.now().isoformat())
            except Exception:
                pass

    def log_results(self, results: Dict[str, Any]) -> None:
        """Log experiment results/metrics."""
        if not self.tracker or not self.config.get("reproducibility", {}).get("experiment_tracking", {}).get("enabled", False):
            return
        log_metric = getattr(self.tracker, "log_metric", None)
        if not callable(log_metric):
            return

        for key, value in results.items():
            if isinstance(value, (int, float)):
                try:
                    log_metric(key, value)
                except Exception:
                    pass
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float)):
                        try:
                            log_metric(f"{key}_{sub_key}", sub_value)
                        except Exception:
                            pass

    def log_artifacts(self, artifacts: Dict[str, str]) -> None:
        """Log artifacts (files/directories) to the tracker."""
        if not self.tracker or not self.config.get("reproducibility", {}).get("experiment_tracking", {}).get("enabled", False):
            return
        log_artifact = getattr(self.tracker, "log_artifact", None)
        log_artifacts = getattr(self.tracker, "log_artifacts", None)

        for artifact_name, artifact_path in artifacts.items():
            path = Path(artifact_path)
            if path.is_file():
                if callable(log_artifact):
                    try:
                        log_artifact(str(path), artifact_name)
                    except Exception:
                        pass
            elif path.is_dir():
                if callable(log_artifacts):
                    try:
                        log_artifacts(str(path), artifact_name)
                    except Exception:
                        pass
            else:
                print(f"Warning: Artifact path {artifact_path} for '{artifact_name}' not found.")

    def save_artifacts(self, run_id: str, artifacts: Dict[str, Any]) -> Dict[str, str]:
        """Save artifacts locally and return their paths."""
        saved_paths = {}
        if not artifacts:
            return saved_paths
        base_path = Path(f"artifacts/{run_id}")
        base_path.mkdir(parents=True, exist_ok=True)

        for artifact_name, artifact_data in artifacts.items():
            try:
                artifact_path = base_path / f"{artifact_name}.json"
                
                with open(artifact_path, "w") as f:
                    if isinstance(artifact_data, (dict, list)):
                        json.dump(artifact_data, f, indent=2, default=str)
                    else:
                        json.dump({"data": str(artifact_data)}, f, indent=2)
                
                saved_paths[artifact_name] = str(artifact_path)
                print(f"Artifact '{artifact_name}' saved to {artifact_path}")
                
            except Exception as e:
                print(f"Error saving artifact '{artifact_name}': {e}")

        return saved_paths

    def get_tracker(self) -> ExperimentTracker:
        """Return the current tracker instance."""
        return self.tracker
    
    def capture_environment_info(self) -> Dict[str, Any]:
        """Capture environment information for logging."""
        import platform
        import sys
        
        env_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "processor": platform.processor(),
            "random_seed": self.config.get("reproducibility", {}).get("random_seed", "not_set")
        }
        
        if self.environment_manager:
            env_info["environment_name"] = self.environment_name
            env_info["python_interpreter"] = self.python_interpreter
        
        return env_info
    
    def save_run_artifacts_locally(self, run_id: str, adapter) -> Dict[str, str]:
        """Save run artifacts locally and return their paths."""
        if not self.project_path:
            # No-op for non-project runs (avoid creating empty artifacts folders).
            return {}

        saved_paths: Dict[str, str] = {}

        # Save model if adapter has one.
        try:
            model_obj = getattr(adapter, "model", None)
        except Exception:
            model_obj = None

        if model_obj is not None:
            model_dir = self.project_path / "artifacts" / "models"
            model_dir.mkdir(parents=True, exist_ok=True)
            model_path = model_dir / f"{run_id}_model.joblib"
            try:
                import joblib
                joblib.dump(model_obj, model_path)
                saved_paths["model"] = str(model_path)
                print(f"[ReproducibilityManager] Model saved to: {model_path}")
            except Exception as e:
                print(f"[ReproducibilityManager] Failed to save model: {e}")
        
        # Log artifacts to tracker
        if saved_paths:
            try:
                self.log_artifacts(saved_paths)
            except Exception:
                pass
        
        return saved_paths 