"""Shorts dashboard: safe local-only manifest selection and review output."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import shorts_dashboard as m


class ShortsDashboardSafetyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "docs").mkdir()
        (self.root / "videos").mkdir()
        self.valid_file = self.root / "docs" / "narration_first_manifest.json"
        self.valid_file.write_text(json.dumps({"topic": "ATS"}), encoding="utf-8")

    def test_accepts_known_manifest_in_docs(self):
        self.assertEqual(
            m.get_local_manifest(self.root, "narration_first_manifest.json"),
            self.valid_file
        )

    def test_rejects_traversal(self):
        for name in ("../secret.json", "../../private.json", "/tmp/evil.json", "x/y.json"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    m.get_local_manifest(self.root, name)

    def test_rejects_demo_manifest_and_untrusted_filename(self):
        for name in ("flow_shorts_manifest.example.json", "", "a.json;rm -rf", ".env"):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    m.get_local_manifest(self.root, name)

    def test_rejects_missing_manifest(self):
        with self.assertRaises(FileNotFoundError):
            m.get_local_manifest(self.root, "missing.json")

    def test_rejects_symlink_outside_docs(self):
        secret = self.root / "credentials.json"
        secret.write_text('{"secret":"not for display"}')
        (self.root / "docs" / "linked.json").symlink_to(secret)
        with self.assertRaises(ValueError):
            m.get_local_manifest(self.root, "linked.json")

    def test_job_never_uploads_and_produces_review_url(self):
        with mock.patch.object(m, "render", return_value={
            "status": "REVIEW_ONLY", "duration": 45.0, "size": "720x1280"
        }) as render:
            report = m.run_review(self.root, "narration_first_manifest.json", "shorts_abc123")
            self.assertEqual(report["status"], "REVIEW_ONLY")
            self.assertEqual(report["video_url"], "/media/video/shorts_abc123")
            self.assertEqual(report["upload_performed"], False)
            self.assertIn("shorts_abc123_final.mp4", str(render.call_args.args[1]))

    def test_rejects_untrusted_job_identifiers(self):
        with self.assertRaises(ValueError):
            m.run_review(self.root, "narration_first_manifest.json", "../escape")

    def test_rejects_nonlocal_browser_origin(self):
        self.assertFalse(m.origin_is_local("https://evil.example"))
        self.assertFalse(m.origin_is_local("http://127.0.0.1.evil.example"))
        self.assertTrue(m.origin_is_local("http://127.0.0.1:8501"))
        self.assertTrue(m.origin_is_local("http://localhost:8501"))
        self.assertTrue(m.origin_is_local(None))


if __name__ == "__main__":
    unittest.main()
