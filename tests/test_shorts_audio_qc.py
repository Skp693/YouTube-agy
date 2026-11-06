"""No-cost, deterministic checks for Shorts audio preflight."""
import math
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np
from scripts.shorts_audio_qc import inspect_audio


def save_wav(path, data, rate=16000):
    x = np.clip(data, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((x * 32767).astype("<i2").tobytes())


class TestAudioQC(unittest.TestCase):
    def test_silence_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "silence.wav"
            save_wav(p, np.zeros(16000 * 3))
            report = inspect_audio(p)
            self.assertEqual(report["decision"], "BLOCK")
            self.assertIn("SILENCE", report["flags"])

    def test_harmonic_robot_tone_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            rate = 16000
            t = np.arange(rate * 3) / rate
            sample = (0.6 * np.sin(2*math.pi*180*t) +
                      0.25*np.sin(2*math.pi*360*t) +
                      0.15*np.sin(2*math.pi*540*t)) * 0.25
            p = Path(tmp) / "tone.wav"
            save_wav(p, sample)
            report = inspect_audio(p)
            self.assertEqual(report["decision"], "BLOCK")
            self.assertIn("POSSIBLE_SYNTHETIC_TONE", report["flags"])

    def test_broadband_signal_requires_manual_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "noise.wav"
            save_wav(p, np.random.default_rng(42).normal(0, 0.1, 16000*3))
            report = inspect_audio(p)
            self.assertEqual(report["decision"], "HUMAN_REVIEW_REQUIRED")
            self.assertFalse(report["is_natural_voice_verified"])

    def test_invalid_media_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "broken.mp4"
            p.write_bytes(b"not a real mp4")
            with self.assertRaises(RuntimeError):
                inspect_audio(p)


if __name__ == "__main__":
    unittest.main()
