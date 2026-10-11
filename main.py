"""Main orchestrator for the Autonomous YouTube Video Pipeline.

Usage:
  python main.py --all
  python main.py --tool "Cursor AI" --title "How to Code 10x Faster with Cursor"
  python main.py --stage 1
  python main.py --project-id 20261011_140000 --stage 3
  python main.py --schedule --interval-hours 24
"""

import argparse
import sys
from datetime import datetime
from typing import Optional, List
from config.settings import settings
from config.logging_config import setup_logger
from src.models import ProjectState, Topic
from src.utils.file_manager import FileManager
from src.stages import (
    BaseStage,
    TopicSelectionStage,
    ScriptResearchStage,
    VoiceoverStage,
    VisualsStage,
    VideoAssemblyStage,
    MetadataThumbnailStage,
    YouTubeUploadStage,
)

logger = setup_logger("orchestrator")

ALL_STAGES: List[BaseStage] = [
    TopicSelectionStage(),
    ScriptResearchStage(),
    VoiceoverStage(),
    VisualsStage(),
    VideoAssemblyStage(),
    MetadataThumbnailStage(),
    YouTubeUploadStage(),
]

def run_pipeline(
    project_id: Optional[str] = None,
    specific_stage: Optional[int] = None,
    tool_name: Optional[str] = None,
    custom_title: Optional[str] = None,
) -> ProjectState:
    """Executes the pipeline either end-to-end or for a single stage.
    
    Args:
        project_id: Optional existing project ID to resume.
        specific_stage: Optional 1-indexed stage number to execute.
        tool_name: Optional specific AI tool to feature.
        custom_title: Optional custom title for the video.
        
    Returns:
        Final ProjectState.
    """
    settings.ensure_directories()

    # Load or initialize project state
    if project_id:
        state = FileManager.load_state(project_id)
        if not state:
            logger.error(f"Project ID '{project_id}' not found in metadata storage.")
            sys.exit(1)
        logger.info(f"Loaded existing project state: {project_id}")
    else:
        new_project_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        state = ProjectState(project_id=new_project_id)
        logger.info(f"Initialized new project state: {new_project_id}")

    # Set topic if custom tool provided
    if tool_name:
        state.topic = Topic(
            id=state.project_id,
            tool_name=tool_name,
            title=custom_title or f"How to Use {tool_name} (Complete 2026 Tutorial)",
            value_proposition=f"Learn step-by-step how to automate workflows and save hours with {tool_name}."
        )

    # Determine stages to execute
    if specific_stage is not None:
        if not (1 <= specific_stage <= len(ALL_STAGES)):
            logger.error(f"Invalid stage number: {specific_stage}. Must be between 1 and {len(ALL_STAGES)}.")
            sys.exit(1)
        stages_to_run = [ALL_STAGES[specific_stage - 1]]
    else:
        stages_to_run = ALL_STAGES

    # Execute stages sequentially
    for stage in stages_to_run:
        try:
            state = stage.run(state)
        except Exception as exc:
            logger.critical(f"Pipeline stopped at Stage {stage.stage_number} ({stage.stage_name}): {exc}")
            sys.exit(1)

    logger.info("==================================================")
    logger.info(f"Pipeline run finished for Project: {state.project_id}")
    logger.info(f"Status: {state.status.upper()}")
    if state.final_video_path:
        logger.info(f"Final Video: {state.final_video_path}")
    if state.youtube_video_url:
        logger.info(f"YouTube URL: {state.youtube_video_url}")
    logger.info("==================================================")

    return state

def parse_args():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous YouTube Video Generation Pipeline for AI Tools"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run full end-to-end pipeline (Stages 1 through 7)"
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=range(1, 8),
        help="Run only a specific stage (1: Topic, 2: Script, 3: Voiceover, 4: Visuals, 5: Assembly, 6: Metadata, 7: Upload)"
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help="Resume or inspect a specific project ID"
    )
    parser.add_argument(
        "--tool",
        type=str,
        help="AI Tool name to feature (e.g., 'Midjourney v7', 'Perplexity AI')"
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Custom title for the video"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run pipeline on a recurring schedule"
    )
    parser.add_argument(
        "--interval-hours",
        type=int,
        default=24,
        help="Hours between scheduled runs (default: 24)"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    if args.schedule:
        from src.scheduler import start_scheduler
        start_scheduler(interval_hours=args.interval_hours)
    else:
        # Default to full pipeline if no specific stage is given
        specific_stage = args.stage if args.stage else (None if args.all or not args.stage else None)
        run_pipeline(
            project_id=args.project_id,
            specific_stage=args.stage,
            tool_name=args.tool,
            custom_title=args.title
        )

if __name__ == "__main__":
    main()
