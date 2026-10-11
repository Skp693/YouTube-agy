"""Utility functions for file management and project state persistence."""

import json
from pathlib import Path
from typing import Optional
from config.settings import settings
from src.models import ProjectState

class FileManager:
    """Manages paths and persistent state serialization for pipeline runs."""

    @staticmethod
    def get_project_dir(project_id: str) -> Path:
        """Returns or creates a project-specific directory under videos/."""
        project_dir = settings.VIDEOS_DIR / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    @staticmethod
    def save_state(state: ProjectState) -> Path:
        """Saves project state to JSON in the project directory and metadata directory."""
        state.update_timestamp()
        
        # Save to metadata directory for quick tracking
        state_file = settings.METADATA_DIR / f"{state.project_id}_state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))

        return state_file

    @staticmethod
    def load_state(project_id: str) -> Optional[ProjectState]:
        """Loads an existing project state from disk."""
        state_file = settings.METADATA_DIR / f"{project_id}_state.json"
        if not state_file.exists():
            return None
        
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ProjectState.model_validate(data)
