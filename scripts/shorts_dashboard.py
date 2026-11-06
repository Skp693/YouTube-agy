"""Local dashboard bridge to the narration-first Shorts review renderer.

Accepts an existing approved manifest from <project>/docs only.
No third-party Flow login, paid APIs, voice synthesis or YouTube publication.
"""
from pathlib import Path
from urllib.parse import urlsplit
import re

from scripts.narration_first_shorts import render

MANIFEST_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\.json\Z")
JOB_RE = re.compile(r"shorts_[a-zA-Z0-9]{6,18}\Z")


def origin_is_local(origin):
    """Require a local origin for browser-triggered preview renders."""
    if origin is None:
        return True  # desktop CLI/curl requests do not send Origin
    try:
        parsed = urlsplit(origin)
        return parsed.scheme == "http" and parsed.hostname in ("localhost", "127.0.0.1")
    except ValueError:
        return False


def get_local_manifest(base_dir, name):
    """Reject path traversal, symlinks, examples, and missing media manifests."""
    if not isinstance(name, str) or not MANIFEST_RE.fullmatch(name):
        raise ValueError("Manifest must be a simple .json filename in docs/")
    if name.endswith(".example.json"):
        raise ValueError("Examples must be copied and completed before rendering")
    project = Path(base_dir).resolve()
    docs = (project / "docs").resolve()
    path = docs / name
    if path.is_symlink() or path.resolve().parent != docs:
        raise ValueError("Manifest must be a real local file inside project docs/")
    if not path.is_file():
        raise FileNotFoundError(
            f"No prepared manifest found: docs/{name}. "
            "Copy docs/narration_first_manifest.example.json, "
            "fill real approved media paths and verify the script."
        )
    return path


def run_review(base_dir, manifest_name, job_id):
    """Build one review-only Short and return a playable local dashboard URL."""
    if not isinstance(job_id, str) or not JOB_RE.fullmatch(job_id):
        raise ValueError("Invalid Shorts review job identifier")
    base = Path(base_dir).resolve()
    manifest = get_local_manifest(base, manifest_name)
    videos_dir = base / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)
    outfile = videos_dir / f"{job_id}_final.mp4"
    if outfile.exists():
        raise FileExistsError("Review output already exists; refusing overwrite")
    result = render(manifest, outfile, width=720, height=1280)
    if result.get("status") != "REVIEW_ONLY":
        raise RuntimeError("Short renderer returned an unexpected publishing status")
    return {
        **result,
        "video_url": f"/media/video/{job_id}",
        "upload_performed": False,
        "privacy": "review_only",
        "manifest": manifest.name,
    }
