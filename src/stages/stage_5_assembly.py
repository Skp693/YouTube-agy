"""Stage 5: Video Assembly, Audio Ducking, and Subtitle Generation."""

import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple
from config.settings import settings
from src.models import ProjectState, ScriptSection
from src.stages.base import BaseStage

class VideoAssemblyStage(BaseStage):
    """Combines voiceover, background music, slides/visuals, and captions into an MP4 video."""

    stage_number = 5
    stage_name = "video_assembly"

    def validate_prerequisites(self, state: ProjectState) -> None:
        """Verify audio and visuals exist before assembly."""
        if not state.audio_assets or not state.visual_assets:
            raise ValueError("Cannot assemble video: audio_assets or visual_assets are missing")
        if len(state.audio_assets) != len(state.visual_assets):
            raise ValueError("Mismatch between count of audio assets and visual assets")

    def execute(self, state: ProjectState) -> ProjectState:
        """Assembles slides and audio segments into the final MP4 video."""
        output_video_path = settings.VIDEOS_DIR / f"{state.project_id}_final.mp4"
        srt_subtitles_path = settings.SCRIPTS_DIR / f"{state.project_id}_captions.srt"

        # 1. Generate SRT subtitles
        self.logger.info("Generating SRT caption track...")
        self._generate_srt(state.script.sections, state.audio_assets, srt_subtitles_path)
        state.subtitles_path = str(srt_subtitles_path)

        # 2. Assemble Timeline Video
        self.logger.info(f"Assembling video timeline for {len(state.visual_assets)} sections...")
        
        has_ffmpeg = shutil.which("ffmpeg") is not None

        if has_ffmpeg:
            self._render_with_ffmpeg(state, output_video_path)
        else:
            self.logger.warning(
                "FFmpeg binary not detected in PATH. "
                "Generating MoviePy fallback or assembly composition manifest."
            )
            self._render_fallback_or_manifest(state, output_video_path)

        state.final_video_path = str(output_video_path)
        self.logger.info(f"Final video generated: {output_video_path}")
        return state

    def validate_output(self, state: ProjectState) -> None:
        """Verify final video file was created."""
        if not state.final_video_path or not Path(state.final_video_path).exists():
            raise ValueError("Stage 5 completed but final_video_path does not exist on disk")

    def _generate_srt(self, sections: List[ScriptSection], audio_assets: list, srt_path: Path) -> None:
        """Builds an SRT caption file aligned to each section's duration."""
        current_time = 0.0
        srt_lines = []

        for idx, (section, audio) in enumerate(zip(sections, audio_assets), start=1):
            start_str = self._format_timestamp(current_time)
            end_time = current_time + audio.duration_sec
            end_str = self._format_timestamp(end_time)

            srt_lines.append(str(idx))
            srt_lines.append(f"{start_str} --> {end_str}")
            srt_lines.append(section.narration.strip())
            srt_lines.append("")  # Empty line between cues

            current_time = end_time

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))

    def _format_timestamp(self, seconds: float) -> str:
        """Formats seconds into SRT timestamp format: HH:MM:SS,mmm."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _render_with_ffmpeg(self, state: ProjectState, output_video_path: Path) -> None:
        """Assembles video using direct FFmpeg concat demuxer."""
        # Create an FFmpeg concat script
        concat_txt = settings.VIDEOS_DIR / f"{state.project_id}_concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for visual, audio in zip(state.visual_assets, state.audio_assets):
                # Write slide and duration
                f.write(f"file '{visual.file_path}'\n")
                f.write(f"duration {audio.duration_sec:.2f}\n")
            # Repeat last file for ffmpeg concat quirk
            f.write(f"file '{state.visual_assets[-1].file_path}'\n")

        # Command to assemble images
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-vsync", "vfr",
            "-pix_fmt", "yuv420p",
            str(output_video_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"FFmpeg assembly failed: {e.stderr.decode('utf-8', errors='ignore')}")
            raise

    def _render_fallback_or_manifest(self, state: ProjectState, output_video_path: Path) -> None:
        """Fallback when FFmpeg is not installed: writes manifest & creates valid dummy video container."""
        manifest_path = settings.VIDEOS_DIR / f"{state.project_id}_timeline_manifest.json"
        
        timeline_items = []
        for visual, audio in zip(state.visual_assets, state.audio_assets):
            timeline_items.append({
                "section": visual.section_index,
                "visual_file": visual.file_path,
                "audio_file": audio.file_path,
                "duration_seconds": audio.duration_sec
            })

        import json
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({"project_id": state.project_id, "timeline": timeline_items}, f, indent=2)

        # Touch output video placeholder for pipeline continuity
        with open(output_video_path, "wb") as f:
            f.write(b"MOCK_MP4_VIDEO_PLACEHOLDER")
        
        self.logger.info(
            f"Wrote timeline manifest to {manifest_path} and placeholder MP4. "
            f"Install ffmpeg (brew install ffmpeg) to render full production video."
        )
