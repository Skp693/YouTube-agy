"""Master Orchestrator (main_pipeline.py)

Autonomous YouTube Pipeline for 8–12 Minute Educational AI Tool Videos.
Executes Stages 1 through 7 in sequence:
  Stage 1: Topic Selector       (topic_selector.py)
  Stage 2: Script Writer        (script_writer.py)
  Stage 3: Voiceover            (voiceover.py)
  Stage 4: Visuals              (visuals.py)
  Stage 5: Video Assembly       (assemble_video.py)
  Stage 6: Metadata & Thumbnail (metadata.py)
  Stage 7: YouTube Uploader     (youtube_uploader.py)

Modes:
  --review (Default): Assembles video and metadata, then stops for manual review.
  --auto:            Executes full pipeline and automatically uploads to YouTube.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from config.settings import settings
from config.logging_config import setup_logger

import topic_selector
import script_writer
import voiceover
import visuals
import assemble_video
import metadata
import youtube_uploader
from compliance_checker import ComplianceChecker

logger = setup_logger("main_pipeline")

def run_pipeline(
    tool_name: Optional[str] = None,
    angle: Optional[str] = None,
    auto_upload: bool = False,
    privacy: Optional[str] = None,
    project_id: Optional[str] = None,
    voice_avatar: Optional[str] = None,
    ken_burns: bool = True,
    speaking_rate: Optional[int] = None
) -> Dict[str, Any]:
    """Runs the complete YouTube generation pipeline.
    
    Args:
        tool_name: Optional explicit AI tool to target.
        angle: Optional angle/focus for the tutorial.
        auto_upload: If True, uploads immediately to YouTube (Full Auto). If False, stops for review.
        privacy: YouTube privacy status ("private", "unlisted", "public").
        project_id: Optional project identifier.
        
    Returns:
        Summary dictionary with all output asset paths and status.
    """
    start_time = time.time()
    settings.ensure_directories()
    project_id = project_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    mode_str = "FULL AUTO (LIVE UPLOAD)" if auto_upload else "REVIEW MODE (SAFE PREVIEW)"

    logger.info("================================================================================")
    logger.info(f"STARTING AUTONOMOUS YOUTUBE PIPELINE | Project ID: {project_id}")
    logger.info(f"Execution Mode: {mode_str}")
    logger.info("================================================================================")

    # --------------------------------------------------------------------------
    # STAGE 1: Topic Selection
    # --------------------------------------------------------------------------
    logger.info(">>> [1/7] STAGE 1: Topic Selection & Research...")
    topic_res = topic_selector.select_topic(
        tool_name=tool_name,
        angle=angle,
        project_id=project_id
    )
    logger.info(f"Selected Tool: {topic_res['tool_name']} ('{topic_res['suggested_title']}')")

    # --------------------------------------------------------------------------
    # STAGE 2: Research & 8-12 Min Script Writing (1400-1800 words)
    # --------------------------------------------------------------------------
    logger.info(">>> [2/7] STAGE 2: Script Writing (1400-1800 Words Target)...")
    script_res = script_writer.write_script(
        topic_data=topic_res,
        project_id=project_id
    )
    logger.info(
        f"Script generated: {script_res['word_count']} words | "
        f"Est. Runtime: {script_res['estimated_total_minutes']} mins | "
        f"{len(script_res['sections'])} sections"
    )

    # --------------------------------------------------------------------------
    # STAGE 3: AI Voiceover & Audio Timing
    # --------------------------------------------------------------------------
    logger.info(">>> [3/7] STAGE 3: Professional AI Voiceover Synthesis...")
    voice_res = voiceover.generate_voiceover(
        script_data=script_res,
        project_id=project_id,
        voice_name=voice_avatar,
        speaking_rate=speaking_rate
    )
    logger.info(
        f"Voiceover complete: {voice_res['total_duration_sec']:.2f}s "
        f"({voice_res['total_duration_sec']/60:.2f} mins)"
    )

    # --------------------------------------------------------------------------
    # STAGE 4: Educational Visuals & Scenes Timeline
    # --------------------------------------------------------------------------
    logger.info(">>> [4/7] STAGE 4: Educational 1080p Visuals & Scene Generation...")
    # Load audio timing for scene duration matching
    with open(voice_res["timing_json_path"], "r", encoding="utf-8") as f:
        timing_data = json.load(f)

    visuals_res = visuals.generate_visuals(
        script_data=script_res,
        timing_data=timing_data,
        project_id=project_id
    )
    logger.info(f"Generated {visuals_res['total_scenes']} visual scenes for video timeline.")

    # Optional: Capture Live Web Screencast B-Roll
    try:
        from src.utils.browser_recorder import capture_web_broll
        broll_dir = settings.IMAGES_DIR / project_id
        capture_web_broll(topic_res["tool_name"], broll_dir)
        logger.info(f"Captured live web B-roll for {topic_res['tool_name']}")
    except Exception as e:
        logger.warning(f"B-roll capture skipped: {e}")

    # --------------------------------------------------------------------------
    # STAGE 5: Video Assembly (Voice + Slides + Ducked Music + Captions)
    # --------------------------------------------------------------------------
    logger.info(">>> [5/7] STAGE 5: Video Assembly, Transitions & Audio Ducking...")
    with open(visuals_res["timeline_json_path"], "r", encoding="utf-8") as f:
        scenes_data = json.load(f)

    assembly_res = assemble_video.assemble_video(
        project_id=project_id,
        script_data=script_res,
        timing_data=timing_data,
        scenes_data=scenes_data,
        ken_burns=ken_burns
    )
    logger.info(f"Video assembly finished -> {assembly_res['final_video_path']}")

    # --------------------------------------------------------------------------
    # STAGE 6: Metadata & 1280x720 Thumbnail Generation
    # --------------------------------------------------------------------------
    logger.info(">>> [6/7] STAGE 6: SEO Metadata & High-CTR Thumbnail...")
    meta_res = metadata.generate_metadata_and_thumbnail(
        project_id=project_id,
        script_data=script_res,
        timing_data=timing_data
    )
    logger.info(f"Metadata & Thumbnail generated -> {meta_res['thumbnail_path']}")

    # --------------------------------------------------------------------------
    # STAGE 7: YouTube Upload or Review Hold
    # --------------------------------------------------------------------------
    if auto_upload:
        logger.info(">>> [7/7] STAGE 7: Full Auto Upload to YouTube Channel...")
        upload_res = youtube_uploader.upload_to_youtube(
            project_id=project_id,
            privacy=privacy,
            dry_run=False
        )
    else:
        logger.info(">>> [7/7] STAGE 7: Review Mode Active (Upload Paused)...")
        upload_res = youtube_uploader.upload_to_youtube(
            project_id=project_id,
            privacy=privacy,
            dry_run=True
        )

    elapsed_time = round(time.time() - start_time, 2)

    # Audit compliance against YouTube monetization policies
    audit_res = ComplianceChecker.audit_project(
        title=meta_res.get("title", ""),
        description=meta_res.get("description", ""),
        narration_full=script_res.get("full_text", ""),
        tags=meta_res.get("tags", []),
        has_ai_disclosure=True
    )

    # --------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------------------------------
    summary = {
        "project_id": project_id,
        "mode": "auto" if auto_upload else "review",
        "tool_name": topic_res["tool_name"],
        "title": meta_res["title"],
        "word_count": script_res["word_count"],
        "duration_minutes": round(voice_res["total_duration_sec"] / 60.0, 2),
        "video_path": assembly_res["final_video_path"],
        "thumbnail_path": meta_res["thumbnail_path"],
        "metadata_path": meta_res["metadata_json_path"],
        "captions_path": assembly_res["captions_srt_path"],
        "upload_status": upload_res["status"].upper(),
        "youtube_url": upload_res["video_url"],
        "compliance_score": audit_res.get("score", 100),
        "compliance_status": audit_res.get("status", "PASS"),
        "elapsed_seconds": elapsed_time
    }

    logger.info("================================================================================")
    logger.info(f"PIPELINE COMPLETED IN {elapsed_time}s | Project: {project_id}")
    logger.info(f"Video:     {summary['video_path']}")
    logger.info(f"Thumbnail: {summary['thumbnail_path']}")
    logger.info(f"Status:    {summary['upload_status']}")
    logger.info("================================================================================")

    return summary

def print_summary_card(summary: Dict[str, Any]) -> None:
    """Prints a clean CLI summary card for the user."""
    print("\n" + "=" * 70)
    print("🎬 AUTONOMOUS YOUTUBE VIDEO PIPELINE - EXECUTION SUMMARY")
    print("=" * 70)
    print(f"Project ID:       {summary['project_id']}")
    print(f"Mode:             {summary['mode'].upper()} {'(Ready for Inspection)' if summary['mode'] == 'review' else '(Uploaded)'}")
    print(f"Tool Featured:    {summary['tool_name']}")
    print(f"Video Title:      {summary['title']}")
    print(f"Script Length:    {summary['word_count']} words (~{summary['duration_minutes']} minutes)")
    print("-" * 70)
    print(f"📹 Final Video:    {summary['video_path']}")
    print(f"🖼️ Thumbnail:      {summary['thumbnail_path']}")
    print(f"📝 Metadata:       {summary['metadata_path']}")
    print(f"💬 Captions (SRT): {summary['captions_path']}")
    print("-" * 70)
    print(f"🚀 Upload Status:  {summary['upload_status']}")
    print(f"🔗 YouTube Link:   {summary['youtube_url']}")
    print("=" * 70 + "\n")

def run_schedule_loop(interval_hours: int = 24, auto_upload: bool = False) -> None:
    """Runs pipeline continuously on a recurring schedule."""
    logger.info(f"Starting pipeline scheduler daemon. Interval: every {interval_hours} hours.")
    print(f"\n⏰ Pipeline scheduler active. Running every {interval_hours} hours. Press Ctrl+C to stop.\n")

    while True:
        try:
            logger.info("Triggering scheduled video generation job...")
            summary = run_pipeline(auto_upload=auto_upload)
            print_summary_card(summary)
            logger.info(f"Scheduled run complete. Sleeping for {interval_hours} hours...")
            time.sleep(interval_hours * 3600)
        except KeyboardInterrupt:
            logger.info("Scheduler daemon stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error during scheduled run: {e}")
            logger.info("Retrying in 1 hour...")
            time.sleep(3600)

def main():
    parser = argparse.ArgumentParser(
        description="Autonomous 8-12 Minute YouTube Video Creation & Upload Pipeline"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--review",
        action="store_true",
        default=True,
        help="Default safe mode: builds finished video & thumbnail, stops before uploading"
    )
    group.add_argument(
        "--auto",
        action="store_true",
        help="Full auto mode: builds video and immediately uploads to YouTube"
    )

    parser.add_argument("--tool", type=str, help="AI tool to feature (e.g. 'Cursor AI', 'NotebookLM')")
    parser.add_argument("--angle", type=str, help="Tutorial angle or focus")
    parser.add_argument("--privacy", type=str, choices=["private", "unlisted", "public"], help="Upload privacy status")
    parser.add_argument("--schedule", action="store_true", help="Run continuously on an autonomous schedule")
    parser.add_argument("--interval-hours", type=int, default=24, help="Hours between scheduled runs (default: 24)")

    args = parser.parse_args()

    # Determine auto_upload
    auto_upload = args.auto

    if args.schedule:
        run_schedule_loop(interval_hours=args.interval_hours, auto_upload=auto_upload)
    else:
        summary = run_pipeline(
            tool_name=args.tool,
            angle=args.angle,
            auto_upload=auto_upload,
            privacy=args.privacy
        )
        print_summary_card(summary)

if __name__ == "__main__":
    main()
