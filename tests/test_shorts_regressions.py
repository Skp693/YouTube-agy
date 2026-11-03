"""Regression tests for production-safe Shorts generation and upload."""
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import voiceover
import assemble_video
import youtube_uploader


class ShortsSafetyRegressions(unittest.TestCase):
    def test_failed_speech_does_not_create_fake_robot_audio(self):
        with tempfile.TemporaryDirectory() as td:
            settings = SimpleNamespace(
                AUDIO_DIR=Path(td), TTS_PROVIDER="local",
                ensure_directories=lambda: None
            )
            sample = {"sections": [{"id": 1, "narration": "This is a real narration test.",
                                     "title": "Intro", "duration_estimate_sec": 4}]}
            with mock.patch.object(voiceover, "settings", settings), \
                 mock.patch.object(voiceover, "synthesize_macos_speech", return_value=None), \
                 mock.patch.object(voiceover, "synthesize_local_speech_wave",
                                   side_effect=AssertionError("Synthetic tone should never run")):
                with self.assertRaisesRegex(RuntimeError, "speech"):
                    voiceover.generate_voiceover(sample, project_id="speech-fail")

    def test_missing_ffmpeg_never_produces_placeholder_mp4(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            settings = SimpleNamespace(
                AUDIO_DIR=root / "audio", VIDEOS_DIR=root / "videos",
                SCRIPTS_DIR=root / "scripts", MUSIC_DIR=root / "music",
                MUSIC_VOLUME=0.1, ensure_directories=lambda: None
            )
            for p in [settings.VIDEOS_DIR, settings.SCRIPTS_DIR, settings.AUDIO_DIR / "sample"]:
                p.mkdir(parents=True, exist_ok=True)
            scene = root / "slide.png"
            scene.write_bytes(b"not a real scene")
            (settings.AUDIO_DIR / "sample" / "full_voiceover.wav").write_bytes(b"wav")
            with mock.patch.object(assemble_video, "settings", settings), \
                 mock.patch.object(assemble_video.shutil, "which", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "FFmpeg"):
                    assemble_video.assemble_video(
                        "sample",
                        timing_data={"sections": [{"start_time_sec": 0, "end_time_sec": 2, "narration": "Hello"}]},
                        scenes_data={"scenes": [{"image_path": str(scene), "duration_sec": 2}]}
                    )
            self.assertFalse((settings.VIDEOS_DIR / "sample_final.mp4").exists())

    def test_invalid_mp4_is_rejected_before_upload_even_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            videos, meta, thumbs = (root / "videos", root / "meta", root / "thumbs")
            for p in [videos, meta, thumbs]:
                p.mkdir()
            (videos / "fake_final.mp4").write_bytes(b"fake mp4")
            (meta / "fake_metadata.json").write_text(json.dumps({"title": "test"}))
            settings = SimpleNamespace(
                VIDEOS_DIR=videos, METADATA_DIR=meta, THUMBNAILS_DIR=thumbs,
                YOUTUBE_CATEGORY_ID="27", YOUTUBE_DEFAULT_PRIVACY="private",
                YOUTUBE_AI_DISCLOSURE=True, YOUTUBE_CLIENT_SECRETS_FILE=root / "missing",
                ensure_directories=lambda: None
            )
            with mock.patch.object(youtube_uploader, "settings", settings):
                with self.assertRaisesRegex((RuntimeError, ValueError), "video|MP4|media"):
                    youtube_uploader.upload_to_youtube("fake", dry_run=True)


if __name__ == "__main__":
    unittest.main()
