"""Stage 6: Metadata Generation (Title, Description, Chapters, Tags) & Thumbnail Creation."""

import json
from pathlib import Path
from typing import List
from PIL import Image, ImageDraw
from config.settings import settings
from src.models import ProjectState, VideoMetadata, ChapterMarker
from src.stages.base import BaseStage

class MetadataThumbnailStage(BaseStage):
    """Generates SEO-optimized YouTube metadata, chapter markers, and high-CTR thumbnail."""

    stage_number = 6
    stage_name = "metadata_and_thumbnail"

    def validate_prerequisites(self, state: ProjectState) -> None:
        """Verify script and audio assets are available to compute accurate chapters."""
        if not state.script or not state.audio_assets:
            raise ValueError("Cannot generate metadata: script or audio_assets missing")

    def execute(self, state: ProjectState) -> ProjectState:
        """Constructs YouTube metadata package and generates thumbnail."""
        topic = state.topic
        script = state.script

        self.logger.info(f"Generating SEO metadata and thumbnail for '{topic.tool_name}'...")

        # 1. Compute chapter timestamps
        chapters = self._compute_chapters(script.sections, state.audio_assets)

        # 2. Build Title (<70 chars for best mobile/desktop CTR)
        title = f"How to Use {topic.tool_name} (Complete 2026 Tutorial)"
        if len(title) > 70:
            title = f"{topic.tool_name} Full Tutorial (2026 Guide)"

        # 3. Build Description with chapters and SEO keywords
        description = self._build_description(topic, script, chapters)

        # 4. Generate Tags
        tags = [
            topic.tool_name,
            f"{topic.tool_name} tutorial",
            f"how to use {topic.tool_name}",
            "ai tools 2026",
            "artificial intelligence tutorial",
            "ai productivity",
            "step by step guide",
            "tech explainer"
        ] + [kw for kw in topic.search_keywords if kw not in tags]

        metadata = VideoMetadata(
            title=title,
            description=description,
            tags=tags[:15],
            category_id=settings.YOUTUBE_CATEGORY_ID,
            privacy_status=settings.YOUTUBE_PRIVACY_STATUS,
            chapters=chapters
        )

        # 5. Save metadata JSON
        metadata_file = settings.METADATA_DIR / f"{state.project_id}_metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            f.write(metadata.model_dump_json(indent=2))

        # 6. Generate 1280x720 High-CTR Thumbnail
        thumbnail_path = settings.THUMBNAILS_DIR / f"{state.project_id}_thumb.png"
        self._generate_thumbnail(topic.tool_name, thumbnail_path)

        state.metadata = metadata
        state.thumbnail_path = str(thumbnail_path)
        self.logger.info(f"Generated metadata ({metadata_file}) and thumbnail ({thumbnail_path})")
        return state

    def validate_output(self, state: ProjectState) -> None:
        """Verify metadata and thumbnail exist."""
        if not state.metadata or not state.thumbnail_path:
            raise ValueError("Stage 6 completed without setting metadata or thumbnail_path")
        if not Path(state.thumbnail_path).exists():
            raise ValueError("Thumbnail image was not written to disk")

    def _compute_chapters(self, sections: list, audio_assets: list) -> List[ChapterMarker]:
        """Calculates precise chapter timestamps based on audio durations."""
        chapters = []
        accumulated_seconds = 0.0

        for section, audio in zip(sections, audio_assets):
            formatted_time = self._format_chapter_time(accumulated_seconds)
            chapters.append(
                ChapterMarker(
                    title=section.section_title,
                    timestamp_seconds=accumulated_seconds,
                    timestamp_formatted=formatted_time
                )
            )
            accumulated_seconds += audio.duration_sec

        return chapters

    def _format_chapter_time(self, seconds: float) -> str:
        """Formats seconds into MM:SS format required by YouTube chapters."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def _build_description(self, topic, script, chapters: List[ChapterMarker]) -> str:
        """Constructs formatted YouTube description."""
        desc_lines = [
            f"Learn how to master {topic.tool_name} from scratch in this comprehensive, step-by-step 2026 guide.",
            f"\n{topic.value_proposition}\n",
            "⏱️ TIMESTAMPS / CHAPTERS:",
        ]
        for ch in chapters:
            desc_lines.append(f"{ch.timestamp_formatted} - {ch.title}")

        desc_lines.extend([
            "\n📌 KEY TAKEAWAYS:",
            f"• Complete workflow and setup for {topic.tool_name}",
            "• Best practices for prompt engineering and structured outputs",
            "• Monetization models and client deliverable workflows",
            "• Honest comparison of pricing and limitations",
            "\n🔔 Subscribe to the channel for weekly deep-dives into the latest AI tools and automation strategies!",
            "\n#AI #TechTutorial #ArtificialIntelligence #Productivity"
        ])

        return "\n".join(desc_lines)

    def _generate_thumbnail(self, tool_name: str, output_path: Path) -> None:
        """Generates a high-contrast 1280x720 YouTube thumbnail."""
        width, height = 1280, 720
        # Dark dramatic gradient base
        img = Image.new("RGB", (width, height), color=(10, 15, 30))
        draw = ImageDraw.Draw(img)

        # Bold contrasting background shapes
        draw.rectangle([0, 0, width, 16], fill=(239, 68, 68))  # Red top bar
        draw.rectangle([60, 60, width - 60, height - 60], outline=(59, 130, 246), width=6)

        # Eye-catching badge
        draw.rectangle([100, 100, 360, 160], fill=(239, 68, 68))
        draw.text((120, 115), "STEP-BY-STEP", fill=(255, 255, 255))

        # Main Catchy Typography
        draw.text((100, 220), tool_name.upper()[:20], fill=(255, 255, 255))
        draw.text((100, 320), "FULL GUIDE", fill=(250, 204, 21))  # Bright yellow

        # Sub-badge
        draw.rectangle([100, 440, 520, 520], fill=(30, 41, 59))
        draw.text((120, 465), "ZERO TO HERO • 2026", fill=(56, 189, 248))

        img.save(output_path, "PNG")
