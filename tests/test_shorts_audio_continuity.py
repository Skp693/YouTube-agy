"""Tests that a finished Short still carries the original narration recording."""
import shutil
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np
from scripts.audio_continuity_qa import compare_audio


def make_wav(path, pattern, rate=16000):
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes((np.clip(pattern, -1, 1) * 32767).astype('<i2').tobytes())


@unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required')
class AudioContinuityTest(unittest.TestCase):
    def test_identical_master_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rate = 16000
            t = np.arange(3*rate)/rate
            rng = np.random.default_rng(4)
            sound = 0.3 * np.sin(2*np.pi*(190+55*np.sin(t*7))*t) * (0.4 + 0.6*np.sin(t*3)**2)
            sound += 0.017 * rng.normal(size=len(t))
            master, output = root/'a.wav', root/'b.wav'
            make_wav(master, sound)
            make_wav(output, sound*0.7)
            report = compare_audio(master, output)
            self.assertEqual(report['decision'], 'CONTINUITY_PASS')
            self.assertGreater(report['envelope_similarity'], 0.96)

    def test_unrelated_narration_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rate = 16000
            t = np.arange(3*rate)/rate
            rng = np.random.default_rng(6)
            a = rng.normal(0, 0.13, len(t)) * (np.sin(t*4)**2)
            b = rng.normal(0, 0.13, len(t)) * (np.cos(t*9)**2)
            p, q = root/'original.wav', root/'other.wav'
            make_wav(p, a)
            make_wav(q, b)
            report = compare_audio(p, q)
            self.assertEqual(report['decision'], 'BLOCK')
            self.assertLess(report['envelope_similarity'], 0.90)

    def test_no_audio_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            good = root/'master.wav'
            make_wav(good, np.zeros(16000*3))
            bad = root/'fake.mp4'
            bad.write_bytes(b'fake')
            with self.assertRaises(RuntimeError):
                compare_audio(good, bad)

    def test_silence_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p, q = root/'a.wav', root/'b.wav'
            make_wav(p, np.zeros(16000*3))
            make_wav(q, np.zeros(16000*3))
            self.assertEqual(compare_audio(p, q)['decision'], 'BLOCK')


if __name__ == '__main__':
    unittest.main()
