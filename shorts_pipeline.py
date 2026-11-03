"""Local-only, fail-closed YouTube Shorts scene composer.

This is an ASSET COMPOSER, not a lip-sync or text-to-speech generator.
Presenter scenes use the original speaking clip audio, avoiding falsely
synchronizing unrelated narration with a moving face.

    python3 shorts_pipeline.py --manifest examples/shorts_manifest.json

Requires FFmpeg and FFprobe, and source media with permission to use.
Never calls an external video API or publishes to YouTube.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class ShortSpecError(ValueError):
    """A manifest or media file fails the production safety checks."""


def _require_file(value: Any, field: str, base: Path) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ShortSpecError(f"{field} path required")
    target = (base / value).expanduser().resolve()
    if not target.is_file():
        raise ShortSpecError(f"{field} file not found: {target}")
    return target


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Validate portable scene definitions before any media work starts."""
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ShortSpecError(f"manifest file not found: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise ShortSpecError(f"invalid manifest JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ShortSpecError("manifest must be a JSON object")
    scenes = manifest.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ShortSpecError("scenes must be a nonempty array")
    base = path.parent
    resolved = []
    total = 0.0
    for index, scene in enumerate(scenes, 1):
        if not isinstance(scene, dict):
            raise ShortSpecError(f"scene {index} must be an object")
        kind = scene.get("type")
        if kind not in {"presenter_pip", "presenter_full", "broll"}:
            raise ShortSpecError(f"scene {index} invalid type: {kind!r}")
        try:
            seconds = float(scene.get("seconds"))
        except (ValueError, TypeError) as exc:
            raise ShortSpecError(f"scene {index} seconds must be numeric") from exc
        if not math.isfinite(seconds) or seconds <= 0:
            raise ShortSpecError(f"scene {index} seconds must be positive")
        total += seconds
        if total > 60.0:
            raise ShortSpecError("Short duration must not exceed 60 seconds in this quality-first preset")
        if kind == "broll" and not scene.get("narration"):
            raise ShortSpecError(f"scene {index} narration path required")
        video = _require_file(scene.get("video"), f"scene {index} video", base)
        data: dict[str, Any] = {"type": kind, "seconds": seconds, "video": video}
        if kind == "broll":
            data["narration"] = _require_file(scene.get("narration"), f"scene {index} narration", base)
        if kind == "presenter_pip":
            data["background"] = _require_file(scene.get("background"), f"scene {index} background", base)
        resolved.append(data)
    if total > 60.0:
        raise ShortSpecError("Short duration must not exceed 60 seconds in this quality-first preset")
    output_value = manifest.get("output", "shorts_output.mp4")
    if not isinstance(output_value, str) or not output_value.lower().endswith(".mp4"):
        raise ShortSpecError("output must be a .mp4 file path")
    output_path = (base / output_value).expanduser().resolve()
    source_files = {item[key] for item in resolved for key in ("video", "narration", "background") if key in item}
    if output_path in source_files:
        raise ShortSpecError("output must not overwrite a source media file")
    captions = manifest.get("captions")
    caption_path = _require_file(captions, "captions", base) if captions else None
    if caption_path and caption_path.suffix.lower() != ".srt":
        raise ShortSpecError("captions must use .srt subtitle format")
    return {"title": str(manifest.get("title") or "Short"), "output": output_path, "scenes": resolved,
            "captions": caption_path, "seconds": total}


def _probe(path: Path) -> dict[str, Any]:
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                                 "-of", "json", str(path)], check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, ValueError) as exc:
        raise ShortSpecError(f"could not inspect media {path}: {exc}") from exc


def _stream_duration(data: dict[str, Any], kind: str) -> float:
    stream = next((s for s in data.get("streams", []) if s.get("codec_type") == kind), None)
    if stream is None:
        return 0.0
    value = stream.get("duration") or data.get("format", {}).get("duration")
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def validate_media(manifest: dict[str, Any]) -> None:
    """Refuse fake/absent voice, silent presenter clips, and undersized narration."""
    cache: dict[Path, dict[str, Any]] = {}
    def media(path: Path) -> dict[str, Any]:
        if path not in cache:
            cache[path] = _probe(path)
        return cache[path]
    for index, scene in enumerate(manifest["scenes"], 1):
        video = media(scene["video"])
        if _stream_duration(video, "video") <= 0:
            raise ShortSpecError(f"scene {index} has no readable video")
        if scene["type"].startswith("presenter_"):
            if _stream_duration(video, "audio") < scene["seconds"] - 0.12:
                raise ShortSpecError(f"scene {index} presenter clip has missing or too-short audio; no robot/silent fallback")
            if _stream_duration(video, "video") < scene["seconds"] - 0.12:
                raise ShortSpecError(f"scene {index} presenter clip is shorter than requested")
        else:
            narration = media(scene["narration"])
            if _stream_duration(narration, "audio") < scene["seconds"] - 0.12:
                raise ShortSpecError(f"scene {index} narration audio missing or shorter than requested")
        if scene.get("background") and _stream_duration(media(scene["background"]), "video") <= 0:
            raise ShortSpecError(f"scene {index} PIP background has no readable video")


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode:
        error = completed.stderr[-1800:].strip()
        raise RuntimeError(f"FFmpeg failed: {error}")


# Crop/fill portrait without distortion. The presenter PIP remains a separate layer.
PORTRAIT = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
FACE = "scale=440:760:force_original_aspect_ratio=increase,crop=440:760,setsar=1"


def _render_scene(scene: dict[str, Any], target: Path) -> None:
    kind = scene["type"]
    duration = f"{scene['seconds']:.3f}"
    base = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    if kind == "presenter_full":
        inputs = ["-i", str(scene["video"])]
        filters = ["-vf", PORTRAIT]
        mapping = ["-map", "0:v:0", "-map", "0:a:0"]
    elif kind == "presenter_pip":
        inputs = ["-stream_loop", "-1", "-i", str(scene["background"]), "-i", str(scene["video"])]
        filters = ["-filter_complex", f"[0:v]{PORTRAIT}[bg];[1:v]{FACE}[person];[bg][person]overlay=W-w-35:H-h-340:shortest=1[v]"]
        mapping = ["-map", "[v]", "-map", "1:a:0"]
    else:  # broll with its own human/approved narration recording
        inputs = ["-stream_loop", "-1", "-i", str(scene["video"]), "-i", str(scene["narration"])]
        filters = ["-vf", PORTRAIT]
        mapping = ["-map", "0:v:0", "-map", "1:a:0"]
    output = ["-t", duration, "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
              "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
              "-ac", "2", "-movflags", "+faststart", str(target)]
    _run(base + inputs + filters + mapping + output)


def render_short(path: str | Path) -> dict[str, Any]:
    """Render a finished vertical draft; never upload and never make paid calls."""
    manifest = load_manifest(path)
    for cmd in ("ffmpeg", "ffprobe"):
        if shutil.which(cmd) is None:
            raise RuntimeError(f"{cmd} required; install locally before rendering")
    validate_media(manifest)  # Validate all scenes BEFORE creating output.
    output = manifest["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="shorts_segments_") as temp:
        work = Path(temp)
        segments = []
        for number, scene in enumerate(manifest["scenes"], 1):
            segment = work / f"segment_{number:03d}.mp4"
            _render_scene(scene, segment)
            segments.append(segment)
        concat = work / "sequence.txt"
        concat.write_text("".join("file '" + str(p).replace("'", "'\\''") + "'\n" for p in segments), encoding="utf-8")
        merged = work / "merged.mp4"
        _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
              "-c", "copy", "-movflags", "+faststart", str(merged)])
        if manifest["captions"]:
            # ffmpeg libass is needed to burn the supplied, VERIFIED SRT. No fake captions generated.
            p = str(manifest["captions"]).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("[", "\\[").replace("]", "\\]")
            _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(merged),
                  "-vf", f"subtitles='{p}':force_style='Fontsize=18,Outline=2,Shadow=1,Alignment=2,MarginV=200'",
                  "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-c:a", "copy", "-movflags", "+faststart", str(output)])
        else:
            shutil.copy2(merged, output)
    final = _probe(output)
    video = next((s for s in final["streams"] if s.get("codec_type") == "video"), {})
    if (video.get("width"), video.get("height")) != (1080, 1920) or _stream_duration(final, "audio") <= 0:
        output.unlink(missing_ok=True)
        raise RuntimeError("Output quality check failed: expected 1080x1920 with sound")
    return {"output": str(output), "duration_seconds": float(final["format"]["duration"]),
            "scene_count": len(manifest["scenes"]), "size": "1080x1920", "published": False,
            "note": "Presenter scenes preserve clip audio; voice naturalness and lip sync still require human review."}


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed local Shorts composer for Flow presenter clips and B-roll")
    parser.add_argument("--manifest", required=True, help="Path to Shorts scene JSON")
    args = parser.parse_args()
    try:
        print(json.dumps(render_short(args.manifest), indent=2))
    except (ShortSpecError, RuntimeError) as exc:
        parser.exit(2, f"Short not generated: {exc}\n")


if __name__ == "__main__":
    main()
