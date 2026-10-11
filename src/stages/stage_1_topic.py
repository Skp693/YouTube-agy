"""Stage 1: Topic Selection and Scoring."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from config.settings import settings
from src.models import ProjectState, Topic
from src.stages.base import BaseStage

class TopicSelectionStage(BaseStage):
    """Selects an AI tool topic from backlog or generates an optimal trending topic."""

    stage_number = 1
    stage_name = "topic_selection"

    def validate_prerequisites(self, state: ProjectState) -> None:
        """Validate prerequisites before selecting topic."""
        # ProjectState must exist
        if not state.project_id:
            raise ValueError("project_id must be initialized in ProjectState")

    def execute(self, state: ProjectState) -> ProjectState:
        """Selects or loads the topic for the video."""
        # If topic was already assigned (e.g. from CLI argument), keep and validate it
        if state.topic:
            self.logger.info(f"Using pre-assigned topic: {state.topic.tool_name} - '{state.topic.title}'")
            self._save_topic_file(state.topic)
            return state

        # Check for topic backlog file
        backlog_file = settings.TOPICS_DIR / "backlog.json"
        topic: Optional[Topic] = None

        if backlog_file.exists():
            self.logger.info(f"Loading topic from backlog: {backlog_file}")
            topic = self._pop_from_backlog(backlog_file, state.project_id)

        # Fallback default if backlog is empty or missing
        if not topic:
            self.logger.info("No backlog found. Generating default high-demand AI tool topic.")
            topic = Topic(
                id=state.project_id,
                tool_name="Claude Artifacts & Projects",
                title="How to Master Claude Artifacts & Projects (Step-by-Step 2026 Guide)",
                category="AI Productivity & Coding",
                target_audience="Developers, Designers, and Product Managers",
                value_proposition="Learn how to build interactive apps, dashboards, and automated workflows using Claude 3.7",
                search_keywords=[
                    "Claude Artifacts tutorial",
                    "How to use Claude AI",
                    "Claude Projects guide",
                    "Best AI productivity tools 2026"
                ],
                score=9.5
            )

        self._save_topic_file(topic)
        state.topic = topic
        return state

    def validate_output(self, state: ProjectState) -> None:
        """Ensure a valid topic is present on state."""
        if not state.topic:
            raise ValueError("Stage 1 completed without setting state.topic")
        if not state.topic.tool_name or not state.topic.title:
            raise ValueError("Topic missing tool_name or title")

    def _save_topic_file(self, topic: Topic) -> Path:
        """Persist selected topic JSON in topics directory."""
        output_path = settings.TOPICS_DIR / f"{topic.id}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(topic.model_dump_json(indent=2))
        self.logger.info(f"Saved topic definition to {output_path}")
        return output_path

    def _pop_from_backlog(self, backlog_path: Path, project_id: str) -> Optional[Topic]:
        """Reads the first uncompleted topic from backlog."""
        try:
            with open(backlog_path, "r", encoding="utf-8") as f:
                items = json.load(f)
            if not items:
                return None
            
            raw_item = items.pop(0)
            raw_item["id"] = project_id
            topic = Topic.model_validate(raw_item)

            # Rewrite remaining backlog items
            with open(backlog_path, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)

            return topic
        except Exception as e:
            self.logger.warning(f"Failed to pop from backlog: {e}. Falling back to default.")
            return None
