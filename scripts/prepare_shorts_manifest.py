"""Prepare a review-only Shorts manifest from EXISTING approved narration and visuals.

No Google Flow login or credits, no fake voice, no inferred captions, no uploads.
The proposed equal-duration scene timing is NOT word alignment or lip-sync proof.
"""
from __future__ import annotations
import argparse
import json
import math
import subprocess
from pathlib import Path

STILL_EXT = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".m4v"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac"}


def probe_audio_duration(path: Path) -> float:
    """Require a real audio stream, plus video frames when passed a video."""
    proc = subprocess.run([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(path)
    ], capture_output=True, text=True, check=True, timeout=30)
    info = json.loads(proc.stdout)
    kinds = {stream.get("codec_type") for stream in info.get("streams", [])}
    if "audio" not in kinds:
        raise ValueError("Narration file has no real audio track")
    if path.suffix.lower() in VIDEO_EXT and "video" not in kinds:
        raise ValueError("Presenter narration video must contain video frames")
    duration = float(info.get("format", {}).get("duration") or 0)
    if not math.isfinite(duration):
        raise ValueError("Narration duration must be finite")
    return duration


def plan(topic, narration: Path, assets, *, brand="QUADDIS", verified_nontalking_video=False):
    """Create a complete deterministic timeline; human-supplied scene labels."""
    topic = str(topic).strip()
    if not topic or len(topic) > 160:
        raise ValueError("Topic is required (maximum 160 characters)")
    narration = Path(narration).expanduser().resolve()
    if not narration.is_file():
        raise FileNotFoundError(f"Missing approved narration: {narration}")
    if narration.suffix.lower() not in VIDEO_EXT | AUDIO_EXT:
        raise ValueError("Narration must be a video or audio file")
    has_video = narration.suffix.lower() in VIDEO_EXT
    if not assets or len(assets) > (10 if has_video else 12):
        raise ValueError("Provide 1–10 visual assets for video narration or 1–12 for audio")
    if not has_video and len(assets) < 2:
        raise ValueError("Audio-only narration requires at least two visual scenes")
    checked = []
    for media, label, mode in assets:
        media = Path(media).expanduser().resolve()
        label = str(label).strip()
        if not media.is_file():
            raise FileNotFoundError(f"Missing visual asset: {media}")
        if not label or len(label) > 72:
            raise ValueError("Every visual needs a real topic-specific label (1–72 characters)")
        if mode not in ("broll", "pip_still"):
            raise ValueError("Visual mode must be broll or pip_still")
        ext = media.suffix.lower()
        if ext not in STILL_EXT | VIDEO_EXT:
            raise ValueError("Visual asset must be an image or video")
        if mode == "pip_still" and ext not in STILL_EXT:
            raise ValueError("PIP still mode requires a still picture")
        if ext in VIDEO_EXT and not verified_nontalking_video:
            raise ValueError("Moving B-roll requires explicit non-speaking-faces verification")
        checked.append((media, label, mode))

    duration = round(probe_audio_duration(narration), 3)
    if not 8 <= duration <= 60:
        raise ValueError("Approved narration must be between 8 and 60 seconds")

    # Strict millisecond arithmetic avoids gaps/overlaps in the source manifest.
    total_ms = round(duration * 1000)
    intro = round(total_ms * .15) if has_video else 0
    outro = round(total_ms * .12) if has_video else 0
    remaining = total_ms - intro - outro
    if remaining < len(checked) * 110:
        raise ValueError("Narration too short for the number of visual scenes")
    segments = []
    if has_video:
        segments.append((intro, narration, topic[:72], "presenter_native"))
    quotient, extra = divmod(remaining, len(checked))
    for i, (media, label, mode) in enumerate(checked):
        segments.append((quotient + (i < extra), media, label, mode))
    if has_video:
        segments.append((outro, narration, "Review before sharing", "presenter_native"))

    cursor = 0
    scenes = []
    for ms, media, label, mode in segments:
        scene = {
            "start": cursor/1000, "end": (cursor+ms)/1000,
            "media": str(media), "mode": mode, "label": label
        }
        if mode == "broll" and media.suffix.lower() in VIDEO_EXT:
            scene["no_visible_speaking_faces"] = True
        if mode == "presenter_native":
            scene["media_seek"] = cursor/1000
        scenes.append(scene)
        cursor += ms
    assert cursor == total_ms
    return {
        "topic": topic, "brand": str(brand).strip()[:45] or "QUADDIS",
        "narration_source_video" if has_video else "narration_audio": str(narration),
        "scenes": scenes, "captions": [], "review_only": True,
        "production_warning": (
            "Scene timings are an evenly spaced draft, NOT synchronized to words. "
            "Real captions, natural voice, truthful topic graphics and lip-sync require review."
        )
    }


def write_manifest(doc, output: Path) -> Path:
    output = Path(output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_symlink() or output.exists():
        raise FileExistsError("Manifest exists. Choose a new output file; never overwrite approved work")
    with output.open("x", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return output


def parse_asset(value):
    parts = value.rsplit("::", 2)
    if len(parts) == 2:
        return Path(parts[0]), parts[1], "broll"
    if len(parts) == 3:
        return Path(parts[0]), parts[1], parts[2]
    raise argparse.ArgumentTypeError("Use PATH::LABEL or PATH::LABEL::broll/pip_still")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--narration", type=Path, required=True)
    parser.add_argument("--asset", type=parse_asset, action="append", required=True,
                        help="PATH::TOPIC LABEL::broll or PATH::TOPIC LABEL::pip_still")
    parser.add_argument("--output", type=Path, default=Path("docs/narration_first_manifest.json"))
    parser.add_argument("--brand", default="QUADDIS")
    parser.add_argument("--verified-nontalking-video", action="store_true",
                        help="Only after visually checking all moving B-roll has no talking faces")
    args = parser.parse_args()
    doc = plan(args.topic, args.narration, args.asset, brand=args.brand,
               verified_nontalking_video=args.verified_nontalking_video)
    path = write_manifest(doc, args.output)
    print(json.dumps({
        "manifest": str(path), "duration": doc["scenes"][-1]["end"],
        "scenes": len(doc["scenes"]), "review_only": True,
        "warning": doc["production_warning"]
    }, indent=2))


if __name__ == "__main__":
    main()
