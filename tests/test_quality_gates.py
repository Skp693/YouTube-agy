"""Regression tests: production builds must not label mock media as finished output.

Run with: python -m unittest discover -s tests -p 'test_quality_gates.py' -v
No paid service, API key, or FFmpeg installation is required for these tests.
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import assemble_video
import voiceover
from config.settings import settings


class QualityGateTests(unittest.TestCase):
    def test_voiceover_fails_when_no_real_speech_engine_is_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(settings, "AUDIO_DIR", Path(tmp) / "audio"), \
                 patch.object(settings, "TTS_PROVIDER", "google_tts"), \
                 patch.object(voiceover, "synthesize_with_google_tts", return_value=None), \
                 patch.object(voiceover, "synthesize_macos_speech", return_value=None):
                script = {"tool_name": "Example", "sections": [{
                    "id": 1, "title": "Intro", "narration": "Hello from a real narrator.",
                    "duration_estimate_sec": 1.0
                }]}
                with self.assertRaisesRegex(RuntimeError, "No usable speech synthesizer"):
                    voiceover.generate_voiceover(script, project_id="no_fake_audio")
                self.assertFalse((Path(tmp) / "audio" / "no_fake_audio" / "section_01.wav").exists())

    def test_assembly_fails_without_ffmpeg_instead_of_making_fake_mp4(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(settings, "VIDEOS_DIR", root / "videos"), \
                 patch.object(settings, "SCRIPTS_DIR", root / "scripts"), \
                 patch("assemble_video.shutil.which", return_value=None), \
                 patch.object(assemble_video, "find_background_music_track", return_value=None):
                timing = {"sections": [{
                    "start_time_sec": 0, "end_time_sec": 1,
                    "narration": "A real test.", "duration_sec": 1
                }]}
                scenes = {"scenes": [{
                    "image_path": str(root / "still.png"), "duration_sec": 1
                }]}
                with self.assertRaisesRegex(RuntimeError, "FFmpeg is required"):
                    assemble_video.assemble_video(
                        "no_fake_video", timing_data=timing, scenes_data=scenes
                    )
                self.assertFalse((root / "videos" / "no_fake_video_final.mp4").exists())


if __name__ == "__main__":
    unittest.main()
