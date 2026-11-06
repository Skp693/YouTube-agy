"""Dashboard Shorts endpoint refuses nonlocal origins and never uploads."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import desktop_server


class ShortsEndpointTests(unittest.TestCase):
    def make_handler(self, origin="http://127.0.0.1:8501"):
        h = object.__new__(desktop_server.DesktopDashboardHandler)
        h.headers = {"Origin": origin}
        h._send_json = mock.Mock()
        return h

    def test_post_endpoint_routes_to_review_job(self):
        h = self.make_handler()
        h.path = "/api/shorts/start"
        h._read_json_body = mock.Mock(return_value={
            "manifest": "narration_first_manifest.json"})
        h._handle_start_shorts = mock.Mock()
        h.do_POST()
        h._handle_start_shorts.assert_called_once_with({
            "manifest": "narration_first_manifest.json"})

    def test_foreign_browser_origin_cannot_start_job(self):
        h = self.make_handler(origin="https://not-my-dashboard.example")
        with mock.patch("scripts.shorts_dashboard.run_review") as task:
            h._handle_start_shorts({"manifest": "narration_first_manifest.json"})
        self.assertEqual(h._send_json.call_args.kwargs["status"], 403)
        task.assert_not_called()

    def test_prepared_manifest_launches_review_only(self):
        h = self.make_handler()
        fake = Path(tempfile.gettempdir()) / "narration_first_manifest.json"
        # Replace worker thread with deterministic synchronous executor
        class ThreadNow:
            def __init__(self, target, **kwargs):
                self.target = target
            def start(self):
                self.target()
        with mock.patch("scripts.shorts_dashboard.get_local_manifest", return_value=fake), \
             mock.patch("scripts.shorts_dashboard.run_review", return_value={
                "status": "REVIEW_ONLY",
                "video_url": "/media/video/shorts_abc123",
                "upload_performed": False}) as task, \
             mock.patch.object(desktop_server.threading, "Thread", ThreadNow):
            h._handle_start_shorts({"manifest": "narration_first_manifest.json"})
        self.assertEqual(h._send_json.call_args.kwargs["status"], 202)
        self.assertTrue(task.called)
        job_id = h._send_json.call_args.args[0]["job_id"]
        self.assertEqual(desktop_server.ACTIVE_JOBS[job_id]["status"], "completed")
        self.assertEqual(desktop_server.ACTIVE_JOBS[job_id]["summary"]["upload_performed"], False)
        desktop_server.ACTIVE_JOBS.pop(job_id, None)


if __name__ == "__main__":
    unittest.main()
