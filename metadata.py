"""Stage 6: Metadata & Thumbnail Generation (metadata.py)

Generates:
  1. Strong, honest, SEO-friendly YouTube title (under 70 chars)
  2. Full description with accurate timestamped chapters and CTA
  3. Relevant search tags
  4. Eye-catching, high-CTR 1280x720 thumbnail image
Saves metadata in metadata/<project_id>_metadata.json and thumbnail in thumbnails/.
"""

import os
import sys
import json
import struct
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any, List

from config.settings import settings
from config.logging_config import setup_logger
from src.utils.bitmap_font import draw_text_bmp

logger = setup_logger("metadata")

# Check for PIL
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def format_chapter_timestamp(seconds: float) -> str:
    """Formats seconds into MM:SS (or HH:MM:SS) format for YouTube descriptions."""
    total_sec = int(round(seconds))
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hrs > 0:
        return f"{hrs:d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

def render_thumbnail_pil(tool_name: str, output_path: Path, width: int = 1280, height: int = 720) -> None:
    """Renders high-CTR 1280x720 thumbnail with PIL."""
    img = Image.new("RGB", (width, height), color=(10, 15, 30))
    draw = ImageDraw.Draw(img)

    # Top red accent bar
    draw.rectangle([0, 0, width, 16], fill=(239, 68, 68))
    # Border
    draw.rectangle([50, 50, width - 50, height - 50], outline=(59, 130, 246), width=6)

    # Eyebrow Pill Badge
    draw.rectangle([90, 90, 380, 150], fill=(239, 68, 68))
    draw.text((115, 108), "STEP-BY-STEP", fill=(255, 255, 255))

    # Big Headline (Tool Name)
    clean_tool = tool_name.upper()[:22]
    draw.text((90, 200), clean_tool, fill=(255, 255, 255))

    # Catchy Subtitle in Golden Yellow
    draw.text((90, 310), "FULL GUIDE", fill=(250, 204, 21))

    # Bottom Pill
    draw.rectangle([90, 430, 560, 510], fill=(30, 41, 59), outline=(56, 189, 248), width=2)
    draw.text((115, 455), "ZERO TO HERO • 2026", fill=(56, 189, 248))

    img.save(output_path, "PNG")

def render_thumbnail_variant_a(tool_name: str, output_path: Path, width: int = 1280, height: int = 720) -> None:
    """Style A: Bold Tech Masterclass (High contrast navy/cyan/red)."""
    bmp_path = output_path.with_suffix(".bmp")
    row_bytes = width * 3
    padding_bytes = (4 - (row_bytes % 4)) % 4
    stride = row_bytes + padding_bytes
    image_size = stride * height
    file_size = 54 + image_size

    header = bytearray(b"BM")
    header.extend(struct.pack("<I", file_size))
    header.extend(struct.pack("<H", 0))
    header.extend(struct.pack("<H", 0))
    header.extend(struct.pack("<I", 54))
    header.extend(struct.pack("<I", 40))
    header.extend(struct.pack("<i", width))
    header.extend(struct.pack("<i", height))
    header.extend(struct.pack("<H", 1))
    header.extend(struct.pack("<H", 24))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<I", image_size))
    header.extend(struct.pack("<i", 2835))
    header.extend(struct.pack("<i", 2835))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<I", 0))

    dark_bgr = bytes([25, 15, 10])
    red_bgr = bytes([68, 68, 239])
    yellow_bgr = bytes([21, 204, 250])
    cyan_bgr = bytes([248, 189, 56])
    white_bgr = bytes([255, 255, 255])
    blue_bgr = bytes([246, 130, 59])
    card_bgr = bytes([45, 30, 20])

    pixel_buffer = bytearray(image_size)
    for y in range(height):
        row_offset = y * stride
        for x in range(width):
            px = row_offset + (x * 3)
            pixel_buffer[px : px + 3] = dark_bgr

    def fill_rect(x1: int, y1: int, x2: int, y2: int, color: bytes) -> None:
        for y in range(max(0, y1), min(height, y2)):
            inv_y = (height - 1) - y
            row_offset = inv_y * stride
            for x in range(max(0, x1), min(width, x2)):
                px = row_offset + (x * 3)
                pixel_buffer[px : px + 3] = color

    def outline_rect(x1: int, y1: int, x2: int, y2: int, color: bytes, thickness: int = 4) -> None:
        fill_rect(x1, y1, x2, y1 + thickness, color)
        fill_rect(x1, y2 - thickness, x2, y2, color)
        fill_rect(x1, y1, x1 + thickness, y2, color)
        fill_rect(x2 - thickness, y1, x2, y2, color)

    fill_rect(0, 0, width, 16, red_bgr)
    outline_rect(40, 40, width - 40, height - 40, blue_bgr, thickness=4)
    fill_rect(90, 80, 420, 145, red_bgr)
    draw_text_bmp(pixel_buffer, "STEP-BY-STEP", x=115, y=98, color_bgr=white_bgr, scale=4, width=width, height=height)

    clean_tool = tool_name[:20].upper()
    draw_text_bmp(pixel_buffer, clean_tool, x=90, y=180, color_bgr=white_bgr, scale=6, width=width, height=height)
    draw_text_bmp(pixel_buffer, "FULL 2026 GUIDE", x=90, y=285, color_bgr=yellow_bgr, scale=6, width=width, height=height)

    fill_rect(90, 400, 680, 480, card_bgr)
    outline_rect(90, 400, 680, 480, cyan_bgr, thickness=3)
    draw_text_bmp(pixel_buffer, "ZERO TO HERO • COMPLETE MASTERCLASS", x=115, y=428, color_bgr=cyan_bgr, scale=3, width=width, height=height)
    draw_text_bmp(pixel_buffer, "4K ULTRA HD • 100% PRACTICAL GUIDE", x=90, y=540, color_bgr=white_bgr, scale=3, width=width, height=height)

    with open(bmp_path, "wb") as f:
        f.write(header)
        f.write(pixel_buffer)

    try:
        import subprocess
        subprocess.run(["sips", "-s", "format", "png", str(bmp_path), "--out", str(output_path)], check=True, capture_output=True)
    except Exception:
        import shutil
        shutil.copy(bmp_path, output_path)

def render_thumbnail_variant_b(tool_name: str, output_path: Path, width: int = 1280, height: int = 720) -> None:
    """Style B: Minimalist Pro (Slate gray with emerald green badge)."""
    bmp_path = output_path.with_suffix(".bmp")
    row_bytes = width * 3
    padding_bytes = (4 - (row_bytes % 4)) % 4
    stride = row_bytes + padding_bytes
    image_size = stride * height
    file_size = 54 + image_size

    header = bytearray(b"BM")
    header.extend(struct.pack("<I", file_size))
    header.extend(struct.pack("<H", 0))
    header.extend(struct.pack("<H", 0))
    header.extend(struct.pack("<I", 54))
    header.extend(struct.pack("<I", 40))
    header.extend(struct.pack("<i", width))
    header.extend(struct.pack("<i", height))
    header.extend(struct.pack("<H", 1))
    header.extend(struct.pack("<H", 24))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<I", image_size))
    header.extend(struct.pack("<i", 2835))
    header.extend(struct.pack("<i", 2835))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<I", 0))

    slate_bgr = bytes([35, 25, 20])
    emerald_bgr = bytes([129, 185, 16])
    white_bgr = bytes([255, 255, 255])
    gold_bgr = bytes([50, 215, 250])

    pixel_buffer = bytearray(image_size)
    for y in range(height):
        row_offset = y * stride
        for x in range(width):
            px = row_offset + (x * 3)
            pixel_buffer[px : px + 3] = slate_bgr

    def fill_rect(x1: int, y1: int, x2: int, y2: int, color: bytes) -> None:
        for y in range(max(0, y1), min(height, y2)):
            inv_y = (height - 1) - y
            row_offset = inv_y * stride
            for x in range(max(0, x1), min(width, x2)):
                px = row_offset + (x * 3)
                pixel_buffer[px : px + 3] = color

    fill_rect(0, 0, width, 18, emerald_bgr)
    fill_rect(90, 90, 480, 150, emerald_bgr)
    draw_text_bmp(pixel_buffer, "PRO WORKFLOW • 2026", x=115, y=108, color_bgr=white_bgr, scale=4, width=width, height=height)

    clean_tool = tool_name[:20].upper()
    draw_text_bmp(pixel_buffer, clean_tool, x=90, y=190, color_bgr=white_bgr, scale=6, width=width, height=height)
    draw_text_bmp(pixel_buffer, "TACTICAL DEEP DIVE", x=90, y=295, color_bgr=gold_bgr, scale=5, width=width, height=height)
    draw_text_bmp(pixel_buffer, "SAVE 10+ HOURS WEEKLY • ZERO TO HERO", x=90, y=430, color_bgr=white_bgr, scale=3, width=width, height=height)

    with open(bmp_path, "wb") as f:
        f.write(header)
        f.write(pixel_buffer)

    try:
        import subprocess
        subprocess.run(["sips", "-s", "format", "png", str(bmp_path), "--out", str(output_path)], check=True, capture_output=True)
    except Exception:
        import shutil
        shutil.copy(bmp_path, output_path)

def render_thumbnail_variant_c(tool_name: str, output_path: Path, width: int = 1280, height: int = 720) -> None:
    """Style C: Viral High-Contrast Urgent (Bright warning yellow/red for max mobile CTR)."""
    bmp_path = output_path.with_suffix(".bmp")
    row_bytes = width * 3
    padding_bytes = (4 - (row_bytes % 4)) % 4
    stride = row_bytes + padding_bytes
    image_size = stride * height
    file_size = 54 + image_size

    header = bytearray(b"BM")
    header.extend(struct.pack("<I", file_size))
    header.extend(struct.pack("<H", 0))
    header.extend(struct.pack("<H", 0))
    header.extend(struct.pack("<I", 54))
    header.extend(struct.pack("<I", 40))
    header.extend(struct.pack("<i", width))
    header.extend(struct.pack("<i", height))
    header.extend(struct.pack("<H", 1))
    header.extend(struct.pack("<H", 24))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<I", image_size))
    header.extend(struct.pack("<i", 2835))
    header.extend(struct.pack("<i", 2835))
    header.extend(struct.pack("<I", 0))
    header.extend(struct.pack("<I", 0))

    pure_black = bytes([10, 10, 10])
    bright_yellow = bytes([0, 235, 255])
    bright_red = bytes([30, 30, 240])
    white_bgr = bytes([255, 255, 255])

    pixel_buffer = bytearray(image_size)
    for y in range(height):
        row_offset = y * stride
        for x in range(width):
            px = row_offset + (x * 3)
            pixel_buffer[px : px + 3] = pure_black

    def fill_rect(x1: int, y1: int, x2: int, y2: int, color: bytes) -> None:
        for y in range(max(0, y1), min(height, y2)):
            inv_y = (height - 1) - y
            row_offset = inv_y * stride
            for x in range(max(0, x1), min(width, x2)):
                px = row_offset + (x * 3)
                pixel_buffer[px : px + 3] = color

    fill_rect(0, 0, width, 24, bright_red)
    fill_rect(90, 80, 520, 155, bright_red)
    draw_text_bmp(pixel_buffer, "NEW 2026 UPDATE!", x=115, y=102, color_bgr=white_bgr, scale=4, width=width, height=height)

    clean_tool = tool_name[:20].upper()
    draw_text_bmp(pixel_buffer, clean_tool, x=90, y=185, color_bgr=bright_yellow, scale=6, width=width, height=height)
    draw_text_bmp(pixel_buffer, "DO THIS FIRST", x=90, y=295, color_bgr=white_bgr, scale=6, width=width, height=height)
    draw_text_bmp(pixel_buffer, "DONT MAKE THESE MISTAKES", x=90, y=430, color_bgr=bright_yellow, scale=4, width=width, height=height)

    with open(bmp_path, "wb") as f:
        f.write(header)
        f.write(pixel_buffer)

    try:
        import subprocess
        subprocess.run(["sips", "-s", "format", "png", str(bmp_path), "--out", str(output_path)], check=True, capture_output=True)
    except Exception:
        import shutil
        shutil.copy(bmp_path, output_path)

def render_thumbnail_bmp(tool_name: str, output_path: Path, width: int = 1280, height: int = 720) -> None:
    """Default fallback calling Variant A."""
    render_thumbnail_variant_a(tool_name, output_path, width, height)

def generate_metadata_and_thumbnail(
    project_id: str,
    script_data: Optional[Dict[str, Any]] = None,
    timing_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generates SEO-optimized title, description with chapters, tags, and thumbnail.
    
    Args:
        project_id: Unique project identifier.
        script_data: Optional script dictionary.
        timing_data: Optional audio timing dictionary.
        
    Returns:
        Metadata results dictionary.
    """
    settings.ensure_directories()

    # 1. Load data from disk if not provided
    if not script_data:
        script_path = settings.SCRIPTS_DIR / f"{project_id}_script.json"
        if script_path.exists():
            with open(script_path, "r", encoding="utf-8") as f:
                script_data = json.load(f)
        else:
            raise FileNotFoundError(f"Script data not found for project {project_id}")

    if not timing_data:
        timing_path = settings.AUDIO_DIR / project_id / "timing.json"
        if timing_path.exists():
            with open(timing_path, "r", encoding="utf-8") as f:
                timing_data = json.load(f)
        else:
            raise FileNotFoundError(f"Timing data not found for project {project_id}")

    tool_name = script_data.get("tool_name", "AI Tool")
    timing_sections = timing_data.get("sections", [])

    logger.info(f"Generating SEO metadata and thumbnail for '{tool_name}' (Project {project_id})...")

    # 2. Build Chapter Markers
    chapters = []
    for s in timing_sections:
        title = s.get("title", f"Section {s.get('section_id', 1)}")
        start_sec = s.get("start_time_sec", 0.0)
        formatted_stamp = format_chapter_timestamp(start_sec)
        chapters.append({
            "title": title,
            "timestamp_seconds": start_sec,
            "timestamp_formatted": formatted_stamp
        })

    # Ensure 00:00 chapter exists for YouTube chapter indexing
    if not chapters or chapters[0]["timestamp_formatted"] != "00:00":
        chapters.insert(0, {
            "title": f"Introduction to {tool_name}",
            "timestamp_seconds": 0.0,
            "timestamp_formatted": "00:00"
        })

    # 3. High-CTR SEO Title (< 70 characters)
    if script_data.get("suggested_title"):
        title = script_data["suggested_title"]
        if len(title) > 68:
            title = f"{title[:65]}..."
    else:
        title = f"How to Use {tool_name} (Step-by-Step 2026 Guide)"
        if len(title) > 65:
            title = f"{tool_name} Full Tutorial (Complete 2026 Guide)"

    # 4. Description with Chapters, Key Takeaways & CTA
    desc_intro = script_data.get("description_summary") or (
        f"Master {tool_name} from setup to pro workflows in this complete step-by-step 2026 guide.\n"
        f"Learn how to streamline tasks, automate complex steps, and build production-ready projects in minutes."
    )
    desc_lines = [
        desc_intro + "\n",
        "⏱️ TIMESTAMPS / CHAPTERS:",
    ]
    for ch in chapters:
        desc_lines.append(f"{ch['timestamp_formatted']} - {ch['title']}")

    desc_lines.extend([
        "\n📌 WHAT YOU'LL LEARN IN THIS VIDEO:",
        f"• How to set up and configure {tool_name} for maximum efficiency",
        "• The core prompting and execution framework",
        "• Advanced power-user shortcuts and multi-file automation",
        "• Common pitfalls, rate limits, and mistakes to avoid",
        "• Real-world monetization strategies and client workflows",
        "\n🔔 If you found this tutorial valuable, please LIKE the video and SUBSCRIBE for weekly AI deep-dives!",
        "💬 What project are you building with this tool? Drop your thoughts in the comments below!\n",
        "#AITools #ArtificialIntelligence #Tutorial #Productivity #TechGuide"
    ])
    full_description = "\n".join(desc_lines)

    # 5. Search Tags
    tags = [
        tool_name,
        f"{tool_name} tutorial",
        f"how to use {tool_name}",
        f"{tool_name} guide",
        f"{tool_name} 2026",
        "ai tools 2026",
        "artificial intelligence",
        "ai productivity",
        "best ai tools",
        "step by step tutorial",
        "workflow automation",
        "tech explainer"
    ]

    metadata_payload = {
        "project_id": project_id,
        "tool_name": tool_name,
        "title": title,
        "description": full_description,
        "tags": tags[:15],
        "category_id": settings.YOUTUBE_CATEGORY_ID,
        "privacy_status": settings.YOUTUBE_DEFAULT_PRIVACY,
        "ai_disclosure": settings.YOUTUBE_AI_DISCLOSURE,
        "chapters": chapters
    }

    # 6. Generate 3 distinct 1280x720 Thumbnail Image variations for A/B testing
    thumbnail_path = settings.THUMBNAILS_DIR / f"{project_id}_thumbnail.png"
    thumb_a = settings.THUMBNAILS_DIR / f"{project_id}_thumb_A.png"
    thumb_b = settings.THUMBNAILS_DIR / f"{project_id}_thumb_B.png"
    thumb_c = settings.THUMBNAILS_DIR / f"{project_id}_thumb_C.png"

    # Render Variation A (Bold Tech Masterclass)
    render_thumbnail_variant_a(tool_name, thumb_a)
    # Render Variation B (Minimalist Pro)
    render_thumbnail_variant_b(tool_name, thumb_b)
    # Render Variation C (Viral High-Contrast)
    render_thumbnail_variant_c(tool_name, thumb_c)

    # Set default active thumbnail to Variation A
    import shutil
    shutil.copy(thumb_a, thumbnail_path)

    metadata_payload["thumbnail_variations"] = {
        "A": {"name": "Bold Tech Masterclass", "file": thumb_a.name, "path": str(thumb_a)},
        "B": {"name": "Minimalist Pro", "file": thumb_b.name, "path": str(thumb_b)},
        "C": {"name": "Viral High-Contrast", "file": thumb_c.name, "path": str(thumb_c)}
    }

    # Save JSON metadata with variations
    metadata_json_path = settings.METADATA_DIR / f"{project_id}_metadata.json"
    with open(metadata_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)

    logger.info(f"Saved metadata to {metadata_json_path}")
    logger.info(f"Generated 3 thumbnail A/B variations: {thumb_a.name}, {thumb_b.name}, {thumb_c.name}")

    return {
        "project_id": project_id,
        "title": title,
        "metadata_json_path": str(metadata_json_path),
        "thumbnail_path": str(thumbnail_path),
        "thumbnail_variations": metadata_payload["thumbnail_variations"],
        "chapters_count": len(chapters)
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stage 6: Metadata & Thumbnail")
    parser.add_argument("--project-id", type=str, help="Project ID")
    args = parser.parse_args()

    project_id = args.project_id
    if not project_id:
        candidate_dirs = [
            d for d in settings.AUDIO_DIR.iterdir()
            if d.is_dir() and (d / "timing.json").exists()
        ]
        if candidate_dirs:
            project_id = sorted(candidate_dirs)[-1].name
        else:
            logger.error("No valid project audio directory found. Run stages 1-3 first.")
            sys.exit(1)

    res = generate_metadata_and_thumbnail(project_id)
    print("\n--- Metadata & Thumbnail Generated ---")
    print(f"Project ID:    {res['project_id']}")
    print(f"Title:         {res['title']}")
    print(f"Metadata JSON: {res['metadata_json_path']}")
    print(f"Thumbnail:     {res['thumbnail_path']}")
    print(f"Chapters:      {res['chapters_count']}")

if __name__ == "__main__":
    main()
