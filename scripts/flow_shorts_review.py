"""Build a 9:16 Shorts review MP4 from already-exported Google Flow clips.

No unofficial Flow MCP, browser cookies, paid API, or publication.
Requires ffmpeg/ffprobe with drawtext support. Source speech is preserved.
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

W, H, FPS = 1080, 1920, 30


def command(args):
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError(f"{args[0]} failed:\n{proc.stderr[-2500:]}")


def inspect(path):
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(path)], capture_output=True, text=True, check=True
    )
    return json.loads(proc.stdout)


def validate_input(path):
    if not path.is_file():
        raise FileNotFoundError(f"Missing Flow export: {path}")
    data = inspect(path)
    kinds = {s.get("codec_type") for s in data.get("streams", [])}
    if not {"video", "audio"}.issubset(kinds):
        raise ValueError(f"Video and spoken audio are required: {path}")
    if float(data.get("format", {}).get("duration", 0)) < 2:
        raise ValueError(f"Source clip is too short: {path}")


def write_text(workdir, filename, value):
    path = workdir / filename
    path.write_text(str(value)[:56], encoding="utf-8")
    return path


def drawtext(path, size, x, y, color="white"):
    return (f"drawtext=font='Arial':textfile='{path.as_posix()}':"
            f"fontsize={size}:fontcolor={color}:x={x}:y={y}:"
            "borderw=2:bordercolor=black@0.5")


def render_scene(src, target, scene, brand, workdir, index):
    title_file = write_text(workdir, f"title_{index}.txt", scene.get("label", f"Scene {index+1}"))
    brand_file = write_text(workdir, f"brand_{index}.txt", brand)
    mode = scene.get("mode", "full")
    if mode == "full":
        video_filter = (
            f"scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},setsar=1,"
            "drawbox=x=0:y=0:w=iw:h=220:color=black@0.58:t=fill,"
            + drawtext(title_file, 52, 58, 72) + ","
            + drawtext(brand_file, 28, 60, 148, "0xffc0cc")
            + f",fps={FPS},format=yuv420p"
        )
        args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(src), "-vf", video_filter,
                "-map", "0:v:0", "-map", "0:a:0"]
    elif mode == "pip":
        lines = scene.get("cards") or []
        if not isinstance(lines, list) or not 1 <= len(lines) <= 3:
            raise ValueError("PIP scene requires 1–3 topic-specific cards")
        lines = [str(x).replace("\\n", " ").strip()[:32] for x in lines]
        if not all(lines):
            raise ValueError("PIP cards cannot be blank")
        cards = []
        for i, line in enumerate(lines):
            fp = write_text(workdir, f"card_{index}_{i}.txt", line)
            cards.append(
                f"drawbox=x=65:y={420+i*175}:w=950:h=140:"
                "color=0x1f3452@0.92:t=fill,"
                + drawtext(fp, 47, 95, 455+i*175)
            )
        graph = (
            "[1:v]drawbox=x=0:y=0:w=iw:h=230:color=0x13243a:t=fill,"
            + drawtext(title_file, 52, 58, 72) + ","
            + drawtext(brand_file, 28, 60, 148, "0xffc0cc") + ","
            + ",".join(cards) + "[bg];"
            "[0:v]scale=460:818:force_original_aspect_ratio=decrease,"
            "setsar=1[presenter];"
            "[bg][presenter]overlay=x=595:y=1040:shortest=1,"
            "format=yuv420p[v]"
        )
        args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(src), "-f", "lavfi",
                "-i", f"color=c=0x0a1527:s={W}x{H}:r={FPS}",
                "-filter_complex", graph, "-map", "[v]", "-map", "0:a:0"]
    else:
        raise ValueError("Each scene mode must be full or pip")
    args += [
        "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:a", "aac",
        "-b:a", "160k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", str(target)
    ]
    command(args)


def render_outro(target, brand, cta, workdir):
    title_file = write_text(workdir, "outro_brand.txt", brand)
    cta_file = write_text(workdir, "outro_cta.txt", cta)
    vf = (
        "drawbox=x=50:y=700:w=980:h=470:color=0x172f4d:t=fill,"
        + drawtext(title_file, 78, 130, 780, "0xffc0cc") + ","
        + drawtext(cta_file, 44, 130, 955)
    )
    command([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0a1527:s={W}x{H}:r={FPS}:d=3",
        "-f", "lavfi", "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-vf", vf, "-map", "0:v", "-map", "1:a",
        "-t", "3", "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "22", "-r", str(FPS), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-ac", "2", str(target)
    ])


def make_review(manifest, output):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and FFprobe required; fake video files forbidden")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    topic = data.get("topic", "")
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("A topic is required to match visuals to the subject")
    scenes = data.get("scenes") or []
    if not 3 <= len(scenes) <= 12:
        raise ValueError("Supply 3 to 12 pre-generated clips")
    if any(x.get("mode") == "pip" and not x.get("cards") for x in scenes):
        raise ValueError("Every PIP scene needs topic-specific cards")
    paths = []
    durations = []
    for scene in scenes:
        path = Path(scene["path"]).expanduser()
        if not path.is_absolute():
            path = (manifest.parent / path).resolve()
        validate_input(path)
        durations.append(float(inspect(path).get("format", {}).get("duration", 0)))
        paths.append(path)
    if sum(durations) + 3 > 60:
        raise ValueError("Short would exceed 60 seconds; trim or use fewer clips")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="flow_shorts_") as folder:
        work = Path(folder)
        parts = []
        for i, (source, scene) in enumerate(zip(paths, scenes)):
            target = work / f"scene_{i:02d}.mp4"
            render_scene(source, target, scene, data.get("brand", "QUADDIS"), work, i)
            parts.append(target)
        outro = work / "outro.mp4"
        render_outro(outro, data.get("brand", "QUADDIS"),
                     data.get("cta", "Get a free CV audit"), work)
        parts.append(outro)
        playlist = work / "concat.txt"
        playlist.write_text("\n".join(
            "file '" + str(part).replace("'", "'\\''") + "'" for part in parts
        ) + "\n", encoding="utf-8")
        command([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(playlist),
            "-c", "copy", "-movflags", "+faststart", str(output)
        ])
    check = inspect(output)
    streams = check.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"]
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    length = float(check.get("format", {}).get("duration", 0))
    if (not videos or not audio or videos[0].get("width") != W
            or videos[0].get("height") != H or length < 15):
        output.unlink(missing_ok=True)
        raise RuntimeError("Output failed technical QA")
    return {
        "status": "REVIEW_ONLY_NOT_PUBLISHED", "output": str(output),
        "duration_seconds": round(length, 2), "resolution": f"{W}x{H}",
        "topic": topic, "brand": data.get("brand", "QUADDIS"),
        "source_clips": len(paths),
        "flow_credits_used": 0,
        "warning": "Naturalness, factual content and lip-sync require human review."
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path,
                        default=Path("videos/flow_shorts_review.mp4"))
    parser.add_argument("--mobile-output", type=Path,
                        help="Optional iPhone-compatible 720x1280 preview")
    options = parser.parse_args()
    report = make_review(options.manifest, options.output)
    if options.mobile_output:
        options.mobile_output.parent.mkdir(parents=True, exist_ok=True)
        command([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(options.output), "-vf", "scale=720:1280",
            "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "26", "-profile:v", "main", "-level", "3.1",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(options.mobile_output)
        ])
        mobile = inspect(options.mobile_output)
        streams = mobile.get("streams", [])
        v = [x for x in streams if x.get("codec_type") == "video"]
        a = [x for x in streams if x.get("codec_type") == "audio"]
        if not v or not a or v[0].get("width") != 720 or v[0].get("height") != 1280:
            options.mobile_output.unlink(missing_ok=True)
            raise RuntimeError("Mobile output failed stream/dimension QA")
        report["mobile_preview"] = str(options.mobile_output)
    print(json.dumps(report, indent=2))
