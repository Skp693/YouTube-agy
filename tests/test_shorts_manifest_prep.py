"""Safety regression tests for creating a review-only manifest from recorded media."""
import json
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock
from scripts import prepare_shorts_manifest as prep


class PrepareManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.media = self.root / "local_assets"
        self.media.mkdir()
        for p in ("presenter.mp4", "narration.wav", "resume.png", "skills.jpg", "flowclip.mp4"):
            (self.media / p).write_bytes(b"local test fixture")
        self.out = self.root / "docs" / "narration_first_manifest.json"

    @mock.patch.object(prep, "probe_audio_duration", return_value=45.001)
    def test_presenter_video_creates_contiguous_native_intro_and_outro(self, duration):
        doc = prep.plan("ATS tips", self.media/"presenter.mp4", [
            (self.media/"resume.png", "Clear headings", "broll"),
            (self.media/"skills.jpg", "Truthful keywords", "pip_still")])
        self.assertEqual(doc["topic"], "ATS tips")
        self.assertEqual(doc["narration_source_video"], str(self.media/"presenter.mp4"))
        self.assertEqual(doc["scenes"][0]["mode"], "presenter_native")
        self.assertEqual(doc["scenes"][-1]["mode"], "presenter_native")
        self.assertEqual(doc["scenes"][0]["start"], 0)
        self.assertAlmostEqual(doc["scenes"][-1]["end"], 45.001, delta=.003)
        for a,b in zip(doc["scenes"], doc["scenes"][1:]):
            self.assertEqual(a["end"], b["start"])
        self.assertEqual(doc["captions"], [])
        self.assertTrue(doc["review_only"])

    @mock.patch.object(prep, "probe_audio_duration", return_value=45)
    def test_audio_only_creates_no_moving_talking_head(self, duration):
        doc = prep.plan("ATS tips", self.media/"narration.wav", [
            (self.media/"resume.png", "Resume format", "broll"),
            (self.media/"skills.jpg", "Skills", "pip_still")])
        self.assertEqual(doc["narration_audio"], str(self.media/"narration.wav"))
        self.assertTrue(all(s["mode"] != "presenter_native" for s in doc["scenes"]))
        self.assertEqual(doc["scenes"][-1]["end"], 45.0)

    @mock.patch.object(prep, "probe_audio_duration", return_value=45)
    def test_moving_broll_requires_explicit_non_speaking_review(self, duration):
        assets = [(self.media/"flowclip.mp4", "Illustration", "broll")]
        with self.assertRaisesRegex(ValueError, "non-speaking"):
            prep.plan("ATS", self.media/"presenter.mp4", assets)
        doc = prep.plan("ATS", self.media/"presenter.mp4", assets,
                        verified_nontalking_video=True)
        self.assertTrue(doc["scenes"][1]["no_visible_speaking_faces"])

    @mock.patch.object(prep, "probe_audio_duration", return_value=45)
    def test_no_overwrite_existing_approved_manifest(self, duration):
        self.out.parent.mkdir()
        self.out.write_text("approved content")
        doc = prep.plan("ATS", self.media/"presenter.mp4", [
            (self.media/"resume.png", "Clear headings", "broll")])
        with self.assertRaises(FileExistsError):
            prep.write_manifest(doc, self.out)
        self.assertEqual(self.out.read_text(), "approved content")

    @mock.patch.object(prep, "probe_audio_duration", return_value=65)
    def test_overlong_narration_rejected(self, duration):
        with self.assertRaisesRegex(ValueError, "8.*60"):
            prep.plan("ATS", self.media/"presenter.mp4", [
                (self.media/"resume.png", "Resume format", "broll")])

    @mock.patch.object(prep, "probe_audio_duration", return_value=45)
    def test_missing_image_and_blank_label_rejected(self, duration):
        with self.assertRaises(FileNotFoundError):
            prep.plan("ATS", self.media/"presenter.mp4", [
                (self.media/"missing.png", "Resume", "broll")])
        with self.assertRaisesRegex(ValueError, "label"):
            prep.plan("ATS", self.media/"presenter.mp4", [
                (self.media/"resume.png", "   ", "broll")])

    @mock.patch.object(prep, "probe_audio_duration", return_value=45)
    def test_pip_portrait_must_be_still(self, duration):
        with self.assertRaisesRegex(ValueError, "still"):
            prep.plan("ATS", self.media/"presenter.mp4", [
                (self.media/"flowclip.mp4", "Flow", "pip_still")],
                verified_nontalking_video=True)

    def test_video_file_with_no_video_stream_is_rejected(self):
        fake = self.media/"renamed_audio.mp4"
        with wave.open(str(fake), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
            w.writeframes(b"\x00\x00"*8000*10)
        with self.assertRaisesRegex(ValueError, "video frames"):
            prep.probe_audio_duration(fake)

    @mock.patch.object(prep, "probe_audio_duration", return_value=45)
    def test_write_valid_review_only_manifest(self, duration):
        doc = prep.plan("ATS", self.media/"presenter.mp4", [
            (self.media/"resume.png", "Resume", "broll")])
        dest = prep.write_manifest(doc, self.out)
        self.assertEqual(dest, self.out)
        self.assertTrue(json.loads(dest.read_text())["review_only"])


if __name__ == "__main__":
    unittest.main()
