# ExpOps

`expops` is a project-based experiment runner: keep each experiment isolated under a workspace, run pipelines, and save run artifacts (with optional tracking/backends).

**Install**:

```bash
pip install expops
```

The installed CLI command is **`expops`** (alias: `expops-platform`).

## Platform Capabilities

ExpOps provides a comprehensive MLOps platform with the following features:

- **Project-Based Workflow**: Each ML project is isolated in its own workspace with independent configurations, dependencies, and artifacts
- **DAG Pipeline Execution**: Define complex ML pipelines as directed acyclic graphs (DAGs) using NetworkX, with support for parallel execution, conditional logic, and loops
- **Distributed Computing**: Execute pipelines on clusters using Dask (with SLURM support) or run locally with multi-worker parallelism
- **Environment Isolation**: Automatic virtual environment management (venv/conda) with separate environments for training and reporting
- **Caching & Reproducibility**: Intelligent step-level caching with configurable backends (local filesystem, GCS) and reproducibility guarantees via random seed management
- **Static & Dynamic Reporting**: Generate static charts (PNG) and interactive dynamic charts that update in real-time

## Quick start (built-in template)

```bash
mkdir -p ~/expops-workspace && cd ~/expops-workspace

expops create sklearn-basic --template sklearn-basic
expops run sklearn-basic --local
```

This creates `projects/sklearn-basic/` and runs a minimal scikit-learn example. The config is at `projects/sklearn-basic/configs/project_config.yaml`.

By default, the template uses a **local-first cache backend** (however the metrics, charts and the web UI only works with a remote kv backend). To enable cross-process live metrics (web UI) or remote backends, update `model.parameters.cache.backend` in the project config.

To run on a distributed cluster (e.g. SLURM), a `cluster_config.yaml` should be added under configs and the --local flag can be removed when running.

## Create a project

```bash
expops create my-project
expops run my-project
```

## Template projects

Templates are available via `expops create --template ...`:

- `sklearn-basic`: runnable project skeleton (configs/data/models/charts + requirements) that trains a tiny sklearn model and generates basic plots  

- `premier-league`: more comprehensive ML project predicting results of football matches, contains cluster config and dynamic charts as well

## Project Structure

Each project follows a standardized directory structure. Here's what each component does:

### Configuration Files

**`configs/project_config.yaml`**: Main project configuration file that defines:
- **Metadata**: Project name, description, version
- **Environment**: Virtual environment settings with separate requirements for training and reporting
- **Reproducibility**: Random seed configuration and experiment tracking settings
- **Model Configuration**: Framework selection, custom script paths, hyperparameters
- **Pipeline Definition**: DAG structure (`process_adjlist`) and process definitions with dependencies
- **Reporting**: Chart definitions (static and dynamic) with probe paths for metrics extraction

**`configs/cluster_config.yaml`**: Optional cluster execution configuration:
- **Provider**: Cluster provider (e.g., `slurm`, `dask`)
- **Workers**: Number of worker nodes and resource allocation (cores, memory)
- **Queue Settings**: Job queue, walltime, and scheduler configuration

### Model Code

**`models/<model_name>.py`**: Custom model implementation file containing:
- **Process Definitions**: Functions decorated with `@process()` that define pipeline steps
- **Step Functions**: Functions decorated with `@step()` that perform specific operations (data loading, preprocessing, training, inference)
- **Pipeline Logic**: Data transformations, model training, evaluation, and ensemble methods
- **Metrics Logging**: Integration with `log_metric()` for experiment tracking

### Chart Generation

**`charts/plot_metrics.py`**: Python script for static chart generation:
- **Chart Functions**: Functions decorated with `@chart()` that generate PNG visualizations
- **Metrics Access**: Reads metrics from previous pipeline steps via `ChartContext`
- **Static Output**: Produces static image files (e.g., PCA scree plots, metric comparisons, distribution histograms)

**`charts/plot_metrics.js`**: JavaScript file for dynamic, interactive charts:
- **Real-time Updates**: Charts that update dynamically as metrics are logged during pipeline execution
- **Chart.js Integration**: Uses Chart.js library for interactive visualizations
- **Live Metrics**: Subscribes to metric streams from multiple pipeline steps (e.g., training loss over epochs)
- **Web UI Integration**: Rendered in the web UI for interactive exploration

### Dependencies

**`requirements.txt`**: Main project dependencies for training and inference:
- Core ML libraries (scikit-learn, XGBoost, PyTorch, TensorFlow, etc.)
- Data processing libraries (pandas, numpy)
- Any other dependencies needed for model execution

**`charts/requirements.txt`**: Reporting-specific dependencies:
- Visualization libraries (matplotlib, seaborn)
- Minimal dependencies needed only for chart generation
- Kept separate to reduce overhead in training environments

### Data & Artifacts

**`data/`**: Directory for input datasets (CSV, Parquet, etc.)

**`logs/`**: Execution logs for each pipeline run

**`keys/`**: Credentials and authentication files (e.g., `firestore.json` for GCP integration)

## Local Web UI

```bash
python -m expops.web.server
```

Open `http://127.0.0.1:8000`. Choose a project and Run ID (from the configured KV backend in `configs/project_config.yaml`). The web UI allows you to:
- Browse projects and runs
- View static charts
- Interact with dynamic charts (real-time metric visualization)