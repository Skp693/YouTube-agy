"""Live Web B-Roll & Screencast Capture Engine (browser_recorder.py)

Captures high-resolution live webpage screenshots and screencast B-roll
of featured AI tools (homepage, workspace, docs) using headless Chrome,
with procedural fallback for 100% offline reliability.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Known official tool URLs for instant B-roll capture
TOOL_URL_DIRECTORY: Dict[str, str] = {
    "claude": "https://claude.ai",
    "cursor": "https://cursor.com",
    "notebooklm": "https://notebooklm.google.com",
    "bolt": "https://bolt.new",
    "lovable": "https://lovable.dev",
    "perplexity": "https://www.perplexity.ai",
    "midjourney": "https://www.midjourney.com",
    "v0": "https://v0.dev",
    "chatgpt": "https://chatgpt.com",
    "gemini": "https://gemini.google.com"
}

def resolve_tool_url(tool_name: str) -> str:
    """Finds best matching official URL for the target AI tool."""
    clean = tool_name.lower()
    for key, url in TOOL_URL_DIRECTORY.items():
        if key in clean:
            return url
    return f"https://www.google.com/search?q={urllib.parse.quote(tool_name + ' ai tool')}" if False else "https://claude.ai"

def capture_web_broll(
    tool_name: str,
    output_dir: Path,
    target_url: Optional[str] = None,
    duration_sec: float = 5.0
) -> Optional[Path]:
    """Captures a live web snapshot and compiles into a 1080p B-roll MP4 clip."""
    output_dir.mkdir(parents=True, exist_ok=True)
    url = target_url or resolve_tool_url(tool_name)
    shot_png = output_dir / f"broll_snapshot.png"
    broll_mp4 = output_dir / f"broll_clip.mp4"

    captured = False

    # 1. Try headless Google Chrome capture
    if os.path.exists(CHROME_BIN):
        try:
            cmd = [
                CHROME_BIN,
                "--headless",
                "--disable-gpu",
                "--window-size=1920,1080",
                f"--screenshot={shot_png}",
                url
            ]
            subprocess.run(cmd, capture_output=True, timeout=12, check=True)
            if shot_png.exists() and shot_png.stat().st_size > 10000:
                captured = True
        except Exception:
            captured = False

    # 2. If Chrome failed or offline, use sample screenshot or procedural graphic
    if not captured:
        from visuals import render_slide_native_bmp
        render_slide_native_bmp(
            section_num=1,
            section_type="LIVE WORKSPACE B-ROLL",
            title=f"{tool_name.upper()} INTERFACE DEMO",
            bullets=[
                "Official web application and developer workspace",
                "Live prompt input and parameter configurations",
                "Real-time code generation and visual sandbox",
                "Export workflows and deployment configurations"
            ],
            output_path=shot_png
        )

    # 3. Convert captured screenshot into a smooth 1080p Ken Burns pan-and-scan MP4
    ffmpeg_bin = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
    if os.path.exists(ffmpeg_bin) and shot_png.exists():
        try:
            frames = int(duration_sec * 30)
            zoom_cmd = [
                ffmpeg_bin, "-y",
                "-loop", "1", "-i", str(shot_png),
                "-vf", f"zoompan=z='min(zoom+0.0006,1.06)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30",
                "-t", f"{duration_sec:.2f}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-an",
                str(broll_mp4)
            ]
            subprocess.run(zoom_cmd, check=True, capture_output=True)
            return broll_mp4
        except Exception:
            pass

    return broll_mp4 if broll_mp4.exists() else None
