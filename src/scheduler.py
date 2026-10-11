"""Scheduled job runner for autonomous video generation and uploads."""

import time
import schedule
from datetime import datetime
from config.logging_config import setup_logger

logger = setup_logger("scheduler")

def run_scheduled_pipeline() -> None:
    """Executes a full pipeline run as a scheduled job."""
    from main import run_pipeline
    logger.info("Executing scheduled YouTube video generation job...")
    try:
        state = run_pipeline()
        logger.info(f"Scheduled pipeline run completed successfully: Project {state.project_id}")
    except Exception as e:
        logger.error(f"Scheduled pipeline run encountered an error: {e}")

def start_scheduler(interval_hours: int = 24) -> None:
    """Starts a long-running scheduler loop.
    
    Args:
        interval_hours: Frequency in hours to run the pipeline.
    """
    logger.info(f"Starting pipeline scheduler. Interval: every {interval_hours} hours.")
    
    # Schedule job
    schedule.every(interval_hours).hours.do(run_scheduled_pipeline)

    # Run immediately on boot
    run_scheduled_pipeline()

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")

if __name__ == "__main__":
    start_scheduler()
