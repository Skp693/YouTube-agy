"""Standalone Desktop Dashboard Server (desktop_server.py)

Multi-threaded Python HTTP Server providing:
  1. High-end Glassmorphic Studio Dashboard UI
  2. Full REST APIs for topic suggestion, prompt remodeling, pipeline jobs, and compliance audits
  3. Video/Audio media streaming with HTTP byte-range seeking
  4. 100% standard library implementation (zero pip dependencies required)
"""

import os
import sys
import json
import time
import mimetypes
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

from config.settings import settings
from config.logging_config import setup_logger
from compliance_checker import ComplianceChecker
from topic_refiner import TopicRefiner
from model_advisor import ModelAdvisor

logger = setup_logger("desktop_server")

# Active pipeline job tracking container
ACTIVE_JOBS: Dict[str, Dict[str, Any]] = {}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP Server for responsive concurrent API & media streaming."""
    daemon_threads = True

class DesktopDashboardHandler(SimpleHTTPRequestHandler):
    """Custom request handler with REST API and byte-range media streaming."""

    def do_GET(self):
        """Handles GET requests for UI and REST APIs."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        # 1. UI Root
        if path in ["/", "/index.html"]:
            self._serve_file(settings.BASE_DIR / "static" / "index.html", "text/html; charset=utf-8")
            return

        # 2. Static Assets (/static/...)
        if path.startswith("/static/"):
            rel_path = path.replace("/static/", "", 1)
            file_path = settings.BASE_DIR / "static" / rel_path
            self._serve_file(file_path)
            return

        # 3. Media Streams (/media/video/..., /media/thumbnail/..., /media/audio/...)
        if path.startswith("/media/"):
            self._handle_media_stream(path)
            return

        # 4. REST APIs
        if path == "/api/status":
            advisor = ModelAdvisor.get_recommendations()
            self._send_json({"status": "running", "advisor": advisor, "time": time.time()})
            return

        if path == "/api/projects":
            self._handle_list_projects()
            return

        if path.startswith("/api/project/"):
            project_id = path.replace("/api/project/", "").strip()
            self._handle_get_project(project_id)
            return

        if path.startswith("/api/pipeline/job/"):
            job_id = path.replace("/api/pipeline/job/", "").strip()
            job = ACTIVE_JOBS.get(job_id, {"status": "not_found"})
            self._send_json(job)
            return

        if path == "/api/compliance/latest":
            self._handle_compliance_latest()
            return

        # Fallback 404
        self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        """Handles POST API requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        body = self._read_json_body()

        if path == "/api/topics/suggest":
            niche = body.get("niche", "all")
            suggestions = TopicRefiner.get_trending_suggestions(niche)
            self._send_json({"suggestions": suggestions})
            return

        if path == "/api/topics/remodify":
            raw_input = body.get("input", "")
            video_format = body.get("format", "step_by_step")
            notes = body.get("notes", "")
            refined = TopicRefiner.remodify_topic(raw_input, video_format=video_format, reference_notes=notes)
            self._send_json({"refined": refined})
            return

        if path == "/api/compliance/audit":
            title = body.get("title", "")
            description = body.get("description", "")
            narration = body.get("narration", "")
            tags = body.get("tags", [])
            has_ai_disclosure = body.get("has_ai_disclosure", True)
            audit = ComplianceChecker.audit_project(title, description, narration, tags, has_ai_disclosure)
            self._send_json({"audit": audit})
            return

        if path.startswith("/api/project/") and path.endswith("/set_thumbnail"):
            project_id = path.replace("/api/project/", "").replace("/set_thumbnail", "").strip()
            variation = body.get("variation", "A")
            target_var = settings.THUMBNAILS_DIR / f"{project_id}_thumb_{variation}.png"
            active_thumb = settings.THUMBNAILS_DIR / f"{project_id}_thumbnail.png"
            if target_var.exists():
                import shutil
                shutil.copy(target_var, active_thumb)
                self._send_json({"status": "updated", "variation": variation})
            else:
                self.send_error(404, "Thumbnail variation not found")
            return

        if path == "/api/pipeline/start":
            self._handle_start_pipeline(body)
            return

        self.send_error(404, "POST endpoint not found")

    def _read_json_body(self) -> Dict[str, Any]:
        """Reads JSON payload from request body."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                raw_data = self.rfile.read(content_length).decode("utf-8")
                return json.loads(raw_data)
        except Exception as e:
            logger.warning(f"Error parsing JSON body: {e}")
        return {}

    def _send_json(self, data: Any, status: int = 200) -> None:
        """Sends JSON HTTP response."""
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _serve_file(self, file_path: Path, content_type: Optional[str] = None) -> None:
        """Serves a static file safely."""
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, f"File {file_path.name} not found")
            return

        content_type = content_type or mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        file_size = file_path.stat().st_size

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(file_size))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                self.wfile.write(chunk)

    def _handle_media_stream(self, path: str) -> None:
        """Handles byte-range streaming for MP4 videos and WAV audio."""
        parts = path.strip("/").split("/")
        if len(parts) < 3:
            self.send_error(400, "Invalid media request")
            return

        media_type, media_id = parts[1], parts[2]
        file_path = None

        if media_type == "video":
            file_path = settings.VIDEOS_DIR / f"{media_id}_final.mp4"
            content_type = "video/mp4"
        elif media_type == "thumbnail":
            query = parse_qs(urlparse(self.path).query)
            variation = query.get("v", [None])[0]
            if variation and variation in ["A", "B", "C"]:
                file_path = settings.THUMBNAILS_DIR / f"{media_id}_thumb_{variation}.png"
            if not file_path or not file_path.exists():
                file_path = settings.THUMBNAILS_DIR / f"{media_id}_thumbnail.png"
            content_type = "image/png"
        elif media_type == "audio":
            file_path = settings.AUDIO_DIR / media_id / "full_voiceover.wav"
            content_type = "audio/wav"
        else:
            self.send_error(400, "Unknown media type")
            return

        if not file_path or not file_path.exists():
            self.send_error(404, "Media file not found")
            return

        file_size = file_path.stat().st_size
        range_header = self.headers.get("Range")

        # Range streaming support (crucial for video scrubbing in browser)
        if range_header and range_header.startswith("bytes="):
            byte_range = range_header.split("=")[1].strip()
            parts = byte_range.split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else file_size - 1
            length = (end - start) + 1

            self.send_response(206)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk_to_read = min(remaining, 65536)
                    data = f.read(chunk_to_read)
                    if not data:
                        break
                    self.wfile.write(data)
                    remaining -= len(data)
        else:
            self._serve_file(file_path, content_type)

    def _handle_list_projects(self) -> None:
        """Returns list of all generated video projects with metadata preview."""
        projects = []
        meta_files = sorted(settings.METADATA_DIR.glob("*_metadata.json"), reverse=True)

        for mf in meta_files:
            try:
                with open(mf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                pid = data.get("project_id", mf.stem.replace("_metadata", ""))
                v_file = settings.VIDEOS_DIR / f"{pid}_final.mp4"
                t_file = settings.THUMBNAILS_DIR / f"{pid}_thumbnail.png"
                a_file = settings.AUDIO_DIR / pid / "full_voiceover.wav"

                projects.append({
                    "project_id": pid,
                    "title": data.get("title", f"Video {pid}"),
                    "tool_name": data.get("tool_name", "AI Tool"),
                    "chapters_count": len(data.get("chapters", [])),
                    "has_video": v_file.exists() and v_file.stat().st_size > 1024,
                    "video_size_mb": round(v_file.stat().st_size / (1024 * 1024), 2) if v_file.exists() else 0,
                    "has_thumbnail": t_file.exists(),
                    "has_audio": a_file.exists(),
                    "created_at": mf.stat().st_mtime
                })
            except Exception as e:
                logger.warning(f"Error loading project {mf}: {e}")

        self._send_json({"projects": projects})

    def _handle_get_project(self, project_id: str) -> None:
        """Returns complete project details for inspection."""
        meta_file = settings.METADATA_DIR / f"{project_id}_metadata.json"
        script_file = settings.SCRIPTS_DIR / f"{project_id}_script.json"
        timing_file = settings.AUDIO_DIR / project_id / "timing.json"

        if not meta_file.exists():
            self.send_error(404, "Project not found")
            return

        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)

        script = {}
        if script_file.exists():
            with open(script_file, "r", encoding="utf-8") as f:
                script = json.load(f)

        timing = {}
        if timing_file.exists():
            with open(timing_file, "r", encoding="utf-8") as f:
                timing = json.load(f)

        self._send_json({
            "project_id": project_id,
            "metadata": meta,
            "script": script,
            "timing": timing
        })

    def _handle_compliance_latest(self) -> None:
        """Runs audit on the most recent project."""
        meta_files = sorted(settings.METADATA_DIR.glob("*_metadata.json"), reverse=True)
        if not meta_files:
            self._send_json({"audit": None, "message": "No projects generated yet."})
            return

        with open(meta_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)

        title = data.get("title", "")
        description = data.get("description", "")
        tags = data.get("tags", [])
        has_ai_disclosure = data.get("ai_disclosure", True)

        audit = ComplianceChecker.audit_project(
            title=title,
            description=description,
            narration_full=description,
            tags=tags,
            has_ai_disclosure=has_ai_disclosure
        )
        self._send_json({"project_id": data.get("project_id"), "audit": audit})

    def _handle_start_pipeline(self, body: Dict[str, Any]) -> None:
        """Launches pipeline generation in a background worker thread."""
        tool_name = body.get("tool_name", "Claude 3.7 Artifacts")
        angle = body.get("angle")
        auto_upload = bool(body.get("auto_upload", False))
        privacy = body.get("privacy", "private")
        voice_avatar = body.get("voice_avatar", "Daniel")
        ken_burns = bool(body.get("ken_burns", True))
        speaking_rate = int(body.get("speaking_rate", 165))

        job_id = f"job_{int(time.time())}"
        ACTIVE_JOBS[job_id] = {
            "job_id": job_id,
            "tool_name": tool_name,
            "status": "running",
            "stage": 1,
            "stage_name": "Topic Selection",
            "progress_percent": 15,
            "start_time": time.time(),
            "logs": [f"Pipeline initiated for {tool_name} with voice '{voice_avatar}' @ {speaking_rate} WPM (Motion: {'Ken Burns' if ken_burns else 'Static'})"]
        }

        def worker():
            try:
                import main_pipeline
                job = ACTIVE_JOBS[job_id]
                job["logs"].append("Stage 1 & 2: Synthesizing curriculum & script...")
                job["stage"] = 2
                job["progress_percent"] = 30

                # Execute pipeline
                summary = main_pipeline.run_pipeline(
                    tool_name=tool_name,
                    angle=angle,
                    auto_upload=auto_upload,
                    privacy=privacy,
                    voice_avatar=voice_avatar,
                    ken_burns=ken_burns,
                    speaking_rate=speaking_rate
                )

                job["status"] = "completed"
                job["progress_percent"] = 100
                job["project_id"] = summary.get("project_id")
                job["summary"] = summary
                job["logs"].append(f"Pipeline finished! Final MP4: {summary.get('video_path')}")
            except Exception as e:
                logger.error(f"Worker job {job_id} failed: {e}")
                ACTIVE_JOBS[job_id]["status"] = "failed"
                ACTIVE_JOBS[job_id]["error"] = str(e)
                ACTIVE_JOBS[job_id]["logs"].append(f"Error: {e}")

        threading.Thread(target=worker, daemon=True).start()
        self._send_json({"job_id": job_id, "status": "started"})

def run_server(port: int = 8501) -> None:
    """Starts the Desktop Dashboard HTTP server."""
    settings.ensure_directories()
    server = ThreadedHTTPServer(("127.0.0.1", port), DesktopDashboardHandler)
    logger.info(f"Desktop Dashboard Server running at http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    finally:
        server.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8501
    run_server(port)
