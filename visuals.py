"""Stage 4: Visuals & Slide Generation (visuals.py)

Breaks the educational script into logical scenes and generates clean, consistent
educational images/diagrams for each scene using Gemini/Imagen or a built-in
1920x1080 educational slide graphics engine.
Creates a scene timeline JSON and saves numbered images in images/.
"""

import os
import sys
import json
import time
import struct
import zlib
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, List

from config.settings import settings
from config.logging_config import setup_logger
from src.utils.bitmap_font import draw_text_bmp

logger = setup_logger("visuals")

# Check for PIL
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def generate_with_imagen(prompt: str, output_path: Path) -> bool:
    """Calls Google Imagen 3 API via Gemini generateImages endpoint if configured."""
    api_key = settings.IMAGEN_API_KEY or settings.GEMINI_API_KEY
    if not api_key:
        return False

    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9",
            "outputOptions": {"mimeType": "image/png"}
        }
    }

    try:
        import base64
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            b64_img = res_json["predictions"][0]["bytesBase64Encoded"]
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(b64_img))
            return True
    except Exception as e:
        logger.warning(f"Imagen API call failed ({e}). Reverting to built-in slide engine.")
        return False

def render_slide_with_pil(
    section_num: int,
    section_type: str,
    title: str,
    bullets: List[str],
    output_path: Path,
    width: int = 1920,
    height: int = 1080
) -> None:
    """Renders high-res 1080p presentation slide with Pillow."""
    img = Image.new("RGB", (width, height), color=(15, 23, 42))  # Dark Slate 900
    draw = ImageDraw.Draw(img)

    # Top accent bar (Cyan & Blue)
    draw.rectangle([0, 0, width, 14], fill=(56, 189, 248))

    # Outer decorative frame
    draw.rectangle([60, 60, width - 60, height - 60], outline=(30, 41, 59), width=2)

    # Category Pill Badge
    badge_text = f"SECTION {section_num:02d}  •  {section_type.upper()}"
    draw.rectangle([100, 100, 440, 150], fill=(30, 41, 59), outline=(56, 189, 248), width=2)
    draw.text((120, 115), badge_text, fill=(56, 189, 248))

    # Main Slide Title
    clean_title = title[:75]
    draw.text((100, 180), clean_title, fill=(248, 250, 252))

    # Horizontal accent divider
    draw.line([(100, 240), (550, 240)], fill=(99, 102, 241), width=4)

    # Content checklist cards
    y = 310
    for b in bullets:
        # Card box
        draw.rectangle([100, y, width - 120, y + 80], fill=(24, 33, 54), outline=(51, 65, 85), width=1)
        # Checkmark icon badge
        draw.rectangle([120, y + 20, 160, y + 60], fill=(16, 185, 129))
        draw.text((135, y + 28), "✔", fill=(255, 255, 255))
        # Text
        draw.text((180, y + 28), b[:90], fill=(226, 232, 240))
        y += 105

    # Footer Branding
    footer = "AI TOOL EXPLAINER • AUTONOMOUS VIDEO PIPELINE 2026"
    draw.text((100, height - 120), footer, fill=(100, 116, 139))

    img.save(output_path, "PNG")

def render_slide_native_bmp(
    section_num: int,
    section_type: str,
    title: str,
    bullets: List[str],
    output_path: Path,
    width: int = 1920,
    height: int = 1080,
    tool_name: str = "AI TOOL EXPLAINER"
) -> None:
    """Renders 1080p slide image with rasterized typography using pure standard library."""
    bmp_path = output_path.with_suffix(".bmp")

    # 24-bit uncompressed BMP: row size must be multiple of 4 bytes
    row_bytes = width * 3
    padding_bytes = (4 - (row_bytes % 4)) % 4
    stride = row_bytes + padding_bytes
    image_size = stride * height
    file_size = 54 + image_size

    # BMP Header (14 bytes) + DIB Header (40 bytes)
    header = bytearray()
    header.extend(b"BM")
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

    # Color Palette in BGR
    bg_bgr = bytes([30, 20, 15])         # Dark slate
    card_bgr = bytes([48, 30, 22])       # Card navy
    cyan_bgr = bytes([248, 189, 56])     # Cyan accent
    white_bgr = bytes([252, 250, 248])   # White
    text_bgr = bytes([226, 213, 203])    # Light slate
    muted_bgr = bytes([139, 116, 100])   # Muted gray
    border_bgr = bytes([75, 55, 40])     # Border slate
    green_bgr = bytes([129, 185, 16])    # Green check

    # Initialize pixel buffer
    pixel_buffer = bytearray(image_size)

    # 1. Fill base background color
    for y in range(height):
        row_offset = y * stride
        for x in range(width):
            px = row_offset + (x * 3)
            pixel_buffer[px : px + 3] = bg_bgr

    # Helper to draw filled rectangle (screen coordinates: 0,0 is top-left)
    def fill_rect(x1: int, y1: int, x2: int, y2: int, color: bytes) -> None:
        for y in range(max(0, y1), min(height, y2)):
            inv_y = (height - 1) - y
            row_offset = inv_y * stride
            for x in range(max(0, x1), min(width, x2)):
                px = row_offset + (x * 3)
                pixel_buffer[px : px + 3] = color

    # Helper to draw rect outline
    def outline_rect(x1: int, y1: int, x2: int, y2: int, color: bytes, thickness: int = 2) -> None:
        fill_rect(x1, y1, x2, y1 + thickness, color)             # Top
        fill_rect(x1, y2 - thickness, x2, y2, color)             # Bottom
        fill_rect(x1, y1, x1 + thickness, y2, color)             # Left
        fill_rect(x2 - thickness, y1, x2, y2, color)             # Right

    # 2. Top accent stripe (Cyan)
    fill_rect(0, 0, width, 14, cyan_bgr)

    # 3. Outer boundary frame
    outline_rect(60, 60, width - 60, height - 60, border_bgr, thickness=2)

    # 4. Section Badge Box & Text
    outline_rect(100, 95, 480, 150, cyan_bgr, thickness=2)
    fill_rect(102, 97, 478, 148, card_bgr)
    badge_label = f"SECTION {section_num:02d} • {section_type.upper()}"
    draw_text_bmp(pixel_buffer, badge_label, x=120, y=112, color_bgr=cyan_bgr, scale=3, width=width, height=height)

    # 5. Slide Title (Large bold white typography)
    clean_title = title[:50].upper()
    draw_text_bmp(pixel_buffer, clean_title, x=100, y=180, color_bgr=white_bgr, scale=4, width=width, height=height)

    # 6. Horizontal accent line under title
    fill_rect(100, 240, 650, 244, cyan_bgr)

    # 7. Checklist Cards & Content Text
    card_y = 295
    for b in bullets[:4]:
        # Card box
        fill_rect(100, card_y, width - 120, card_y + 80, card_bgr)
        outline_rect(100, card_y, width - 120, card_y + 80, border_bgr, thickness=1)
        # Green icon box
        fill_rect(125, card_y + 18, 165, card_y + 58, green_bgr)
        draw_text_bmp(pixel_buffer, "✔", x=137, y=card_y + 26, color_bgr=white_bgr, scale=2, width=width, height=height)
        # Bullet text (scale=3)
        bullet_clean = b[:60].upper()
        draw_text_bmp(pixel_buffer, bullet_clean, x=185, y=card_y + 26, color_bgr=text_bgr, scale=3, width=width, height=height)
        card_y += 105

    # 8. Footer Branding
    footer = f"{tool_name[:32].upper()} • AUTONOMOUS VIDEO PIPELINE 2026"
    draw_text_bmp(pixel_buffer, footer, x=100, y=height - 120, color_bgr=muted_bgr, scale=2, width=width, height=height)

    # Write BMP file
    with open(bmp_path, "wb") as f:
        f.write(header)
        f.write(pixel_buffer)

    # Convert to PNG using macOS sips if available
    try:
        import subprocess
        subprocess.run(["sips", "-s", "format", "png", str(bmp_path), "--out", str(output_path)], check=True, capture_output=True)
    except Exception:
        import shutil
        shutil.copy(bmp_path, output_path)

def generate_visuals(
    script_data: Dict[str, Any],
    timing_data: Optional[Dict[str, Any]] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """Generates visual graphics and scenes timeline for all script sections.
    
    Args:
        script_data: Script dictionary containing sections.
        timing_data: Optional audio timing dictionary.
        project_id: Optional project identifier.
        
    Returns:
        Dictionary containing scenes timeline and generated image paths.
    """
    settings.ensure_directories()
    project_id = project_id or script_data.get("topic_id") or datetime.now().strftime("%Y%m%d_%H%M%S")
    project_img_dir = settings.IMAGES_DIR / project_id
    project_img_dir.mkdir(parents=True, exist_ok=True)

    sections = script_data.get("sections", [])
    logger.info(f"Generating 1080p visual assets for {len(sections)} scenes (Project: {project_id})...")

    # Map timing records if available
    durations_map = {}
    if timing_data and "sections" in timing_data:
        for t in timing_data["sections"]:
            durations_map[t.get("section_id")] = t.get("duration_sec", 30.0)

    scenes_timeline: List[Dict[str, Any]] = []

    for sec in sections:
        sec_id = sec.get("id", 1)
        sec_type = sec.get("section_type", "step")
        title = sec.get("title", f"Section {sec_id}")
        bullets = sec.get("on_screen_text", [title])
        img_prompt = sec.get("image_prompt", f"Modern explainer slide for {title}")
        duration = durations_map.get(sec_id, sec.get("duration_estimate_sec", 30.0))

        output_img_path = project_img_dir / f"scene_{sec_id:02d}.png"

        # 1. Try Imagen if configured
        generated_by_imagen = False
        if settings.IMAGE_PROVIDER == "imagen":
            generated_by_imagen = generate_with_imagen(img_prompt, output_img_path)

        # 2. Render crisp educational slide
        if not generated_by_imagen:
            tool_name = script_data.get("tool_name", "AI Tool")
            if HAS_PIL:
                render_slide_with_pil(sec_id, sec_type, title, bullets, output_img_path)
            else:
                render_slide_native_bmp(sec_id, sec_type, title, bullets, output_img_path, tool_name=tool_name)

        scenes_timeline.append({
            "scene_id": sec_id,
            "section_type": sec_type,
            "title": title,
            "image_path": str(output_img_path),
            "duration_sec": duration,
            "prompt": img_prompt,
            "bullets": bullets
        })

        logger.info(f"Scene {sec_id:02d} rendered ({duration:.2f}s) -> {output_img_path.name}")

    # Save scenes_timeline.json
    timeline_path = project_img_dir / "scenes_timeline.json"
    timeline_data = {
        "project_id": project_id,
        "tool_name": script_data.get("tool_name", "AI Tool"),
        "total_scenes": len(scenes_timeline),
        "scenes": scenes_timeline
    }

    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2)

    logger.info(f"Saved scene timeline JSON to {timeline_path}")

    return {
        "project_id": project_id,
        "timeline_json_path": str(timeline_path),
        "total_scenes": len(scenes_timeline),
        "scenes": scenes_timeline
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4: Visuals")
    parser.add_argument("--script-file", type=str, help="Path to script JSON file")
    args = parser.parse_args()

    script_data = {}
    if args.script_file:
        with open(args.script_file, "r", encoding="utf-8") as f:
            script_data = json.load(f)
    else:
        # Load most recent script in scripts/
        script_files = sorted(settings.SCRIPTS_DIR.glob("*_script.json"))
        if script_files:
            with open(script_files[-1], "r", encoding="utf-8") as f:
                script_data = json.load(f)
        else:
            logger.error("No script files found in scripts/. Run script_writer.py first.")
            sys.exit(1)

    # Look for matching timing.json
    timing_data = None
    timing_file = settings.AUDIO_DIR / script_data.get("topic_id", "") / "timing.json"
    if timing_file.exists():
        with open(timing_file, "r", encoding="utf-8") as f:
            timing_data = json.load(f)

    res = generate_visuals(script_data, timing_data)
    print("\n--- Visuals Generated ---")
    print(f"Project ID:    {res['project_id']}")
    print(f"Total Scenes:  {res['total_scenes']}")
    print(f"Timeline JSON: {res['timeline_json_path']}")

if __name__ == "__main__":
    main()
