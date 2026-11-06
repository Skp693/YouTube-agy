"""Unit tests for topic-specific Shorts inputs without spending Flow credits."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import flow_shorts_review as shorts


class TestFlowShortsSafety(unittest.TestCase):
    def write_manifest(self, folder, payload):
        path = Path(folder) / "manifest.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_topic_is_required(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = self.write_manifest(folder, {"scenes": [
                {"path": "a.mp4"} for _ in range(3)
            ]})
            with mock.patch.object(shorts.shutil, "which", return_value="/usr/bin/ffmpeg"):
                with self.assertRaisesRegex(ValueError, "topic"):
                    shorts.make_review(manifest, Path(folder) / "output.mp4")

    def test_pip_requires_subject_specific_cards(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = self.write_manifest(folder, {
                "topic": "How ATS works",
                "scenes": [
                    {"path": "a.mp4", "mode": "full"},
                    {"path": "b.mp4", "mode": "pip"},
                    {"path": "c.mp4", "mode": "full"},
                ],
            })
            with mock.patch.object(shorts.shutil, "which", return_value="/usr/bin/ffmpeg"):
                with self.assertRaisesRegex(ValueError, "cards"):
                    shorts.make_review(manifest, Path(folder) / "output.mp4")

    def test_over_sixty_seconds_is_rejected_before_rendering(self):
        with tempfile.TemporaryDirectory() as folder:
            manifest = self.write_manifest(folder, {
                "topic": "AI tips",
                "scenes": [
                    {"path": f"scene{i}.mp4", "mode": "full"}
                    for i in range(8)
                ],
            })
            info = {"format": {"duration": "8.0"}}
            with mock.patch.object(shorts.shutil, "which", return_value="/usr/bin/ffmpeg"), \
                 mock.patch.object(shorts, "validate_input"), \
                 mock.patch.object(shorts, "inspect", return_value=info), \
                 mock.patch.object(shorts, "inspect_audio", return_value={
                     "decision": "HUMAN_REVIEW_REQUIRED", "flags": []
                 }), \
                 mock.patch.object(shorts, "command") as command:
                with self.assertRaisesRegex(ValueError, "60 seconds"):
                    shorts.make_review(manifest, Path(folder) / "output.mp4")
                command.assert_not_called()

    def test_pip_card_text_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "1–3"):
                shorts.render_scene(
                    Path("fake.mp4"), Path("output.mp4"),
                    {"mode": "pip", "label": "Resume tips", "cards": ["", "", "", ""]},
                    "QUADDIS", Path(folder), 0
                )


if __name__ == "__main__":
    unittest.main()
