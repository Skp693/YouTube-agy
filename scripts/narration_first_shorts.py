"""Audio-first Quaddis Shorts, for review only. No cloud/Google API required.

A single narration source drives the entire timeline. Talking-video scenes
are allowed automatically ONLY when the audio comes from that SAME source
video and the source start time matches the master timeline. Other scenes are
silent visual overlays. Captions require real supplied time-coded words; this
script never guesses what the narrator says.
"""
import argparse
import json
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path

DEFAULT_FPS = 30


def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"{args[0]} failed: {p.stderr[-1700:]}")
    return p.stdout


def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                           "-of", "json", str(path)]))


def seconds(path):
    return float(probe(path)["format"].get("duration") or 0)


def resolve(root, value):
    path = Path(value).expanduser()
    return (path if path.is_absolute() else root / path).resolve()


def validate(manifest):
    """Validate semantic inputs BEFORE FFmpeg render or upload."""
    root = manifest.parent.resolve()
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not str(data.get("topic", "")).strip():
        raise ValueError("Topic must be nonempty")
    src_video = data.get("narration_source_video")
    audio_file = data.get("narration_audio")
    if bool(src_video) == bool(audio_file):
        raise ValueError("Specify exactly one narration_source_video OR narration_audio")
    master_source = resolve(root, src_video or audio_file)
    if not master_source.is_file():
        raise FileNotFoundError(f"Missing narration source: {master_source}")
    if "audio" not in {s.get("codec_type") for s in probe(master_source)["streams"]}:
        raise ValueError("Narration source must include audio")
    total = seconds(master_source)
    if not 8 <= total <= 60:
        raise ValueError("Master narration must be between 8 and 60 seconds")
    scenes = data.get("scenes", [])
    if not 2 <= len(scenes) <= 12:
        raise ValueError("Supply 2 to 12 scenes")
    cursor = 0.0
    for i, scene in enumerate(scenes):
        start = float(scene["start"])
        end = float(scene["end"])
        if abs(start-cursor) > 0.025 or end <= start + 0.1:
            raise ValueError(f"Scene {i} must be positive and contiguous from {cursor:.2f}")
        cursor = end
        if not str(scene.get("label", "")).strip():
            raise ValueError(f"Scene {i} needs a topic-relevant label")
        media = resolve(root, scene["media"])
        if not media.is_file():
            raise FileNotFoundError(f"Scene {i} media missing: {media}")
        mode = scene.get("mode", "broll")
        if mode not in ("broll", "presenter_native", "pip_still"):
            raise ValueError("Mode must be broll, presenter_native or pip_still")
        if mode == "broll" and media.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            if scene.get("no_visible_speaking_faces") is not True:
                raise ValueError("Moving B-roll needs no_visible_speaking_faces=true: otherwise mouth sync can be wrong")
        if mode == "presenter_native":
            if not src_video or media != master_source:
                raise ValueError("Talking presenter requires the same original narration source video")
            if abs(float(scene.get("media_seek", start))-start) > 0.01:
                raise ValueError("Talking presenter source timeline must match master audio")
        if mode == "pip_still" and media.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            raise ValueError("PIP still must use a non-talking reference portrait")
    if abs(cursor-total) > 0.20:
        raise ValueError(f"Scenes must cover master audio exactly; end={cursor:.2f}, audio={total:.2f}")
    cues = data.get("captions", [])
    prev_end = 0
    for i, cue in enumerate(cues):
        start, end = float(cue["start"]), float(cue["end"])
        if start < prev_end-0.005 or end <= start or end > total + 0.02:
            raise ValueError(f"Caption cue {i} is overlapping or outside audio")
        if not str(cue.get("text", "")).strip():
            raise ValueError(f"Caption cue {i} cannot be empty")
        prev_end = end
    return data, master_source, total


def srtstamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms//3600000:02}:{(ms//60000)%60:02}:{(ms//1000)%60:02},{ms%1000:03}"


def create_srt(cues, path):
    path.write_text("\n\n".join(
        f"{i}\n{srtstamp(float(c['start']))} --> {srtstamp(float(c['end']))}\n{c['text']}"
        for i, c in enumerate(cues, 1)) + ("\n" if cues else ""), encoding="utf-8")


def render(manifest, output, width=720, height=1280):
    for cmd in ("ffmpeg", "ffprobe"):
        if not shutil.which(cmd):
            raise RuntimeError(f"Required executable missing: {cmd}")
    data, source, duration = validate(manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    fps = DEFAULT_FPS
    with tempfile.TemporaryDirectory(prefix="quaddis_narration_") as tmp:
        work = Path(tmp)
        parts = []
        root = manifest.parent.resolve()
        for i, scene in enumerate(data["scenes"]):
            media = resolve(root, scene["media"])
            label = work / f"label_{i}.txt"
            label.write_text(textwrap.fill(str(scene["label"])[:72], width=29), encoding="utf-8")
            brand = work / f"brand_{i}.txt"
            brand.write_text(str(data.get("brand", "QUADDIS"))[:45], encoding="utf-8")
            end = float(scene["end"])
            start = float(scene["start"])
            length = end-start
            target = work / f"part_{i:02}.mp4"
            mode = scene.get("mode", "broll")
            title_filter = f"drawtext=textfile='{label}':fontsize={int(width*.052)}:fontcolor=white:x=40:y=66:box=1:boxcolor=black@0.6:boxborderw=18"
            brand_filter = f"drawtext=textfile='{brand}':fontsize={int(width*.032)}:fontcolor=white:x=40:y=160:box=1:boxcolor=black@0.55:boxborderw=12"
            if mode == "pip_still":
                args = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x12233f:s={width}x{height}:r={fps}", "-loop", "1", "-framerate", str(fps), "-i", str(media)]
                fc = (f"[1:v]scale={int(width*.78)}:-1,setsar=1[portrait];[0:v][portrait]overlay=(W-w)/2:(H-h)/2:shortest=1,"
                      + title_filter + "," + brand_filter + ",format=yuv420p[v]")
                args += ["-filter_complex", fc, "-map", "[v]"]
            else:
                seek = float(scene.get("media_seek", start if mode == "presenter_native" else 0))
                args = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-ss", f"{seek:.3f}", "-i", str(media)]
                vf = (f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                      f"crop={width}:{height},setsar=1," + title_filter + "," + brand_filter + ",format=yuv420p")
                args += ["-vf", vf, "-map", "0:v:0"]
            args += ["-an", "-t", f"{length:.3f}", "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", str(target)]
            run(args)
            parts.append(target)
        playlist = work / "list.txt"
        playlist.write_text("\n".join("file '" + str(x).replace("'", "'\\''") + "'" for x in parts) + "\n", encoding="utf-8")
        captions = work / "captions.srt"
        create_srt(data.get("captions", []), captions)
        temp_audio = source
        if data.get("narration_source_video"):
            temp_audio = work / "narration.wav"
            run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", str(temp_audio)])
        ff = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(playlist), "-i", str(temp_audio)]
        if data.get("captions"):
            # Use only explicitly timed words, never made-up equal-word durations.
            ff += ["-vf", f"subtitles='{captions}':force_style='Fontsize=16,PrimaryColour=&HFFFFFF&,Outline=2,Alignment=2,MarginV=105'"]
        ff += ["-map", "0:v:0", "-map", "1:a:0", "-t", f"{duration:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(output)]
        run(ff)
    final = probe(output)
    streams = final["streams"]
    vs = [s for s in streams if s["codec_type"] == "video"]
    au = [s for s in streams if s["codec_type"] == "audio"]
    real = seconds(output)
    if not vs or not au or vs[0]["width"] != width or vs[0]["height"] != height or abs(real-duration) > 0.5:
        output.unlink(missing_ok=True)
        raise RuntimeError("Rendered output failed QA")
    return {"status": "REVIEW_ONLY", "output": str(output), "topic": data["topic"],
            "duration": round(real, 2), "size": f"{width}x{height}", "single_narration": True,
            "captions_provided": len(data.get("captions", [])),
            "not_verified": "Natural voice, caption wording, and consented lip-sync require human review"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    p.add_argument("--output", type=Path, default=Path("videos/shorts_audio_first_review.mp4"))
    p.add_argument("--width", type=int, choices=[720, 1080], default=720)
    args = p.parse_args()
    print(json.dumps(render(args.manifest, args.output, args.width, args.width*16//9), indent=2))


if __name__ == "__main__":
    main()
