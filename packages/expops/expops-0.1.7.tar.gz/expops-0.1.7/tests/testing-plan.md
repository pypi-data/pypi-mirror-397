# Comprehensive Testing Prompt for MLOps Platform

## Overview
Add comprehensive test coverage to the MLOps platform repository. The platform is a project-based experiment runner with DAG pipeline execution, distributed computing, environment management, caching, and reporting capabilities.

## Current Test Setup
- **Testing Framework**: pytest with pytest-cov
- **Existing Tests**: Only `tests/test_step_context_factory.py` exists (2 tests)
- **Test Configuration**: `tests/conftest.py` sets up `src/` on sys.path
- **Dev install**: `pip install -e ".[dev]"` (installs `pytest`, `pytest-cov`)
- **Coverage Goal**: Target **80%+ coverage for `src/mlops/`** while excluding:
  - `src/mlops/templates/**` (project scaffolds, not runtime logic)
  - `src/mlops/web/ui/**` (static frontend assets)
  - (Optionally) generated packaging files such as `src/mlops/_version.py` when present

## Repo-Specific Testing Constraints (Important)

Your codebase relies heavily on **workspace-relative paths and environment variables**. To keep tests deterministic:

- **Always isolate the workspace**: most path resolution uses `MLOPS_WORKSPACE_DIR` and/or `Path.cwd()`. Tests should set `MLOPS_WORKSPACE_DIR` and `chdir()` into a temp workspace.
- **Beware import-time globals**: some modules compute globals at import time (e.g., `mlops.web.server.WORKSPACE_ROOT/PROJECTS_DIR`, `mlops.cluster.process_runner.WORKSPACE_ROOT`). Set env vars **before importing**, or `importlib.reload()` after `monkeypatch.setenv(...)`.
- **Avoid real side effects**:
  - Patch `subprocess.run`, `subprocess.Popen`, and `os.execv` in CLI/platform tests (otherwise tests may try to create venvs, pip-install, spawn background chart processes, or re-exec).
  - Do not require real Redis/GCP/SLURM/Dask clusters; mock SDK clients and external commands.

## Test Organization Structure

Create tests organized by module structure:

```
tests/
├── conftest.py (existing - enhance with fixtures)
├── unit/
│   ├── __init__.py
│   ├── test_adapters/
│   │   ├── test_base.py
│   │   ├── test_plugin_manager.py
│   │   ├── test_config_schema.py
│   │   ├── test_sklearn_adapter.py
│   │   └── test_custom_adapter.py
│   ├── test_cluster/
│   │   ├── test_controller.py
│   │   ├── test_process_runner.py
│   │   └── test_providers.py
│   ├── test_core/
│   │   ├── test_step_system.py (extend existing)
│   │   ├── test_dask_networkx_executor.py
│   │   ├── test_networkx_parser.py
│   │   ├── test_executor_worker.py
│   │   ├── test_experiment_tracker.py
│   │   ├── test_process_hashing.py
│   │   ├── test_step_state_manager.py
│   │   ├── test_payload_spill.py
│   │   ├── test_pipeline_utils.py
│   │   ├── test_workspace.py
│   │   ├── test_graph_types.py
│   │   └── test_custom_model_base.py
│   ├── test_cli/
│   │   └── test_main.py
│   ├── test_environment/
│   │   ├── test_base.py
│   │   ├── test_venv_manager.py
│   │   ├── test_conda_manager.py
│   │   ├── test_pyenv_manager.py
│   │   ├── test_system_manager.py
│   │   ├── test_factory.py
│   │   ├── test_utils.py
│   │   └── test_setup_env.py
│   ├── test_managers/
│   │   ├── test_project_manager.py
│   │   └── test_reproducibility_manager.py
│   ├── test_platform/
│   │   └── test_platform.py
│   ├── test_runtime/
│   │   ├── test_context.py
│   │   └── test_env_export.py
│   ├── test_storage/
│   │   ├── test_factory.py
│   │   ├── test_path_utils.py
│   │   ├── test_adapters/
│   │   │   ├── test_memory_store.py
│   │   │   ├── test_redis_store.py
│   │   │   ├── test_gcp_kv_store.py
│   │   │   └── test_gcs_object_store.py
│   │   └── test_interfaces/
│   │       └── test_kv_store.py
│   ├── test_reporting/
│   │   ├── test_context.py
│   │   ├── test_entrypoint.py
│   │   ├── test_kv_utils.py
│   │   └── test_registry.py
│   └── test_web/
│       └── test_server.py
├── integration/
│   ├── __init__.py
│   ├── test_pipeline_execution.py
│   ├── test_project_lifecycle.py
│   ├── test_storage_backends.py
│   └── test_cluster_execution.py
└── fixtures/
    ├── __init__.py
    ├── sample_configs.py
    ├── mock_storage.py
    └── sample_data.py
```

## Key Testing Areas

### 1. Core Pipeline Execution (`src/mlops/core/`)

**Priority: HIGH**

#### `step_system.py`
- [ ] Test `StepContext` initialization and state management
- [ ] Test `get_step_result()` with in-memory and cached results
- [ ] Test `get_step_data()` with various data types
- [ ] Test `log_metric()` with different metric types
- [ ] Test `StepContextFactory` context isolation (extend existing tests)
- [ ] Test context reuse for same run_id
- [ ] Test context cleanup and lifecycle
- [ ] Test payload hydration with state manager
- [ ] Test checkpoint save/load functionality
- [ ] Test iteration tracking

#### `dask_networkx_executor.py`
- [ ] Test DAG parsing and validation
- [ ] Test task dependency resolution
- [ ] Test parallel execution of independent tasks
- [ ] Test error handling and task failure propagation
- [ ] Test retry logic
- [ ] Test distributed execution with mock Dask client
- [ ] Test payload serialization/deserialization
- [ ] Test step result caching integration
- [ ] Test conditional execution paths
- [ ] Test loop execution

#### `networkx_parser.py`
- [ ] Test DAG adjacency list parsing
- [ ] Test cycle detection
- [ ] Test topological sorting
- [ ] Test invalid graph handling
- [ ] Test edge case graphs (single node, linear, diamond, etc.)

#### `executor_worker.py`
- [ ] Test worker initialization
- [ ] Test step execution with various step types
- [ ] Test result collection and aggregation
- [ ] Test error handling and exception propagation
- [ ] Test worker cleanup

#### `experiment_tracker.py`
- [ ] Test `NoOpExperimentTracker` (no-op behavior)
- [ ] Test metric logging
- [ ] Test parameter logging
- [ ] Test artifact tracking
- [ ] Test tracker initialization from config

#### `process_hashing.py`
- [ ] Test hash generation for functions
- [ ] Test hash consistency across runs
- [ ] Test hash with different input types
- [ ] Test hash collision handling

#### `step_state_manager.py`
- [ ] Test step result caching
- [ ] Test cache key generation
- [ ] Test cache retrieval
- [ ] Test cache invalidation
- [ ] Test storage backend integration

#### `payload_spill.py`
- [ ] Test payload serialization
- [ ] Test payload reference creation
- [ ] Test payload hydration
- [ ] Test large payload handling
- [ ] Test reference resolution

#### `pipeline_utils.py`
- [ ] Test environment setup
- [ ] Test interpreter path resolution
- [ ] Test requirements installation
- [ ] Test environment activation

#### `workspace.py`
- [ ] Test workspace root detection
- [ ] Test projects root resolution
- [ ] Test source root inference
- [ ] Test path resolution with environment variables

### 2. Project Management (`src/mlops/managers/`)

**Priority: HIGH**

#### `project_manager.py`
- [ ] Test project creation with/without template
- [ ] Test project deletion with confirmation
- [ ] Test project listing
- [ ] Test project existence checking
- [ ] Test project info retrieval
- [ ] Test config file management
- [ ] Test config updates (nested keys)
- [ ] Test project index management
- [ ] Test error handling for invalid project IDs
- [ ] Test workspace isolation

#### `reproducibility_manager.py`
- [ ] Test random seed setting
- [ ] Test seed propagation to different frameworks
- [ ] Test seed persistence across runs
- [ ] Test reproducibility verification

### 3. Storage System (`src/mlops/storage/`)

**Priority: HIGH**

#### `factory.py`
- [ ] Test storage factory initialization
- [ ] Test backend type normalization (aliases)
- [ ] Test storage adapter creation for each backend
- [ ] Test configuration parsing
- [ ] Test error handling for invalid backends

#### Storage Adapters
- [ ] **Memory Store**: Test basic CRUD operations, concurrent access, cleanup
- [ ] **Redis Store**: Test connection handling, key operations, TTL, error handling (with mock Redis)
- [ ] **GCP KV Store**: Test Firestore operations, authentication, error handling (with mock Firestore)
- [ ] **GCS Object Store**: Test object upload/download, path handling, error handling (with mock GCS)

#### `path_utils.py`
- [ ] Test path resolution (absolute, relative, workspace-relative)
- [ ] Test path normalization
- [ ] Test workspace root detection

### 4. Environment Management (`src/mlops/environment/`)

**Priority: MEDIUM**

#### `factory.py`
- [ ] Test environment manager factory
- [ ] Test manager selection based on config
- [ ] Test fallback to system Python

#### Environment Managers
- [ ] **VenvManager**: Test venv creation, activation, package installation (with mocks)
- [ ] **CondaManager**: Test conda env creation, activation (with mocks)
- [ ] **PyenvManager**: Test Python version management (with mocks)
- [ ] **SystemManager**: Test system Python detection

#### `setup_env.py`
- [ ] Test environment setup workflow
- [ ] Test requirements installation
- [ ] Test error handling

### 5. Adapters (`src/mlops/adapters/`)

**Priority: MEDIUM**

#### `plugin_manager.py`
- [ ] Test adapter discovery
- [ ] Test adapter registration
- [ ] Test adapter loading
- [ ] Test adapter selection by framework

#### `config_schema.py`
- [ ] Test config validation
- [ ] Test config parsing from YAML
- [ ] Test default values
- [ ] Test error handling for invalid configs

#### `sklearn/adapter.py`
- [ ] Test adapter initialization
- [ ] Test model training workflow
- [ ] Test model evaluation
- [ ] Test model save/load
- [ ] Test pipeline execution

#### `custom/custom_adapter.py`
- [ ] Test custom model loading
- [ ] Test process/step discovery
- [ ] Test pipeline execution
- [ ] Test error handling

### 6. Cluster Execution (`src/mlops/cluster/`)

**Priority: MEDIUM**

#### `controller.py`
- [ ] Test cluster controller initialization + workspace/src import fallback
- [ ] Test KV/env export wiring from `project_config.yaml` and/or `cluster_config.yaml`
- [ ] Test provider selection + start/stop (`slurm` vs `ansible`) without launching real clusters (mock)
- [ ] Test subprocess command construction (env setup + invoking project run) without executing (mock)
- [ ] Test error handling (missing config, non-zero subprocess return codes)

#### `providers.py`
- [ ] Test `SlurmClusterProvider`:
  - Fallback to `LocalCluster` when `dask-jobqueue` is missing
  - Worker/job prologue env behavior (mock where possible)
- [ ] Test `AnsibleClusterProvider`:
  - Requires `scheduler_address` (options or `DASK_SCHEDULER_ADDRESS`)
  - Connect failure returns `(None, None)` (mock Client)
- [ ] Test provider selection in `controller.py` (only `slurm` and `ansible` exist today)

#### `process_runner.py`
- [ ] Test arg parsing + config loading (workspace env handling)
- [ ] Test SLURM CPU env heuristics (auto-suggest executor `n_workers` when not set)
- [ ] Test `resume_from_process`/`single_process` wiring into adapter.run (mock adapter)
- [ ] Test training data path resolution (absolute vs project-relative vs workspace-relative)
- [ ] Test error propagation (missing config, adapter failures)

### 7. Reporting (`src/mlops/reporting/`)

**Priority: MEDIUM**

#### `context.py`
- [ ] Test chart context initialization
- [ ] Test metric retrieval
- [ ] Test chart generation workflow

#### `entrypoint.py`
- [ ] Test chart entry point execution
- [ ] Test static chart generation
- [ ] Test dynamic chart setup

#### `kv_utils.py`
- [ ] Test key-value operations
- [ ] Test metric storage/retrieval
- [ ] Test namespace handling

#### `registry.py`
- [ ] Test chart registration
- [ ] Test chart discovery
- [ ] Test chart execution

### 8. Runtime (`src/mlops/runtime/`)

**Priority: LOW**

#### `context.py`
- [ ] Test runtime context initialization
- [ ] Test context variable management

#### `env_export.py`
- [ ] Test environment variable export
- [ ] Test variable serialization

### 9. CLI (`src/mlops/main.py`)

**Priority: HIGH**

- [ ] Test `create_project_command()` with various options
- [ ] Test `delete_project_command()` with/without force
- [ ] Test `list_projects_command()`
- [ ] Test `run_project_command()` with local flag
- [ ] Test `config_project_command()` with file and set options
- [ ] Test argument parsing
- [ ] Test workspace override
- [ ] Test environment setup and re-execution
- [ ] Test logging configuration
- [ ] Test cluster delegation

### 10. Platform (`src/mlops/platform.py`)

**Priority: HIGH**

- [ ] Test `MLPlatform` initialization
- [ ] Test `run_pipeline_for_project()` end-to-end (with mocks)
- [ ] Test adapter selection
- [ ] Test tracker initialization
- [ ] Test chart generation workflow
- [ ] Test error handling

### 11. Web Server (`src/mlops/web/`)

**Priority: LOW**

- [ ] Test server initialization
- [ ] Test API endpoints (FastAPI `TestClient`):
  - `/api/projects`, `/api/projects/{project_id}/runs` (KV + filesystem fallback)
  - `/api/projects/{project_id}/graph` (parses `model.parameters.pipeline.process_adjlist`)
  - `/api/projects/{project_id}/runs/{run_id}/charts/fetch` (prefers `cache_path` over `gs://` and local `uri`)
- [ ] Test static file mounts (`/projects` and packaged UI fallback) where feasible

## Test Utilities and Fixtures

### Enhanced `conftest.py`
Add the following fixtures:

```python
from __future__ import annotations

from pathlib import Path
import pytest
import yaml


@pytest.fixture
def tmp_workspace(tmp_path, monkeypatch) -> Path:
    """Temp workspace root; sets MLOPS_WORKSPACE_DIR and chdir() for path stability."""
    workspace = tmp_path / "workspace"
    (workspace / "projects").mkdir(parents=True)
    monkeypatch.setenv("MLOPS_WORKSPACE_DIR", str(workspace))
    monkeypatch.chdir(workspace)
    return workspace

@pytest.fixture
def sample_model_config() -> dict:
    """Minimal dict that satisfies `AdapterConfig(**model)` (see `mlops.adapters.config_schema`)."""
    return {
        "name": "test-model",
        "framework": "custom",
        "language": "python",
        "version": "0.1.0",
        "parameters": {},
        "requirements": {},
    }


@pytest.fixture
def sample_project_config(sample_model_config) -> dict:
    """Minimal `projects/<id>/configs/project_config.yaml` used across tests."""
    return {
        "reproducibility": {
            "random_seed": 123,
            "experiment_tracking": {"backend": "noop", "parameters": {}},
        },
        # Env manager selection keys are {"venv": {...}} / {"conda": {...}} / {"system": {...}}
        "environment": {"system": {}},
        "model": sample_model_config,
        "reporting": {"charts": []},
    }


@pytest.fixture
def write_project_config(tmp_workspace, sample_project_config):
    """Write `project_config.yaml` under a temp workspace and return its path."""
    def _write(project_id: str = "proj", cfg: dict | None = None) -> Path:
        project_root = tmp_workspace / "projects" / project_id
        (project_root / "configs").mkdir(parents=True, exist_ok=True)
        cfg_path = project_root / "configs" / "project_config.yaml"
        cfg_path.write_text(yaml.safe_dump(cfg or sample_project_config, sort_keys=False))
        return cfg_path

    return _write

@pytest.fixture
def mock_dask_client(monkeypatch):
    """Mock Dask distributed client."""
    # Implementation

@pytest.fixture
def mock_storage_backend():
    """Mock storage backend for testing."""
    # Implementation

@pytest.fixture
def mock_environment_manager(monkeypatch):
    """Mock environment manager."""
    # Implementation
```

### Test Data Fixtures
- Sample YAML configs (valid and invalid)
- Sample DAG structures
- Sample step functions
- Sample metrics data

## Testing Best Practices

1. **Use pytest fixtures** for setup/teardown and shared test data
2. **Mock external dependencies**: Dask, Redis, GCP services, subprocess calls, file I/O where appropriate
3. **Use `tmp_path`** for file system operations (pytest built-in)
4. **Test both success and failure paths** for each function
5. **Test edge cases**: empty inputs, None values, invalid types, boundary conditions
6. **Use parametrize** for testing multiple scenarios with similar logic
7. **Isolate tests**: Each test should be independent and not rely on execution order
8. **Use descriptive test names**: `test_<function>_<scenario>_<expected_behavior>`
9. **Test error messages** to ensure helpful debugging information
10. **Use type hints** in test code for better IDE support

## Mocking Strategy

### External Services
- **Dask/Distributed**: Mock `Client`, `Future`, `submit` methods
- **Redis**: Use `fakeredis` or mock `redis.Redis`
- **GCP Services**: Mock `google.cloud.firestore.Client`, `google.cloud.storage.Client`
- **Subprocess**: Use `unittest.mock.patch` for `subprocess.run`
- **File I/O**: Use `tmp_path` fixture, mock `Path` operations if needed

### Import-Time Globals (Repo-Specific)
- **FastAPI server** (`mlops.web.server`): `WORKSPACE_ROOT` and `PROJECTS_DIR` are computed at import time.
  - Set `MLOPS_WORKSPACE_DIR` **before importing** the module in tests, or reload after setting env vars:
    - `import importlib, mlops.web.server as server; importlib.reload(server)`
- **Cluster process runner** (`mlops.cluster.process_runner`): similar import-time workspace handling; set env vars before import/reload.

### Internal Dependencies
- Mock storage backends when testing higher-level components
- Mock environment managers when testing pipeline execution
- Mock experiment trackers when testing step execution

## Integration Tests

Create integration tests that:
1. Test project lifecycle (create → config update → list → delete) in a temp workspace
2. Test platform orchestration **without real env creation** (patch `ReproducibilityManager.setup_environment`, `AdapterPluginManager.create_adapter`, and any subprocess usage)
3. Test storage backend switching via `create_kv_store` fallbacks (memory/redis/gcp) using mocks (no credentials)
4. Test cluster delegation paths (CLI delegates to `cluster/controller.py` and controller selects `slurm|ansible`) without running real clusters

## Running Tests

### Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/mlops --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_core/test_step_system.py

# Run specific test
pytest tests/unit/test_core/test_step_system.py::test_step_context_initialization

# Run with verbose output
pytest -v

# Run only fast tests (skip slow integration tests)
pytest -m "not slow and not integration"
```

### Recommended `pytest.ini`
Add a `pytest.ini` to standardize markers and keep CI fast by default:

```ini
[pytest]
addopts = -ra
markers =
    unit: fast, isolated tests (no network, no subprocess side effects)
    integration: multi-module tests that still avoid external services
    slow: tests that start local clusters, spawn threads/processes, or do heavier IO
    redis: redis-specific tests (should mock redis client or use fakeredis)
    gcp: GCP-specific tests (should mock google-cloud SDKs)
    slurm: SLURM/dask-jobqueue-specific tests (should mock or skip if dependency missing)
```

### Coverage Goals
- **Unit tests**: Aim for 80%+ coverage for **core/managers/storage/runtime/reporting** modules first.
- **Large modules** (`core/step_system.py`, `core/dask_networkx_executor.py`): target **behavioral coverage** (key branches) rather than line coverage early on.
- **Exclude** template scaffolds and static UI assets from coverage as noted above.
- **Integration tests**: Cover critical user workflows
- **Focus areas**: Core pipeline execution, project management, storage system

## Implementation Order

1. **Phase 1**: Core pipeline execution (`step_system`, `dask_networkx_executor`, `networkx_parser`)
2. **Phase 2**: Project management and storage
3. **Phase 3**: Adapters and environment management
4. **Phase 4**: CLI and platform integration
5. **Phase 5**: Cluster, reporting, and web components
6. **Phase 6**: Integration tests and coverage improvements

## Notes

- Some tests may require actual file system operations - use `tmp_path` fixture
- For distributed execution tests, focus on mocking Dask rather than running actual clusters
- Storage adapter tests should test the interface contract, not the underlying storage implementation
- Environment manager tests should mock subprocess calls to avoid actual environment creation
- Consider using `pytest-asyncio` if any async code is added in the future
- Add `pytest.ini` or `pyproject.toml` pytest configuration for test discovery and markers

