"""Audio-first timeline safety tests. No network or source-video assets required."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from scripts import narration_first_shorts as m


class TimelineValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for fn in ("speaker.mp4", "broll.mp4", "portrait.jpg"):
            (self.root / fn).write_bytes(b"fixture")
        self.base = {
            "topic": "ATS guide", "brand": "QUADDIS",
            "narration_source_video": "speaker.mp4",
            "scenes": [
                {"start": 0, "end": 4, "media": "speaker.mp4",
                 "mode": "presenter_native", "label": "Intro"},
                {"start": 4, "end": 9, "media": "portrait.jpg",
                 "mode": "pip_still", "label": "Resume review"},
                {"start": 9, "end": 12, "media": "speaker.mp4",
                 "mode": "presenter_native", "label": "Outro"}
            ],
            "captions": []
        }
        self.mock_probe = mock.patch.object(
            m, "probe",
            return_value={"streams": [{"codec_type": "audio"},
                                      {"codec_type": "video"}],
                          "format": {"duration": "12.0"}}
        )
        self.mock_probe.start()
        self.addCleanup(self.mock_probe.stop)

    def check(self, data):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return m.validate(path)

    def test_valid_original_source(self):
        data, source, length = self.check(self.base)
        self.assertEqual(length, 12.0)
        self.assertEqual(source, self.root / "speaker.mp4")

    def test_reject_mismatched_presenter(self):
        self.base["scenes"][0]["media"] = "broll.mp4"
        with self.assertRaisesRegex(ValueError, "same original"):
            self.check(self.base)

    def test_reject_unsynced_presenter_seek(self):
        self.base["scenes"][2]["media_seek"] = 0
        with self.assertRaisesRegex(ValueError, "source timeline"):
            self.check(self.base)

    def test_reject_broll_with_potential_speaking_faces(self):
        self.base["scenes"][1]["media"] = "broll.mp4"
        self.base["scenes"][1]["mode"] = "broll"
        with self.assertRaisesRegex(ValueError, "no_visible_speaking_faces"):
            self.check(self.base)

    def test_reject_scene_gap(self):
        self.base["scenes"][1]["start"] = 4.2
        with self.assertRaisesRegex(ValueError, "contiguous"):
            self.check(self.base)

    def test_reject_overlap_in_captions(self):
        self.base["captions"] = [
            {"start": 0, "end": 5, "text": "A"},
            {"start": 4, "end": 8, "text": "B"}
        ]
        with self.assertRaisesRegex(ValueError, "Caption cue"):
            self.check(self.base)

    def test_reject_missing_master(self):
        self.base["narration_source_video"] = "missing.mp4"
        with self.assertRaises(FileNotFoundError):
            self.check(self.base)

    def test_exact_caption_timestamps(self):
        path = self.root / "captions.srt"
        m.create_srt([{"start": 0.15, "end": 1.8,
                       "text": "Timed caption"}], path)
        self.assertIn("00:00:00,150 --> 00:00:01,800", path.read_text())


if __name__ == "__main__":
    unittest.main()
