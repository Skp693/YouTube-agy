"""Real localhost HTTP smoke for dashboard Shorts review (no video upload)."""
import json
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

import desktop_server


class ShortsDashboardHTTPSmoke(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "videos").mkdir()
        (self.root / "docs" / "narration_first_manifest.json").write_text(
            '{"topic": "ATS"}', encoding="utf-8")
        self.settings_patch = mock.patch.object(desktop_server.settings, "BASE_DIR", self.root)
        self.settings_patch.start()
        self.addCleanup(self.settings_patch.stop)

        def pretend_review(base, name, job_id):
            return {
                "status": "REVIEW_ONLY",
                "upload_performed": False,
                "video_url": f"/media/video/{job_id}",
            }

        self.render_patch = mock.patch("scripts.shorts_dashboard.run_review",
                                       side_effect=pretend_review)
        self.render_patch.start()
        self.addCleanup(self.render_patch.stop)
        self.server = desktop_server.ThreadedHTTPServer(
            ("127.0.0.1", 0), desktop_server.DesktopDashboardHandler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def submit(self, payload, origin=None):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/shorts/start",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Origin": origin or f"http://127.0.0.1:{self.port}",
                     "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_approved_manifest_start_and_job_status(self):
        status, data = self.submit({"manifest":"narration_first_manifest.json"})
        self.assertEqual(status, 202)
        job_id = data["job_id"]
        last = None
        for _ in range(100):
            with urllib.request.urlopen(
                f"http://127.0.0.1:{self.port}/api/pipeline/job/{job_id}",
                timeout=5,
            ) as resp:
                last = json.loads(resp.read())
            if last["status"] == "completed":
                break
            time.sleep(0.02)
        self.assertEqual(last["status"], "completed")
        self.assertEqual(last["summary"]["status"], "REVIEW_ONLY")
        self.assertFalse(last["summary"]["upload_performed"])
        self.assertEqual(last["summary"]["video_url"], f"/media/video/{job_id}")
        desktop_server.ACTIVE_JOBS.pop(job_id, None)

    def test_remote_origin_is_blocked(self):
        status, data = self.submit(
            {"manifest":"narration_first_manifest.json"},
            origin="https://malicious.example",
        )
        self.assertEqual(status, 403)
        self.assertIn("error", data)

    def test_missing_manifest_returns_actionable_error(self):
        status, data = self.submit({"manifest":"missing.json"})
        self.assertEqual(status, 422)
        self.assertIn("manifest", data["error"].lower())


if __name__ == "__main__":
    unittest.main()
