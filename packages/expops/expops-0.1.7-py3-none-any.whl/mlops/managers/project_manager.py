import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json


class ProjectManager:
    """Manages MLOps projects with isolated state, caching, and configurations."""
    
    def __init__(self, projects_root: Optional[Union[str, Path]] = None):
        # Interpret projects_root relative to workspace root so callers can pass
        # `--workspace` / `MLOPS_WORKSPACE_DIR` and still work from any CWD.
        if projects_root is None:
            try:
                from mlops.core.workspace import get_projects_root
                self.projects_root = get_projects_root()
            except Exception:
                self.projects_root = Path("projects")
        else:
            pr = Path(projects_root)
            if not pr.is_absolute():
                try:
                    from mlops.core.workspace import get_workspace_root
                    pr = get_workspace_root() / pr
                except Exception:
                    pass
            self.projects_root = pr

        self.projects_root.mkdir(parents=True, exist_ok=True)
        self.projects_index_file = self.projects_root / "projects_index.json"
        self._ensure_projects_index()
    
    def _ensure_projects_index(self) -> None:
        """Ensure the projects index file exists."""
        if not self.projects_index_file.exists():
            self._save_projects_index({})
    
    def _load_projects_index(self) -> Dict[str, Any]:
        """Load the projects index."""
        if self.projects_index_file.exists():
            with open(self.projects_index_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_projects_index(self, index: Dict[str, Any]) -> None:
        """Save the projects index."""
        with open(self.projects_index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _list_available_templates(self) -> List[str]:
        """List built-in templates shipped with the package (best-effort)."""
        templates: List[str] = []
        try:
            from importlib import resources

            root = resources.files("mlops") / "templates"
            if not root.is_dir():
                return []
            for child in root.iterdir():
                try:
                    if not child.is_dir():
                        continue
                    # New format: templates/<name>/configs/project_config.yaml
                    if (child / "configs" / "project_config.yaml").is_file():
                        templates.append(child.name)
                        continue
                    # Legacy format: templates/<name>/project_config.yaml
                    if (child / "project_config.yaml").is_file():
                        templates.append(child.name)
                except Exception:
                    continue
        except Exception:
            return []
        return sorted(set([t for t in templates if t]))

    def _apply_template(self, project_path: Path, project_id: str, template: str) -> Path:
        """Copy a built-in template into the project directory and return config path."""
        from importlib import resources
        from pathlib import Path as _Path

        available = self._list_available_templates()
        if template not in available:
            raise ValueError(
                f"Unknown template '{template}'. Available templates: {', '.join(available) if available else '(none found)'}"
            )

        root = resources.files("mlops") / "templates" / template

        # New format: full project folder skeleton under the template root.
        new_cfg = root / "configs" / "project_config.yaml"
        legacy_cfg = root / "project_config.yaml"

        def _copy_tree(src_dir, dst_dir: Path) -> None:
            """Recursively copy an importlib.resources Traversable dir into dst_dir."""
            try:
                entries = list(src_dir.iterdir())
            except Exception:
                entries = []
            for entry in entries:
                try:
                    name = entry.name
                except Exception:
                    continue
                rel = _Path(name)
                try:
                    if entry.is_dir():
                        _copy_tree(entry, dst_dir / rel)
                        continue
                except Exception:
                    # Treat unknown entries as files
                    pass

                dest_path = dst_dir / rel
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Read bytes from resource file
                try:
                    with entry.open("rb") as f:
                        raw = f.read()
                except Exception:
                    raw = b""

                # Best-effort: treat common text files as UTF-8 and expand template vars
                suffix = dest_path.suffix.lower()
                if suffix in {".yaml", ".yml", ".py", ".md", ".txt", ".csv", ".json"}:
                    try:
                        text = raw.decode("utf-8")
                        text = text.replace("{{PROJECT_ID}}", project_id)
                        dest_path.write_text(text, encoding="utf-8")
                        continue
                    except Exception:
                        pass

                dest_path.write_bytes(raw)

        if new_cfg.is_file():
            # Copy the entire template tree into the project root (configs/, data/, models/, charts/, etc.)
            _copy_tree(root, project_path)
            config_dest = project_path / "configs" / "project_config.yaml"
            if not config_dest.exists():
                raise ValueError(f"Template '{template}' did not produce configs/project_config.yaml")
            return config_dest

        # Legacy fallback: copy flat files into expected project folders.
        if legacy_cfg.is_file():
            # Write config (with placeholder expansion)
            try:
                with legacy_cfg.open("r", encoding="utf-8") as f:
                    cfg_text = f.read()
            except TypeError:
                with legacy_cfg.open("r") as f:
                    cfg_text = f.read()
            cfg_text = cfg_text.replace("{{PROJECT_ID}}", project_id)

            config_dest = project_path / "configs" / "project_config.yaml"
            config_dest.parent.mkdir(exist_ok=True)
            config_dest.write_text(cfg_text, encoding="utf-8")

            data_res = root / "train.csv"
            if data_res.is_file():
                data_dest = project_path / "data" / "train.csv"
                data_dest.parent.mkdir(exist_ok=True)
                with data_res.open("rb") as f:
                    data_dest.write_bytes(f.read())
            return config_dest

        raise ValueError(f"Template '{template}' is missing configs/project_config.yaml")

    def create_project(
        self,
        project_id: str,
        base_config_path: Optional[str] = None,
        description: str = "",
        template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new project with isolated workspace.
        
        Args:
            project_id: Unique identifier for the project
            base_config_path: Optional path to base configuration to copy
            description: Project description
            template: Optional built-in template name to scaffold a runnable starter project
            
        Returns:
            Project information dictionary
        """
        if self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' already exists")

        if template and base_config_path:
            raise ValueError("Use either 'template' or 'base_config_path', not both")
        
        # Create project directory structure
        project_path = self.projects_root / project_id
        project_path.mkdir(exist_ok=True)
        try:
            from mlops.core.workspace import get_workspace_root  # local import to avoid cycles

            workspace_root = get_workspace_root()
            rel_project_path = project_path.relative_to(workspace_root)
        except Exception:
            rel_project_path = project_path
        
        # Create subdirectories for isolation (state and cache no longer created locally)
        (project_path / "configs").mkdir(exist_ok=True)
        (project_path / "artifacts").mkdir(exist_ok=True)
        (project_path / "logs").mkdir(exist_ok=True)
        (project_path / "data").mkdir(exist_ok=True)
        (project_path / "keys").mkdir(exist_ok=True)
        (project_path / "models").mkdir(exist_ok=True)
        (project_path / "charts").mkdir(exist_ok=True)
        
        # Create project configuration
        project_info = {
            "project_id": project_id,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "base_config_path": base_config_path,
            # Store the relative (or best-effort) path in metadata for portability.
            "project_path": str(rel_project_path),
            "runs": []
        }
        
        # Apply built-in template (copies config + optional sample data)
        if template:
            config_dest = self._apply_template(project_path, project_id, template)
            project_info["active_config"] = str(config_dest)
            project_info["base_config_path"] = f"template:{template}"

        # Copy base configuration if provided
        if (not template) and base_config_path and Path(base_config_path).exists():
            config_dest = project_path / "configs" / "project_config.yaml"
            shutil.copy2(base_config_path, config_dest)
            project_info["active_config"] = str(config_dest)
        
        # Save project info
        project_info_file = project_path / "project_info.json"
        with open(project_info_file, 'w') as f:
            json.dump(project_info, f, indent=2)
        
        # Update projects index
        projects_index = self._load_projects_index()
        projects_index[project_id] = {
            # Store the same relative/best-effort path in the index so that
            # cloned workspaces resolve against the current workspace root.
            "project_path": str(rel_project_path),
            "created_at": project_info["created_at"],
            "description": description
        }
        self._save_projects_index(projects_index)
        
        print(f"✅ Project '{project_id}' created successfully at: {project_path}")
        return project_info
    
    def delete_project(self, project_id: str, confirm: bool = False) -> bool:
        """
        Delete a project and all its associated data.
        
        Args:
            project_id: Project to delete
            confirm: If True, skip confirmation prompt
            
        Returns:
            True if project was deleted, False otherwise
        """
        if not self.project_exists(project_id):
            print(f"❌ Project '{project_id}' does not exist")
            return False
        
        project_path = self.get_project_path(project_id)
        
        if not confirm:
            response = input(f"⚠️  Are you sure you want to delete project '{project_id}' and all its data? [y/N]: ")
            if response.lower() != 'y':
                print("❌ Project deletion cancelled")
                return False
        
        # Remove project directory
        shutil.rmtree(project_path)
        
        # Update projects index
        projects_index = self._load_projects_index()
        del projects_index[project_id]
        self._save_projects_index(projects_index)
        
        print(f"✅ Project '{project_id}' deleted successfully")
        return True
    
    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists."""
        return project_id in self._load_projects_index()
    
    def get_project_path(self, project_id: str) -> Path:
        """Get the path to a project."""
        projects_index = self._load_projects_index()
        if project_id not in projects_index:
            raise ValueError(f"Project '{project_id}' does not exist")
        raw_path = projects_index[project_id]["project_path"]
        p = Path(raw_path)

        # Backwards-compatible behaviour:
        # - If the index stored an absolute path, keep using it.
        # - If it's relative (new behaviour), resolve it against the current workspace root.
        if not p.is_absolute():
            try:
                from mlops.core.workspace import get_workspace_root  # local import to avoid cycles

                p = get_workspace_root() / p
            except Exception:
                # If resolution fails for any reason, fall back to the raw relative path.
                pass

        return p
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects."""
        projects_index = self._load_projects_index()
        projects = []
        
        for project_id, info in projects_index.items():
            try:
                project_path = Path(info["project_path"])
                project_info_file = project_path / "project_info.json"
                
                if project_info_file.exists():
                    with open(project_info_file, 'r') as f:
                        project_info = json.load(f)
                    projects.append(project_info)
                else:
                    # Fallback to index info if project_info.json is missing
                    projects.append({
                        "project_id": project_id,
                        "description": info.get("description", ""),
                        "created_at": info.get("created_at", ""),
                        "project_path": info["project_path"]
                    })
            except Exception as e:
                print(f"Warning: Could not load info for project '{project_id}': {e}")
                
        return projects
    
    def get_project_info(self, project_id: str) -> Dict[str, Any]:
        """Get detailed information about a project."""
        if not self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_path = self.get_project_path(project_id)
        project_info_file = project_path / "project_info.json"
        
        with open(project_info_file, 'r') as f:
            return json.load(f)
    
    def update_project_config(self, project_id: str, config_updates: Dict[str, Any]) -> None:
        """Update project configuration."""
        if not self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_path = self.get_project_path(project_id)
        config_file = project_path / "configs" / "project_config.yaml"
        
        # Load existing config or create new one
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # Deep merge config updates
        self._deep_merge(config, config_updates)
        
        # Save updated config
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Update project info
        project_info = self.get_project_info(project_id)
        project_info["last_modified"] = datetime.now().isoformat()
        project_info["active_config"] = str(config_file)
        
        project_info_file = project_path / "project_info.json"
        with open(project_info_file, 'w') as f:
            json.dump(project_info, f, indent=2)
        
        print(f"✅ Project '{project_id}' configuration updated")
    
    def _deep_merge(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Deep merge two dictionaries."""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_merge(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get_project_config_path(self, project_id: str) -> Path:
        """Get the path to project's active configuration."""
        if not self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_path = self.get_project_path(project_id)
        config_file = project_path / "configs" / "project_config.yaml"
        
        return config_file
    
    def add_run_to_project(self, project_id: str, run_id: str, config_hash: str) -> None:
        """Add a run record to the project."""
        if not self.project_exists(project_id):
            raise ValueError(f"Project '{project_id}' does not exist")
        
        project_info = self.get_project_info(project_id)
        project_info["runs"].append({
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "config_hash": config_hash
        })
        project_info["last_modified"] = datetime.now().isoformat()
        
        project_path = self.get_project_path(project_id)
        project_info_file = project_path / "project_info.json"
        with open(project_info_file, 'w') as f:
            json.dump(project_info, f, indent=2) 